"""
auth_service.py - Servicio de autenticacion contra la API REST.

Encapsula la logica de login: envia las credenciales a la API,
recibe el token JWT, carga los roles del usuario y calcula las
rutas permitidas segun esos roles.

La verificacion BCrypt ocurre del lado de la API (no aqui).
"""

import requests

from config import API_BASE_URL


# Configuracion de la tabla de usuarios contra la cual se autentica.
TABLA_USUARIOS = "usuario"
CAMPO_USUARIO = "username"
CAMPO_CONTRASENA = "password"
CAMPO_EMAIL = "email"


# ──────────────────────────────────────────────
# RUTAS DEL SISTEMA Y REGLAS POR ROL
# ──────────────────────────────────────────────
# Lista de todas las rutas (paths) que existen en el frontend Flask.
# Se usa como universo para calcular las rutas permitidas por rol.
RUTAS_DISPONIBLES = [
    "/",
    "/termino_clave",
    "/tipo_producto",
    "/proyecto",
    "/palabras_clave",
    "/aa_proyecto",
    "/ods_proyecto",
    "/proyecto_linea",
    "/ac_proyecto",
    "/docente_producto",
    "/aliado_proyecto",
    "/desarrolla",
]


def calcular_rutas_permitidas(roles):
    """
    Dado un conjunto de roles del usuario, devuelve la lista de rutas
    a las que puede acceder.

    Reglas:
        - Admin                -> todas las rutas
        - EncargadoProyectos   -> home + rutas que contengan 'proyecto'
        - Visitante            -> home + /proyecto

    Si un usuario tiene varios roles, se UNEN sus permisos.
    """
    permitidas = set()

    for rol in roles:
        if rol == "Admin":
            permitidas.update(RUTAS_DISPONIBLES)

        elif rol == "EncargadoProyectos":
            permitidas.add("/")
            permitidas.update(r for r in RUTAS_DISPONIBLES if "proyecto" in r)

        elif rol == "Visitante":
            permitidas.update(["/", "/proyecto"])

    return sorted(permitidas)


class AuthService:
    """
    Servicio responsable de autenticar al usuario contra la API,
    cargar sus roles y calcular sus rutas permitidas.

    Metodos publicos:
        login(usuario, contrasena)
            -> (exito, dict_con_token_roles_rutas) o (False, mensaje)
        actualizar_contrasena(usuario, nueva, token)
            -> (exito, mensaje)
    """

    def __init__(self):
        self.base_url = API_BASE_URL

    # ──────────────────────────────────────────────
    # LOGIN: POST /api/Autenticacion/token + carga de roles
    # ──────────────────────────────────────────────
    def login(self, usuario, contrasena):
        """
        Autentica al usuario, obtiene el token JWT y carga sus roles.

        Returns:
            Tupla (exito: bool, datos_o_mensaje)
            En exito: dict con 'token', 'usuario', 'expiracion', 'roles',
                      'rutas_permitidas'.
        """
        try:
            url = f"{self.base_url}/api/Autenticacion/token"

            payload = {
                "tabla": TABLA_USUARIOS,
                "campoUsuario": CAMPO_USUARIO,
                "campoContrasena": CAMPO_CONTRASENA,
                "usuario": usuario,
                "contrasena": contrasena,
            }

            respuesta = requests.post(url, json=payload)
            contenido = respuesta.json()

            if not respuesta.ok:
                mensaje = contenido.get("mensaje", "Credenciales invalidas.")
                return (False, mensaje)

            token = contenido.get("token", "")

            # Cargar los roles del usuario usando el JWT recien obtenido.
            roles = self._obtener_roles(usuario, token)
            rutas_permitidas = calcular_rutas_permitidas(roles)

            return (True, {
                "token": token,
                "usuario": contenido.get("usuario", usuario),
                "expiracion": contenido.get("expiracion"),
                "roles": roles,
                "rutas_permitidas": rutas_permitidas,
            })

        except requests.RequestException as ex:
            return (False, f"Error de conexion con la API: {ex}")
        except ValueError as ex:
            return (False, f"Respuesta invalida de la API: {ex}")

    # ──────────────────────────────────────────────
    # OBTENER ROLES: consulta SQL via ConsultasController
    # ──────────────────────────────────────────────
    def _obtener_roles(self, username, token):
        """
        Consulta la BD para obtener los nombres de los roles del usuario.

        Hace JOIN entre usuario, rol_usuario y rol en UNA sola peticion HTTP.
        Si la consulta falla, devuelve [] (sin roles -> sin rutas).
        """
        url = f"{self.base_url}/api/consultas/ejecutarconsultaparametrizada"

        consulta = (
            'SELECT r."nombre" '
            'FROM "usuario" u '
            'JOIN "rol_usuario" ru ON u."id" = ru."usuario_id" '
            'JOIN "rol" r ON ru."rol_id" = r."id" '
            'WHERE u."username" = @username'
        )

        payload = {
            "consulta": consulta,
            "parametros": {"username": username},
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        try:
            respuesta = requests.post(url, json=payload, headers=headers)

            # 404 = consulta valida pero sin filas (usuario sin roles).
            if respuesta.status_code == 404:
                return []

            if not respuesta.ok:
                return []

            contenido = respuesta.json()
            # La API serializa con camelCase: { "resultados": [...] }
            resultados = contenido.get("resultados") or contenido.get("Resultados") or []

            roles = []
            for fila in resultados:
                nombre = fila.get("nombre") or fila.get("Nombre")
                if nombre:
                    roles.append(nombre)

            return roles

        except (requests.RequestException, ValueError):
            return []

    # ──────────────────────────────────────────────
    # ACTUALIZAR CONTRASENA: PUT /api/usuario/username/{user}?camposEncriptar=password
    # ──────────────────────────────────────────────
    def actualizar_contrasena(self, usuario, nueva_contrasena, token):
        """
        Cambia la contrasena del usuario. La API se encarga de hashearla con BCrypt
        gracias al parametro camposEncriptar=password.

        Returns:
            Tupla (exito: bool, mensaje: str)
        """
        try:
            url = f"{self.base_url}/api/{TABLA_USUARIOS}/{CAMPO_USUARIO}/{usuario}"
            params = {"camposEncriptar": CAMPO_CONTRASENA}
            datos = {CAMPO_CONTRASENA: nueva_contrasena}
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            }

            respuesta = requests.put(url, json=datos, params=params, headers=headers)
            contenido = respuesta.json() if respuesta.content else {}
            mensaje = contenido.get("mensaje", "Operacion completada.")
            return (respuesta.ok, mensaje)

        except requests.RequestException as ex:
            return (False, f"Error de conexion con la API: {ex}")
        except ValueError as ex:
            return (False, f"Respuesta invalida de la API: {ex}")

    # ──────────────────────────────────────────────
    # RESTABLECER CONTRASENA: POST /api/Autenticacion/restablecer-contrasena
    # Endpoint publico ([AllowAnonymous]) que verifica usuario+email
    # contra la BD y actualiza la contrasena con encriptacion BCrypt.
    # ──────────────────────────────────────────────
    def restablecer_contrasena(self, usuario, email, nueva_contrasena):
        """
        Restablece la contrasena de un usuario que olvido su clave.

        La API verifica que el email coincida con el registrado para el usuario
        antes de actualizar. La nueva contrasena se guarda hasheada con BCrypt.

        Returns:
            Tupla (exito: bool, mensaje: str)
        """
        try:
            url = f"{self.base_url}/api/Autenticacion/restablecer-contrasena"
            payload = {
                "tabla": TABLA_USUARIOS,
                "campoUsuario": CAMPO_USUARIO,
                "campoEmail": CAMPO_EMAIL,
                "campoContrasena": CAMPO_CONTRASENA,
                "usuario": usuario,
                "email": email,
                "nuevaContrasena": nueva_contrasena,
            }

            # Este endpoint NO requiere token JWT (es publico).
            respuesta = requests.post(url, json=payload)

            # Intentar parsear el body como JSON. Si la API devuelve HTML
            # (ej: pagina de error de IIS), .json() lanza ValueError.
            contenido = None
            try:
                if respuesta.content:
                    contenido = respuesta.json()
            except ValueError:
                contenido = None

            # Buscar el mensaje en varias claves posibles: la API propia
            # usa 'mensaje', pero ProblemDetails de ASP.NET usa 'title' o 'detail'.
            mensaje = ""
            if isinstance(contenido, dict):
                mensaje = (
                    contenido.get("mensaje")
                    or contenido.get("message")
                    or contenido.get("detalle")
                    or contenido.get("detail")
                    or contenido.get("title")
                    or ""
                )

            # Caso exito: usar el mensaje devuelto o uno por defecto.
            if respuesta.ok:
                return (True, mensaje or "Contrasena restablecida exitosamente.")

            # Caso error: construir mensaje descriptivo cuando la API no
            # devuelve un campo 'mensaje' claro (ej: 404 por endpoint
            # inexistente porque la API aun no se reinicio).
            if not mensaje:
                if respuesta.status_code == 404:
                    mensaje = (
                        "Endpoint no encontrado en la API (HTTP 404). "
                        "Si modifico la API recientemente, reiniciela para "
                        "que cargue el nuevo endpoint."
                    )
                else:
                    cuerpo = (respuesta.text or "").strip()[:200]
                    mensaje = f"Error HTTP {respuesta.status_code}."
                    if cuerpo:
                        mensaje += f" Respuesta: {cuerpo}"

            return (False, mensaje)

        except requests.RequestException as ex:
            return (False, f"Error de conexion con la API: {ex}")

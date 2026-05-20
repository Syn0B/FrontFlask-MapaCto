"""
auth_middleware.py - Middleware de autenticacion y autorizacion.

Intercepta CADA peticion HTTP antes de procesarla:
    1. Si la ruta es publica (/login, /static), deja pasar.
    2. Si no hay sesion, redirige a /login.
    3. Si la ruta esta en rutas_permitidas (o es ruta de cuenta), permite.
    4. En caso contrario, muestra la pagina de acceso denegado (403).

Se registra en app.py con:
    crear_middleware(app)
"""

from flask import session, redirect, url_for, request, render_template


# Rutas a las que se puede acceder SIN estar autenticado.
# /restablecer-contrasena es publica porque por definicion el usuario que la usa
# no recuerda su contrasena y no puede hacer login.
RUTAS_PUBLICAS = ("/login", "/static", "/restablecer-contrasena")

# Rutas que cualquier usuario autenticado puede acceder, independientemente
# de los roles que tenga (cuenta personal, logout).
RUTAS_AUTENTICADO_SIEMPRE = ("/logout", "/cambiar-contrasena")


def _ruta_permitida(path, rutas_permitidas):
    """
    Verifica si el path actual esta cubierto por la lista de rutas permitidas.

    Una ruta esta permitida si coincide exactamente con una de la lista o si
    es una sub-ruta (ej: /proyecto/ver/3 esta cubierta por /proyecto).
    """
    # Home (/) requiere comparacion exacta para no cubrir TODO el sitio.
    if path == "/":
        return "/" in rutas_permitidas

    for ruta in rutas_permitidas:
        if ruta == "/":
            continue
        if path == ruta or path.startswith(ruta + "/"):
            return True

    return False


def crear_middleware(app):
    """
    Registra el middleware before_request en la aplicacion Flask.
    """

    @app.before_request
    def verificar_autenticacion():
        # 1. Rutas publicas: dejar pasar sin verificar sesion.
        if any(request.path.startswith(ruta) for ruta in RUTAS_PUBLICAS):
            return None

        # 2. Si no hay sesion, redirigir a /login.
        if not session.get("usuario"):
            return redirect(url_for("auth.login"))

        # 3. Rutas de cuenta (logout, cambiar contrasena): siempre permitidas.
        if any(request.path.startswith(ruta) for ruta in RUTAS_AUTENTICADO_SIEMPRE):
            return None

        # 4. Verificar contra rutas_permitidas calculadas en login.
        rutas_permitidas = session.get("rutas_permitidas", [])

        if _ruta_permitida(request.path, rutas_permitidas):
            return None

        # 5. Ruta no permitida -> pagina 403.
        return render_template("pages/sin_acceso.html"), 403

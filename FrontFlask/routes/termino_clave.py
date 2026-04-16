"""
termino_clave.py - Blueprint con las rutas CRUD para la tabla Termino Clave.

Campos de la tabla:
    - termino    (clave primaria, texto)
    - termino_ingles    (texto)

Rutas:
    GET  /termino_clave              →  Listar registros y mostrar formulario si corresponde
    POST /termino_clave/crear        →  Crear un nuevo registro
    POST /termino_clave/actualizar   →  Actualizar un registro existente
    POST /termino_clave/eliminar     →  Eliminar un registro
"""

# Importar las funciones necesarias de Flask
from flask import Blueprint, render_template, request, redirect, url_for, flash

# Servicio generico para las llamadas HTTP a la API REST
from services.api_service import ApiService


# ══════════════════════════════════════════════
# CONFIGURACION DEL BLUEPRINT
# ══════════════════════════════════════════════

# Crear Blueprint con nombre 'termino_clave' → se usa en url_for('termino_clave.index')
bp = Blueprint('termino_clave', __name__)

# Instancia del servicio CRUD para comunicarse con la API
api = ApiService()

# Nombre de la tabla en la API
TABLA = 'termino_clave'

# Nombre del campo clave primaria
CLAVE = 'termino'


# ══════════════════════════════════════════════
# LISTAR REGISTROS (GET)
# ══════════════════════════════════════════════

# Responde a GET /termino_clave
@bp.route('/termino_clave')
def index():
    """Muestra la tabla de terminos clave con formulario opcional."""
    # Leer parametros de la URL (query string)
    limite = request.args.get('limite', type=int)       # Limite de registros (entero o None)
    accion = request.args.get('accion', '')              # 'nuevo', 'editar' o '' (vacio)
    valor_clave = request.args.get('clave', '')          # Valor de la PK para editar

    # Obtener registros de la API
    registros = api.listar(TABLA, limite)

    # Determinar estado del formulario
    mostrar_formulario = accion in ('nuevo', 'editar')   # True si hay que mostrar formulario
    editando = accion == 'editar'                        # True solo en modo edicion

    # Buscar el registro a editar en la lista (si aplica)
    registro = None
    if editando and valor_clave:
        # Buscar el primer registro cuyo 'codigo' coincida con valor_clave
        registro = next(
            (r for r in registros if str(r.get(CLAVE)) == valor_clave),
            None  # Retorna None si no encuentra coincidencia
        )

    # Renderizar la pagina pasando las variables al template
    return render_template('pages/termino_clave.html',
        registros=registros,                  # Lista de terminos clave para la tabla HTML
        mostrar_formulario=mostrar_formulario, # Controla visibilidad del formulario
        editando=editando,                     # Controla modo crear vs editar
        registro=registro,                     # Datos del registro a editar (o None)
        limite=limite                          # Mantener el valor de limite en el input
    )


# ══════════════════════════════════════════════
# CREAR REGISTRO (POST)
# ══════════════════════════════════════════════

# Solo acepta peticiones POST (envio de formulario)
@bp.route('/termino_clave/crear', methods=['POST'])
def crear():
    """Crea un nuevo registro de termino clave."""
    # Leer los 4 campos del formulario y armar el diccionario de datos.
    # Todos son tipo texto, no necesitan conversion de tipo.
    datos = {
        'termino':   request.form.get('termino', ''),    # Clave primaria
        'termino_ingles':   request.form.get('termino_ingles', ''),    # Nombre del termino en ingles
    }

    # Enviar POST a la API y obtener resultado
    exito, mensaje = api.crear(TABLA, datos)

    # Guardar alerta (verde si exito, roja si error) y redirigir al listado
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('termino_clave.index'))


# ══════════════════════════════════════════════
# ACTUALIZAR REGISTRO (POST)
# ══════════════════════════════════════════════

@bp.route('/termino_clave/actualizar', methods=['POST'])
def actualizar():
    """Actualiza un registro existente de termino clave."""
    # Leer la clave primaria del registro a actualizar
    valor = request.form.get('termino', '')

    # Campos editables (sin la clave primaria, que va en la URL)
    datos = {
        'termino_ingles':   request.form.get('termino_ingles', ''),    # Nuevo nombre en ingles
    }

    # Enviar PUT a la API: /api/termino_clave/termino/{valor}
    exito, mensaje = api.actualizar(TABLA, CLAVE, valor, datos)

    # Guardar alerta y redirigir
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('termino_clave.index'))


# ══════════════════════════════════════════════
# ELIMINAR REGISTRO (POST)
# ══════════════════════════════════════════════

@bp.route('/termino_clave/eliminar', methods=['POST'])
def eliminar():
    """Elimina un registro de termino clave."""
    # Leer la clave primaria desde el campo oculto del formulario de eliminar
    valor = request.form.get('termino', '')

    # Enviar DELETE a la API: /api/termino_clave/termino/{valor}
    exito, mensaje = api.eliminar(TABLA, CLAVE, valor)

    # Guardar alerta y redirigir
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('termino_clave.index'))

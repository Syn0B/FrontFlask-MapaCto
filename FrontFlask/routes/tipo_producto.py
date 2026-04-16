"""
tipo_producto.py - Blueprint con las rutas CRUD para la tabla Tipo Producto.

Campos de la tabla:
    - id    (clave primaria, texto)
    - categoria    (texto)
    - clase     (texto)
    - nombre  (texto)
    - tipologia  (texto)

Rutas:
    GET  /tipo_producto              →  Listar registros y mostrar formulario si corresponde
    POST /tipo_producto/crear        →  Crear un nuevo registro
    POST /tipo_producto/actualizar   →  Actualizar un registro existente
    POST /tipo_producto/eliminar     →  Eliminar un registro
"""

# Importar las funciones necesarias de Flask (ver empresa.py para detalle de cada una)
from flask import Blueprint, render_template, request, redirect, url_for, flash

# Servicio generico para las llamadas HTTP a la API REST
from services.api_service import ApiService


# ══════════════════════════════════════════════
# CONFIGURACION DEL BLUEPRINT
# ══════════════════════════════════════════════

# Crear Blueprint con nombre 'tipo_producto' → se usa en url_for('tipo_producto.index')
bp = Blueprint('tipo_producto', __name__)

# Instancia del servicio CRUD para comunicarse con la API
api = ApiService()

# Nombre de la tabla en la API
TABLA = 'tipo_producto'

# Nombre del campo clave primaria
CLAVE = 'id'



# ══════════════════════════════════════════════
# LISTAR REGISTROS (GET)
# ══════════════════════════════════════════════

# Responde a GET /tipo_producto
@bp.route('/tipo_producto')
def index():
    """Muestra la tabla de tipo_producto con formulario opcional."""
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
    return render_template('pages/tipo_producto.html',
        registros=registros,                  # Lista de tipo_producto para la tabla HTML
        mostrar_formulario=mostrar_formulario, # Controla visibilidad del formulario
        editando=editando,                     # Controla modo crear vs editar
        registro=registro,                     # Datos del registro a editar (o None)
        limite=limite                          # Mantener el valor de limite en el input
    )


# ══════════════════════════════════════════════
# CREAR REGISTRO (POST)
# ══════════════════════════════════════════════

# Solo acepta peticiones POST (envio de formulario)
@bp.route('/tipo_producto/crear', methods=['POST'])
def crear():
    """Crea un nuevo registro de tipo_producto."""
    # Leer los 4 campos del formulario y armar el diccionario de datos.
    # Todos son tipo texto, no necesitan conversion de tipo.
    datos = {
        'id':       request.form.get('id', ''),        # Clave primaria
        'categoria':   request.form.get('categoria', ''),
        'clase': request.form.get('clase', ''),
        'nombre': request.form.get('nombre', ''),
        'tipologia': request.form.get('tipologia', '')
    }

    # Enviar POST a la API y obtener resultado
    exito, mensaje = api.crear(TABLA, datos)

    # Guardar alerta (verde si exito, roja si error) y redirigir al listado
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('tipo_producto.index'))


# ══════════════════════════════════════════════
# ACTUALIZAR REGISTRO (POST)
# ══════════════════════════════════════════════

@bp.route('/tipo_producto/actualizar', methods=['POST'])
def actualizar():
    """Actualiza un registro existente de tipo_producto."""
    # Leer la clave primaria del registro a actualizar
    valor = request.form.get('id', '')

    # Campos editables (sin la clave primaria, que va en la URL)
    datos = {
        'categoria':   request.form.get('categoria', ''),    # Nuevo nombre
        'clase':    request.form.get('clase', ''),     # Nuevo email
        'nombre': request.form.get('nombre', ''),   # Nuevo telefono
        'tipologia': request.form.get('tipologia', '')
    }

    # Enviar PUT a la API: /api/tipo_producto/id/{valor}
    exito, mensaje = api.actualizar(TABLA, CLAVE, valor, datos)

    # Guardar alerta y redirigir
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('tipo_producto.index'))


# ══════════════════════════════════════════════
# ELIMINAR REGISTRO (POST)
# ══════════════════════════════════════════════

@bp.route('/tipo_producto/eliminar', methods=['POST'])
def eliminar():
    """Elimina un registro de tipo_producto."""
    # Leer la clave primaria desde el campo oculto del formulario de eliminar
    valor = request.form.get('id', '')

    # Enviar DELETE a la API: /api/tipo_producto/id/{valor}
    exito, mensaje = api.eliminar(TABLA, CLAVE, valor)

    # Guardar alerta y redirigir
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('tipo_producto.index'))

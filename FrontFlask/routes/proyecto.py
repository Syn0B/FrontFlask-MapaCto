"""
proyecto.py - Blueprint con las rutas CRUD para la tabla Proyecto.

Campos de la tabla:
    - id    (clave primaria, texto)
    - titulo    (texto)
    - resumen     (texto)
    - presupuesto  (texto)
    - tipo financiacion  (texto)
    - tipo fondos  (texto)
    - fecha inicio  (texto)
    - fecha fin  (texto)

Rutas:
    GET  /proyecto              →  Listar registros y mostrar formulario si corresponde
    POST /proyecto/crear        →  Crear un nuevo registro
    POST /proyecto/actualizar   →  Actualizar un registro existente
    POST /proyecto/eliminar     →  Eliminar un registro
"""

# Importar las funciones necesarias de Flask (ver empresa.py para detalle de cada una)
from flask import Blueprint, render_template, request, redirect, url_for, flash

# Servicio generico para las llamadas HTTP a la API REST
from services.api_service import ApiService

# Para manejo de fechas (llevarlas al template de manera que se visualicen)
from datetime import datetime


# ══════════════════════════════════════════════
# CONFIGURACION DEL BLUEPRINT
# ══════════════════════════════════════════════

# Crear Blueprint con nombre 'proyecto' → se usa en url_for('proyecto.index')
bp = Blueprint('proyecto', __name__)

# Instancia del servicio CRUD para comunicarse con la API
api = ApiService()

# Nombre de la tabla en la API
TABLA = 'proyecto'

# Nombre del campo clave primaria
CLAVE = 'id'


# ══════════════════════════════════════════════
# LISTAR REGISTROS (GET)
# ══════════════════════════════════════════════

# Responde a GET /proyecto
@bp.route('/proyecto')
def index():
    """Muestra la tabla de proyectos con formulario opcional."""
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

    # Convertir fechas a formato legible (solo para mostrar en la tabla)
    for r in registros:
        if r.get("fecha_inicio"):
            r["fecha_inicio"] = r["fecha_inicio"][:10]

        if r.get("fecha_fin"):
            r["fecha_fin"] = r["fecha_fin"][:10]

    # Renderizar la pagina pasando las variables al template
    return render_template('pages/proyecto.html',
        registros=registros,                  # Lista de proyectos para la tabla HTML
        mostrar_formulario=mostrar_formulario, # Controla visibilidad del formulario
        editando=editando,                     # Controla modo crear vs editar
        registro=registro,                     # Datos del registro a editar (o None)
        limite=limite                          # Mantener el valor de limite en el input
    )


# ══════════════════════════════════════════════
# CREAR REGISTRO (POST)
# ══════════════════════════════════════════════

# Solo acepta peticiones POST (envio de formulario)
@bp.route('/proyecto/crear', methods=['POST'])
def crear():
    """Crea un nuevo registro de proyecto."""
    # Leer los 4 campos del formulario y armar el diccionario de datos.
    # Todos son tipo texto, no necesitan conversion de tipo.
    datos = {
        'id':       request.form.get('id', ''),         # Clave primaria
        'titulo':   request.form.get('titulo', ''),     # Titulo del proyecto
        'resumen':   request.form.get('resumen', ''),
        'presupuesto':   request.form.get('presupuesto', ''),
        'tipo_financiacion':   request.form.get('tipo_financiacion', ''),
        'tipo_fondos':   request.form.get('tipo_fondos', ''),
        'fecha_inicio': request.form.get('fecha_inicio', ''),  # Fecha de inicio
        'fecha_fin': request.form.get('fecha_fin', '')   # Fecha de finalizacion
    }

    # Enviar POST a la API y obtener resultado
    exito, mensaje = api.crear(TABLA, datos)

    # Guardar alerta (verde si exito, roja si error) y redirigir al listado
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('proyecto.index'))


# ══════════════════════════════════════════════
# ACTUALIZAR REGISTRO (POST)
# ══════════════════════════════════════════════

@bp.route('/proyecto/actualizar', methods=['POST'])
def actualizar():
    """Actualiza un registro existente de proyecto."""
    # Leer la clave primaria del registro a actualizar
    valor = request.form.get('id', '')

    # Campos editables (sin la clave primaria, que va en la URL)
    datos = {
        'titulo':   request.form.get('titulo', ''),     # Nuevo titulo
        'resumen':   request.form.get('resumen', ''),
        'presupuesto':   request.form.get('presupuesto', ''),
        'tipo_financiacion':   request.form.get('tipo_financiacion', ''),
        'tipo_fondos':   request.form.get('tipo_fondos', ''),
        'fecha_inicio': request.form.get('fecha_inicio', ''),  # Nueva fecha de inicio
        'fecha_fin': request.form.get('fecha_fin', '')   # Nueva fecha de finalizacion
    }

    # Enviar PUT a la API: /api/proyecto/id/{valor}
    exito, mensaje = api.actualizar(TABLA, CLAVE, valor, datos)

    # Guardar alerta y redirigir
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('proyecto.index'))


# ══════════════════════════════════════════════
# ELIMINAR REGISTRO (POST)
# ══════════════════════════════════════════════

@bp.route('/proyecto/eliminar', methods=['POST'])
def eliminar():
    """Elimina un registro de proyecto."""
    # Leer la clave primaria desde el campo oculto del formulario de eliminar
    valor = request.form.get('id', '')

    # Enviar DELETE a la API: /api/proyecto/id/{valor}
    exito, mensaje = api.eliminar(TABLA, CLAVE, valor)

    # Guardar alerta y redirigir
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('proyecto.index'))

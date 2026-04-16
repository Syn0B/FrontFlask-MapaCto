"""
ods_proyecto.py - Blueprint con las rutas para la tabla intermedia ods_proyecto.

Tabla intermedia (relacion N:M) entre proyecto y ods.

Campos:
    - proyecto  (entero, FK -> proyecto.id)
    - ods       (entero, FK -> ods.id)

Clave primaria compuesta: (proyecto, ods)

Como es una tabla intermedia pura, no tiene sentido "actualizar":
cualquier cambio en uno de los dos campos genera un registro distinto.
Por eso solo se exponen CREAR y ELIMINAR.

Rutas:
    GET  /ods_proyecto           -> Listar registros y mostrar formulario si corresponde
    POST /ods_proyecto/crear     -> Crear un nuevo registro
    POST /ods_proyecto/eliminar  -> Eliminar un registro (PK compuesta)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.api_service import ApiService


# ══════════════════════════════════════════════
# CONFIGURACION DEL BLUEPRINT
# ══════════════════════════════════════════════

bp = Blueprint('ods_proyecto', __name__)
api = ApiService()

TABLA = 'ods_proyecto'


# ══════════════════════════════════════════════
# LISTAR REGISTROS (GET)
# ══════════════════════════════════════════════

@bp.route('/ods_proyecto')
def index():
    """Muestra la tabla de ods_proyecto con formulario opcional."""
    # Parametros de la URL
    limite = request.args.get('limite', type=int)
    accion = request.args.get('accion', '')   # 'nuevo' o '' (vacio)

    # Registros de la tabla intermedia
    registros = api.listar(TABLA, limite)

    # Cargar las tablas relacionadas para los <select> del formulario.
    # Se traen SIN limite para tener todas las opciones disponibles.
    proyectos = api.listar('proyecto', None) or []
    ods_lista  = api.listar('objetivo_desarrollo_sostenible', None) or []

    # Solo hay modo "nuevo": no existe edicion en una tabla intermedia pura
    mostrar_formulario = accion == 'nuevo'

    return render_template('pages/ods_proyecto.html',
        registros=registros,                  # Lista de ods_proyecto para la tabla HTML
        proyectos=proyectos,                  # Para el <select> de proyecto
        ods_lista=ods_lista,                  # Para el <select> de ods
        mostrar_formulario=mostrar_formulario,
        limite=limite
    )


# ══════════════════════════════════════════════
# CREAR REGISTRO (POST)
# ══════════════════════════════════════════════

@bp.route('/ods_proyecto/crear', methods=['POST'])
def crear():
    """Crea un nuevo registro en ods_proyecto."""
    # Los valores vienen de los <select>: ambos son el id (entero) del registro seleccionado.
    datos = {
        'proyecto': request.form.get('proyecto', ''),
        'ods':      request.form.get('ods', '')
    }

    exito, mensaje = api.crear(TABLA, datos)

    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('ods_proyecto.index'))


# ══════════════════════════════════════════════
# ELIMINAR REGISTRO (POST)
# ══════════════════════════════════════════════

@bp.route('/ods_proyecto/eliminar', methods=['POST'])
def eliminar():
    """Elimina un registro de ods_proyecto usando la PK compuesta."""
    # Los dos valores de la PK vienen en campos ocultos del formulario
    proyecto = request.form.get('proyecto', '')
    ods      = request.form.get('ods', '')

    # Para PK compuesta enviamos las dos columnas y los dos valores
    # separados por coma. El ApiService construye una URL del tipo:
    #   DELETE /api/ods_proyecto/proyecto/{p}/ods/{o}
    claves  = 'proyecto,ods'
    valores = f'{proyecto},{ods}'

    exito, mensaje = api.eliminar(TABLA, claves, valores)

    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('ods_proyecto.index'))

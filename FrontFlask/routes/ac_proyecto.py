"""
ac_proyecto.py - Blueprint con las rutas para la tabla intermedia ac_proyecto.

Tabla intermedia (relacion N:M) entre proyecto y area_conocimiento.

Campos:
    - proyecto           (entero, FK -> proyecto.id)
    - area_conocimiento  (entero, FK -> area_conocimiento.id)

Clave primaria compuesta: (proyecto, area_conocimiento)

Como es una tabla intermedia pura, no tiene sentido "actualizar":
cualquier cambio en uno de los dos campos genera un registro distinto.
Por eso solo se exponen CREAR y ELIMINAR.

Rutas:
    GET  /ac_proyecto           -> Listar registros y mostrar formulario si corresponde
    POST /ac_proyecto/crear     -> Crear un nuevo registro
    POST /ac_proyecto/eliminar  -> Eliminar un registro (PK compuesta)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.api_service import ApiService


# ══════════════════════════════════════════════
# CONFIGURACION DEL BLUEPRINT
# ══════════════════════════════════════════════

bp = Blueprint('ac_proyecto', __name__)
api = ApiService()

TABLA = 'ac_proyecto'


# ══════════════════════════════════════════════
# LISTAR REGISTROS (GET)
# ══════════════════════════════════════════════

@bp.route('/ac_proyecto')
def index():
    """Muestra la tabla de ac_proyecto con formulario opcional."""
    # Parametros de la URL
    limite = request.args.get('limite', type=int)
    accion = request.args.get('accion', '')   # 'nuevo' o '' (vacio)

    # Registros de la tabla intermedia
    registros = api.listar(TABLA, limite)

    # Cargar las tablas relacionadas para los <select> del formulario.
    # Se traen SIN limite para tener todas las opciones disponibles.
    proyectos           = api.listar('proyecto', None) or []
    areas_conocimiento  = api.listar('area_conocimiento', None) or []

    # Solo hay modo "nuevo": no existe edicion en una tabla intermedia pura
    mostrar_formulario = accion == 'nuevo'

    return render_template('pages/ac_proyecto.html',
        registros=registros,                        # Lista de ac_proyecto para la tabla HTML
        proyectos=proyectos,                        # Para el <select> de proyecto
        areas_conocimiento=areas_conocimiento,      # Para el <select> de area_conocimiento
        mostrar_formulario=mostrar_formulario,
        limite=limite
    )


# ══════════════════════════════════════════════
# CREAR REGISTRO (POST)
# ══════════════════════════════════════════════

@bp.route('/ac_proyecto/crear', methods=['POST'])
def crear():
    """Crea un nuevo registro en ac_proyecto."""
    # Los valores vienen de los <select>: ambos son el id (entero) del registro seleccionado.
    datos = {
        'proyecto':          request.form.get('proyecto', ''),
        'area_conocimiento': request.form.get('area_conocimiento', '')
    }

    exito, mensaje = api.crear(TABLA, datos)

    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('ac_proyecto.index'))


# ══════════════════════════════════════════════
# ELIMINAR REGISTRO (POST)
# ══════════════════════════════════════════════

@bp.route('/ac_proyecto/eliminar', methods=['POST'])
def eliminar():
    """Elimina un registro de ac_proyecto usando la PK compuesta."""
    # Los dos valores de la PK vienen en campos ocultos del formulario
    proyecto          = request.form.get('proyecto', '')
    area_conocimiento = request.form.get('area_conocimiento', '')

    # Para PK compuesta enviamos las dos columnas y los dos valores
    # separados por coma. El ApiService construye una URL del tipo:
    #   DELETE /api/ac_proyecto/proyecto/{p}/area_conocimiento/{a}
    claves  = 'proyecto,area_conocimiento'
    valores = f'{proyecto},{area_conocimiento}'

    exito, mensaje = api.eliminar(TABLA, claves, valores)

    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('ac_proyecto.index'))

"""
aa_proyecto.py - Blueprint con las rutas para la tabla intermedia aa_proyecto.

Tabla intermedia (relacion N:M) entre proyecto y area_aplicacion.

Campos:
    - proyecto         (entero, FK -> proyecto.id)
    - area_aplicacion  (entero, FK -> area_aplicacion.id)

Clave primaria compuesta: (proyecto, area_aplicacion)

Como es una tabla intermedia pura, no tiene sentido "actualizar":
cualquier cambio en uno de los dos campos genera un registro distinto.
Por eso solo se exponen CREAR y ELIMINAR.

Rutas:
    GET  /aa_proyecto           -> Listar registros y mostrar formulario si corresponde
    POST /aa_proyecto/crear     -> Crear un nuevo registro
    POST /aa_proyecto/eliminar  -> Eliminar un registro (PK compuesta)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.api_service import ApiService


# ══════════════════════════════════════════════
# CONFIGURACION DEL BLUEPRINT
# ══════════════════════════════════════════════

bp = Blueprint('aa_proyecto', __name__)
api = ApiService()

TABLA = 'aa_proyecto'


# ══════════════════════════════════════════════
# LISTAR REGISTROS (GET)
# ══════════════════════════════════════════════

@bp.route('/aa_proyecto')
def index():
    """Muestra la tabla de aa_proyecto con formulario opcional."""
    # Parametros de la URL
    limite = request.args.get('limite', type=int)
    accion = request.args.get('accion', '')   # 'nuevo' o '' (vacio)

    # Registros de la tabla intermedia
    registros = api.listar(TABLA, limite)

    # Cargar las tablas relacionadas para los <select> del formulario.
    # Se traen SIN limite para tener todas las opciones disponibles.
    proyectos        = api.listar('proyecto', None) or []
    areas_aplicacion = api.listar('area_aplicacion', None) or []

    # Solo hay modo "nuevo": no existe edicion en una tabla intermedia pura
    mostrar_formulario = accion == 'nuevo'

    return render_template('pages/aa_proyecto.html',
        registros=registros,                      # Lista de aa_proyecto para la tabla HTML
        proyectos=proyectos,                      # Para el <select> de proyecto
        areas_aplicacion=areas_aplicacion,        # Para el <select> de area_aplicacion
        mostrar_formulario=mostrar_formulario,
        limite=limite
    )


# ══════════════════════════════════════════════
# CREAR REGISTRO (POST)
# ══════════════════════════════════════════════

@bp.route('/aa_proyecto/crear', methods=['POST'])
def crear():
    """Crea un nuevo registro en aa_proyecto."""
    # Los valores vienen de los <select>: ambos son el id (entero) del registro seleccionado.
    datos = {
        'proyecto':        request.form.get('proyecto', ''),
        'area_aplicacion': request.form.get('area_aplicacion', '')
    }

    exito, mensaje = api.crear(TABLA, datos)

    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('aa_proyecto.index'))


# ══════════════════════════════════════════════
# ELIMINAR REGISTRO (POST)
# ══════════════════════════════════════════════

@bp.route('/aa_proyecto/eliminar', methods=['POST'])
def eliminar():
    """Elimina un registro de aa_proyecto usando la PK compuesta."""
    # Los dos valores de la PK vienen en campos ocultos del formulario
    proyecto        = request.form.get('proyecto', '')
    area_aplicacion = request.form.get('area_aplicacion', '')

    # Para PK compuesta enviamos las dos columnas y los dos valores
    # separados por coma. El ApiService construye una URL del tipo:
    #   DELETE /api/aa_proyecto/proyecto/{p}/area_aplicacion/{a}
    claves  = 'proyecto,area_aplicacion'
    valores = f'{proyecto},{area_aplicacion}'

    exito, mensaje = api.eliminar(TABLA, claves, valores)

    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('aa_proyecto.index'))

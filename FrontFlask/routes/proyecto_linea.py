"""
proyecto_linea.py - Blueprint con las rutas para la tabla intermedia proyecto_linea.

Tabla intermedia (relacion N:M) entre proyecto y linea_investigacion.

Campos:
    - proyecto            (entero, FK -> proyecto.id)
    - linea_investigacion (entero, FK -> linea_investigacion.id)

Clave primaria compuesta: (proyecto, linea_investigacion)

Como es una tabla intermedia pura, no tiene sentido "actualizar":
cualquier cambio en uno de los dos campos genera un registro distinto.
Por eso solo se exponen CREAR y ELIMINAR.

Rutas:
    GET  /proyecto_linea           -> Listar registros y mostrar formulario si corresponde
    POST /proyecto_linea/crear     -> Crear un nuevo registro
    POST /proyecto_linea/eliminar  -> Eliminar un registro (PK compuesta)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.api_service import ApiService


# ══════════════════════════════════════════════
# CONFIGURACION DEL BLUEPRINT
# ══════════════════════════════════════════════

bp = Blueprint('proyecto_linea', __name__)
api = ApiService()

TABLA = 'proyecto_linea'


# ══════════════════════════════════════════════
# LISTAR REGISTROS (GET)
# ══════════════════════════════════════════════

@bp.route('/proyecto_linea')
def index():
    """Muestra la tabla de proyecto_linea con formulario opcional."""
    limite = request.args.get('limite', type=int)
    accion = request.args.get('accion', '')   # 'nuevo' o '' (vacio)

    registros = api.listar(TABLA, limite)

    # Cargar tablas relacionadas para los <select> del formulario
    proyectos  = api.listar('proyecto', None) or []
    lineas     = api.listar('linea_investigacion', None) or []

    mostrar_formulario = accion == 'nuevo'

    return render_template('pages/proyecto_linea.html',
        registros=registros,
        proyectos=proyectos,
        lineas=lineas,
        mostrar_formulario=mostrar_formulario,
        limite=limite
    )


# ══════════════════════════════════════════════
# CREAR REGISTRO (POST)
# ══════════════════════════════════════════════

@bp.route('/proyecto_linea/crear', methods=['POST'])
def crear():
    """Crea un nuevo registro en proyecto_linea."""
    datos = {
        'proyecto':            request.form.get('proyecto', ''),
        'linea_investigacion': request.form.get('linea_investigacion', '')
    }

    exito, mensaje = api.crear(TABLA, datos)

    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('proyecto_linea.index'))


# ══════════════════════════════════════════════
# ELIMINAR REGISTRO (POST)
# ══════════════════════════════════════════════

@bp.route('/proyecto_linea/eliminar', methods=['POST'])
def eliminar():
    """Elimina un registro de proyecto_linea usando la PK compuesta."""
    proyecto            = request.form.get('proyecto', '')
    linea_investigacion = request.form.get('linea_investigacion', '')

    # DELETE /api/proyecto_linea/proyecto/{p}/linea_investigacion/{l}
    claves  = 'proyecto,linea_investigacion'
    valores = f'{proyecto},{linea_investigacion}'

    exito, mensaje = api.eliminar(TABLA, claves, valores)

    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('proyecto_linea.index'))

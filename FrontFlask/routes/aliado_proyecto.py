"""
aliado_proyecto.py - Blueprint con las rutas para la tabla intermedia aliado_proyecto.

Tabla intermedia (relacion N:M) entre aliado y proyecto.

Campos:
    - aliado    (entero, FK -> aliado.nit)
    - proyecto  (entero, FK -> proyecto.id)

Clave primaria compuesta: (aliado, proyecto)

Como es una tabla intermedia pura, no tiene sentido "actualizar":
cualquier cambio en uno de los dos campos genera un registro distinto.
Por eso solo se exponen CREAR y ELIMINAR.

Rutas:
    GET  /aliado_proyecto           -> Listar registros y mostrar formulario si corresponde
    POST /aliado_proyecto/crear     -> Crear un nuevo registro
    POST /aliado_proyecto/eliminar  -> Eliminar un registro (PK compuesta)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.api_service import ApiService


# ══════════════════════════════════════════════
# CONFIGURACION DEL BLUEPRINT
# ══════════════════════════════════════════════

bp = Blueprint('aliado_proyecto', __name__)
api = ApiService()

TABLA = 'aliado_proyecto'


# ══════════════════════════════════════════════
# LISTAR REGISTROS (GET)
# ══════════════════════════════════════════════

@bp.route('/aliado_proyecto')
def index():
    """Muestra la tabla de aliado_proyecto con formulario opcional."""
    # Parametros de la URL
    limite = request.args.get('limite', type=int)
    accion = request.args.get('accion', '')   # 'nuevo' o '' (vacio)

    # Registros de la tabla intermedia
    registros = api.listar(TABLA, limite)

    # Cargar las tablas relacionadas para los <select> del formulario.
    # Se traen SIN limite para tener todas las opciones disponibles.
    aliados   = api.listar('aliado', None) or []
    proyectos = api.listar('proyecto', None) or []

    # Solo hay modo "nuevo": no existe edicion en una tabla intermedia pura
    mostrar_formulario = accion == 'nuevo'

    return render_template('pages/aliado_proyecto.html',
        registros=registros,                  # Lista de aliado_proyecto para la tabla HTML
        aliados=aliados,                      # Para el <select> de aliado
        proyectos=proyectos,                  # Para el <select> de proyecto
        mostrar_formulario=mostrar_formulario,
        limite=limite
    )


# ══════════════════════════════════════════════
# CREAR REGISTRO (POST)
# ══════════════════════════════════════════════

@bp.route('/aliado_proyecto/crear', methods=['POST'])
def crear():
    """Crea un nuevo registro en aliado_proyecto."""
    # Los valores vienen de los <select>: ambos son el id (entero) del registro seleccionado.
    datos = {
        'aliado':   request.form.get('aliado', ''),
        'proyecto': request.form.get('proyecto', '')
    }

    exito, mensaje = api.crear(TABLA, datos)

    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('aliado_proyecto.index'))


# ══════════════════════════════════════════════
# ELIMINAR REGISTRO (POST)
# ══════════════════════════════════════════════

@bp.route('/aliado_proyecto/eliminar', methods=['POST'])
def eliminar():
    """Elimina un registro de aliado_proyecto usando la PK compuesta."""
    # Los dos valores de la PK vienen en campos ocultos del formulario
    aliado   = request.form.get('aliado', '')
    proyecto = request.form.get('proyecto', '')

    # Para PK compuesta enviamos las dos columnas y los dos valores
    # separados por coma. El ApiService construye una URL del tipo:
    #   DELETE /api/aliado_proyecto/aliado/{a}/proyecto/{p}
    claves  = 'aliado,proyecto'
    valores = f'{aliado},{proyecto}'

    exito, mensaje = api.eliminar(TABLA, claves, valores)

    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('aliado_proyecto.index'))

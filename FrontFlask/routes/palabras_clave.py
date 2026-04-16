"""
palabras_clave.py - Blueprint con las rutas para la tabla intermedia Palabras Clave.

Tabla intermedia (relacion N:M) entre proyecto y termino_clave.

Campos:
    - proyecto       (entero, FK -> proyecto.id)
    - termino_clave  (texto,  FK -> termino_clave.termino)

Clave primaria compuesta: (proyecto, termino_clave)

Como es una tabla intermedia pura, no tiene sentido "actualizar":
cualquier cambio en uno de los dos campos genera un registro distinto.
Por eso solo se exponen CREAR y ELIMINAR.

Rutas:
    GET  /palabras_clave           -> Listar registros y mostrar formulario si corresponde
    POST /palabras_clave/crear     -> Crear un nuevo registro
    POST /palabras_clave/eliminar  -> Eliminar un registro (PK compuesta)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.api_service import ApiService


# ══════════════════════════════════════════════
# CONFIGURACION DEL BLUEPRINT
# ══════════════════════════════════════════════

bp = Blueprint('palabras_clave', __name__)
api = ApiService()

TABLA = 'palabras_clave'


# ══════════════════════════════════════════════
# LISTAR REGISTROS (GET)
# ══════════════════════════════════════════════

@bp.route('/palabras_clave')
def index():
    """Muestra la tabla de palabras_clave con formulario opcional."""
    # Parametros de la URL
    limite = request.args.get('limite', type=int)
    accion = request.args.get('accion', '')   # 'nuevo' o '' (vacio)

    # Registros de la tabla intermedia
    registros = api.listar(TABLA, limite)

    # Cargar las tablas relacionadas para los <select> del formulario.
    # Se traen SIN limite para tener todas las opciones disponibles.
    proyectos = api.listar('proyecto', None) or []
    terminos  = api.listar('termino_clave', None) or []

    # Solo hay modo "nuevo": no existe edicion en una tabla intermedia pura
    mostrar_formulario = accion == 'nuevo'

    return render_template('pages/palabras_clave.html',
        registros=registros,                  # Lista de palabras_clave para la tabla HTML
        proyectos=proyectos,                  # Para el <select> de proyecto
        terminos=terminos,                    # Para el <select> de termino_clave
        mostrar_formulario=mostrar_formulario,
        limite=limite
    )


# ══════════════════════════════════════════════
# CREAR REGISTRO (POST)
# ══════════════════════════════════════════════

@bp.route('/palabras_clave/crear', methods=['POST'])
def crear():
    """Crea un nuevo registro en palabras_clave."""
    # Los valores vienen de los <select>: 'proyecto' es el id del proyecto
    # y 'termino_clave' es el termino (texto) seleccionado.
    datos = {
        'proyecto':      request.form.get('proyecto', ''),
        'termino_clave': request.form.get('termino_clave', '')
    }

    exito, mensaje = api.crear(TABLA, datos)

    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('palabras_clave.index'))


# ══════════════════════════════════════════════
# ELIMINAR REGISTRO (POST)
# ══════════════════════════════════════════════

@bp.route('/palabras_clave/eliminar', methods=['POST'])
def eliminar():
    """Elimina un registro de palabras_clave usando la PK compuesta."""
    # Los dos valores de la PK vienen en campos ocultos del formulario
    proyecto      = request.form.get('proyecto', '')
    termino_clave = request.form.get('termino_clave', '')

    # Para PK compuesta enviamos las dos columnas y los dos valores
    # separados por coma. El ApiService debe construir una URL del tipo:
    #   DELETE /api/palabras_clave/proyecto/{p}/termino_clave/{t}
    claves  = 'proyecto,termino_clave'
    valores = f'{proyecto},{termino_clave}'

    exito, mensaje = api.eliminar(TABLA, claves, valores)

    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('palabras_clave.index'))
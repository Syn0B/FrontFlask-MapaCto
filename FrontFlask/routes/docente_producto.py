"""
docente_producto.py - Blueprint con las rutas para la tabla intermedia docente_producto.

Tabla intermedia (relacion N:M) entre docente y producto.

Campos:
    - docente   (entero, FK -> docente.cedula)
    - producto  (entero, FK -> producto.id)

Clave primaria compuesta: (docente, producto)

Como es una tabla intermedia pura, no tiene sentido "actualizar":
cualquier cambio en uno de los dos campos genera un registro distinto.
Por eso solo se exponen CREAR y ELIMINAR.

Rutas:
    GET  /docente_producto           -> Listar registros y mostrar formulario si corresponde
    POST /docente_producto/crear     -> Crear un nuevo registro
    POST /docente_producto/eliminar  -> Eliminar un registro (PK compuesta)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.api_service import ApiService


# ══════════════════════════════════════════════
# CONFIGURACION DEL BLUEPRINT
# ══════════════════════════════════════════════

bp = Blueprint('docente_producto', __name__)
api = ApiService()

TABLA = 'docente_producto'


# ══════════════════════════════════════════════
# LISTAR REGISTROS (GET)
# ══════════════════════════════════════════════

@bp.route('/docente_producto')
def index():
    """Muestra la tabla de docente_producto con formulario opcional."""
    # Parametros de la URL
    limite = request.args.get('limite', type=int)
    accion = request.args.get('accion', '')   # 'nuevo' o '' (vacio)

    # Registros de la tabla intermedia
    registros = api.listar(TABLA, limite)

    # Cargar las tablas relacionadas para los <select> del formulario.
    # Se traen SIN limite para tener todas las opciones disponibles.
    docentes  = api.listar('docente', None) or []
    productos = api.listar('producto', None) or []

    # Solo hay modo "nuevo": no existe edicion en una tabla intermedia pura
    mostrar_formulario = accion == 'nuevo'

    return render_template('pages/docente_producto.html',
        registros=registros,                  # Lista de docente_producto para la tabla HTML
        docentes=docentes,                    # Para el <select> de docente
        productos=productos,                  # Para el <select> de producto
        mostrar_formulario=mostrar_formulario,
        limite=limite
    )


# ══════════════════════════════════════════════
# CREAR REGISTRO (POST)
# ══════════════════════════════════════════════

@bp.route('/docente_producto/crear', methods=['POST'])
def crear():
    """Crea un nuevo registro en docente_producto."""
    # Los valores vienen de los <select>: ambos son el id (entero) del registro seleccionado.
    datos = {
        'docente':  request.form.get('docente', ''),
        'producto': request.form.get('producto', '')
    }

    exito, mensaje = api.crear(TABLA, datos)

    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('docente_producto.index'))


# ══════════════════════════════════════════════
# ELIMINAR REGISTRO (POST)
# ══════════════════════════════════════════════

@bp.route('/docente_producto/eliminar', methods=['POST'])
def eliminar():
    """Elimina un registro de docente_producto usando la PK compuesta."""
    # Los dos valores de la PK vienen en campos ocultos del formulario
    docente  = request.form.get('docente', '')
    producto = request.form.get('producto', '')

    # Para PK compuesta enviamos las dos columnas y los dos valores
    # separados por coma. El ApiService construye una URL del tipo:
    #   DELETE /api/docente_producto/docente/{d}/producto/{p}
    claves  = 'docente,producto'
    valores = f'{docente},{producto}'

    exito, mensaje = api.eliminar(TABLA, claves, valores)

    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('docente_producto.index'))

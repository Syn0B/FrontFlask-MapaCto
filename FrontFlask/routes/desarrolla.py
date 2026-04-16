"""
desarrolla.py - Blueprint con las rutas CRUD para la tabla intermedia desarrolla.

Tabla intermedia (relacion N:M) entre docente y proyecto.

Campos:
    - docente     (entero, FK -> docente.cedula)  — parte de la PK compuesta
    - proyecto    (entero, FK -> proyecto.id)     — parte de la PK compuesta
    - rol         (texto, VARCHAR(45))            — campo editable
    - descripcion (texto, VARCHAR(256))           — campo editable

Clave primaria compuesta: (docente, proyecto)

A diferencia de otras tablas intermedias puras, esta tiene campos adicionales
(rol, descripcion) que si pueden editarse sin alterar la identidad del registro.
Por eso se exponen CREAR, ACTUALIZAR y ELIMINAR.

Rutas:
    GET  /desarrolla              -> Listar registros y mostrar formulario si corresponde
    POST /desarrolla/crear        -> Crear un nuevo registro
    POST /desarrolla/actualizar   -> Actualizar rol y descripcion de un registro existente
    POST /desarrolla/eliminar     -> Eliminar un registro (PK compuesta)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.api_service import ApiService


# ══════════════════════════════════════════════
# CONFIGURACION DEL BLUEPRINT
# ══════════════════════════════════════════════

bp = Blueprint('desarrolla', __name__)
api = ApiService()

TABLA = 'desarrolla'


# ══════════════════════════════════════════════
# LISTAR REGISTROS (GET)
# ══════════════════════════════════════════════

@bp.route('/desarrolla')
def index():
    """Muestra la tabla de desarrolla con formulario opcional (crear o editar)."""
    # Parametros de la URL
    limite        = request.args.get('limite', type=int)
    accion        = request.args.get('accion', '')        # 'nuevo', 'editar' o ''
    clave_docente  = request.args.get('clave_docente', '')  # PK parte 1 para editar
    clave_proyecto = request.args.get('clave_proyecto', '') # PK parte 2 para editar

    # Registros de la tabla intermedia
    registros = api.listar(TABLA, limite)

    # Cargar tablas relacionadas para los <select> del formulario
    docentes  = api.listar('docente', None)  or []
    proyectos = api.listar('proyecto', None) or []

    # Determinar modo del formulario
    mostrar_formulario = accion in ('nuevo', 'editar')
    editando           = accion == 'editar'

    # Buscar el registro a editar en la lista cargada (si aplica)
    registro = None
    if editando and clave_docente and clave_proyecto:
        registro = next(
            (r for r in registros
             if str(r.get('docente'))  == clave_docente
             and str(r.get('proyecto')) == clave_proyecto),
            None
        )

    return render_template('pages/desarrolla.html',
        registros=registros,
        docentes=docentes,
        proyectos=proyectos,
        mostrar_formulario=mostrar_formulario,
        editando=editando,
        registro=registro,
        limite=limite
    )


# ══════════════════════════════════════════════
# CREAR REGISTRO (POST)
# ══════════════════════════════════════════════

@bp.route('/desarrolla/crear', methods=['POST'])
def crear():
    """Crea un nuevo registro en desarrolla."""
    datos = {
        'docente':     request.form.get('docente', ''),
        'proyecto':    request.form.get('proyecto', ''),
        'rol':         request.form.get('rol', ''),
        'descripcion': request.form.get('descripcion', '')
    }

    exito, mensaje = api.crear(TABLA, datos)

    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('desarrolla.index'))


# ══════════════════════════════════════════════
# ACTUALIZAR REGISTRO (POST)
# ══════════════════════════════════════════════

@bp.route('/desarrolla/actualizar', methods=['POST'])
def actualizar():
    """Actualiza rol y descripcion de un registro existente de desarrolla."""
    # Las dos partes de la PK vienen como campos ocultos
    docente  = request.form.get('docente', '')
    proyecto = request.form.get('proyecto', '')

    # Solo se actualizan los campos que no son parte de la PK
    datos = {
        'rol':         request.form.get('rol', ''),
        'descripcion': request.form.get('descripcion', '')
    }

    # PK compuesta: docente/X/proyecto/Y
    claves  = 'docente,proyecto'
    valores = f'{docente},{proyecto}'

    exito, mensaje = api.actualizar(TABLA, claves, valores, datos)

    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('desarrolla.index'))


# ══════════════════════════════════════════════
# ELIMINAR REGISTRO (POST)
# ══════════════════════════════════════════════

@bp.route('/desarrolla/eliminar', methods=['POST'])
def eliminar():
    """Elimina un registro de desarrolla usando la PK compuesta."""
    docente  = request.form.get('docente', '')
    proyecto = request.form.get('proyecto', '')

    claves  = 'docente,proyecto'
    valores = f'{docente},{proyecto}'

    exito, mensaje = api.eliminar(TABLA, claves, valores)

    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('desarrolla.index'))

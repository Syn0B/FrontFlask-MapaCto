"""
proyecto.py - Blueprint maestro-detalle para Proyecto y sus Productos.

Maestro: proyecto (id, titulo, resumen, presupuesto, tipo_financiacion,
                   tipo_fondos, fecha_inicio, fecha_fin)
Detalle: producto  (id, nombre, categoria, fecha_entrega, tipo_producto FK)

La lista de proyectos usa la API generica (GET /api/proyecto).
El formulario de crear/editar usa Stored Procedures para garantizar
que el proyecto y sus productos se guarden en una sola transaccion.

Rutas:
    GET  /proyecto              -> Listar proyectos (tabla) y mostrar formulario si aplica
    POST /proyecto/crear        -> SP: sp_insertar_proyecto_y_productos
    POST /proyecto/actualizar   -> SP: sp_actualizar_proyecto_y_productos
    POST /proyecto/eliminar     -> SP: sp_borrar_proyecto_y_productos
"""

import json
from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.api_service import ApiService


# ══════════════════════════════════════════════
# CONFIGURACION DEL BLUEPRINT
# ══════════════════════════════════════════════

bp = Blueprint('proyecto', __name__)
api = ApiService()

TABLA = 'proyecto'
CLAVE = 'id'


# ══════════════════════════════════════════════
# LISTAR / FORMULARIO (GET)
# ══════════════════════════════════════════════

@bp.route('/proyecto')
def index():
    """
    Muestra la tabla de proyectos.
    Si accion='nuevo' abre el formulario de creacion con una fila de producto vacia.
    Si accion='editar' abre el formulario precargado con los productos del proyecto.
    """
    limite      = request.args.get('limite', type=int)
    accion      = request.args.get('accion', '')
    valor_clave = request.args.get('clave', '')

    # Lista de proyectos para la tabla (siempre se carga)
    registros = api.listar(TABLA, limite)

    # Formatear fechas para la tabla y para el formulario de edicion
    for r in registros:
        if r.get('fecha_inicio'):
            r['fecha_inicio'] = r['fecha_inicio'][:10]
        if r.get('fecha_fin'):
            r['fecha_fin'] = r['fecha_fin'][:10]

    mostrar_formulario = accion in ('nuevo', 'editar')
    editando           = accion == 'editar'

    registro             = None   # Datos del proyecto a editar
    productos_existentes = []     # Productos actuales del proyecto (solo en modo editar)
    tipos_producto       = []     # Para el <select> de cada fila de producto

    if editando and valor_clave:
        # Buscar el proyecto en la lista ya cargada
        registro = next(
            (r for r in registros if str(r.get(CLAVE)) == valor_clave),
            None
        )
        # Cargar los productos del proyecto via SP
        if registro:
            exito, datos = api.ejecutar_sp('sp_consultar_proyecto_y_productos', {
                'p_id':       int(valor_clave),
                'p_resultado': None
            })
            if exito and isinstance(datos, dict):
                productos_existentes = datos.get('productos', [])

    if mostrar_formulario:
        # Tipos de producto para el <select> de cada fila
        tipos_producto = api.listar('tipo_producto', None) or []

    return render_template('pages/proyecto.html',
        registros=registros,
        mostrar_formulario=mostrar_formulario,
        editando=editando,
        registro=registro,
        limite=limite,
        tipos_producto=tipos_producto,
        productos_existentes=productos_existentes
    )


# ══════════════════════════════════════════════
# CREAR (POST)
# SP: sp_insertar_proyecto_y_productos
# ══════════════════════════════════════════════

@bp.route('/proyecto/crear', methods=['POST'])
def crear():
    """Crea un proyecto con sus productos en una sola transaccion via SP."""
    # ── Maestro ──
    id_proyecto       = request.form.get('id', '')
    titulo            = request.form.get('titulo', '')
    resumen           = request.form.get('resumen', '')
    presupuesto       = request.form.get('presupuesto', 0, type=float)
    tipo_financiacion = request.form.get('tipo_financiacion', '')
    tipo_fondos       = request.form.get('tipo_fondos', '')
    fecha_inicio      = request.form.get('fecha_inicio', '')
    fecha_fin         = request.form.get('fecha_fin', '') or None

    # ── Detalle: listas paralelas ──
    nombres        = request.form.getlist('prod_nombre[]')
    categorias     = request.form.getlist('prod_categoria[]')
    fechas_entrega = request.form.getlist('prod_fecha_entrega[]')
    tipos          = request.form.getlist('prod_tipo_producto[]')

    productos_lista = []
    for nombre, cat, fecha, tipo in zip(nombres, categorias, fechas_entrega, tipos):
        if nombre.strip() and cat.strip():
            productos_lista.append({
                'nombre':        nombre,
                'categoria':     cat,
                'fecha_entrega': fecha,
                'tipo_producto': int(tipo) if tipo else None
            })

    exito, datos = api.ejecutar_sp('sp_insertar_proyecto_y_productos', {
        'p_id':                int(id_proyecto) if id_proyecto else None,
        'p_titulo':            titulo,
        'p_resumen':           resumen,
        'p_presupuesto':       presupuesto,
        'p_tipo_financiacion': tipo_financiacion,
        'p_tipo_fondos':       tipo_fondos,
        'p_fecha_inicio':      fecha_inicio,
        'p_fecha_fin':         fecha_fin,
        'p_productos':         json.dumps(productos_lista),
        'p_resultado':         None
    })

    if exito:
        flash('Proyecto creado exitosamente.', 'success')
    else:
        flash(f'Error al crear proyecto: {datos}', 'danger')

    return redirect(url_for('proyecto.index'))


# ══════════════════════════════════════════════
# ACTUALIZAR (POST)
# SP: sp_actualizar_proyecto_y_productos
# El SP hace replace-all de productos: elimina los anteriores e inserta los nuevos.
# ══════════════════════════════════════════════

@bp.route('/proyecto/actualizar', methods=['POST'])
def actualizar():
    """Actualiza un proyecto y reemplaza sus productos en una sola transaccion via SP."""
    # ── Maestro ──
    id_proyecto       = request.form.get('id', 0, type=int)
    titulo            = request.form.get('titulo', '')
    resumen           = request.form.get('resumen', '')
    presupuesto       = request.form.get('presupuesto', 0, type=float)
    tipo_financiacion = request.form.get('tipo_financiacion', '')
    tipo_fondos       = request.form.get('tipo_fondos', '')
    fecha_inicio      = request.form.get('fecha_inicio', '')
    fecha_fin         = request.form.get('fecha_fin', '') or None

    # ── Detalle ──
    nombres        = request.form.getlist('prod_nombre[]')
    categorias     = request.form.getlist('prod_categoria[]')
    fechas_entrega = request.form.getlist('prod_fecha_entrega[]')
    tipos          = request.form.getlist('prod_tipo_producto[]')
    ids_producto   = request.form.getlist('prod_id[]')    # IDs de productos ya existentes

    productos_lista = []
    for i, (nombre, cat, fecha, tipo) in enumerate(
            zip(nombres, categorias, fechas_entrega, tipos)):
        if nombre.strip() and cat.strip():
            prod = {
                'nombre':        nombre,
                'categoria':     cat,
                'fecha_entrega': fecha,
                'tipo_producto': int(tipo) if tipo else None
            }
            # Si el producto ya existia, incluir su id para que el SP lo reconozca
            if i < len(ids_producto) and ids_producto[i]:
                prod['id'] = int(ids_producto[i])
            productos_lista.append(prod)

    exito, datos = api.ejecutar_sp('sp_actualizar_proyecto_y_productos', {
        'p_id':                id_proyecto,
        'p_titulo':            titulo,
        'p_resumen':           resumen,
        'p_presupuesto':       presupuesto,
        'p_tipo_financiacion': tipo_financiacion,
        'p_tipo_fondos':       tipo_fondos,
        'p_fecha_inicio':      fecha_inicio,
        'p_fecha_fin':         fecha_fin,
        'p_productos':         json.dumps(productos_lista),
        'p_resultado':         None
    })

    if exito:
        flash('Proyecto actualizado exitosamente.', 'success')
    else:
        flash(f'Error al actualizar proyecto: {datos}', 'danger')

    return redirect(url_for('proyecto.index'))


# ══════════════════════════════════════════════
# ELIMINAR (POST)
# SP: sp_borrar_proyecto_y_productos
# Elimina el proyecto y todos sus productos en una sola transaccion.
# ══════════════════════════════════════════════

@bp.route('/proyecto/eliminar', methods=['POST'])
def eliminar():
    """Elimina un proyecto y todos sus productos via SP."""
    id_proyecto = request.form.get('id', 0, type=int)

    exito, datos = api.ejecutar_sp('sp_borrar_proyecto_y_productos', {
        'p_id':       id_proyecto,
        'p_resultado': None
    })

    if exito:
        flash('Proyecto y sus productos eliminados exitosamente.', 'success')
    else:
        flash(f'Error al eliminar proyecto: {datos}', 'danger')

    return redirect(url_for('proyecto.index'))

"""
producto.py - Blueprint de consulta para la tabla Producto.

Los productos se crean y editan desde la pagina de Proyecto (maestro-detalle).
Esta pagina solo muestra el listado completo de todos los productos registrados
en el sistema, con sus relaciones a proyecto y tipo_producto, como referencia.

Ruta:
    GET /producto -> Lista todos los productos con informacion de proyecto y tipo
"""

from flask import Blueprint, render_template, request
from services.api_service import ApiService


# ══════════════════════════════════════════════
# CONFIGURACION DEL BLUEPRINT
# ══════════════════════════════════════════════

bp  = Blueprint('producto', __name__)
api = ApiService()


# ══════════════════════════════════════════════
# LISTAR (GET /producto)
# ══════════════════════════════════════════════

@bp.route('/producto')
def index():
    """Muestra todos los productos registrados en el sistema."""
    limite = request.args.get('limite', type=int)

    # Cargar productos, proyectos y tipos para resolver los FK en el template
    productos      = api.listar('producto',      limite) or []
    proyectos      = api.listar('proyecto',      None)   or []
    tipos_producto = api.listar('tipo_producto', None)   or []

    # Formatear fechas de entrega
    for p in productos:
        if p.get('fecha_entrega'):
            p['fecha_entrega'] = p['fecha_entrega'][:10]

    return render_template('pages/producto.html',
        productos=productos,
        proyectos=proyectos,
        tipos_producto=tipos_producto,
        limite=limite
    )

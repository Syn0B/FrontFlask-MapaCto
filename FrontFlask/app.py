"""
app.py - Punto de entrada de la aplicacion Flask.

Crea la aplicacion, registra los Blueprints (uno por tabla)
e inicia el servidor de desarrollo en el puerto 5100.
"""

# Flask: clase principal del framework web para crear la aplicacion
from flask import Flask

# SECRET_KEY: clave secreta definida en config.py, necesaria para mensajes flash
from config import SECRET_KEY


# ══════════════════════════════════════════════
# CREAR LA APLICACION FLASK
# ══════════════════════════════════════════════

# Flask(__name__) crea la instancia de la aplicacion.
# __name__ le indica a Flask en que modulo esta corriendo (necesario para encontrar templates y static).
app = Flask(__name__)

# La clave secreta es necesaria para los mensajes flash (alertas).
# Flask la usa internamente para firmar las cookies de sesion.
app.secret_key = SECRET_KEY


# ══════════════════════════════════════════════
# REGISTRAR BLUEPRINTS
# Cada Blueprint agrupa las rutas de una tabla.
# Es el equivalente a tener una pagina separada por tabla.
# ══════════════════════════════════════════════
"""
# Importar el Blueprint de cada modulo de rutas.
from routes.home import bp as home_bp
from routes.termino_clave import bp as termino_clave_bp
from routes.tipo_producto import bp as tipo_producto_bp
from routes.proyecto import bp as proyecto_bp
from routes.palabras_clave import bp as palabras_clave_bp
from routes.aa_proyecto import bp as aa_proyecto_bp
from routes.ods_proyecto import bp as ods_proyecto_bp
from routes.proyecto_linea import bp as proyecto_linea_bp
from routes.ac_proyecto import bp as ac_proyecto_bp
from routes.docente_producto import bp as docente_producto_bp
from routes.aliado_proyecto import bp as aliado_proyecto_bp


# register_blueprint() conecta las rutas del Blueprint a la aplicacion Flask.
app.register_blueprint(home_bp)
app.register_blueprint(termino_clave_bp)
app.register_blueprint(tipo_producto_bp)
app.register_blueprint(proyecto_bp)
app.register_blueprint(palabras_clave_bp)
app.register_blueprint(aa_proyecto_bp)
app.register_blueprint(ods_proyecto_bp)
app.register_blueprint(proyecto_linea_bp)
app.register_blueprint(ac_proyecto_bp)
app.register_blueprint(docente_producto_bp)
app.register_blueprint(aliado_proyecto_bp)
"""

# ══════════════════════════════════════════════
# INICIAR EL SERVIDOR
# ══════════════════════════════════════════════

if __name__ == '__main__':
    # app.run() inicia el servidor de desarrollo de Flask.
    # debug=True: recarga automaticamente al guardar cambios y muestra errores detallados.
    # port=5100: puerto del frontend, diferente al de la API (5034) para evitar conflicto.
    app.run(debug=True, port=5100)

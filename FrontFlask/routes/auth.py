"""
auth.py - Blueprint para autenticacion y manejo de cuenta.

Rutas:
    GET  /login                - Muestra el formulario de login.
    POST /login                - Procesa el formulario, llama a la API y guarda el JWT.
    GET  /logout               - Cierra la sesion y redirige al login.
    GET  /cambiar-contrasena   - Muestra el formulario de cambio de contrasena.
    POST /cambiar-contrasena   - Valida y actualiza la contrasena via API.
    GET  /restablecer-contrasena - Formulario "olvide mi contrasena" (publico).
    POST /restablecer-contrasena - Verifica usuario+email y restablece la contrasena.
"""

import re

from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from services.auth_service import AuthService


bp = Blueprint('auth', __name__)
auth = AuthService()


def _validar_nueva_contrasena(nueva, confirmacion):
    """
    Aplica las reglas de seguridad a una nueva contrasena.

    Reglas:
        - nueva y confirmacion deben coincidir
        - minimo 6 caracteres
        - al menos 1 mayuscula
        - al menos 1 numero

    Returns:
        None si es valida. Una cadena con el mensaje de error si no lo es.
    """
    if nueva != confirmacion:
        return "Las contrasenas no coinciden."
    if len(nueva) < 6:
        return "La contrasena debe tener al menos 6 caracteres."
    if not re.search(r'[A-Z]', nueva):
        return "La contrasena debe incluir al menos una letra mayuscula."
    if not re.search(r'\d', nueva):
        return "La contrasena debe incluir al menos un numero."
    return None


# ══════════════════════════════════════════════
# GET /login - Mostrar formulario
# ══════════════════════════════════════════════
@bp.route('/login', methods=['GET'])
def login():
    """Renderiza el formulario de login. Si ya hay sesion, redirige al home."""
    if session.get("usuario"):
        return redirect(url_for("home.index"))
    return render_template('pages/login.html')


# ══════════════════════════════════════════════
# POST /login - Procesar credenciales
# ══════════════════════════════════════════════
@bp.route('/login', methods=['POST'])
def login_post():
    """Verifica credenciales contra la API, obtiene token y carga roles."""
    usuario = request.form.get('usuario', '').strip()
    contrasena = request.form.get('contrasena', '')

    if not usuario or not contrasena:
        flash("Debe ingresar usuario y contrasena.", "danger")
        return redirect(url_for('auth.login'))

    exito, datos = auth.login(usuario, contrasena)

    if not exito:
        flash(f"Error al iniciar sesion: {datos}", "danger")
        return redirect(url_for('auth.login'))

    # Guardar JWT, usuario, roles y rutas permitidas en la cookie firmada.
    session['usuario'] = datos['usuario']
    session['token'] = datos['token']
    session['expiracion'] = str(datos.get('expiracion', ''))
    session['roles'] = datos.get('roles', [])
    session['rutas_permitidas'] = datos.get('rutas_permitidas', [])

    if not session['roles']:
        flash(
            f"Bienvenido, {datos['usuario']}. (Sin roles asignados: acceso limitado al inicio.)",
            "warning",
        )
    else:
        flash(
            f"Bienvenido, {datos['usuario']}. Roles: {', '.join(session['roles'])}.",
            "success",
        )

    return redirect(url_for('home.index'))


# ══════════════════════════════════════════════
# GET /logout - Cerrar sesion
# ══════════════════════════════════════════════
@bp.route('/logout')
def logout():
    """Limpia toda la sesion y redirige al login."""
    session.clear()
    flash("Sesion cerrada correctamente.", "success")
    return redirect(url_for('auth.login'))


# ══════════════════════════════════════════════
# GET /cambiar-contrasena - Formulario
# ══════════════════════════════════════════════
@bp.route('/cambiar-contrasena', methods=['GET'])
def cambiar_contrasena():
    """Renderiza el formulario para cambiar la contrasena del usuario logueado."""
    return render_template('pages/cambiar_contrasena.html')


# ══════════════════════════════════════════════
# POST /cambiar-contrasena - Procesar
# ══════════════════════════════════════════════
@bp.route('/cambiar-contrasena', methods=['POST'])
def cambiar_contrasena_post():
    """Valida la nueva contrasena y la actualiza via API."""
    nueva = request.form.get('nueva', '')
    confirmacion = request.form.get('confirmacion', '')

    error = _validar_nueva_contrasena(nueva, confirmacion)
    if error:
        flash(error, "danger")
        return redirect(url_for('auth.cambiar_contrasena'))

    # Llamar al servicio para actualizar (con JWT y encriptacion BCrypt).
    usuario = session.get('usuario')
    token = session.get('token')

    exito, mensaje = auth.actualizar_contrasena(usuario, nueva, token)

    if exito:
        flash("Contrasena actualizada correctamente.", "success")
        return redirect(url_for('home.index'))
    else:
        flash(f"Error al actualizar contrasena: {mensaje}", "danger")
        return redirect(url_for('auth.cambiar_contrasena'))


# ══════════════════════════════════════════════
# GET /restablecer-contrasena - Formulario publico
# ══════════════════════════════════════════════
@bp.route('/restablecer-contrasena', methods=['GET'])
def restablecer_contrasena():
    """Renderiza el formulario 'Olvide mi contrasena' (accesible sin sesion)."""
    if session.get("usuario"):
        return redirect(url_for("home.index"))
    return render_template('pages/restablecer_contrasena.html')


# ══════════════════════════════════════════════
# POST /restablecer-contrasena - Procesar restablecimiento
# ══════════════════════════════════════════════
@bp.route('/restablecer-contrasena', methods=['POST'])
def restablecer_contrasena_post():
    """Verifica usuario+email contra la API y restablece la contrasena (encriptada)."""
    usuario = request.form.get('usuario', '').strip()
    email = request.form.get('email', '').strip()
    nueva = request.form.get('nueva', '')
    confirmacion = request.form.get('confirmacion', '')

    if not usuario or not email:
        flash("Debe ingresar usuario y email.", "danger")
        return redirect(url_for('auth.restablecer_contrasena'))

    error = _validar_nueva_contrasena(nueva, confirmacion)
    if error:
        flash(error, "danger")
        return redirect(url_for('auth.restablecer_contrasena'))

    # Llamar al endpoint publico (la API encripta con BCrypt).
    exito, mensaje = auth.restablecer_contrasena(usuario, email, nueva)

    if exito:
        flash("Contrasena restablecida. Ya puede iniciar sesion.", "success")
        return redirect(url_for('auth.login'))
    else:
        flash(f"No se pudo restablecer la contrasena: {mensaje}", "danger")
        return redirect(url_for('auth.restablecer_contrasena'))

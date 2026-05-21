"""
config.py - Configuracion centralizada de la aplicacion Flask.

Lee los valores sensibles desde variables de entorno. En local se cargan
del archivo .env (via python-dotenv). En produccion (Render) las inyecta
la plataforma automaticamente al proceso, asi que load_dotenv() es no-op.

Variables de entorno esperadas:
    SECRET_KEY       Clave para firmar cookies de sesion Flask.
    API_BASE_URL     URL base de la API REST (ej: http://localhost:5035).

Copia .env.example a .env y rellena los valores antes de correr la app
localmente. El archivo .env NO se sube al repo (esta gitignored).
"""

import os
from dotenv import load_dotenv

# Carga las variables del archivo .env si existe. En Render no existe,
# pero sus env vars ya estan en os.environ desde el arranque del proceso,
# por lo que esta llamada simplemente no hace nada y la app funciona igual.
load_dotenv()


# ──────────────────────────────────────────────
# URL base de la API REST que consume este frontend.
# Default util para desarrollo local con la API corriendo en el puerto 5035.
# En produccion debe apuntar a la API desplegada (ej: MonsterASP).
# ──────────────────────────────────────────────
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:5035")


# ──────────────────────────────────────────────
# Clave secreta para firmar cookies de sesion y mensajes flash.
# DEBE estar definida en produccion. El default solo es valido para
# desarrollo local y no debe usarse jamas en un entorno real.
# ──────────────────────────────────────────────
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-cambiar-en-produccion")

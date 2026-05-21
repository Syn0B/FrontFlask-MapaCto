# Constitución del Proyecto: FrontFlask-MapaCto

Según **Spec-Kit de GitHub**: la constitución actúa como el "ADN arquitectónico del sistema", asegurando que toda implementación generada mantenga consistencia, simplicidad y calidad. Es lo **PRIMERO** que lee la IA antes de generar código. Si la IA viola alguna de estas reglas, el código generado se rechaza.

**Referencia**: [spec-driven.md - Los Nueve Artículos Constitucionales](https://github.com/github/spec-kit/blob/main/spec-driven.md)

---

## Artículo I: Stack Tecnológico

Toda implementación **DEBE** usar exclusivamente estas tecnologías:

| Capa | Tecnología | Versión | Justificación |
|------|------------|---------|---------------|
| Lenguaje | Python | 3.10+ | Lenguaje del curso, los estudiantes ya lo conocen |
| Framework web | Flask | 3.x | Microframework sin magia, el estudiante ve cada línea |
| Templates | Jinja2 | (incluido en Flask) | Separación clara lógica/presentación |
| CSS | Bootstrap 5 | 5.3 CDN | Sin npm ni build tools, responsive |
| API backend | ApiCsharpNeon-MapaCto | .NET 9.0 | API genérica desplegada en runasp.net |
| BD | PostgreSQL (Neon) | 17 | BD del curso, hosteada en Neon Cloud |
| HTTP Client | requests | 2.31+ | Síncrono, simple, sin async |
| Control versiones | Git + GitHub | N/A | Trabajo colaborativo con ramas |

---

## Artículo II: Arquitectura del Sistema

### Arquitectura general: Cliente-Servidor en 3 capas

```
┌─────────────────────────────┐
│   CAPA DE PRESENTACIÓN      │   FrontFlask-MapaCto (este proyecto)
│   Flask + Jinja2 + Bootstrap│   Puerto 5100
│   routes/ + templates/      │   Responsabilidad: UI, navegación, formularios
└─────────────┬───────────────┘
              │ HTTP (requests)
              │ Authorization: Bearer {JWT}
              v
┌─────────────────────────────┐
│   CAPA DE NEGOCIO (API)     │   ApiCsharpNeon-MapaCto (.NET 9.0)
│   Controllers + Services    │   apicsharpneon-mapacto.runasp.net
│   BCrypt, JWT, CRUD genérico│   Responsabilidad: validación, lógica, seguridad
└─────────────┬───────────────┘
              │ SQL (ADO.NET)
              v
┌─────────────────────────────┐
│   CAPA DE DATOS             │   PostgreSQL 17 (Neon Cloud)
│   Tablas, FKs, índices      │   Hosteado en Neon Serverless
│   ACID transaccional        │   Responsabilidad: persistencia, integridad
└─────────────────────────────┘
```

**Principio**: el frontend **NUNCA** accede a la BD directamente. Todo pasa por la API REST. Cada capa solo conoce a la inmediatamente inferior (no hay saltos).

### Arquitectura interna del frontend: MVC adaptado a Flask

```
                    ┌──────────────────────┐
                    │    MODELO (Model)     │
                    │  services/            │
                    │  api_service.py       │   Llama a la API via HTTP
                    │  auth_service.py      │   Logica de autenticacion
                    └──────────┬───────────┘
                               │
┌──────────────────┐           │           ┌──────────────────┐
│  VISTA (View)    │           │           │ CONTROLADOR      │
│  templates/      │ <─────────┼──────────>│ routes/          │
│  pages/*.html    │  renderiza│           │ producto.py      │
│  layout/base.html│           │           │ auth.py          │
└──────────────────┘           │           └──────────────────┘
                               │
                    ┌──────────┴───────────┐
                    │  MIDDLEWARE           │
                    │  middleware/          │
                    │  auth_middleware.py   │   Intercepta ANTES de cada request
                    └──────────────────────┘
```

| Componente MVC | Carpeta Flask | Responsabilidad |
|----------------|---------------|-----------------|
| Modelo | `services/` | Lógica de negocio, llamadas HTTP a la API |
| Vista | `templates/` | HTML con Jinja2, presentación al usuario |
| Controlador | `routes/` | Recibe requests, llama servicios, devuelve templates |
| Middleware | `middleware/` | Intercepta requests (auth, permisos) |

### Estructura de carpetas (no negociable)

```
app.py                       <- Punto de entrada (crea Flask, registra todo)
config.py                    <- Configuración centralizada (URLs, claves)
routes/                      <- Controladores (Blueprints)
  auth.py                    <- Login y logout
  home.py                    <- Página principal
  proyecto.py                <- CRUD proyecto
  producto.py                <- CRUD producto
  termino_clave.py           <- CRUD término clave
  tipo_producto.py           <- CRUD tipo producto
  palabras_clave.py          <- CRUD palabras clave
  aa_proyecto.py             <- Áreas académicas del proyecto
  ac_proyecto.py             <- Áreas de conocimiento del proyecto
  ods_proyecto.py            <- ODS del proyecto
  proyecto_linea.py          <- Líneas del proyecto
  aliado_proyecto.py         <- Aliados del proyecto
  docente_producto.py        <- Docentes del producto
  desarrolla.py              <- Relación desarrolla (proyecto-docente)
services/                    <- Servicios: lógica de negocio, llamadas HTTP
  api_service.py             <- Cliente HTTP genérico hacia la API
  auth_service.py            <- Autenticación, JWT, permisos
middleware/                  <- Middleware: intercepta requests (auth)
  auth_middleware.py         <- Verifica sesión antes de cada request
templates/
  layout/base.html           <- Layout base (sidebar + content)
  components/nav_menu.html   <- Menú lateral
  pages/{tabla}.html         <- Una página por tabla
static/css/                  <- Estilos
sdd/                         <- Documentación SDD (ESTOS archivos)
```

---

## Artículo III: Convenciones de Código

| Elemento | Convención | Ejemplo |
|----------|------------|---------|
| Archivos Python | snake_case | `auth_service.py`, `api_service.py` |
| Variables/funciones | snake_case | `obtener_roles_usuario()` |
| Clases | PascalCase | `ApiService`, `AuthService` |
| Constantes | UPPER_SNAKE | `API_BASE_URL`, `SECRET_KEY` |
| Rutas URL | minusculas-guiones | `/proyecto`, `/termino-clave` |
| Tablas BD | minusculas_guion_bajo | `aa_proyecto`, `docente_producto` |
| Blueprints | nombre de la tabla | `bp = Blueprint("producto", __name__)` |
| Templates | nombre de la tabla | `templates/pages/producto.html` |

---

## Artículo IV: Patrón CRUD

Cada tabla sigue este patrón exacto (**no negociable**):

```python
# routes/{tabla}.py
bp = Blueprint("{tabla}", __name__)
api = ApiService()

@bp.route("/{tabla}")                              # Listar
def index(): ...

@bp.route("/{tabla}/crear", methods=["POST"])      # Crear
def crear(): ...

@bp.route("/{tabla}/editar/<id>", methods=["POST"])# Editar
def editar(id): ...

@bp.route("/{tabla}/eliminar/<id>")                # Eliminar
def eliminar(id): ...
```

---

## Artículo V: Seguridad (3 capas obligatorias)

| Capa | Dónde | Qué protege | Cómo |
|------|-------|-------------|------|
| BCrypt | BD (vía API) | Contraseñas | `?camposEncriptar=contrasena` |
| JWT | API (header HTTP) | Datos del backend | `Authorization: Bearer {token}` |
| Sesión | Frontend (cookie Flask) | Páginas | Middleware `before_request` |

### Middleware obligatorio

- `@app.before_request` intercepta **CADA** request
- Rutas públicas: `/login`, `/logout`, `/static`
- Sin sesión → `redirect /login`
- Ruta no permitida → página 403

### Descubrimiento dinámico

- PKs y FKs se descubren vía `/api/estructuras/basedatos`
- **NO** se hardcodean nombres de columnas
- Compatible con PostgreSQL y SqlServer

---

## Artículo VI: Prohibiciones

| Prohibido | Razón |
|-----------|-------|
| Acceder a la BD directamente | Todo va por la API REST |
| Usar ORM (SQLAlchemy) | No hay BD directa |
| Push directo a `main` | Trabajo en ramas `feature/` |
| Hardcodear URLs de la API | Van en `config.py` |
| Hardcodear nombres FK/PK | Se descubren via API |
| Contraseñas en texto plano | BCrypt obligatorio |
| Paquetes sin `requirements.txt` | Rompe entorno de otros |
| JavaScript para lógica de negocio | Lógica en Python |

---

## Artículo VII: Principios SOLID

Los principios SOLID son guías de diseño orientado a objetos que producen código mantenible, extensible y testeable. Aplican a las clases y módulos de este proyecto.

| Principio | Sigla | Qué dice | Cómo se aplica en este proyecto |
|-----------|-------|----------|----------------------------------|
| Single Responsibility | S | Una clase tiene UNA sola razón para cambiar | `ApiService` solo hace HTTP, `AuthService` solo hace auth, cada Blueprint maneja UNA tabla |
| Open/Closed | O | Abierto para extensión, cerrado para modificación | Agregar un CRUD nuevo = crear archivos nuevos, **NO** modificar los existentes |
| Liskov Substitution | L | Los subtipos deben ser sustituibles por sus tipos base | `ApiService` y `AuthService` son intercambiables donde se necesite un servicio HTTP |
| Interface Segregation | I | No forzar a depender de interfaces que no se usan | `ApiService` tiene solo 4 métodos (listar, crear, actualizar, eliminar), no un método gigante |
| Dependency Inversion | D | Depender de abstracciones, no de implementaciones | Las rutas dependen de `ApiService` (abstracción), no de `requests` directamente |

### Aplicación concreta

```
CORRECTO (S - Single Responsibility):
  routes/producto.py            <- Solo maneja rutas de producto
  services/api_service.py       <- Solo hace llamadas HTTP
  middleware/auth_middleware.py <- Solo verifica permisos

INCORRECTO:
  routes/producto.py que tambien hace llamadas HTTP directas
  app.py que tiene logica de negocio mezclada con registro de blueprints
```

```
CORRECTO (O - Open/Closed):
  Para agregar CRUD de "linea_investigacion":
    1. Crear routes/linea_investigacion.py (NUEVO)
    2. Crear templates/pages/linea_investigacion.html (NUEVO)
    3. Registrar blueprint en app.py (1 linea)
  NO se modifica: api_service.py, auth_service.py, base.html

INCORRECTO:
  Agregar un if/elif en api_service.py para cada tabla nueva
```

---

## Artículo VIII: Principios ACID (Base de Datos)

ACID son las propiedades que garantizan la integridad de las transacciones en la base de datos. PostgreSQL las cumple por defecto.

| Principio | Qué garantiza | Ejemplo en este proyecto |
|-----------|---------------|--------------------------|
| **A**tomicity (Atomicidad) | Una transacción se ejecuta COMPLETA o NO se ejecuta | Crear un proyecto con sus líneas y ODS: si falla un INSERT, no se crea nada |
| **C**onsistency (Consistencia) | La BD pasa de un estado válido a otro estado válido | Un FK `fkcodproyecto` en `producto` siempre apunta a un proyecto que existe |
| **I**solation (Aislamiento) | Transacciones concurrentes no se interfieren | Dos docentes registrando productos al mismo tiempo no se pisan |
| **D**urability (Durabilidad) | Una vez confirmada, la transacción persiste aunque se caiga el servidor | Después de COMMIT, el registro existe aunque se reinicie PostgreSQL |

### Dónde aplica ACID en este proyecto

ACID lo maneja **PostgreSQL + la API** (capa de datos).
El frontend (Flask) **NO** maneja transacciones directamente.

```
Frontend (Flask)          API (C#)              BD (PostgreSQL)
   POST /proyecto  ──>  Recibe datos  ──>  BEGIN TRANSACTION
                                          INSERT proyecto
                                          INSERT proyecto_linea (N)
                                          INSERT ods_proyecto (M)
                                          COMMIT (atomico)

Si falla un INSERT ──>  ROLLBACK  ──>  Nada se guarda (atomicidad)
```

---

## Artículo IX: Patrones de Diseño

Patrones de diseño utilizados en este proyecto, con referencia a dónde se aplican.

| Patrón | Tipo | Dónde se usa | Qué resuelve |
|--------|------|--------------|--------------|
| **MVC** (Model-View-Controller) | Arquitectónico | `services/` + `templates/` + `routes/` | Separar lógica, presentación y control |
| **Blueprint** (Flask) | Estructural | `routes/*.py` | Modularizar rutas por funcionalidad |
| **Service Layer** | Arquitectónico | `services/api_service.py` | Encapsular lógica de negocio en una capa |
| **Middleware/Interceptor** | Comportamiento | `middleware/auth_middleware.py` | Ejecutar lógica ANTES de cada request |
| **Template Method** | Comportamiento | `templates/layout/base.html` | Layout común, cada página llena los bloques |
| **Facade** | Estructural | `services/api_service.py` | Interfaz simple para la API REST compleja |
| **Cache** | Rendimiento | `auth_service._fk_cache` | No repetir consultas a la API |
| **Strategy** (fallback) | Comportamiento | `auth_service`: ConsultasController o GETs | Cambiar estrategia según disponibilidad |

### Ejemplo: Patrón Template Method en Jinja2

```html
<!-- base.html (template padre) -->
<div class="sidebar">{% include 'components/nav_menu.html' %}</div>
<div class="content">{% block content %}{% endblock %}</div>

<!-- proyecto.html (template hijo) -->
{% extends 'layout/base.html' %}
{% block content %}
  <!-- Solo el contenido especifico de proyecto -->
  <table>...</table>
{% endblock %}
```

### Ejemplo: Patrón Facade en ApiService

```python
# El usuario de ApiService no necesita saber de HTTP, headers, JSON, etc.
# Solo llama metodos simples:

api = ApiService()
datos = api.listar("proyecto")            # Facade oculta: GET + headers + JSON parse
ok, msg = api.crear("proyecto", {...})    # Facade oculta: POST + headers + response check
```

---

## Artículo X: Simplicidad

Según Spec-Kit Artículo VII: *"Máximo complejidad inicial mínima."*

- Cada archivo tiene **UNA** responsabilidad (SOLID - S)
- Cada ruta tiene **UN** blueprint
- Cada servicio tiene **UNA** clase
- Sin abstracciones prematuras
- Sin features especulativas

---

## Artículo XI: API REST

### Endpoints permitidos

| Método | Endpoint | Para qué |
|--------|----------|----------|
| GET | `/api/{tabla}?limite=N` | Listar |
| POST | `/api/{tabla}` | Crear |
| PUT | `/api/{tabla}/{pk}/{valor}` | Actualizar |
| DELETE | `/api/{tabla}/{pk}/{valor}` | Eliminar |
| POST | `/api/autenticacion/token` | Login BCrypt+JWT |
| GET | `/api/estructuras/basedatos` | Descubrir PKs/FKs |
| POST | `/api/consultas/ejecutarconsultaparametrizada` | SQL con JOINs |

---

## Artículo XII: Trabajo Colaborativo

| Regla | Detalle |
|-------|---------|
| Estrategia | GitHub Flow: `main` estable, `feature/` para trabajo |
| Merge | Terminal: `git fetch` + `git merge`, nunca push directo |
| Commits | Descriptivos: `feat: CRUD proyecto`, `fix: error select` |
| Roles | Samuel (desarrollador), Jostin (desarrollador) |
| Dependencias | Solo `flask` y `requests` sin aprobación |

---

## Fecha de ratificación

- **Versión**: 1.0
- **Fecha**: 2026-05-21
- **Autores**: Samuel Giraldo, Jostin (Estudiantes Construcción de Software USB)
- **Referencia Spec-Kit**: [github.com/github/spec-kit](https://github.com/github/spec-kit)

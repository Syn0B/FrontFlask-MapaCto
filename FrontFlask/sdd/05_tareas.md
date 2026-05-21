# Etapa 5: Tareas y Código

Según **Spec-Kit**: las tareas se derivan del plan y se organizan por **historia de usuario**. Cada tarea tiene ruta de archivo específica y marcadores de paralelización `[P]`. Se generan con `/speckit.tasks`.

**Referencia**: [tasks-template.md](https://github.com/github/spec-kit/blob/main/templates/tasks-template.md)

---

## Leyenda

- `[x]` = **Completado**
- `[ ]` = **Pendiente**
- `[P]` = **Paralelizable** (puede hacerse al mismo tiempo que otra tarea `[P]`)
- `->` = **Dependencia** (requiere que la tarea anterior esté completada)

---

## Historia 1: Proyecto base

**Samuel** — Rama: `main` (commit inicial)

- [x] Crear carpeta `FrontFlask-MapaCto/FrontFlask/`
- [x] Crear entorno virtual: `python -m venv venv`
- [x] Instalar dependencias: `pip install flask requests`
- [x] Crear `requirements.txt`: `pip freeze > requirements.txt`
- [x] Crear `requirements-prod.txt` para deploy
- [x] Crear `Procfile` para deploy en runasp.net
- [x] Crear `config.py` con `API_BASE_URL` y `SECRET_KEY`
  - Archivo: [config.py](../config.py)
  - `API_BASE_URL = "http://apicsharpneon-mapacto.runasp.net"`
- [x] Crear `app.py` con Flask y registro de blueprints
  - Archivo: [app.py](../app.py)
- [x] Crear `routes/__init__.py` y `services/__init__.py`
- [x] Inicializar git, primer commit, push a GitHub
- [x] Invitar colaborador (Jostin)

---

## Historia 2: Servicio API

**Samuel** — Rama: `feature/api-service`

- [x] Crear `services/api_service.py` con clase `ApiService`
  - Archivo: [services/api_service.py](../services/api_service.py)
  - Métodos: `listar()`, `crear()`, `actualizar()`, `eliminar()`, `ejecutar_sp()`
  - Helper `_headers()` para agregar JWT automáticamente
  - Helper `_ruta_clave()` para soportar PK simple **y compuesta** (`docente,proyecto/X,Y`)
- [x] Verificar conexión con la API: `GET /api/tipo_producto`
- [x] Verificar `ejecutar_sp` con `sp_consultar_proyecto_y_productos`
- [x] Merge a `main`

---

## Historia 3: Layout y navegación

**Samuel** — Rama: `feature/layout`

- [x] Crear `templates/layout/base.html` con Bootstrap 5 CDN
  - Sidebar + top-row + content area
- [x] Crear `templates/components/nav_menu.html` con links a todas las páginas
- [x] Crear `templates/pages/home.html` (página inicio)
- [x] Crear `routes/home.py` con Blueprint
- [x] Registrar blueprint en `app.py`
- [x] Crear `static/css/` con estilos custom
- [x] Merge a `main`

---

## Historia 4: CRUD Catálogos `[P]`

**Samuel** — Rama: `feature/crud-catalogos`

CRUDs simples (una sola tabla, sin FKs complicadas). Se pueden hacer en paralelo entre ellos.

- [x] `[P]` Crear `routes/tipo_producto.py` + `templates/pages/tipo_producto.html`
- [x] `[P]` Crear `routes/termino_clave.py` + `templates/pages/termino_clave.html`
- [x] `[P]` Crear `routes/palabras_clave.py` + `templates/pages/palabras_clave.html`
- [x] Registrar los 3 blueprints en `app.py`
- [x] Merge a `main`

---

## Historia 5: Maestro-detalle Proyecto con Stored Procedures

**Samuel** — Rama: `feature/proyecto-sp`
**Depende de**: Historia 2 (`ejecutar_sp`) + Historia 4 (`tipo_producto` para el select)

### 5.1 Stored Procedures en BD

Los 5 SPs reales definidos en `ProcedimientosAlmacenados.sql`:

- [x] Crear SP `sp_consultar_proyecto_y_productos(p_id INT)` — devuelve `{ proyecto, productos[] }`
- [x] Crear SP `sp_insertar_proyecto_y_productos(p_id, p_titulo, ...)` — autocalcula IDs si vienen NULL
- [x] Crear SP `sp_actualizar_proyecto_y_productos(p_id, ...)` — **SYNC diferencial** (UPDATE/INSERT/DELETE)
- [x] Crear SP `sp_borrar_proyecto_y_productos(p_id)` — limpia las 7 tablas puente + productos y borra el maestro
- [x] Crear SP `sp_listar_proyecto_y_productos(p_limite)` (opcional) — lista con productos anidados
- [x] Probar SPs desde pgAdmin/Neon Console antes de integrar

> **No hay triggers**: toda la lógica transaccional vive en los SPs.

### 5.2 Frontend Flask

- [x] Crear `routes/proyecto.py` con lógica maestro-detalle
  - Archivo: [routes/proyecto.py](../routes/proyecto.py)
  - `index()`: lista proyectos + modo nuevo/editar con productos prellenados
  - `crear()`: llama `sp_insertar_proyecto_y_productos`
  - `actualizar()`: llama `sp_actualizar_proyecto_y_productos`
  - `eliminar()`: llama `sp_borrar_proyecto_y_productos`
- [x] Crear `templates/pages/proyecto.html`
  - Cabecera: título, resumen, presupuesto, tipo_financiacion, tipo_fondos, fechas
  - Detalle: tabla dinámica de productos con nombre, categoría, fecha_entrega, tipo_producto (`<select>`)
  - JavaScript para agregar/eliminar filas de productos
- [x] Registrar blueprint en `app.py`
- [x] Merge a `main`

---

## Historia 6: Consulta Producto

**Jostin** — Rama: `feature/consulta-producto`
**Depende de**: Historia 5 (proyectos creados)

- [x] Crear `routes/producto.py` (solo consulta, sin CRUD propio)
  - Archivo: [routes/producto.py](../routes/producto.py)
  - `index()`: lista productos con resolución de FKs (proyecto, tipo_producto)
- [x] Crear `templates/pages/producto.html`
  - Tabla con nombre del proyecto y tipo de producto (no IDs)
- [x] Registrar blueprint en `app.py`
- [x] Merge a `main`

---

## Historia 7: Tablas N:M de relación con proyecto `[P]`

**Jostin** — Rama: `feature/nm-proyecto`
**Depende de**: Historia 5 (proyectos existen)

5 tablas N:M con la misma estructura: dos selects FK + un POST. Paralelizables entre ellas.

- [x] `[P]` Crear `routes/aa_proyecto.py` + `templates/pages/aa_proyecto.html`
- [x] `[P]` Crear `routes/ac_proyecto.py` + `templates/pages/ac_proyecto.html`
- [x] `[P]` Crear `routes/ods_proyecto.py` + `templates/pages/ods_proyecto.html`
- [x] `[P]` Crear `routes/proyecto_linea.py` + `templates/pages/proyecto_linea.html`
- [x] `[P]` Crear `routes/aliado_proyecto.py` + `templates/pages/aliado_proyecto.html`
- [x] Registrar los 5 blueprints en `app.py`
- [x] Verificar eliminación con PK compuesta vía `_ruta_clave()`
- [x] Merge a `main`

---

## Historia 8: Relaciones de docentes

**Jostin** — Rama: `feature/docentes`
**Depende de**: Historia 5 + Historia 6

### 8.1 docente_producto (N:M puro)

- [x] Crear `routes/docente_producto.py` + `templates/pages/docente_producto.html`
  - Dos selects: docente (FK) + producto (FK)
  - CRUD básico: crear y eliminar (no se edita, solo se borra y vuelve a crear)

### 8.2 desarrolla (N:M con atributos)

- [x] Crear `routes/desarrolla.py` + `templates/pages/desarrolla.html`
  - Archivo: [routes/desarrolla.py](../routes/desarrolla.py)
  - PK compuesta: `(docente, proyecto)`
  - Atributos editables: `rol`, `descripcion`
  - `crear()`: POST con los 4 campos
  - `actualizar()`: solo actualiza `rol` y `descripcion` (no la PK)
  - `eliminar()`: usa PK compuesta `docente,proyecto/X,Y`

- [x] Registrar los 2 blueprints en `app.py`
- [x] Merge a `main`

---

## Historia 9: Login y Control de Acceso

**Samuel + Jostin** — Rama: `feature/login`
**Depende de**: Todas las historias anteriores

### 9.1 Servicio de autenticación

- [x] Crear `services/auth_service.py`
  - Archivo: [services/auth_service.py](../services/auth_service.py)
  - `login()`: POST `/api/Autenticacion/token`
  - `_obtener_roles()`: SQL con JOIN vía `ConsultasController`
  - `calcular_rutas_permitidas(roles)`: mapea roles a rutas permitidas
    - `Admin` → todas las rutas
    - `EncargadoProyectos` → home + rutas con "proyecto"
    - `Visitante` → home + `/proyecto`
  - `actualizar_contrasena()`: PUT con `?camposEncriptar=password`
  - `restablecer_contrasena()`: POST endpoint público `[AllowAnonymous]`

### 9.2 Middleware

- [x] Crear `middleware/auth_middleware.py`
  - `crear_middleware(app)`: registra `before_request`
  - Rutas públicas: `/login`, `/logout`, `/restablecer-contrasena`, `/static`
  - Sin sesión → `redirect /login`
  - Ruta no permitida → página `sin_acceso.html` (403)

### 9.3 Rutas de autenticación

- [x] Crear `routes/auth.py` con Blueprint
  - `GET/POST /login`: formulario y validación
  - `GET /logout`: limpia sesión
  - `GET/POST /cambiar-contrasena`: usuario autenticado
  - `GET/POST /restablecer-contrasena`: público (olvidé mi contraseña)
  - Guardar token JWT en `session["token"]`
  - Verificar roles no vacíos (sin roles → mensaje claro)
  - Validación contraseña (6 chars, mayúscula, número)

### 9.4 JWT en ApiService

- [x] `services/api_service.py` lee `session["token"]` en `_headers()`
- [x] Cada `requests.get/post/put/delete` envía `Authorization: Bearer {JWT}`

### 9.5 Templates de auth

- [x] `templates/pages/login.html` — formulario login
- [x] `templates/pages/cambiar_contrasena.html` — cambiar contraseña
- [x] `templates/pages/restablecer_contrasena.html` — recuperar contraseña
- [x] `templates/pages/sin_acceso.html` — página 403

### 9.6 Context processor

- [x] `app.py` registra `context_processor` que inyecta:
  - `usuario`: nombre del usuario logueado
  - `roles`: lista de roles
  - `rutas_permitidas`: set para validar en templates
- [x] `nav_menu.html` solo muestra links que estén en `rutas_permitidas`

### 9.7 Modificar existentes

- [x] `app.py`: registrar `crear_middleware(app)` al final
- [x] `app.py`: registrar `auth_bp`
- [x] `templates/layout/base.html`: agregar botón login/logout en top-row

---

## Validación final

- [x] Login con usuario sin roles → "No tiene roles asignados"
- [x] Login con `Visitante` → entra, solo ve `/` y `/proyecto`
- [x] Login con `EncargadoProyectos` → ve todas las rutas con "proyecto"
- [x] Login con `Admin` → acceso total
- [x] JWT se envía en cada petición (verificar en F12 → Network)
- [x] Ruta no permitida → página 403 con mensaje claro
- [x] Cambiar contraseña funciona con BCrypt
- [x] Restablecer contraseña funciona sin sesión (público)
- [x] Maestro-detalle proyecto: crear, editar y eliminar son atómicos (SP)
- [x] Tablas N:M con PK compuesta: crear y eliminar funcionan
- [x] `desarrolla` permite editar `rol`/`descripcion` sin perder la PK
- [x] El proyecto arranca con `python app.py` sin errores
- [x] Funciona desplegado en `apicsharpneon-mapacto.runasp.net`

---

## Tareas pendientes (siguiente entrega)

- [ ] Tablas `ruta` y `rutarol` en BD para reemplazar las reglas hardcodeadas en `auth_service.py` (actualmente las rutas permitidas por rol se calculan en `calcular_rutas_permitidas`)
- [ ] Paginación real para tablas con muchos registros
- [ ] Exportación de listados a PDF/Excel
- [ ] Dashboard con estadísticas (proyectos por área, productos por docente)
- [ ] Notificación por email al crear/actualizar proyecto (vía SMTP)
- [ ] Tests automatizados con pytest

---

## Artefactos generados (resultado del SDD)

Siguiendo Spec-Kit, estos son los artefactos que se produjeron:

| Artefacto SDD | Archivo en este proyecto |
|---------------|--------------------------|
| `constitution.md` | [sdd/01_constitucion.md](01_constitucion.md) |
| `spec.md` | [sdd/02_especificacion.md](02_especificacion.md) |
| `clarify` | [sdd/03_clarificacion.md](03_clarificacion.md) |
| `plan.md` | [sdd/04_plan.md](04_plan.md) |
| `tasks.md` | [sdd/05_tareas.md](05_tareas.md) (ESTE archivo) |
| Código fuente | [app.py](../app.py), [routes/](../routes/), [services/](../services/), [templates/](../templates/) |
| Stored Procedures | `sp_consultar_proyecto_y_productos`, `sp_insertar_proyecto_y_productos`, `sp_actualizar_proyecto_y_productos` (SYNC diferencial), `sp_borrar_proyecto_y_productos`, `sp_listar_proyecto_y_productos` |

> *"Lo más importante del SDD es que la documentación es un entregable que se versiona, y el código es el resultado de esta documentación."*

---

## Reparto de trabajo entre Samuel y Jostin

| Estudiante | Historias | Responsabilidades |
|------------|-----------|-------------------|
| **Samuel** | 1, 2, 3, 4, 5, 9 | Setup, ApiService, Layout, Catálogos, Maestro-detalle proyecto (SPs), Login |
| **Jostin** | 6, 7, 8 | Consulta productos, 5 tablas N:M, Relaciones de docentes (`docente_producto`, `desarrolla` con PK compuesta) |
| **Ambos** | 9 (validación) | Pruebas de seguridad, integración final, documentación SDD |

---

## Referencias

- [GitHub Spec-Kit](https://github.com/github/spec-kit) — Toolkit oficial SDD
- [spec-driven.md](https://github.com/github/spec-kit/blob/main/spec-driven.md) — Documento técnico SDD
- [Diving Into SDD With Spec Kit (Microsoft)](https://devblogs.microsoft.com/blog/spec-driven-development-spec-kit)
- [Video: La forma CORRECTA de programar con IA en 2026](https://www.youtube.com/results?search_query=spec+driven+development+2026)

---

## Fecha de ratificación

- **Versión**: 1.0
- **Fecha**: 2026-05-21
- **Autores**: Samuel Giraldo, Jostin (Estudiantes Construcción de Software USB)
- **Referencia Spec-Kit**: [github.com/github/spec-kit](https://github.com/github/spec-kit)

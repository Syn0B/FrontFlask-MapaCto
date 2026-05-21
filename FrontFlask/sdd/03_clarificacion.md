# Etapa 3: Clarificación

Según **Spec-Kit de GitHub**: la clarificación (`/speckit.clarify`) resuelve ambigüedades **ANTES** de la planificación técnica, reduciendo retrabajos posteriores. *"La IA te hace preguntas sobre lo que olvidaste. Te fuerza a pensar para no dejar agujeros."*

**Referencia**: [spec-driven.md](https://github.com/github/spec-kit/blob/main/spec-driven.md)

---

## 1. Preguntas resueltas sobre la arquitectura

### P: ¿Por qué Flask y no Django?

**R**: Flask es un microframework sin magia. Como estudiantes vemos cada línea de código y entendemos qué hace. Django tiene ORM, admin, auth integrado — no aprenderíamos cómo funciona por debajo. Flask nos obliga a construir todo manualmente, que es el objetivo del trabajo: aprender los fundamentos.

### P: ¿Por qué no usar SQLAlchemy si Flask lo soporta?

**R**: Porque el frontend **no accede a la BD**. Todo va por HTTP a la API REST (`apicsharpneon-mapacto.runasp.net`). Si usáramos SQLAlchemy, aprenderíamos ORM pero no aprenderíamos a consumir APIs, que es lo que se necesita en el mundo real (microservicios, frontends desacoplados).

### P: ¿Por qué la API es en C# y no en Python?

**R**: Para que quede claro que frontend y backend son independientes. Si ambos fueran Python, podríamos confundir Flask con la API. Con C# queda obvio: Flask es el frontend, C# es el backend, se comunican por HTTP.

### P: ¿Qué pasa si la API no está corriendo?

**R**: Los servicios (`ApiService`, `AuthService`) tienen `try/except` que capturan `requests.RequestException`. Si la API no responde, se muestra un mensaje de error en pantalla sin que la app crashee. El login falla con "Error de conexión".

### P: ¿Por qué la API está hospedada en `runasp.net` y no en `localhost`?

**R**: Para que Samuel y Jostin podamos consumir la misma API desde nuestros equipos sin necesidad de levantar un backend local cada uno. Así trabajamos en paralelo sobre la misma BD y los cambios se ven entre ambos. En el ejemplo del profesor la API era local (`localhost:5035`) porque era para un solo estudiante.

---

## 2. Preguntas resueltas sobre seguridad

### P: Si la sesión es una cookie, ¿el usuario puede manipularla?

**R**: Flask firma la cookie con `SECRET_KEY` usando HMAC. Si el usuario cambia un byte, la firma no coincide y Flask la invalida. No puede inyectar roles ni rutas.

### P: ¿Por qué guardar el JWT si Flask ya tiene sesión?

**R**: Son **dos capas diferentes**:

- La **sesión Flask** protege las páginas del frontend (middleware verifica antes de cada request)
- El **JWT** protege los datos de la API (si tiene `[Authorize]`, rechaza sin token)

Sin JWT, alguien puede abrir Postman y hacer `DELETE /api/proyecto/id/5` sin haber hecho login.

### P: ¿Qué pasa si el JWT expira durante la sesión?

**R**: La API responde 401. El `ApiService` no maneja esto automáticamente — el usuario ve un error y debe hacer login de nuevo. En un sistema de producción se implementaría refresh token, pero está fuera del alcance del trabajo.

### P: ¿Por qué no usar Spring Security / Passport.js / otro framework de auth?

**R**: Porque el objetivo es que **entendamos cómo funciona la autenticación**. Si usamos un framework de auth, solo configuramos y no aprendemos. Construirlo manualmente nos enseña: BCrypt, JWT, sesión, middleware, roles, rutas.

### P: ¿Las contraseñas viajan en texto plano por HTTP?

**R**: En desarrollo local (`http://localhost:5100`) viajan en texto plano por la red local. La API en `runasp.net` ya usa HTTPS. La contraseña viaja en el body del POST (no en la URL) y solo el servidor la lee. La API inmediatamente la compara con el hash BCrypt — **nunca** se guarda en texto plano.

---

## 3. Preguntas resueltas sobre el CRUD

### P: ¿Cómo sabe el formulario qué tipo de input usar para cada campo?

**R**: Los templates tienen los tipos hardcodeados por tabla (ej: `type="number"` para `presupuesto`, `type="date"` para `fecha_inicio`, `type="text"` para `titulo`). En un generador genérico se descubriría el tipo vía `/api/estructuras/basedatos` y se mapearía: `varchar -> text`, `integer -> number`, `boolean -> checkbox`, `date -> date`, etc.

### P: ¿Qué pasa con los campos FK en los formularios?

**R**: Se renderizan como `<select>` cargados desde la API. Ejemplo: en `producto`, el campo `fktipo_producto` se muestra como un dropdown con todos los tipos de producto. El template hace `{% for t in tipos_producto %}` para llenar las opciones.

### P: ¿Y si una tabla tiene muchos registros (1000+)?

**R**: Se usa `?limite=N` en la URL de la API. Los CRUDs del trabajo no implementan paginación — traen todo con un límite alto. En producción se implementaría paginación real (fuera del alcance).

### P: ¿Cómo se manejan los errores de la API (400, 404, 500)?

**R**: `ApiService` retorna tupla `(exito, mensaje)`. La ruta usa `flash(mensaje, "danger")` para mostrar el error al usuario. No se propagan excepciones al template.

### P: ¿Por qué `proyecto` usa Stored Procedures y los demás CRUDs no?

**R**: Porque `proyecto` es un **maestro-detalle** (proyecto + N productos). Si crearamos el proyecto con una llamada y los productos con N llamadas más, no habría atomicidad: si falla la llamada 3 de 5, quedaría un proyecto a medias. El SP `sp_insertar_proyecto_y_productos` inserta todo en una sola transacción atómica. Los demás CRUDs (catálogos, N:M simples) son operaciones de una sola tabla y no requieren SP.

---

## 4. Preguntas resueltas sobre el descubrimiento dinámico

### P: ¿Por qué no hardcodear `fkemail` y `fkidrol`?

**R**: Porque si otra BD usa `id_usuario` o `email_usuario`, el código deja de funcionar. El descubrimiento dinámico vía `/api/estructuras/basedatos` permite que el mismo código funcione con cualquier BD que tenga las 5 tablas de auth, sin importar cómo se llamen las columnas.

### P: ¿Qué pasa si la API no tiene el endpoint `/api/estructuras`?

**R**: El `AuthService` tiene métodos fallback (`_obtener_roles_fallback`, `_obtener_rutas_fallback`) que usan GETs separados al CRUD genérico. Si los FKs no se descubren, se activa el fallback automáticamente.

### P: ¿Por qué usar `ConsultasController` en vez de los GETs separados?

**R**: **Eficiencia**. Los GETs separados traen tablas COMPLETAS y filtran en Python. `ConsultasController` ejecuta 1 SQL con JOINs y WHERE en la BD — solo viajan las filas del usuario. Reduce el tráfico de red de varias tablas completas a unas pocas filas.

---

## 5. Preguntas resueltas sobre el trabajo colaborativo

### P: ¿Qué pasa si Samuel y Jostin crean la misma ruta?

**R**: Conflicto de merge en `app.py`. Se resuelve en la rama `feature/` antes de mergear a `main`. Por eso nos repartimos las tablas (Samuel: maestro-detalle proyecto-producto y catálogos; Jostin: tablas N:M y relaciones de docentes).

### P: ¿Qué pasa si uno instala un paquete nuevo?

**R**: Debe hacer `pip freeze > requirements.txt` y commitear el cambio. Si no lo hace, al otro le falla el proyecto con `ModuleNotFoundError`.

### P: ¿Quién resuelve conflictos de merge?

**R**: Quien abra el PR. Antes de hacer PR, debe hacer `git fetch origin` y mergear `main` a su rama local para resolver conflictos en su entorno, no en `main`.

### P: ¿Por qué un repositorio único y no uno por persona?

**R**: Porque la entrega es un único proyecto integrado. Tener repos separados duplicaría código (mismo `app.py`, mismo `api_service.py`) y haría imposible probar los CRUDs cruzados (ej: un producto necesita ver los tipos de producto que creó el otro).

---

## 6. Decisiones de diseño documentadas

| Decisión | Alternativa descartada | Razón |
|----------|------------------------|-------|
| Flask (microframework) | Django (fullstack) | Vemos todo, nada es magia |
| Jinja2 (templates server-side) | React/Vue (SPA) | Menos complejidad, un solo lenguaje |
| `requests` (HTTP client) | `httpx`, `aiohttp` | Síncrono y simple, sin async |
| `session` (cookie firmada) | JWT-only (stateless) | Flask lo trae integrado, fácil de aplicar |
| `ConsultasController` (1 SQL) | GETs separados | Eficiencia, menos tráfico de red |
| Bootstrap CDN | Tailwind, Material UI | Sin build tools, funciona con un link |
| Descubrimiento dinámico FK/PK | Hardcodear nombres | Funciona con cualquier BD |
| Middleware `before_request` | Decorador `@login_required` | Protege TODAS las rutas automáticamente |
| PostgreSQL en Neon Cloud | MySQL, SQLite, local | ACID completo, accesible desde cualquier equipo |
| Stored Procedures (proyecto) | N llamadas POST seguidas | Atomicidad en operaciones maestro-detalle |
| 3FN (normalización) | Desnormalizar para rendimiento | Integridad sobre velocidad en sistema académico |
| Tablas intermedias N:M | Arrays en columna | 1FN: valores atómicos, sin grupos repetidos |

---

## 7. Preguntas resueltas sobre el modelo de datos

### P: ¿Por qué `proyecto` y `producto` están en tablas separadas si un producto pertenece a un solo proyecto?

**R**: Porque un proyecto tiene **muchos productos** (1:N). Si pusiéramos los productos como columnas de `proyecto`, violaríamos 1FN (valores atómicos). Además, `producto` también tiene FK a `tipo_producto`, lo que requiere su propia entidad.

### P: ¿Por qué `desarrolla` tiene PK compuesta `(docente, proyecto)` y no un `id` autoincremental?

**R**: Porque la combinación `(docente, proyecto)` debe ser **única** — un docente no debería estar dos veces en el mismo proyecto. Una PK compuesta lo garantiza naturalmente sin necesidad de un UNIQUE constraint extra. Además, `desarrolla` tiene atributos propios (`rol`, `descripcion`), por eso no es una tabla intermedia "pura" como `aa_proyecto`.

### P: ¿Por qué los productos guardan `fecha_entrega` si el proyecto ya tiene `fecha_inicio` y `fecha_fin`?

**R**: Porque un proyecto dura años y produce múltiples productos en distintas fechas. La `fecha_entrega` del producto es independiente del rango del proyecto y permite saber exactamente cuándo se generó cada entregable.

### P: ¿Por qué `usuario` tiene `email` como PK y no un id numérico?

**R**: Porque el email es único y natural — es lo que el usuario escribe para hacer login. Usar un id numérico obligaría a hacer un JOIN extra para buscar por email. Además, simplifica las FKs en `rol_usuario` (`fkemail` es legible).

### P: ¿Por qué las tablas de seguridad están separadas de las de negocio?

**R**: Principio de Single Responsibility (SOLID - S). Las tablas de negocio (`proyecto`, `producto`, `docente`) manejan datos del dominio. Las tablas de seguridad (`rol`, `ruta`) manejan permisos. Si un día se cambia el sistema de permisos, no se tocan las tablas de negocio.

### P: ¿Por qué no usar herencia de tablas (una tabla padre "persona" para `docente` y `aliado`)?

**R**: Porque PostgreSQL soporta herencia pero no es portable a SQL Server. Además, `docente` y `aliado` tienen atributos diferentes (un aliado puede ser una empresa, un docente es siempre una persona natural). Usar tablas separadas es más simple y claro.

### P: ¿Por qué ACID y no BASE (eventual consistency)?

**R**: Este es un sistema transaccional (proyectos, presupuestos, asignaciones académicas). ACID garantiza que un proyecto se crea completo con sus productos o no se crea. BASE es para sistemas distribuidos de alta escala (redes sociales, IoT) donde se acepta inconsistencia temporal. Un sistema académico **NO** puede tener inconsistencia temporal — un proyecto no puede "eventualmente" tener su presupuesto y productos asociados.

### P: ¿Por qué los ODS están como tabla y no como un enum?

**R**: Porque los ODS son 17 valores estables, pero al ser tabla podemos relacionarlos N:M con varios proyectos (`ods_proyecto`) y guardar información adicional (nombre completo, descripción, color). Un enum solo permitiría almacenar el ID, no más metadata.

---

## 8. Principios de diseño aplicados (resumen)

| Principio | Categoría | Dónde aplica | Referencia |
|-----------|-----------|--------------|------------|
| SOLID - S (Single Responsibility) | OOP | Cada archivo/clase tiene 1 responsabilidad | [01_constitucion.md](01_constitucion.md), Art. VII |
| SOLID - O (Open/Closed) | OOP | Agregar CRUD = archivos nuevos, no modificar existentes | [01_constitucion.md](01_constitucion.md), Art. VII |
| SOLID - D (Dependency Inversion) | OOP | Routes dependen de `ApiService`, no de `requests` | [01_constitucion.md](01_constitucion.md), Art. VII |
| ACID | BD | PostgreSQL garantiza transacciones íntegras | [01_constitucion.md](01_constitucion.md), Art. VIII |
| Atomicidad vía SP | BD | `sp_insertar_proyecto_y_productos` garantiza maestro-detalle atómico | [02_especificacion.md](02_especificacion.md), Flujo 3 |
| 3FN (Normalización) | BD | Sin datos redundantes, FKs para relaciones | [02_especificacion.md](02_especificacion.md), sección ER |
| MVC | Arquitectura | `services/` + `templates/` + `routes/` | [01_constitucion.md](01_constitucion.md), Art. II |
| Facade | Patrón | `ApiService` oculta complejidad HTTP | [01_constitucion.md](01_constitucion.md), Art. IX |
| Strategy (fallback) | Patrón | `ConsultasController` o GETs según disponibilidad | [01_constitucion.md](01_constitucion.md), Art. IX |
| Middleware/Interceptor | Patrón | `before_request` verifica auth en CADA request | [01_constitucion.md](01_constitucion.md), Art. IX |

---

## Fecha de ratificación

- **Versión**: 1.0
- **Fecha**: 2026-05-21
- **Autores**: Samuel Giraldo, Jostin (Estudiantes Diseño de Software USB)
- **Referencia Spec-Kit**: [github.com/github/spec-kit](https://github.com/github/spec-kit)

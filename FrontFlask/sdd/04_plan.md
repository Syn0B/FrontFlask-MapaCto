# Etapa 4: Plan de Implementación

Según **Spec-Kit**: el plan traduce los requisitos de la especificación en **decisiones técnicas concretas**. *"Cada elección de tecnología tiene una rationale documentada."* El plan se genera con `/speckit.plan` y el humano lo valida.

**Referencia**: [plan-template.md](https://github.com/github/spec-kit/blob/main/templates/plan-template.md)

---

## 1. Resumen técnico

Frontend web en **Flask** que consume la API genérica C# (`apicsharpneon-mapacto.runasp.net`) vía HTTP. Arquitectura **MVC adaptada**: `routes/` (controladores) + `services/` (lógica) + `templates/` (vistas). Autenticación con **BCrypt + JWT + sesión Flask**. Control de acceso por roles (`Admin`, `EncargadoProyectos`, `Visitante`) y rutas con middleware `before_request`. Operaciones maestro-detalle (proyecto + productos) implementadas con **Stored Procedures** para garantizar atomicidad.

---

## 2. Estructura de archivos del proyecto

```
FrontFlask-MapaCto/
└── FrontFlask/
    ├── app.py                           <- Punto de entrada: crea Flask, registra todo
    ├── config.py                        <- API_BASE_URL, SECRET_KEY
    ├── requirements.txt                 <- flask, requests
    ├── requirements-prod.txt            <- Para deploy en runasp.net
    ├── Procfile                         <- Para deploy en runasp.net
    │
    ├── services/
    │   ├── __init__.py
    │   ├── api_service.py               <- CRUD generico + ejecutar_sp (SPs)
    │   └── auth_service.py              <- Login, roles, rutas, ConsultasController, restablecer
    │
    ├── routes/
    │   ├── __init__.py
    │   ├── home.py                      <- /
    │   ├── auth.py                      <- /login, /logout, /cambiar-contrasena, /restablecer
    │   ├── proyecto.py                  <- /proyecto (maestro-detalle con SPs)
    │   ├── producto.py                  <- /producto (solo consulta)
    │   ├── tipo_producto.py             <- /tipo_producto (CRUD catalogo)
    │   ├── termino_clave.py             <- /termino_clave (CRUD catalogo)
    │   ├── palabras_clave.py            <- /palabras_clave (CRUD catalogo)
    │   ├── aa_proyecto.py               <- /aa_proyecto (N:M)
    │   ├── ac_proyecto.py               <- /ac_proyecto (N:M)
    │   ├── ods_proyecto.py              <- /ods_proyecto (N:M)
    │   ├── proyecto_linea.py            <- /proyecto_linea (N:M)
    │   ├── aliado_proyecto.py           <- /aliado_proyecto (N:M)
    │   ├── docente_producto.py          <- /docente_producto (N:M)
    │   └── desarrolla.py                <- /desarrolla (N:M con atributos rol/descripcion)
    │
    ├── middleware/
    │   └── auth_middleware.py           <- before_request + context_processor
    │
    ├── templates/
    │   ├── layout/
    │   │   └── base.html                <- Layout: sidebar + top-row + content + Bootstrap
    │   ├── components/
    │   │   └── nav_menu.html            <- Menu lateral colapsable
    │   └── pages/
    │       ├── home.html
    │       ├── login.html
    │       ├── cambiar_contrasena.html
    │       ├── restablecer_contrasena.html
    │       ├── sin_acceso.html
    │       ├── proyecto.html             <- Maestro-detalle con filas dinamicas
    │       ├── producto.html
    │       ├── tipo_producto.html
    │       ├── termino_clave.html
    │       ├── palabras_clave.html
    │       ├── aa_proyecto.html
    │       ├── ac_proyecto.html
    │       ├── ods_proyecto.html
    │       ├── proyecto_linea.html
    │       ├── aliado_proyecto.html
    │       ├── docente_producto.html
    │       └── desarrolla.html
    │
    ├── static/css/                      <- Estilos custom
    │
    └── sdd/                             <- Documentacion SDD (estos archivos)
```

---

## 3. Orden de implementación (por etapas)

Cada etapa corresponde a un grupo de funcionalidades y a una o más ramas `feature/`.

| Orden | Etapa | Qué se implementa | Dependencias | Responsable |
|-------|-------|-------------------|--------------|-------------|
| 1 | Etapa 0 | Plan de desarrollo, reglas SDD | Ninguna | Samuel + Jostin |
| 2 | Etapa 1 | Proyecto base: `app.py`, `config.py`, Git | Etapa 0 | Samuel |
| 3 | Etapa 2 | `ApiService` (CRUD + `ejecutar_sp`) | Etapa 1 | Samuel |
| 4 | Etapa 3 | Layout base, `nav_menu`, `home` | Etapa 2 | Samuel |
| 5 | Etapa 4 | CRUD catálogos: `tipo_producto`, `termino_clave`, `palabras_clave` | Etapa 3 | Samuel |
| 6 | Etapa 5 | Maestro-detalle `proyecto` + SPs | Etapa 4 | Samuel |
| 7 | Etapa 6 | Consulta `producto` | Etapa 5 | Jostin |
| 8 | Etapa 7 | N:M: `aa_proyecto`, `ac_proyecto`, `ods_proyecto`, `proyecto_linea`, `aliado_proyecto` | Etapa 5 | Jostin |
| 9 | Etapa 8 | N:M docentes: `docente_producto`, `desarrolla` (PK compuesta) | Etapa 7 | Jostin |
| 10 | Etapa 9 | Login + JWT + middleware + roles + restablecer | Etapa 3 | Samuel + Jostin |

### Diagrama de dependencias

```
Etapa 0 (plan SDD)
  |
  v
Etapa 1 (proyecto base)
  |
  v
Etapa 2 (ApiService)
  |
  v
Etapa 3 (layout + nav + home)
  |
  +---------+----------+
  v         v          v
Etapa 4   Etapa 9     (paralelo: catalogos / login)
  |         |
  v         |
Etapa 5     |  (maestro-detalle proyecto con SPs)
  |         |
  +---------+
  |
  v
Etapa 6 + 7 + 8  (paralelo: consulta producto, N:M, desarrolla)
```

---

## 4. Modelo de datos

### Tablas de negocio

| Tabla | PK | Campos clave | FKs |
|-------|-----|--------------|-----|
| `proyecto` | `id` | `titulo`, `resumen`, `presupuesto`, `tipo_financiacion`, `tipo_fondos`, `fecha_inicio`, `fecha_fin` | — |
| `producto` | `id` | `nombre`, `categoria`, `fecha_entrega` | `fkproyecto` → `proyecto`, `fktipo_producto` → `tipo_producto` |
| `tipo_producto` | `id` | `nombre` | — |
| `docente` | `cedula` | `nombre`, `correo` | — |
| `aliado` | `id` | `nombre` | — |

### Tablas catálogo

| Tabla | PK | Campos |
|-------|-----|--------|
| `termino_clave` | `id` | `termino` |
| `palabras_clave` | `id` | `palabra` |
| `aa` | `id` | `nombre` (Área Académica) |
| `ac` | `id` | `nombre` (Área de Conocimiento) |
| `ods` | `id` | `nombre`, `numero` |
| `linea` | `id` | `nombre` |

### Tablas relacionales (N:M)

| Tabla | PK compuesta | Atributos extra |
|-------|--------------|-----------------|
| `aa_proyecto` | `(fkproyecto, fkaa)` | — |
| `ac_proyecto` | `(fkproyecto, fkac)` | — |
| `ods_proyecto` | `(fkproyecto, fkods)` | — |
| `proyecto_linea` | `(fkproyecto, fklinea)` | — |
| `aliado_proyecto` | `(fkproyecto, fkaliado)` | — |
| `docente_producto` | `(fkdocente, fkproducto)` | — |
| `desarrolla` | `(docente, proyecto)` | `rol`, `descripcion` |

### Tablas de seguridad (auth)

| Tabla | PK | Campos | FKs |
|-------|-----|--------|-----|
| `usuario` | `id` | `username`, `email`, `password` (BCrypt) | — |
| `rol` | `id` | `nombre` | — |
| `rol_usuario` | `id` | — | `usuario_id`, `rol_id` |
| `ruta` | `id` | `ruta`, `descripcion` | — |
| `rutarol` | `id` | — | `fkidrol`, `fkidruta` |

---

## 5. Decisiones técnicas

| Decisión | Alternativa | Razón |
|----------|-------------|-------|
| Stored Procedures para `proyecto` | N llamadas POST individuales | Atomicidad maestro-detalle |
| `ConsultasController` (1 SQL) | GETs separados | Eficiencia: la BD filtra, no Python |
| Cookie firmada (Flask session) | JWT stateless | Flask lo trae integrado |
| `requests` síncrono | `httpx` async | Simplicidad para trabajo académico |
| Bootstrap CDN | `npm install` | Sin build tools |
| Middleware `before_request` | Decorador `@login_required` | Protege TODO automáticamente |
| `context_processor` | Pasar vars manual | Inyecta en todas las templates |
| API en `runasp.net` (remota) | API local | Permite trabajo colaborativo Samuel + Jostin |
| Roles hardcodeados en `auth_service` | Tabla `rutarol` en BD | Implementación inicial simple; futura migración a `rutarol` |

---

## 6. Endpoints de la API utilizados

### CRUD genérico (cada tabla)

```
GET    /api/{tabla}?limite=N                                 <- Listar
POST   /api/{tabla}                                          <- Crear
PUT    /api/{tabla}/{pk}/{valor}                             <- Actualizar
PUT    /api/{tabla}/{pk1}/{val1}/{pk2}/{val2}                <- Actualizar PK compuesta
DELETE /api/{tabla}/{pk}/{valor}                             <- Eliminar
DELETE /api/{tabla}/{pk1}/{val1}/{pk2}/{val2}                <- Eliminar PK compuesta
```

### Stored Procedures (maestro-detalle)

```
POST   /api/procedimientos/ejecutarsp                        <- Ejecuta cualquier SP
   sp_insertar_proyecto_y_productos
   sp_actualizar_proyecto_y_productos
   sp_borrar_proyecto_y_productos
   sp_consultar_proyecto_y_productos
```

### Autenticación y seguridad

```
POST   /api/Autenticacion/token                              <- Login BCrypt + JWT
POST   /api/Autenticacion/restablecer-contrasena             <- Restablecer (publico)
POST   /api/consultas/ejecutarconsultaparametrizada          <- SQL JOIN roles
PUT    /api/usuario/{pk}/{val}?camposEncriptar=password      <- Cambiar clave
```

---

## 7. Diagramas de secuencia

Los diagramas de secuencia muestran la interacción entre componentes en el tiempo. Formato **Mermaid** — se renderiza automáticamente en GitHub.

### 7.1 Secuencia: Login completo

```mermaid
sequenceDiagram
    actor U as Usuario (Samuel/Jostin)
    participant B as Navegador
    participant F as Flask (routes/auth.py)
    participant AS as AuthService
    participant API as API C# (runasp.net)
    participant BD as PostgreSQL (Neon)

    U->>B: Abre http://localhost:5100
    B->>F: GET /
    F->>F: Middleware: no hay sesion
    F-->>B: Redirect /login
    B->>U: Muestra formulario login

    U->>B: Escribe username + password
    B->>F: POST /login (form-data)
    F->>AS: login(usuario, contrasena)
    AS->>API: POST /api/Autenticacion/token
    API->>BD: SELECT password FROM usuario WHERE username=?
    BD-->>API: hash BCrypt
    API->>API: BCrypt.Verify(contrasena, hash)
    API-->>AS: {token, usuario, expiracion}

    AS->>API: POST /api/consultas/ejecutar (SQL JOIN roles)
    API->>BD: SELECT r.nombre FROM usuario JOIN rol_usuario JOIN rol
    BD-->>API: [{nombre: "Admin"}]
    API-->>AS: {resultados: [...]}
    AS->>AS: calcular_rutas_permitidas(roles)
    AS-->>F: (True, {token, roles, rutas_permitidas})

    F->>F: session["token"] = token
    F->>F: session["roles"] = roles
    F->>F: session["rutas_permitidas"] = rutas
    F-->>B: Redirect /home
    B-->>U: Muestra home con sidebar segun roles
```

### 7.2 Secuencia: CRUD Listar con JWT

```mermaid
sequenceDiagram
    actor U as Usuario
    participant B as Navegador
    participant F as Flask (routes/tipo_producto.py)
    participant M as Middleware
    participant AS as ApiService
    participant API as API C#
    participant BD as PostgreSQL

    U->>B: Click "Tipo Producto"
    B->>F: GET /tipo_producto
    F->>M: before_request
    M->>M: ¿session.token existe?
    M->>M: ¿/tipo_producto in rutas_permitidas?
    M-->>F: OK, continuar

    F->>AS: api.listar("tipo_producto")
    AS->>AS: _headers() agrega Authorization: Bearer {JWT}
    AS->>API: GET /api/tipo_producto
    API->>API: Valida JWT [Authorize]
    API->>BD: SELECT * FROM tipo_producto
    BD-->>API: [{id:1, nombre:"Articulo Q1"}, ...]
    API-->>AS: {datos: [...]}
    AS-->>F: lista de dicts

    F->>F: render_template("pages/tipo_producto.html", registros=...)
    F-->>B: HTML renderizado
    B-->>U: Muestra tabla
```

### 7.3 Secuencia: CRUD Crear proyecto con SP (maestro-detalle)

```mermaid
sequenceDiagram
    actor U as Usuario
    participant B as Navegador
    participant F as Flask (routes/proyecto.py)
    participant AS as ApiService
    participant API as API C#
    participant BD as PostgreSQL

    U->>B: Llena formulario proyecto + N productos
    B->>F: POST /proyecto/crear (form-data + arrays)
    F->>F: Recoge titulo, resumen, presupuesto, fechas
    F->>F: Recoge listas paralelas prod_nombre[], prod_categoria[], ...
    F->>F: Construye productos_lista = [{nombre, categoria, ...}]

    F->>AS: ejecutar_sp("sp_insertar_proyecto_y_productos", {...})
    AS->>API: POST /api/procedimientos/ejecutarsp
    API->>BD: BEGIN TRANSACTION
    API->>BD: INSERT INTO proyecto (titulo, ...) RETURNING id
    BD-->>API: nuevo_id
    loop Por cada producto
        API->>BD: INSERT INTO producto (nombre, fkproyecto, ...)
    end
    API->>BD: COMMIT
    BD-->>API: OK
    API-->>AS: {resultados:[{p_resultado: "..."}]}
    AS-->>F: (True, datos)

    F->>F: flash("Proyecto creado exitosamente", "success")
    F-->>B: Redirect /proyecto
    B-->>U: Lista de proyectos con flash
```

### 7.4 Secuencia: Acceso denegado

```mermaid
sequenceDiagram
    actor U as Usuario
    participant B as Navegador
    participant F as Flask
    participant M as Middleware

    U->>B: Click "Tipo Producto" (rol Visitante)
    B->>F: GET /tipo_producto
    F->>M: before_request
    M->>M: session.token existe ✔
    M->>M: ¿/tipo_producto in rutas_permitidas?
    M->>M: NO (Visitante solo tiene "/" y "/proyecto")
    M-->>F: render sin_acceso.html (403)
    F-->>B: HTML "Acceso Denegado"
    B-->>U: Muestra pagina 403
```

### 7.5 Secuencia: Cambiar contraseña

```mermaid
sequenceDiagram
    actor U as Usuario
    participant B as Navegador
    participant F as Flask (routes/auth.py)
    participant AS as AuthService
    participant API as API C#
    participant BD as PostgreSQL

    U->>B: Click "Cambiar contrasena"
    B->>F: GET /cambiar-contrasena
    F-->>B: Formulario (actual + nueva + confirmar)

    U->>B: Llena formulario y submit
    B->>F: POST /cambiar-contrasena
    F->>F: Valida 6 chars + mayuscula + numero
    F->>AS: actualizar_contrasena(usuario, nueva, token)
    AS->>API: PUT /api/usuario/username/{user}?camposEncriptar=password
    API->>API: BCrypt.HashPassword(nueva)
    API->>BD: UPDATE usuario SET password=hash WHERE username=?
    BD-->>API: OK
    API-->>AS: {mensaje: "Actualizado"}
    AS-->>F: (True, mensaje)

    F->>F: flash("Contrasena cambiada", "success")
    F-->>B: Redirect /home
```

### 7.6 Secuencia: Restablecer contraseña (público)

```mermaid
sequenceDiagram
    actor U as Usuario olvidadizo
    participant B as Navegador
    participant F as Flask (routes/auth.py)
    participant AS as AuthService
    participant API as API C#
    participant BD as PostgreSQL

    U->>B: Click "Olvide mi contrasena" desde /login
    B->>F: GET /restablecer-contrasena
    F-->>B: Formulario (username + email + nueva)

    U->>B: Llena y submit
    B->>F: POST /restablecer-contrasena
    F->>AS: restablecer_contrasena(usuario, email, nueva)
    AS->>API: POST /api/Autenticacion/restablecer-contrasena [AllowAnonymous]
    API->>BD: SELECT email FROM usuario WHERE username=?
    BD-->>API: email_registrado
    API->>API: ¿email == email_registrado?
    API->>API: BCrypt.HashPassword(nueva)
    API->>BD: UPDATE usuario SET password=hash WHERE username=?
    BD-->>API: OK
    API-->>AS: {mensaje: "Restablecida"}
    AS-->>F: (True, mensaje)
    F-->>B: Redirect /login con flash
```

---

## 8. Diagrama de clases

Muestra las clases Python del proyecto, sus atributos, métodos y relaciones. Formato **Mermaid** — se renderiza en GitHub.

### 8.1 Diagrama de clases completo

```mermaid
classDiagram
    class Flask {
        +secret_key: str
        +context_processor()
        +register_blueprint()
        +before_request()
    }

    class ApiService {
        -base_url: str
        +listar(tabla, limite) list
        +crear(tabla, datos, encriptar) tuple
        +actualizar(tabla, pk, valor, datos) tuple
        +eliminar(tabla, pk, valor) tuple
        +ejecutar_sp(nombre, params) tuple
        -_headers() dict
        -_ruta_clave(pk, val) str
    }

    class AuthService {
        -base_url: str
        +login(usuario, contrasena) tuple
        +actualizar_contrasena(usr, nueva, token) tuple
        +restablecer_contrasena(usr, email, nueva) tuple
        -_obtener_roles(username, token) list
    }

    class AuthMiddleware {
        +before_request()
        +context_processor()
    }

    class BlueprintAuth {
        +login()
        +logout()
        +cambiar_contrasena()
        +restablecer_contrasena()
    }

    class BlueprintProyecto {
        +index()
        +crear()
        +actualizar()
        +eliminar()
    }

    class BlueprintCatalogo {
        +index()
        +crear()
        +actualizar()
        +eliminar()
    }

    class BlueprintNM {
        +index()
        +crear()
        +actualizar()
        +eliminar()
    }

    Flask "1" *-- "1" AuthMiddleware : registra
    Flask "1" *-- "*" BlueprintAuth : registra
    Flask "1" *-- "*" BlueprintProyecto : registra
    Flask "1" *-- "*" BlueprintCatalogo : registra
    Flask "1" *-- "*" BlueprintNM : registra

    BlueprintProyecto ..> ApiService : usa
    BlueprintCatalogo ..> ApiService : usa
    BlueprintNM ..> ApiService : usa
    BlueprintAuth ..> AuthService : usa
    BlueprintAuth ..> ApiService : usa

    ApiService ..> Flask : lee session.token
    AuthMiddleware ..> Flask : lee session
```

### 8.2 Relaciones entre clases

| Relación | Tipo | Descripción |
|----------|------|-------------|
| `Flask` → `AuthMiddleware` | Composición | Flask registra el middleware al iniciar |
| `Flask` → `Blueprints` | Composición | Flask registra todos los blueprints |
| `BlueprintProyecto` → `ApiService` | Dependencia | Usa `ejecutar_sp` para SPs maestro-detalle |
| `BlueprintCatalogo` → `ApiService` | Dependencia | Usa `listar/crear/actualizar/eliminar` |
| `BlueprintNM` → `ApiService` | Dependencia | Usa CRUD con PK compuesta |
| `BlueprintAuth` → `AuthService` | Dependencia | Usa login, roles, restablecer |
| `ApiService` → `Flask session` | Uso | Lee token JWT para `_headers()` |
| `AuthService` — `ApiService` | Independiente | Cada uno usa `requests` por separado |

### 8.3 ¿Por qué `AuthService` es independiente de `ApiService`?

```
AuthService usa requests.post/put directo, NO ApiService.

Razón: ApiService asume que ya hay un JWT en la sesión (lee session.token
en _headers()). Pero AuthService es quien GENERA el JWT — todavía no hay
sesión cuando se hace login. Si AuthService usara ApiService, habría una
dependencia circular: ApiService necesita el token que AuthService aún
no ha obtenido.

Además, AuthService con requests directo funciona en CUALQUIER proyecto
Flask, sin importar como esté implementado ApiService.

AuthService                    ApiService
  |                              |
  +-- requests.post/put          +-- requests.get/post/put/delete
  |   (sin token o con token     |   (con _headers() lee session.token)
  |    pasado por parametro)     |
  v                              v
  API Generica C# en runasp.net  API Generica C# en runasp.net
```

---

## Referencias Spec-Kit

- **Formato plan**: [plan-template.md](https://github.com/github/spec-kit/blob/main/templates/plan-template.md)
- **Principio de simplicidad**: [spec-driven.md, Artículo VII](https://github.com/github/spec-kit/blob/main/spec-driven.md)
- **Flujo SDD**: [README de Spec-Kit](https://github.com/github/spec-kit)
- **Mermaid (diagramas)**: [mermaid.js.org](https://mermaid.js.org)

---

## Fecha de ratificación

- **Versión**: 1.0
- **Fecha**: 2026-05-21
- **Autores**: Samuel Giraldo, Jostin (Estudiantes Diseño de Software USB)
- **Referencia Spec-Kit**: [github.com/github/spec-kit](https://github.com/github/spec-kit)

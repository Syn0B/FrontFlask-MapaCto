# Etapa 2: Especificación

Según **Spec-Kit de GitHub**: la especificación (`/speckit.specify`) documenta **QUÉ** construir y **POR QUÉ**, sin enfocarse en tecnología. Se genera `spec.md` con historias de usuario y requisitos funcionales. *"Se comienza con una idea, a menudo vaga, que evoluciona hacia un documento de requisitos comprensivo."*

**Referencia**: [spec-driven.md](https://github.com/github/spec-kit/blob/main/spec-driven.md)

---

## 1. Problema que resuelve

La universidad necesita un sistema centralizado para **mapear y gestionar los proyectos de investigación** que desarrollan los docentes, junto con los productos académicos derivados (artículos, software, libros, capítulos), las áreas de conocimiento, las líneas de investigación, los ODS y los aliados externos. No existe una herramienta interna que:

- Permita registrar un **proyecto con sus múltiples productos** en una sola transacción
- Relacione los proyectos con sus **áreas académicas, áreas de conocimiento, ODS y aliados** de forma estructurada
- Permita un control de acceso por roles (administrador, docente, consulta) con seguridad real
- Sirva de fuente de consulta para reportes institucionales y procesos de acreditación
- Pueda replicarse como base para otros mapeos académicos (mapeo curricular, mapeo de competencias)

---

## 2. Para quién va dirigido

| Audiencia | Nivel | Qué saben | Qué necesitan |
|-----------|-------|-----------|---------------|
| Administrador del sistema | Avanzado | Gestión académica, datos institucionales | Registrar proyectos, asignar docentes, generar reportes |
| Docentes investigadores | Intermedio | Su proyecto y sus productos | Registrar y actualizar sus propios productos |
| Coordinadores de área | Intermedio | Áreas académicas y de conocimiento | Consultar proyectos por área y línea |
| Estudiantes (Samuel, Jostin) | Aprendiz | Python básico, HTML, BD relacional | Aprender Flask + API REST + JWT + control de acceso |

---

## 3. Qué se construye

Un frontend web completo en **Flask** que consume la API REST `apicsharpneon-mapacto.runasp.net` y permite:

### 3.1 Funcionalidades principales

| # | Funcionalidad | Descripción | Tablas involucradas |
|---|---------------|-------------|---------------------|
| 1 | CRUD proyecto-productos | Crear, editar y eliminar proyectos con sus productos en una transacción (Stored Procedure) | `proyecto`, `producto`, `tipo_producto` |
| 2 | CRUD `tipo_producto` | Catálogo institucional de tipos (categoria, clase, nombre, tipologia) | `tipo_producto` |
| 3 | CRUD `termino_clave` | Catálogo de términos (PK es la cadena `termino`, opcionalmente `termino_ingles`) | `termino_clave` |
| 4 | Asignación N:M `palabras_clave` | Vincula proyectos con términos clave (NO es un catálogo: es una tabla puente) | `palabras_clave` (proyecto, termino_clave) |
| 5 | Asignaciones N:M de proyecto | Asociar a un proyecto sus áreas de aplicación, áreas de conocimiento, ODS, líneas y aliados | `aa_proyecto`, `ac_proyecto`, `ods_proyecto`, `proyecto_linea`, `aliado_proyecto` |
| 6 | Relación docente-producto | Asignar docentes a los productos derivados | `docente_producto` |
| 7 | Relación desarrolla | Asignar docentes a proyectos con rol y descripción | `desarrolla` (PK compuesta + atributos) |
| 8 | Login | Autenticación con username + password (BCrypt vía API) | `usuario` |
| 9 | Control de acceso | Roles hardcodeados en `auth_service.py` (Admin, EncargadoProyectos, Visitante) — **no hay tabla `ruta`/`rutarol`** | `rol`, `rol_usuario` |
| 10 | Navegación | Sidebar con menú colapsable, layout base Bootstrap 5 | N/A |

### 3.2 Modelo de datos (tablas de la BD)

```
                                  SEGURIDAD
   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
   │   usuario    │──<──│ rol_usuario  │──>──│     rol      │
   │ id        PK │     │ usuario_id PK│     │ id        PK │
   │ username UK  │     │ rol_id     PK│     │ nombre    UK │
   │ password     │     └──────────────┘     │ descripcion  │
   │ email     UK │           N:M            │ activo       │
   │ nombre_compl │                          │ fecha_creac. │
   │ activo       │                          └──────────────┘
   │ fechas       │
   └──────────────┘
   (No existen tablas "ruta" ni "rutarol": las rutas permitidas se calculan
    en auth_service.py segun el rol — Admin / EncargadoProyectos / Visitante.)

                              NEGOCIO MAESTRO-DETALLE
   ┌──────────────┐         ┌──────────────────┐         ┌─────────────────────┐
   │   proyecto   │────<────│     producto     │────>────│    tipo_producto    │
   │ id        PK │         │ id            PK │         │ id              PK  │
   │ titulo (70)  │         │ nombre (45)      │         │ categoria (45)      │
   │ resumen(256) │         │ categoria (45)   │         │ clase (45)          │
   │ presupuesto  │         │ fecha_entrega    │         │ nombre (45)         │
   │ tipo_finan.  │         │ proyecto    FK   │         │ tipologia (45)      │
   │ tipo_fondos  │         │ tipo_producto FK │         └─────────────────────┘
   │ fecha_inicio │         └─────────┬────────┘
   │ fecha_fin    │                   │
   └──────┬───────┘                   v
          │                  ┌──────────────────┐         ┌────────────────┐
          │                  │ docente_producto │────>────│    docente     │
          │                  │ docente    PK    │         │ cedula      PK │
          │                  │ producto   PK    │         │ nombres        │
          │                  └──────────────────┘         │ apellidos      │
          │                                               │ genero, cargo  │
          │     ┌─────────────────────┐                   │ correo, tel    │
          ├──<──│     desarrolla      │──>────────────────┤ url_cvlac, ... │
          │     │ docente    PK       │                   │ escalafon      │
          │     │ proyecto   PK       │                   │ perfil (text)  │
          │     │ rol         (45) NN │                   │ cat_minciencia │
          │     │ descripcion (256)NN │                   │ conv_minciencia│
          │     └─────────────────────┘                   │ nacionalidaad  │
          │                                               │ linea_principal│
          │                                               └────────────────┘

                          TABLAS PUENTE (N:M con proyecto)
   proyecto <──<── aa_proyecto     ──>── area_aplicacion   (id, nombre)
   proyecto <──<── ac_proyecto     ──>── area_conocimiento (id, gran_area, area, disciplina)
   proyecto <──<── ods_proyecto    ──>── objetivo_desarrollo_sostenible (id, nombre, categoria)
   proyecto <──<── proyecto_linea  ──>── linea_investigacion (id, nombre, descripcion)
   proyecto <──<── aliado_proyecto ──>── aliado (nit PK, razon_social, ...)
   proyecto <──<── palabras_clave  ──>── termino_clave (termino PK str, termino_ingles)
```

### 3.3 Modelo Entidad-Relación (ER) detallado

El modelo ER define las **entidades** (tablas), sus **atributos** (columnas), las **relaciones** entre ellas (FKs) y las **restricciones** (PKs, NOT NULL, UNIQUE). Es la base para el diseño de la BD.

#### Normalización aplicada

| Forma Normal | Qué exige | Cumple? | Ejemplo |
|--------------|-----------|---------|---------|
| 1FN | Valores atómicos, sin grupos repetidos | Sí | Cada columna tiene un solo valor, no hay arrays |
| 2FN | Todo atributo depende de TODA la PK | Sí | En `desarrolla`, `rol` y `descripcion` dependen de `(docente + proyecto)`, no solo de uno |
| 3FN | No hay dependencias transitivas | Sí | El nombre del docente NO se duplica en `docente_producto` — se accede vía FK a `docente` |

#### Tabla de entidades y atributos

> Los nombres, tipos y nullabilidad provienen del dump real `BdMapaConocimiento.sql`. Ver [data-model.md](data-model.md) para el DDL completo.

**Entidades de negocio (maestro-detalle):**

| Entidad | PK | Atributo | Tipo | NULL? | Descripción |
|---------|-----|----------|------|-------|-------------|
| `proyecto` | `id` (int) | `titulo` | varchar(70) | NN | Título del proyecto |
| | | `resumen` | varchar(256) | NN | Resumen ejecutivo |
| | | `presupuesto` | double precision | NN | Presupuesto asignado |
| | | `tipo_financiacion` | varchar(45) | NN | Tipo de financiación |
| | | `tipo_fondos` | varchar(45) | NN | Tipo de fondos |
| | | `fecha_inicio` | date | NN | Fecha de arranque |
| | | `fecha_fin` | date | NULL | Fecha estimada de cierre |
| `producto` | `id` (int) | `nombre` | varchar(45) | NN | Nombre del producto |
| | | `categoria` | varchar(45) | NN | Categoría del producto |
| | | `fecha_entrega` | date | NN | Fecha de entrega prevista |
| | | `proyecto` | int FK | NULL | → `proyecto.id` (nullable en el esquema) |
| | | `tipo_producto` | int FK | NN | → `tipo_producto.id` |
| `tipo_producto` | `id` (int) | `categoria` | varchar(45) | NN | Categoría institucional |
| | | `clase` | varchar(45) | NN | Clase |
| | | `nombre` | varchar(45) | NN | Nombre del tipo |
| | | `tipologia` | varchar(45) | NN | Tipología |
| `docente` | `cedula` (int) | `nombres` | varchar(60) | NN | Nombres |
| | | `apellidos` | varchar(60) | NN | Apellidos |
| | | `genero` | varchar(12) | NN | Género |
| | | `cargo` | varchar(30) | NN | Cargo |
| | | `fecha_nacimiento` | date | NN | Fecha de nacimiento |
| | | `correo` | varchar(70) | NN | Correo institucional |
| | | `telefono` | varchar(20) | NN | Teléfono |
| | | `url_cvlac` | varchar(128) | NN | URL del CvLAC |
| | | `fecha_actualizacion` | date | NN | Última actualización |
| | | `escalafon` | varchar(45) | NN | Escalafón |
| | | `perfil` | text | NN | Perfil descriptivo |
| | | `cat_minciencia` | varchar(45) | NULL | Categoría MinCiencias |
| | | `conv_minciencia` | varchar(45) | NN | Convocatoria MinCiencias |
| | | `nacionalidaad` | varchar(45) | NN | Nacionalidad (typo del esquema) |
| | | `linea_investigacion_principal` | int FK | NULL | → `linea_investigacion.id` |
| `aliado` | `nit` (int) | `razon_social` | varchar(60) | NN | Razón social |
| | | `nombre_contacto` | varchar(60) | NN | Persona de contacto |
| | | `correo` | varchar(70) | NN | Correo |
| | | `telefono` | varchar(45) | NN | Teléfono |
| | | `ciudad` | varchar(45) | NN | Ciudad |

**Entidades catálogo / maestras:**

| Entidad | PK | Atributos | Notas |
|---------|-----|-----------|-------|
| `termino_clave` | `termino` varchar(30) | `termino_ingles` varchar(30) NULL | **PK es la cadena**, no un id |
| `area_aplicacion` | `id` (int) | `nombre` varchar(60) NN | Referenciada como "aa" en tablas puente |
| `area_conocimiento` | `id` (int) | `gran_area`, `area`, `disciplina` varchar(60) NN | Referenciada como "ac" |
| `objetivo_desarrollo_sostenible` | `id` (int) | `nombre` varchar(60) NN, `categoria` varchar(45) NN | Referenciada como "ods" |
| `linea_investigacion` | `id` (int) | `nombre` varchar(45) NN, `descripcion` varchar(256) NN | No se llama solo "linea" |

**Tablas puente (N:M):**

> **Importante**: no tienen columna `id` propia ni prefijos `fk`. Sus PKs son compuestas y sus columnas se llaman como las entidades referenciadas.

| Tabla puente | PK compuesta | Atributos extra | Descripción |
|--------------|--------------|-----------------|-------------|
| `aa_proyecto` | `(proyecto, area_aplicacion)` | — | Áreas de aplicación del proyecto |
| `ac_proyecto` | `(proyecto, area_conocimiento)` | — | Áreas de conocimiento del proyecto |
| `ods_proyecto` | `(proyecto, ods)` | — | ODS asociados al proyecto |
| `proyecto_linea` | `(proyecto, linea_investigacion)` | — | Líneas de investigación del proyecto |
| `aliado_proyecto` | `(aliado, proyecto)` | — | Aliados que apoyan el proyecto |
| `palabras_clave` | `(proyecto, termino_clave)` | — | **N:M proyecto ↔ termino_clave** (no es catálogo) |
| `docente_producto` | `(docente, producto)` | — | Docentes autores del producto |
| `desarrolla` | `(docente, proyecto)` | `rol` varchar(45) NN, `descripcion` varchar(256) NN | Docente desarrolla proyecto con un rol |

**Entidades de seguridad:**

| Entidad | PK | Atributo | Tipo | NULL? | Notas |
|---------|-----|----------|------|-------|-------|
| `usuario` | `id` (serial) | `username` | varchar(100) | NN, UNIQUE | login |
| | | `password` | varchar(255) | NN | Hash BCrypt |
| | | `email` | varchar(150) | NN, UNIQUE | Para restablecer pwd |
| | | `nombre_completo` | varchar(200) | NULL | Nombre para mostrar |
| | | `activo` | boolean | NULL (default true) | |
| | | `fecha_creacion` | timestamp | NULL (default now) | |
| | | `fecha_actualizacion` | timestamp | NULL (default now) | |
| `rol` | `id` (serial) | `nombre` | varchar(100) | NN, UNIQUE | Admin / EncargadoProyectos / Visitante |
| | | `descripcion` | text | NULL | |
| | | `activo` | boolean | NULL (default true) | |
| | | `fecha_creacion` | timestamp | NULL (default now) | |
| `rol_usuario` | `(usuario_id, rol_id)` | `usuario_id` | int FK | NN | → `usuario.id` ON DELETE CASCADE |
| | | `rol_id` | int FK | NN | → `rol.id` ON DELETE CASCADE |

> **No existen tablas `ruta` ni `rutarol` en el esquema actual**. Las rutas permitidas por rol se calculan en `services/auth_service.py` (función `calcular_rutas_permitidas`) según el rol del usuario.

#### Cardinalidad de las relaciones

| Relación | Tipo | Lectura | Tabla intermedia |
|----------|------|---------|------------------|
| `proyecto` ↔ `producto` | 1:N | Un proyecto tiene 0 o N productos (FK nullable) | No (FK directo) |
| `tipo_producto` ↔ `producto` | 1:N | Un tipo se usa en 0 o N productos | No (FK directo, NOT NULL) |
| `proyecto` ↔ `area_aplicacion` | N:M | Un proyecto en varias áreas de aplicación | Sí: `aa_proyecto` |
| `proyecto` ↔ `area_conocimiento` | N:M | Un proyecto en varias áreas de conocimiento | Sí: `ac_proyecto` |
| `proyecto` ↔ `objetivo_desarrollo_sostenible` | N:M | Un proyecto aporta a varios ODS | Sí: `ods_proyecto` |
| `proyecto` ↔ `linea_investigacion` | N:M | Un proyecto puede tocar varias líneas | Sí: `proyecto_linea` |
| `proyecto` ↔ `aliado` | N:M | Un proyecto tiene varios aliados | Sí: `aliado_proyecto` |
| `proyecto` ↔ `termino_clave` | N:M | Un proyecto tiene N términos clave | Sí: `palabras_clave` |
| `proyecto` ↔ `docente` | N:M | Un docente desarrolla varios proyectos | Sí: `desarrolla` (con `rol` y `descripcion`) |
| `producto` ↔ `docente` | N:M | Un producto tiene varios autores | Sí: `docente_producto` |
| `usuario` ↔ `rol` | N:M | Un usuario tiene N roles, un rol tiene N usuarios | Sí: `rol_usuario` (ON DELETE CASCADE) |

#### Integridad referencial

```
ON DELETE en el esquema real:
  - rol_usuario: ON DELETE CASCADE (al borrar usuario o rol, se borran sus asignaciones)
  - Resto de FKs: NO ACTION por defecto (no hay CASCADE declarado)

ON UPDATE: NO ACTION en todas las FKs.

Consecuencia practica:
  - No se puede borrar un docente que tenga registros en desarrolla o
    docente_producto sin antes desasignarlo (NO ACTION).
  - No se puede borrar un tipo_producto que este siendo usado por algun
    producto.
  - El SP sp_borrar_proyecto_y_productos limpia las 7 tablas puente
    (aa_proyecto, ac_proyecto, aliado_proyecto, desarrolla, ods_proyecto,
    palabras_clave, proyecto_linea) y todos los productos del proyecto antes
    de borrar el maestro, simulando un ON DELETE CASCADE.

Triggers: el esquema actual NO define triggers. Toda la logica
transaccional vive en los 5 stored procedures.
```

### 3.4 Flujos de usuario

#### Flujo 1: Login

```
Usuario abre app -> Middleware detecta sin sesión -> Redirect /login
-> Escribe email + contraseña -> POST /login
-> API verifica BCrypt -> Genera JWT -> Devuelve token
-> Cargar roles y rutas (1 SQL vía ConsultasController)
-> Guardar en sesión Flask -> Redirect /home
```

#### Flujo 2: CRUD genérico (catálogos)

```
Usuario navega a /tipo_producto -> Middleware verifica sesión + ruta permitida
-> ApiService.listar("tipo_producto") con JWT en header
-> API devuelve datos -> Jinja2 renderiza tabla HTML
-> Usuario llena formulario -> POST /tipo_producto/crear
-> ApiService.crear("tipo_producto", datos) con JWT -> API inserta en BD
-> Flash "Registro creado" -> Redirect /tipo_producto
```

#### Flujo 3: Proyecto maestro-detalle (con Stored Procedure)

```
Usuario navega a /proyecto -> Lista proyectos existentes
-> Clic "Nuevo proyecto" -> Formulario con:
   - Cabecera: titulo, resumen, presupuesto, tipo_financiacion, tipo_fondos,
               fecha_inicio, fecha_fin
   - Detalle: tabla dinámica de productos con nombre, categoria,
              fecha_entrega, tipo_producto (select FK)
   - JavaScript agrega/elimina filas de producto
-> POST /proyecto/crear -> Ejecuta SP sp_insertar_proyecto_y_productos
   (cabecera + productos en una sola transaccion atomica)
```

#### Flujo 4: Asignación N:M (ej. ODS de un proyecto)

```
Usuario navega a /ods_proyecto -> Lista asociaciones
-> Clic "Nueva asociación" -> Formulario con:
   - Select de proyecto (FK)
   - Select de ODS (FK)
-> POST /ods_proyecto/crear -> ApiService.crear("ods_proyecto", {...})
-> Flash + Redirect
```

---

## 4. Qué NO se construye (exclusiones explícitas)

| Excluido | Razón |
|----------|-------|
| API REST | Ya existe (`apicsharpneon-mapacto.runasp.net`) |
| Base de datos | Ya existe (PostgreSQL en Neon Cloud) |
| Registro libre de usuarios | Los crea el admin vía CRUD de `usuario` |
| Panel de reportes/dashboards | Fuera del alcance de esta entrega |
| Exportación a PDF/Excel | Fuera del alcance |
| Internacionalización (i18n) | Solo español por ahora |
| Tests automatizados | Se prueban manualmente (es un trabajo académico) |
| Deploy en producción (frontend) | Se ejecuta localmente (`python app.py`) |
| Notificaciones en tiempo real | Fuera del alcance |
| Recuperación de contraseña por SMTP | No requerido para esta entrega |

---

## 5. Criterios de aceptación

### Para cada CRUD de catálogo (`tipo_producto`, `termino_clave`, `palabras_clave`)

- [ ] Listar registros en tabla HTML con todos los campos
- [ ] Crear registro con formulario (tipos HTML correctos por tipo de dato)
- [ ] Editar registro (formulario prellenado con datos actuales)
- [ ] Eliminar registro con confirmación
- [ ] Mensajes flash de éxito/error después de cada operación

### Para el maestro-detalle de proyecto

- [ ] Crear un proyecto con N productos en una sola transacción (SP)
- [ ] Editar un proyecto y sus productos (replace-all vía SP)
- [ ] Eliminar un proyecto borra también sus productos (SP atómico)
- [ ] El formulario permite agregar/eliminar filas de productos con JavaScript
- [ ] El select de `tipo_producto` se llena dinámicamente desde la API

### Para las asignaciones N:M

- [ ] `aa_proyecto`, `ac_proyecto`, `ods_proyecto`, `proyecto_linea`, `aliado_proyecto`, `docente_producto` funcionan con sus dos selects (FK + FK)
- [ ] `desarrolla` permite editar `rol` y `descripcion` sin perder la PK compuesta
- [ ] Eliminar usa PK compuesta (`docente,proyecto/X,Y`)

### Para login y seguridad

- [ ] Login con email + contraseña verificada con BCrypt
- [ ] JWT capturado y enviado en cada petición a la API
- [ ] Roles cargados desde la BD (no hardcodeados)
- [ ] Rutas permitidas verificadas en **CADA** request (middleware)
- [ ] Usuario sin roles → rechazado con mensaje claro
- [ ] Ruta no permitida → página 403 "Acceso Denegado"
- [ ] Cambiar contraseña con validación (6 chars, mayúscula, número)
- [ ] Sesión persiste al navegar, se pierde al cerrar navegador

### Para trabajo colaborativo

- [ ] Samuel y Jostin trabajan cada uno en su rama `feature/`
- [ ] Merge a `main` sin conflictos (o resueltos en la rama)
- [ ] Cada cambio importante tiene su commit descriptivo
- [ ] El proyecto arranca con `python app.py` después de cada merge

---

## 6. Métricas de éxito

| Métrica | Valor esperado |
|---------|----------------|
| Tablas con CRUD funcionando | 14 (1 maestro-detalle + 3 catálogos + 6 N:M + 1 con atributos + 3 seguridad) |
| Tiempo de login (con `ConsultasController`) | < 2 segundos |
| Estudiantes que completan la entrega | 2/2 (Samuel y Jostin) |
| El proyecto compila y corre después de merge | Sí |
| Cada entrega tiene documentación SDD versionada | Sí (`sdd/01..07.md` + `data-model.md`) |
| Stored Procedures funcionando atómicamente | `sp_insertar_proyecto_y_productos`, `sp_actualizar_proyecto_y_productos`, `sp_borrar_proyecto_y_productos`, `sp_consultar_proyecto_y_productos` |

---

## Fecha de ratificación

- **Versión**: 1.0
- **Fecha**: 2026-05-21
- **Autores**: Samuel Giraldo, Jostin (Estudiantes Construcción de Software USB)
- **Referencia Spec-Kit**: [github.com/github/spec-kit](https://github.com/github/spec-kit)

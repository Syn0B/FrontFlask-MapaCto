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
| 2 | CRUD catálogos | Listar/crear/editar/eliminar `tipo_producto`, `termino_clave`, `palabras_clave` | `tipo_producto`, `termino_clave`, `palabras_clave` |
| 3 | Asignaciones de proyecto | Asociar a un proyecto sus áreas académicas, áreas de conocimiento, ODS, líneas y aliados | `aa_proyecto`, `ac_proyecto`, `ods_proyecto`, `proyecto_linea`, `aliado_proyecto` |
| 4 | Relación docente-producto | Asignar docentes a los productos derivados | `docente_producto` |
| 5 | Relación desarrolla | Asignar docentes a proyectos con rol y descripción | `desarrolla` (PK compuesta) |
| 6 | Login | Autenticación con email + contraseña (BCrypt vía API) | `usuario` |
| 7 | Control de acceso | Roles y rutas permitidas por rol, verificación en cada request | `rol`, `rol_usuario`, `ruta`, `rutarol` |
| 8 | Navegación | Sidebar con menú colapsable, layout base Bootstrap 5 | N/A |
| 9 | Descubrimiento dinámico | PKs y FKs se descubren de la API, no se hardcodean | Todas |

### 3.2 Modelo de datos (tablas de la BD)

```
┌──────────┐     ┌──────────────┐     ┌──────┐     ┌──────────┐     ┌──────┐
│ usuario  │──<──│ rol_usuario  │──>──│ rol  │──<──│ rutarol  │──>──│ ruta │
│ email PK │     │ fkemail      │     │ id   │     │ fkidrol  │     │ id   │
│ contrase │     │ fkidrol      │     │ nomb │     │ fkidruta │     │ ruta │
└──────────┘     └──────────────┘     └──────┘     └──────────┘     └──────┘

┌──────────┐         ┌──────────────────┐         ┌────────────────┐
│ proyecto │────<────│ producto         │────>────│ tipo_producto  │
│ id  PK   │         │ id  PK           │         │ id  PK         │
│ titulo   │         │ nombre           │         │ nombre         │
│ resumen  │         │ categoria        │         └────────────────┘
│ presup.  │         │ fecha_entrega    │
│ fechas   │         │ fkproyecto       │
└────┬─────┘         │ fktipo_producto  │
     │               └────────┬─────────┘
     │                        │
     │                        v
     │               ┌──────────────────┐         ┌──────────┐
     │               │ docente_producto │────>────│ docente  │
     │               │ fkproducto       │         │ cedula PK│
     │               │ fkdocente        │         │ nombre   │
     │               └──────────────────┘         └────┬─────┘
     │                                                  │
     │           ┌─────────────────────┐                │
     ├──<────────│ desarrolla          │────────────────┤
     │           │ docente, proyecto PK│                │
     │           │ rol, descripcion    │                │
     │           └─────────────────────┘                │
     │
     ├──<───┐  ┌─────────────┐  ┌─────┐
     │      └──│ aa_proyecto │──│ aa  │   Areas academicas
     │         └─────────────┘  └─────┘
     │
     ├──<───┐  ┌─────────────┐  ┌─────┐
     │      └──│ ac_proyecto │──│ ac  │   Areas de conocimiento
     │         └─────────────┘  └─────┘
     │
     ├──<───┐  ┌──────────────┐ ┌─────┐
     │      └──│ ods_proyecto │─│ ods │   Objetivos de Desarrollo Sostenible
     │         └──────────────┘ └─────┘
     │
     ├──<───┐  ┌──────────────────┐ ┌──────┐
     │      └──│ proyecto_linea   │─│ linea│   Lineas de investigacion
     │         └──────────────────┘ └──────┘
     │
     └──<───┐  ┌──────────────────┐ ┌────────┐
            └──│ aliado_proyecto  │─│ aliado │   Aliados externos
               └──────────────────┘ └────────┘

┌────────────────┐    ┌────────────────┐
│ termino_clave  │    │ palabras_clave │
│ id PK, termino │    │ id PK, palabra │
└────────────────┘    └────────────────┘
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

**Entidades de negocio (maestro-detalle):**

| Entidad | PK | Atributos | Tipo | NOT NULL | Descripción |
|---------|-----|-----------|------|----------|-------------|
| `proyecto` | `id` (serial) | `titulo` | varchar | sí | Título del proyecto |
| | | `resumen` | text | sí | Resumen ejecutivo |
| | | `presupuesto` | decimal | sí | Presupuesto asignado |
| | | `tipo_financiacion` | varchar | sí | Interna / Externa |
| | | `tipo_fondos` | varchar | sí | Recurrentes / Frescos |
| | | `fecha_inicio` | date | sí | Fecha de arranque |
| | | `fecha_fin` | date | no | Fecha estimada de cierre |
| `producto` | `id` (serial) | `nombre` | varchar | sí | Nombre del producto académico |
| | | `categoria` | varchar | sí | Artículo, libro, software, etc. |
| | | `fecha_entrega` | date | sí | Fecha de entrega prevista |
| | | `fkproyecto` | integer FK | sí | → `proyecto.id` |
| | | `fktipo_producto` | integer FK | sí | → `tipo_producto.id` |
| `tipo_producto` | `id` (serial) | `nombre` | varchar | sí | Nombre del tipo (Artículo Q1, Libro, etc) |
| `docente` | `cedula` (integer) | `nombre` | varchar | sí | Nombre del docente |
| | | `correo` | varchar | no | Correo institucional |

**Entidades catálogo:**

| Entidad | PK | Atributos | Tipo | NOT NULL | Descripción |
|---------|-----|-----------|------|----------|-------------|
| `termino_clave` | `id` (serial) | `termino` | varchar | sí | Término de búsqueda |
| `palabras_clave` | `id` (serial) | `palabra` | varchar | sí | Palabra clave del proyecto |
| `aa` | `id` (serial) | `nombre` | varchar | sí | Área académica |
| `ac` | `id` (serial) | `nombre` | varchar | sí | Área de conocimiento |
| `ods` | `id` (integer) | `nombre` | varchar | sí | Objetivo de Desarrollo Sostenible (1–17) |
| `linea` | `id` (serial) | `nombre` | varchar | sí | Línea de investigación |
| `aliado` | `id` (serial) | `nombre` | varchar | sí | Aliado externo (empresa, universidad) |

**Entidades relacionales (N:M):**

| Entidad | PK compuesta | Atributos extra | Descripción |
|---------|--------------|-----------------|-------------|
| `aa_proyecto` | `(fkproyecto, fkaa)` | — | Proyectos por área académica |
| `ac_proyecto` | `(fkproyecto, fkac)` | — | Proyectos por área de conocimiento |
| `ods_proyecto` | `(fkproyecto, fkods)` | — | ODS asociados al proyecto |
| `proyecto_linea` | `(fkproyecto, fklinea)` | — | Líneas de investigación del proyecto |
| `aliado_proyecto` | `(fkproyecto, fkaliado)` | — | Aliados que apoyan el proyecto |
| `docente_producto` | `(fkdocente, fkproducto)` | — | Docentes autores del producto |
| `desarrolla` | `(docente, proyecto)` | `rol`, `descripcion` | Docente desarrolla proyecto con un rol |

**Entidades de seguridad:**

| Entidad | PK | Atributos | Tipo | NOT NULL | Descripción |
|---------|-----|-----------|------|----------|-------------|
| `usuario` | `email` (varchar) | `contrasena` | varchar | sí | Hash BCrypt (irreversible) |
| | | `nombre` | varchar | no | Nombre para mostrar |
| `rol` | `id` (serial) | `nombre` | varchar | sí | Administrador, Docente, Consulta |
| `rol_usuario` | `id` (serial) | `fkemail` | varchar FK | sí | → `usuario.email` |
| | | `fkidrol` | integer FK | sí | → `rol.id` |
| `ruta` | `id` (serial) | `ruta` | varchar | sí | Path de la página (`/proyecto`) |
| `rutarol` | `id` (serial) | `fkidrol` | integer FK | sí | → `rol.id` |
| | | `fkidruta` | integer FK | sí | → `ruta.id` |

#### Cardinalidad de las relaciones

| Relación | Tipo | Lectura | Tabla intermedia |
|----------|------|---------|------------------|
| `proyecto` ↔ `producto` | 1:N | Un proyecto tiene 0 o N productos | No (FK directo) |
| `tipo_producto` ↔ `producto` | 1:N | Un tipo se usa en 0 o N productos | No (FK directo) |
| `proyecto` ↔ `aa` | N:M | Un proyecto en varias áreas académicas | Sí: `aa_proyecto` |
| `proyecto` ↔ `ac` | N:M | Un proyecto en varias áreas de conocimiento | Sí: `ac_proyecto` |
| `proyecto` ↔ `ods` | N:M | Un proyecto aporta a varios ODS | Sí: `ods_proyecto` |
| `proyecto` ↔ `linea` | N:M | Un proyecto puede tocar varias líneas | Sí: `proyecto_linea` |
| `proyecto` ↔ `aliado` | N:M | Un proyecto tiene varios aliados | Sí: `aliado_proyecto` |
| `proyecto` ↔ `docente` | N:M | Un docente desarrolla varios proyectos | Sí: `desarrolla` (con atributos) |
| `producto` ↔ `docente` | N:M | Un producto tiene varios autores | Sí: `docente_producto` |
| `usuario` ↔ `rol` | N:M | Un usuario tiene N roles, un rol tiene N usuarios | Sí: `rol_usuario` |
| `rol` ↔ `ruta` | N:M | Un rol accede a N rutas | Sí: `rutarol` |

#### Integridad referencial

```
ON DELETE: Las FKs principales usan NO ACTION (no se puede borrar un proyecto
           si tiene productos asociados, salvo que se use el SP que limpia
           todo en cascada controlada).

ON UPDATE: NO ACTION. Si se cambia una PK, los FKs no se actualizan
           automaticamente.

Consecuencia practica:
  - No se puede borrar un docente que tenga registros en desarrolla o
    docente_producto sin antes desasignarlo.
  - No se puede borrar un tipo_producto que este siendo usado por algun producto.
  - El SP sp_borrar_proyecto_y_productos elimina el proyecto y todas sus
    relaciones en una sola transaccion (atomica).
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
- **Autores**: Samuel Giraldo, Jostin (Estudiantes Diseño de Software USB)
- **Referencia Spec-Kit**: [github.com/github/spec-kit](https://github.com/github/spec-kit)

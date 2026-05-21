# Modelo de Datos - FrontFlask-MapaCto

Según **Spec-Kit de GitHub**, cada feature puede tener un archivo `data-model.md` dedicado con el esquema detallado de entidades. Este archivo contiene el **SQL completo** para crear todas las tablas del proyecto MapaCto, incluyendo los **Stored Procedures** usados para operaciones maestro-detalle.

**Referencia**: estructura `.specify/specs/{feature}/data-model.md`

---

## 1. Diagrama Entidad-Relación (ER)

```
                                    SEGURIDAD
   ┌──────────┐     ┌──────────────┐     ┌──────┐     ┌──────────┐     ┌──────┐
   │ usuario  │──<──│ rol_usuario  │──>──│ rol  │──<──│ rutarol  │──>──│ ruta │
   │ id PK    │     │ usuario_id   │     │ id PK│     │ fkidrol  │     │ id PK│
   │ username │     │ rol_id       │     │ nomb │     │ fkidruta │     │ ruta │
   │ email    │     └──────────────┘     └──────┘     └──────────┘     │ desc │
   │ password │           N:M                              N:M         └──────┘
   │ nombre   │
   └──────────┘

                                CATALOGOS
   ┌────────────────┐    ┌────────────────┐    ┌────────────────┐
   │ tipo_producto  │    │ termino_clave  │    │ palabras_clave │
   │ id PK          │    │ id PK          │    │ id PK          │
   │ nombre         │    │ termino        │    │ palabra        │
   └────────────────┘    └────────────────┘    └────────────────┘

   ┌──────┐    ┌──────┐    ┌──────┐    ┌────────┐    ┌────────┐
   │  aa  │    │  ac  │    │ ods  │    │ linea  │    │ aliado │
   │ id PK│    │ id PK│    │ id PK│    │ id PK  │    │ id PK  │
   │ nomb │    │ nomb │    │ nomb │    │ nombre │    │ nombre │
   └──────┘    └──────┘    └──────┘    └────────┘    └────────┘

                                NEGOCIO (maestro-detalle)
                              ┌──────────────────────┐
                              │      proyecto        │
                              │ id PK                │
                              │ titulo               │
                              │ resumen              │
                              │ presupuesto          │
                              │ tipo_financiacion    │
                              │ tipo_fondos          │
                              │ fecha_inicio         │
                              │ fecha_fin            │
                              └──────┬───────────────┘
                                     │ 1:N
                                     v
                              ┌──────────────────────┐     ┌────────────────┐
                              │      producto        │──>──│ tipo_producto  │
                              │ id PK                │ N:1 │ id PK          │
                              │ nombre               │     │ nombre         │
                              │ categoria            │     └────────────────┘
                              │ fecha_entrega        │
                              │ fkproyecto FK        │
                              │ fktipo_producto FK   │
                              └──────────────────────┘

                            RELACIONES N:M con proyecto
   proyecto <──<── aa_proyecto      ──>── aa       (areas academicas)
   proyecto <──<── ac_proyecto      ──>── ac       (areas de conocimiento)
   proyecto <──<── ods_proyecto     ──>── ods      (ODS)
   proyecto <──<── proyecto_linea   ──>── linea    (lineas de investigacion)
   proyecto <──<── aliado_proyecto  ──>── aliado   (aliados externos)

                            RELACIONES con docente
   ┌──────────┐
   │ docente  │
   │cedula PK │
   │ nombre   │──<── docente_producto ──>── producto    (autores del producto)
   │ correo   │──<── desarrolla       ──>── proyecto    (con rol y descripcion)
   └──────────┘
```

---

## 2. SQL completo para PostgreSQL (Neon Cloud)

### 2.1 Tablas de catálogo

```sql
-- ═══════════════════════════════════════════════════════
-- TABLAS DE CATALOGO
-- ═══════════════════════════════════════════════════════

-- Tipo de producto: Articulo Q1, Libro, Software, etc.
CREATE TABLE tipo_producto (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

-- Termino clave: terminos de busqueda institucional
CREATE TABLE termino_clave (
    id SERIAL PRIMARY KEY,
    termino VARCHAR(200) NOT NULL
);

-- Palabras clave: palabras de los proyectos
CREATE TABLE palabras_clave (
    id SERIAL PRIMARY KEY,
    palabra VARCHAR(200) NOT NULL
);

-- Areas Academicas (ej: Ingenieria, Ciencias Sociales)
CREATE TABLE aa (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL
);

-- Areas de Conocimiento (mas especificas)
CREATE TABLE ac (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL
);

-- ODS: Objetivos de Desarrollo Sostenible (17 valores fijos)
CREATE TABLE ods (
    id INTEGER PRIMARY KEY,        -- 1 a 17
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT DEFAULT ''
);

-- Lineas de investigacion
CREATE TABLE linea (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL
);

-- Aliado externo (empresa, universidad, ONG)
CREATE TABLE aliado (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    tipo VARCHAR(100) DEFAULT ''   -- Empresa, Universidad, ONG, Gubernamental
);

-- Docente (investigador)
CREATE TABLE docente (
    cedula INTEGER PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    correo VARCHAR(200) DEFAULT ''
);
```

### 2.2 Tablas de negocio (maestro-detalle)

```sql
-- ═══════════════════════════════════════════════════════
-- TABLAS DE NEGOCIO (maestro-detalle)
-- ═══════════════════════════════════════════════════════

-- Proyecto: entidad principal del sistema
CREATE TABLE proyecto (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(300) NOT NULL,
    resumen TEXT NOT NULL,
    presupuesto DECIMAL(18,2) NOT NULL DEFAULT 0,
    tipo_financiacion VARCHAR(100) NOT NULL,  -- Interna / Externa
    tipo_fondos VARCHAR(100) NOT NULL,        -- Recurrentes / Frescos
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE                            -- nullable
);

-- Producto: entregable academico del proyecto
-- 1 proyecto tiene N productos (detalle)
CREATE TABLE producto (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(300) NOT NULL,
    categoria VARCHAR(100) NOT NULL,
    fecha_entrega DATE NOT NULL,
    fkproyecto INTEGER NOT NULL REFERENCES proyecto(id),
    fktipo_producto INTEGER NOT NULL REFERENCES tipo_producto(id)
);
```

### 2.3 Tablas relacionales (N:M)

```sql
-- ═══════════════════════════════════════════════════════
-- TABLAS RELACIONALES N:M
-- PK compuesta para garantizar unicidad (no duplicar la asociacion)
-- ═══════════════════════════════════════════════════════

-- Proyectos por area academica
CREATE TABLE aa_proyecto (
    fkproyecto INTEGER NOT NULL REFERENCES proyecto(id),
    fkaa INTEGER NOT NULL REFERENCES aa(id),
    PRIMARY KEY (fkproyecto, fkaa)
);

-- Proyectos por area de conocimiento
CREATE TABLE ac_proyecto (
    fkproyecto INTEGER NOT NULL REFERENCES proyecto(id),
    fkac INTEGER NOT NULL REFERENCES ac(id),
    PRIMARY KEY (fkproyecto, fkac)
);

-- ODS por proyecto
CREATE TABLE ods_proyecto (
    fkproyecto INTEGER NOT NULL REFERENCES proyecto(id),
    fkods INTEGER NOT NULL REFERENCES ods(id),
    PRIMARY KEY (fkproyecto, fkods)
);

-- Lineas de investigacion del proyecto
CREATE TABLE proyecto_linea (
    fkproyecto INTEGER NOT NULL REFERENCES proyecto(id),
    fklinea INTEGER NOT NULL REFERENCES linea(id),
    PRIMARY KEY (fkproyecto, fklinea)
);

-- Aliados del proyecto
CREATE TABLE aliado_proyecto (
    fkproyecto INTEGER NOT NULL REFERENCES proyecto(id),
    fkaliado INTEGER NOT NULL REFERENCES aliado(id),
    PRIMARY KEY (fkproyecto, fkaliado)
);

-- Docentes autores del producto
CREATE TABLE docente_producto (
    fkdocente INTEGER NOT NULL REFERENCES docente(cedula),
    fkproducto INTEGER NOT NULL REFERENCES producto(id),
    PRIMARY KEY (fkdocente, fkproducto)
);

-- Desarrolla: docente desarrolla un proyecto con un rol especifico
-- A diferencia de las otras N:M, esta TIENE atributos propios
CREATE TABLE desarrolla (
    docente INTEGER NOT NULL REFERENCES docente(cedula),
    proyecto INTEGER NOT NULL REFERENCES proyecto(id),
    rol VARCHAR(45) NOT NULL,           -- Investigador Principal, Coinvestigador, etc.
    descripcion VARCHAR(256) DEFAULT '',
    PRIMARY KEY (docente, proyecto)
);
```

### 2.4 Tablas de seguridad

```sql
-- ═══════════════════════════════════════════════════════
-- TABLAS DE SEGURIDAD (autenticacion y autorizacion)
-- ═══════════════════════════════════════════════════════

-- Usuario: credenciales de acceso
-- password se guarda como hash BCrypt (irreversible)
CREATE TABLE usuario (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,    -- login
    email VARCHAR(200) NOT NULL UNIQUE,        -- para restablecer contrasena
    password VARCHAR(200) NOT NULL,            -- hash BCrypt, NUNCA texto plano
    nombre VARCHAR(200) DEFAULT ''
);

-- Rol: tipos de usuario del sistema
CREATE TABLE rol (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL              -- Admin, EncargadoProyectos, Visitante
);

-- Rol_usuario: asigna roles a usuarios (relacion N:M)
-- Un usuario puede tener varios roles
CREATE TABLE rol_usuario (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuario(id),
    rol_id INTEGER NOT NULL REFERENCES rol(id)
);

-- Ruta: paginas/endpoints del sistema
CREATE TABLE ruta (
    id SERIAL PRIMARY KEY,
    ruta VARCHAR(200) NOT NULL,              -- ej: "/proyecto", "/producto"
    descripcion TEXT DEFAULT ''
);

-- Rutarol: define que paginas puede acceder cada rol (relacion N:M)
CREATE TABLE rutarol (
    id SERIAL PRIMARY KEY,
    fkidrol INTEGER NOT NULL REFERENCES rol(id),
    fkidruta INTEGER NOT NULL REFERENCES ruta(id)
);
```

---

## 3. Stored Procedures (maestro-detalle)

El proyecto usa **4 Stored Procedures** para garantizar atomicidad en las operaciones maestro-detalle de `proyecto + producto`.

### 3.1 SP: Insertar proyecto y productos

```sql
CREATE OR REPLACE FUNCTION sp_insertar_proyecto_y_productos(
    p_id INTEGER,                       -- NULL si autoincremental
    p_titulo VARCHAR,
    p_resumen TEXT,
    p_presupuesto DECIMAL,
    p_tipo_financiacion VARCHAR,
    p_tipo_fondos VARCHAR,
    p_fecha_inicio DATE,
    p_fecha_fin DATE,
    p_productos JSONB,                  -- array de productos como JSON
    INOUT p_resultado TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    nuevo_id INTEGER;
    prod JSONB;
BEGIN
    -- Insertar el proyecto (cabecera)
    INSERT INTO proyecto (titulo, resumen, presupuesto,
                          tipo_financiacion, tipo_fondos,
                          fecha_inicio, fecha_fin)
    VALUES (p_titulo, p_resumen, p_presupuesto,
            p_tipo_financiacion, p_tipo_fondos,
            p_fecha_inicio, p_fecha_fin)
    RETURNING id INTO nuevo_id;

    -- Insertar productos (detalle) iterando sobre el JSON
    FOR prod IN SELECT * FROM jsonb_array_elements(p_productos)
    LOOP
        INSERT INTO producto (nombre, categoria, fecha_entrega,
                              fkproyecto, fktipo_producto)
        VALUES (
            prod->>'nombre',
            prod->>'categoria',
            (prod->>'fecha_entrega')::DATE,
            nuevo_id,
            (prod->>'tipo_producto')::INTEGER
        );
    END LOOP;

    p_resultado := json_build_object(
        'exito', true,
        'id', nuevo_id,
        'mensaje', 'Proyecto creado con sus productos'
    )::TEXT;
END;
$$;
```

### 3.2 SP: Actualizar proyecto y productos (replace-all)

```sql
CREATE OR REPLACE FUNCTION sp_actualizar_proyecto_y_productos(
    p_id INTEGER,
    p_titulo VARCHAR,
    p_resumen TEXT,
    p_presupuesto DECIMAL,
    p_tipo_financiacion VARCHAR,
    p_tipo_fondos VARCHAR,
    p_fecha_inicio DATE,
    p_fecha_fin DATE,
    p_productos JSONB,
    INOUT p_resultado TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    prod JSONB;
BEGIN
    -- 1. Actualizar la cabecera
    UPDATE proyecto SET
        titulo = p_titulo,
        resumen = p_resumen,
        presupuesto = p_presupuesto,
        tipo_financiacion = p_tipo_financiacion,
        tipo_fondos = p_tipo_fondos,
        fecha_inicio = p_fecha_inicio,
        fecha_fin = p_fecha_fin
    WHERE id = p_id;

    -- 2. Eliminar productos anteriores (estrategia replace-all)
    --    Antes hay que limpiar docente_producto que dependa de estos productos
    DELETE FROM docente_producto
    WHERE fkproducto IN (SELECT id FROM producto WHERE fkproyecto = p_id);
    DELETE FROM producto WHERE fkproyecto = p_id;

    -- 3. Insertar los productos nuevos
    FOR prod IN SELECT * FROM jsonb_array_elements(p_productos)
    LOOP
        INSERT INTO producto (nombre, categoria, fecha_entrega,
                              fkproyecto, fktipo_producto)
        VALUES (
            prod->>'nombre',
            prod->>'categoria',
            (prod->>'fecha_entrega')::DATE,
            p_id,
            (prod->>'tipo_producto')::INTEGER
        );
    END LOOP;

    p_resultado := json_build_object(
        'exito', true,
        'mensaje', 'Proyecto y productos actualizados'
    )::TEXT;
END;
$$;
```

### 3.3 SP: Borrar proyecto y productos (cascada controlada)

```sql
CREATE OR REPLACE FUNCTION sp_borrar_proyecto_y_productos(
    p_id INTEGER,
    INOUT p_resultado TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Limpiar todas las dependencias en orden inverso al de creacion
    DELETE FROM docente_producto
    WHERE fkproducto IN (SELECT id FROM producto WHERE fkproyecto = p_id);

    DELETE FROM producto WHERE fkproyecto = p_id;

    DELETE FROM desarrolla WHERE proyecto = p_id;
    DELETE FROM aa_proyecto WHERE fkproyecto = p_id;
    DELETE FROM ac_proyecto WHERE fkproyecto = p_id;
    DELETE FROM ods_proyecto WHERE fkproyecto = p_id;
    DELETE FROM proyecto_linea WHERE fkproyecto = p_id;
    DELETE FROM aliado_proyecto WHERE fkproyecto = p_id;

    -- Finalmente, borrar el proyecto
    DELETE FROM proyecto WHERE id = p_id;

    p_resultado := json_build_object(
        'exito', true,
        'mensaje', 'Proyecto y todos sus productos eliminados'
    )::TEXT;
END;
$$;
```

### 3.4 SP: Consultar proyecto con sus productos

```sql
CREATE OR REPLACE FUNCTION sp_consultar_proyecto_y_productos(
    p_id INTEGER,
    INOUT p_resultado TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_proyecto JSONB;
    v_productos JSONB;
BEGIN
    -- Obtener el proyecto
    SELECT to_jsonb(p) INTO v_proyecto
    FROM proyecto p
    WHERE p.id = p_id;

    -- Obtener los productos del proyecto
    SELECT jsonb_agg(to_jsonb(pr)) INTO v_productos
    FROM producto pr
    WHERE pr.fkproyecto = p_id;

    p_resultado := json_build_object(
        'proyecto', v_proyecto,
        'productos', COALESCE(v_productos, '[]'::JSONB)
    )::TEXT;
END;
$$;
```

---

## 4. SQL para SqlServer (equivalente)

```sql
-- Las diferencias con PostgreSQL:
--   SERIAL                  -> INT IDENTITY(1,1)
--   BOOLEAN                 -> BIT
--   TEXT                    -> NVARCHAR(MAX)
--   VARCHAR                 -> NVARCHAR
--   DATE                    -> DATE (igual)
--   DECIMAL                 -> DECIMAL (igual)
--   REFERENCES              -> FOREIGN KEY ... REFERENCES (igual)
--   JSONB                   -> NVARCHAR(MAX) (parsear con OPENJSON)
--   Functions con INOUT     -> Stored Procedures con OUTPUT

-- Ejemplo: tabla proyecto en SqlServer
CREATE TABLE proyecto (
    id INT IDENTITY(1,1) PRIMARY KEY,
    titulo NVARCHAR(300) NOT NULL,
    resumen NVARCHAR(MAX) NOT NULL,
    presupuesto DECIMAL(18,2) NOT NULL DEFAULT 0,
    tipo_financiacion NVARCHAR(100) NOT NULL,
    tipo_fondos NVARCHAR(100) NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE
);
```

---

## 5. Datos iniciales de ejemplo

```sql
-- ═══════════════════════════════════════════════════════
-- ROLES DEL SISTEMA
-- ═══════════════════════════════════════════════════════
INSERT INTO rol (nombre) VALUES ('Admin');
INSERT INTO rol (nombre) VALUES ('EncargadoProyectos');
INSERT INTO rol (nombre) VALUES ('Visitante');

-- ═══════════════════════════════════════════════════════
-- USUARIOS DE PRUEBA (Samuel y Jostin)
-- La contrasena se crea via API con BCrypt:
-- POST http://apicsharpneon-mapacto.runasp.net/api/usuario?camposEncriptar=password
-- ═══════════════════════════════════════════════════════
-- Body: {"username":"samuel","email":"samuelgiraldo5@gmail.com","password":"Samuel123","nombre":"Samuel Giraldo"}
-- Body: {"username":"jostin", "email":"jostin@usb.edu.co",        "password":"Jostin123","nombre":"Jostin"}

-- Asignar rol Admin a Samuel y Jostin
INSERT INTO rol_usuario (usuario_id, rol_id) VALUES (1, 1);  -- samuel -> Admin
INSERT INTO rol_usuario (usuario_id, rol_id) VALUES (2, 1);  -- jostin -> Admin

-- ═══════════════════════════════════════════════════════
-- RUTAS DEL SISTEMA
-- ═══════════════════════════════════════════════════════
INSERT INTO ruta (ruta, descripcion) VALUES ('/',                 'Pagina inicio');
INSERT INTO ruta (ruta, descripcion) VALUES ('/proyecto',         'Gestion de proyectos');
INSERT INTO ruta (ruta, descripcion) VALUES ('/producto',         'Consulta de productos');
INSERT INTO ruta (ruta, descripcion) VALUES ('/tipo_producto',    'Catalogo tipo producto');
INSERT INTO ruta (ruta, descripcion) VALUES ('/termino_clave',    'Catalogo terminos clave');
INSERT INTO ruta (ruta, descripcion) VALUES ('/palabras_clave',   'Catalogo palabras clave');
INSERT INTO ruta (ruta, descripcion) VALUES ('/aa_proyecto',      'Areas academicas');
INSERT INTO ruta (ruta, descripcion) VALUES ('/ac_proyecto',      'Areas de conocimiento');
INSERT INTO ruta (ruta, descripcion) VALUES ('/ods_proyecto',     'ODS por proyecto');
INSERT INTO ruta (ruta, descripcion) VALUES ('/proyecto_linea',   'Lineas de investigacion');
INSERT INTO ruta (ruta, descripcion) VALUES ('/aliado_proyecto',  'Aliados del proyecto');
INSERT INTO ruta (ruta, descripcion) VALUES ('/docente_producto', 'Autores del producto');
INSERT INTO ruta (ruta, descripcion) VALUES ('/desarrolla',       'Docentes que desarrollan');

-- Asignar todas las rutas al rol Admin
INSERT INTO rutarol (fkidrol, fkidruta)
SELECT 1, id FROM ruta;

-- ═══════════════════════════════════════════════════════
-- ODS (Objetivos de Desarrollo Sostenible)
-- ═══════════════════════════════════════════════════════
INSERT INTO ods (id, nombre) VALUES (1,  'Fin de la pobreza');
INSERT INTO ods (id, nombre) VALUES (2,  'Hambre cero');
INSERT INTO ods (id, nombre) VALUES (3,  'Salud y bienestar');
INSERT INTO ods (id, nombre) VALUES (4,  'Educacion de calidad');
INSERT INTO ods (id, nombre) VALUES (5,  'Igualdad de genero');
INSERT INTO ods (id, nombre) VALUES (6,  'Agua limpia y saneamiento');
INSERT INTO ods (id, nombre) VALUES (7,  'Energia asequible y no contaminante');
INSERT INTO ods (id, nombre) VALUES (8,  'Trabajo decente y crecimiento economico');
INSERT INTO ods (id, nombre) VALUES (9,  'Industria, innovacion e infraestructura');
INSERT INTO ods (id, nombre) VALUES (10, 'Reduccion de las desigualdades');
INSERT INTO ods (id, nombre) VALUES (11, 'Ciudades y comunidades sostenibles');
INSERT INTO ods (id, nombre) VALUES (12, 'Produccion y consumo responsables');
INSERT INTO ods (id, nombre) VALUES (13, 'Accion por el clima');
INSERT INTO ods (id, nombre) VALUES (14, 'Vida submarina');
INSERT INTO ods (id, nombre) VALUES (15, 'Vida de ecosistemas terrestres');
INSERT INTO ods (id, nombre) VALUES (16, 'Paz, justicia e instituciones solidas');
INSERT INTO ods (id, nombre) VALUES (17, 'Alianzas para lograr los objetivos');

-- ═══════════════════════════════════════════════════════
-- TIPOS DE PRODUCTO
-- ═══════════════════════════════════════════════════════
INSERT INTO tipo_producto (nombre) VALUES ('Articulo Q1');
INSERT INTO tipo_producto (nombre) VALUES ('Articulo Q2');
INSERT INTO tipo_producto (nombre) VALUES ('Libro');
INSERT INTO tipo_producto (nombre) VALUES ('Capitulo de libro');
INSERT INTO tipo_producto (nombre) VALUES ('Software');
INSERT INTO tipo_producto (nombre) VALUES ('Ponencia');
```

---

## 6. Diccionario de datos

| Tipo de dato | PostgreSQL | SqlServer | Python | HTML input |
|--------------|------------|-----------|--------|------------|
| Texto corto | `VARCHAR(N)` | `NVARCHAR(N)` | `str` | `type="text"` |
| Texto largo | `TEXT` | `NVARCHAR(MAX)` | `str` | `<textarea>` |
| Entero | `INTEGER` | `INT` | `int` | `type="number"` |
| Decimal | `DECIMAL(18,2)` | `DECIMAL(18,2)` | `float` | `type="number" step="0.01"` |
| Booleano | `BOOLEAN` | `BIT` | `bool` | `type="checkbox"` |
| Fecha | `DATE` | `DATE` | `datetime.date` | `type="date"` |
| Fecha/hora | `TIMESTAMP` | `DATETIME2` | `datetime` | `type="datetime-local"` |
| Auto-incremento | `SERIAL` | `IDENTITY(1,1)` | (generado por BD) | (oculto) |
| Email | `VARCHAR(200)` | `NVARCHAR(200)` | `str` | `type="email"` |
| Contraseña | `VARCHAR(200)` | `NVARCHAR(200)` | `str` (hash) | `type="password"` |
| JSON (PostgreSQL) | `JSONB` | `NVARCHAR(MAX)` | `dict`/`list` | — |

---

## 7. Cardinalidades resumen

| Relación | Tipo | Tabla intermedia |
|----------|------|------------------|
| `proyecto` ↔ `producto` | 1:N | No (FK directo) |
| `tipo_producto` ↔ `producto` | 1:N | No (FK directo) |
| `proyecto` ↔ `aa` | N:M | `aa_proyecto` |
| `proyecto` ↔ `ac` | N:M | `ac_proyecto` |
| `proyecto` ↔ `ods` | N:M | `ods_proyecto` |
| `proyecto` ↔ `linea` | N:M | `proyecto_linea` |
| `proyecto` ↔ `aliado` | N:M | `aliado_proyecto` |
| `proyecto` ↔ `docente` | N:M (con atributos) | `desarrolla` |
| `producto` ↔ `docente` | N:M | `docente_producto` |
| `usuario` ↔ `rol` | N:M | `rol_usuario` |
| `rol` ↔ `ruta` | N:M | `rutarol` |

---

## 8. Integridad referencial

| Acción | Comportamiento | Justificación |
|--------|---------------|----------------|
| `ON DELETE` | `NO ACTION` por defecto | No se puede borrar un proyecto que tenga productos sin usar el SP |
| `ON UPDATE` | `NO ACTION` por defecto | Las PKs no cambian |
| Borrar proyecto | Vía `sp_borrar_proyecto_y_productos` | Atómico: borra productos, N:M, desarrolla y luego el proyecto |
| Borrar `tipo_producto` | Bloqueado si tiene productos | Mantener integridad |
| Borrar `docente` | Bloqueado si tiene desarrolla/docente_producto | Mantener historial académico |

---

## Referencias

- **Formato data-model**: Spec-Kit estructura de specs
- **Normalización**: [02_especificacion.md](02_especificacion.md), sección 3.3
- **ACID**: [01_constitucion.md](01_constitucion.md), Artículo VIII
- **Compatibilidad Postgres/SqlServer**: [03_clarificacion.md](03_clarificacion.md), sección 4
- **Plan técnico con SPs**: [04_plan.md](04_plan.md), sección 7.3

---

## Fecha de ratificación

- **Versión**: 1.0
- **Fecha**: 2026-05-21
- **Autores**: Samuel Giraldo, Jostin (Estudiantes Diseño de Software USB)
- **BD**: PostgreSQL 17 en Neon Cloud (compatible con SqlServer)

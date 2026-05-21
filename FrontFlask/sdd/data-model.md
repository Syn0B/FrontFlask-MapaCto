# Modelo de Datos - FrontFlask-MapaCto

Según **Spec-Kit de GitHub**, cada feature puede tener un archivo `data-model.md` dedicado con el esquema detallado de entidades. Este archivo contiene el **DDL real** de todas las tablas que el proyecto MapaCto consume, junto con los **Stored Procedures** definidos en `ProcedimientosAlmacenados.sql`.

**Referencia**: estructura `.specify/specs/{feature}/data-model.md`

**Fuente de los datos**: `BdMapaConocimiento.sql` (dump PostgreSQL 18.1) + `ProcedimientosAlmacenados.sql`.

---

## 1. Diagrama Entidad-Relación (ER) — tablas usadas por el frontend

El proyecto MapaCto consume un subconjunto del esquema institucional. Estas son las entidades y relaciones que el frontend Flask realmente toca:

```
                                    SEGURIDAD
        ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
        │   usuario    │──<──│ rol_usuario  │──>──│     rol      │
        │ id PK        │     │ usuario_id PK│     │ id PK        │
        │ username     │     │ rol_id    PK │     │ nombre       │
        │ password     │     └──────────────┘     │ descripcion  │
        │ email        │           N:M            │ activo       │
        │ nombre_compl │                          │ fecha_creac  │
        │ activo       │                          └──────────────┘
        └──────────────┘

                            CATALOGOS / ENTIDADES MAESTRAS

   ┌──────────────────┐        ┌──────────────────────┐
   │  termino_clave   │        │    tipo_producto     │
   │ termino  PK (str)│        │ id          PK       │
   │ termino_ingles   │        │ categoria            │
   └──────────────────┘        │ clase                │
                               │ nombre               │
                               │ tipologia            │
                               └──────────────────────┘

   ┌────────────────────┐  ┌────────────────────┐  ┌──────────────────────┐
   │  area_aplicacion   │  │ area_conocimiento  │  │ obj_desarr_sostenible│
   │ id        PK       │  │ id         PK      │  │ id          PK       │
   │ nombre             │  │ gran_area          │  │ nombre               │
   └────────────────────┘  │ area               │  │ categoria            │
                           │ disciplina         │  └──────────────────────┘
                           └────────────────────┘

   ┌────────────────────┐                       ┌──────────────────────┐
   │ linea_investigacion│                       │       aliado         │
   │ id          PK     │                       │ nit         PK       │
   │ nombre             │                       │ razon_social         │
   │ descripcion        │                       │ nombre_contacto      │
   └────────────────────┘                       │ correo               │
                                                │ telefono             │
                                                │ ciudad               │
                                                └──────────────────────┘

   ┌──────────────────────────────┐
   │           docente            │
   │ cedula                  PK   │
   │ nombres, apellidos           │
   │ genero, cargo, escalafon     │
   │ fecha_nacimiento             │
   │ correo, telefono             │
   │ url_cvlac, fecha_actualiz    │
   │ perfil, cat_minciencia       │
   │ conv_minciencia              │
   │ nacionalidaad                │
   │ linea_investigacion_princ FK │
   └──────────────────────────────┘

                          NEGOCIO (maestro-detalle)
                      ┌──────────────────────────┐
                      │         proyecto         │
                      │ id                  PK   │
                      │ titulo (70)              │
                      │ resumen (256)            │
                      │ presupuesto              │
                      │ tipo_financiacion (45)   │
                      │ tipo_fondos       (45)   │
                      │ fecha_inicio             │
                      │ fecha_fin                │
                      └──────────┬───────────────┘
                                 │ 1:N
                                 v
                      ┌──────────────────────────┐
                      │         producto         │
                      │ id                  PK   │
                      │ nombre (45)              │
                      │ categoria (45)           │
                      │ fecha_entrega            │
                      │ proyecto       FK (null) │
                      │ tipo_producto  FK        │
                      └──────────────────────────┘

                          TABLAS PUENTE (N:M con proyecto)

   proyecto <──<── aa_proyecto     ──>── area_aplicacion
   proyecto <──<── ac_proyecto     ──>── area_conocimiento
   proyecto <──<── ods_proyecto    ──>── objetivo_desarrollo_sostenible
   proyecto <──<── proyecto_linea  ──>── linea_investigacion
   proyecto <──<── aliado_proyecto ──>── aliado
   proyecto <──<── palabras_clave  ──>── termino_clave   (¡es N:M, NO catalogo!)
   proyecto <──<── desarrolla      ──>── docente   (con rol y descripcion)
   producto <──<── docente_producto──>── docente
```

> **Nota importante**: las tablas puente **no tienen columna `id` propia** ni nombres prefijados con `fk`. Sus claves primarias son **compuestas** y formadas por los nombres de las entidades relacionadas.

---

## 2. DDL real (PostgreSQL) — tablas usadas por el frontend

> Las definiciones siguientes corresponden al dump `BdMapaConocimiento.sql`. Se incluyen únicamente las tablas que el frontend Flask consume; el esquema institucional completo contiene más tablas (programa, facultad, grupo_investigacion, semillero, etc.) que no son parte del alcance de esta entrega.

### 2.1 Entidades catálogo / maestras

```sql
-- ─────────────────────────────────────────────────────────────
-- termino_clave  — PK es la cadena del termino (NO un id)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE public.termino_clave (
    termino        character varying(30) NOT NULL,
    termino_ingles character varying(30)
);
ALTER TABLE ONLY public.termino_clave
    ADD CONSTRAINT termino_clave_pkey PRIMARY KEY (termino);


-- ─────────────────────────────────────────────────────────────
-- tipo_producto  — 4 campos descriptivos (no es un simple "nombre")
-- ─────────────────────────────────────────────────────────────
CREATE TABLE public.tipo_producto (
    id        integer               NOT NULL,
    categoria character varying(45) NOT NULL,
    clase     character varying(45) NOT NULL,
    nombre    character varying(45) NOT NULL,
    tipologia character varying(45) NOT NULL
);
ALTER TABLE ONLY public.tipo_producto
    ADD CONSTRAINT tipo_producto_pkey PRIMARY KEY (id);


-- ─────────────────────────────────────────────────────────────
-- area_aplicacion  — tabla referenciada como "aa" en las tablas puente
-- ─────────────────────────────────────────────────────────────
CREATE TABLE public.area_aplicacion (
    id     integer               NOT NULL,
    nombre character varying(60) NOT NULL
);
ALTER TABLE ONLY public.area_aplicacion
    ADD CONSTRAINT area_aplicacion_pkey PRIMARY KEY (id);


-- ─────────────────────────────────────────────────────────────
-- area_conocimiento  — referenciada como "ac" en tablas puente
-- ─────────────────────────────────────────────────────────────
CREATE TABLE public.area_conocimiento (
    id         integer               NOT NULL,
    gran_area  character varying(60) NOT NULL,
    area       character varying(60) NOT NULL,
    disciplina character varying(60) NOT NULL
);
ALTER TABLE ONLY public.area_conocimiento
    ADD CONSTRAINT area_conocimiento_pkey PRIMARY KEY (id);


-- ─────────────────────────────────────────────────────────────
-- objetivo_desarrollo_sostenible  — referenciada como "ods"
-- ─────────────────────────────────────────────────────────────
CREATE TABLE public.objetivo_desarrollo_sostenible (
    id        integer               NOT NULL,
    nombre    character varying(60) NOT NULL,
    categoria character varying(45) NOT NULL
);
ALTER TABLE ONLY public.objetivo_desarrollo_sostenible
    ADD CONSTRAINT objetivo_desarrollo_sostenible_pkey PRIMARY KEY (id);


-- ─────────────────────────────────────────────────────────────
-- linea_investigacion  — NO se llama solo "linea"
-- ─────────────────────────────────────────────────────────────
CREATE TABLE public.linea_investigacion (
    id          integer                NOT NULL,
    nombre      character varying(45)  NOT NULL,
    descripcion character varying(256) NOT NULL
);
ALTER TABLE ONLY public.linea_investigacion
    ADD CONSTRAINT linea_investigacion_pkey PRIMARY KEY (id);


-- ─────────────────────────────────────────────────────────────
-- aliado  — PK es "nit" (NO un id autoincremental)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE public.aliado (
    nit             integer               NOT NULL,
    razon_social    character varying(60) NOT NULL,
    nombre_contacto character varying(60) NOT NULL,
    correo          character varying(70) NOT NULL,
    telefono        character varying(45) NOT NULL,
    ciudad          character varying(45) NOT NULL
);
ALTER TABLE ONLY public.aliado
    ADD CONSTRAINT aliado_pkey PRIMARY KEY (nit);


-- ─────────────────────────────────────────────────────────────
-- docente  — entidad rica con muchos atributos
-- ─────────────────────────────────────────────────────────────
CREATE TABLE public.docente (
    cedula                        integer                NOT NULL,
    nombres                       character varying(60)  NOT NULL,
    apellidos                     character varying(60)  NOT NULL,
    genero                        character varying(12)  NOT NULL,
    cargo                         character varying(30)  NOT NULL,
    fecha_nacimiento              date                   NOT NULL,
    correo                        character varying(70)  NOT NULL,
    telefono                      character varying(20)  NOT NULL,
    url_cvlac                     character varying(128) NOT NULL,
    fecha_actualizacion           date                   NOT NULL,
    escalafon                     character varying(45)  NOT NULL,
    perfil                        text                   NOT NULL,
    cat_minciencia                character varying(45),
    conv_minciencia               character varying(45)  NOT NULL,
    nacionalidaad                 character varying(45)  NOT NULL,  -- typo del esquema institucional
    linea_investigacion_principal integer
);
ALTER TABLE ONLY public.docente
    ADD CONSTRAINT docente_pkey PRIMARY KEY (cedula);
```

### 2.2 Entidades de negocio (maestro-detalle)

```sql
-- ─────────────────────────────────────────────────────────────
-- proyecto  — maestro
-- ─────────────────────────────────────────────────────────────
CREATE TABLE public.proyecto (
    id                integer                NOT NULL,
    titulo            character varying(70)  NOT NULL,
    resumen           character varying(256) NOT NULL,
    presupuesto       double precision       NOT NULL,
    tipo_financiacion character varying(45)  NOT NULL,
    tipo_fondos       character varying(45)  NOT NULL,
    fecha_inicio      date                   NOT NULL,
    fecha_fin         date
);
ALTER TABLE ONLY public.proyecto
    ADD CONSTRAINT proyecto_pkey PRIMARY KEY (id);


-- ─────────────────────────────────────────────────────────────
-- producto  — detalle del proyecto (proyecto es NULLABLE)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE public.producto (
    id            integer               NOT NULL,
    nombre        character varying(45) NOT NULL,
    categoria     character varying(45) NOT NULL,
    fecha_entrega date                  NOT NULL,
    proyecto      integer,                              -- FK opcional
    tipo_producto integer               NOT NULL        -- FK obligatorio
);
ALTER TABLE ONLY public.producto
    ADD CONSTRAINT producto_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.producto
    ADD CONSTRAINT producto_proyecto_fkey
        FOREIGN KEY (proyecto) REFERENCES public.proyecto(id);
ALTER TABLE ONLY public.producto
    ADD CONSTRAINT producto_tipo_producto_fkey
        FOREIGN KEY (tipo_producto) REFERENCES public.tipo_producto(id);
```

### 2.3 Tablas puente (N:M)

> Todas las tablas puente tienen **PK compuesta** y **no llevan columna `id` propia**. Sus columnas se llaman como las entidades referenciadas (no llevan prefijo `fk`).

```sql
-- ─────────────────────────────────────────────────────────────
-- aa_proyecto  — proyectos x area_aplicacion
-- ─────────────────────────────────────────────────────────────
CREATE TABLE public.aa_proyecto (
    proyecto        integer NOT NULL,
    area_aplicacion integer NOT NULL
);
ALTER TABLE ONLY public.aa_proyecto
    ADD CONSTRAINT aa_proyecto_pkey PRIMARY KEY (proyecto, area_aplicacion);
ALTER TABLE ONLY public.aa_proyecto
    ADD CONSTRAINT aa_proyecto_proyecto_fkey
        FOREIGN KEY (proyecto) REFERENCES public.proyecto(id);
ALTER TABLE ONLY public.aa_proyecto
    ADD CONSTRAINT aa_proyecto_area_aplicacion_fkey
        FOREIGN KEY (area_aplicacion) REFERENCES public.area_aplicacion(id);


-- ─────────────────────────────────────────────────────────────
-- ac_proyecto  — proyectos x area_conocimiento
-- ─────────────────────────────────────────────────────────────
CREATE TABLE public.ac_proyecto (
    proyecto          integer NOT NULL,
    area_conocimiento integer NOT NULL
);
ALTER TABLE ONLY public.ac_proyecto
    ADD CONSTRAINT ac_proyecto_pkey PRIMARY KEY (proyecto, area_conocimiento);


-- ─────────────────────────────────────────────────────────────
-- ods_proyecto  — proyectos x ODS
-- ─────────────────────────────────────────────────────────────
CREATE TABLE public.ods_proyecto (
    proyecto integer NOT NULL,
    ods      integer NOT NULL
);
ALTER TABLE ONLY public.ods_proyecto
    ADD CONSTRAINT ods_proyecto_pkey PRIMARY KEY (proyecto, ods);


-- ─────────────────────────────────────────────────────────────
-- proyecto_linea  — proyectos x linea_investigacion
-- ─────────────────────────────────────────────────────────────
CREATE TABLE public.proyecto_linea (
    proyecto            integer NOT NULL,
    linea_investigacion integer NOT NULL
);
ALTER TABLE ONLY public.proyecto_linea
    ADD CONSTRAINT proyecto_linea_pkey PRIMARY KEY (proyecto, linea_investigacion);


-- ─────────────────────────────────────────────────────────────
-- aliado_proyecto  — aliados x proyectos
-- ─────────────────────────────────────────────────────────────
CREATE TABLE public.aliado_proyecto (
    aliado   integer NOT NULL,
    proyecto integer NOT NULL
);
ALTER TABLE ONLY public.aliado_proyecto
    ADD CONSTRAINT aliado_proyecto_pkey PRIMARY KEY (aliado, proyecto);


-- ─────────────────────────────────────────────────────────────
-- palabras_clave  — IMPORTANTE: ES N:M, NO ES UN CATALOGO!
--                   Relaciona proyectos con terminos clave.
-- ─────────────────────────────────────────────────────────────
CREATE TABLE public.palabras_clave (
    proyecto      integer               NOT NULL,
    termino_clave character varying(30) NOT NULL
);
ALTER TABLE ONLY public.palabras_clave
    ADD CONSTRAINT palabras_clave_pkey PRIMARY KEY (proyecto, termino_clave);


-- ─────────────────────────────────────────────────────────────
-- docente_producto  — docentes autores de un producto
-- ─────────────────────────────────────────────────────────────
CREATE TABLE public.docente_producto (
    docente  integer NOT NULL,
    producto integer NOT NULL
);
ALTER TABLE ONLY public.docente_producto
    ADD CONSTRAINT docente_producto_pkey PRIMARY KEY (docente, producto);


-- ─────────────────────────────────────────────────────────────
-- desarrolla  — N:M con atributos (rol y descripcion son NOT NULL)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE public.desarrolla (
    docente     integer                NOT NULL,
    proyecto    integer                NOT NULL,
    rol         character varying(45)  NOT NULL,
    descripcion character varying(256) NOT NULL    -- NOT NULL, no acepta vacio
);
ALTER TABLE ONLY public.desarrolla
    ADD CONSTRAINT desarrolla_pkey PRIMARY KEY (docente, proyecto);
```

### 2.4 Tablas de seguridad

```sql
-- ─────────────────────────────────────────────────────────────
-- usuario  — credenciales (password se guarda como hash BCrypt)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE public.usuario (
    id                  integer                        NOT NULL,
    username            character varying(100)         NOT NULL,
    password            character varying(255)         NOT NULL,  -- hash BCrypt
    email               character varying(150)         NOT NULL,
    nombre_completo     character varying(200),
    activo              boolean                        DEFAULT true,
    fecha_creacion      timestamp without time zone    DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion timestamp without time zone    DEFAULT CURRENT_TIMESTAMP
);
ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_username_key UNIQUE (username);
ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_email_key UNIQUE (email);

CREATE SEQUENCE public.usuario_id_seq AS integer
    START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;
ALTER SEQUENCE public.usuario_id_seq OWNED BY public.usuario.id;
ALTER TABLE ONLY public.usuario
    ALTER COLUMN id SET DEFAULT nextval('public.usuario_id_seq'::regclass);


-- ─────────────────────────────────────────────────────────────
-- rol
-- ─────────────────────────────────────────────────────────────
CREATE TABLE public.rol (
    id             integer                        NOT NULL,
    nombre         character varying(100)         NOT NULL,
    descripcion    text,
    activo         boolean                        DEFAULT true,
    fecha_creacion timestamp without time zone    DEFAULT CURRENT_TIMESTAMP
);
ALTER TABLE ONLY public.rol
    ADD CONSTRAINT rol_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.rol
    ADD CONSTRAINT rol_nombre_key UNIQUE (nombre);

CREATE SEQUENCE public.rol_id_seq AS integer
    START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;
ALTER SEQUENCE public.rol_id_seq OWNED BY public.rol.id;
ALTER TABLE ONLY public.rol
    ALTER COLUMN id SET DEFAULT nextval('public.rol_id_seq'::regclass);


-- ─────────────────────────────────────────────────────────────
-- rol_usuario  — N:M con ON DELETE CASCADE
-- ─────────────────────────────────────────────────────────────
CREATE TABLE public.rol_usuario (
    usuario_id integer NOT NULL,
    rol_id     integer NOT NULL
);
ALTER TABLE ONLY public.rol_usuario
    ADD CONSTRAINT rol_usuario_pkey PRIMARY KEY (usuario_id, rol_id);
ALTER TABLE ONLY public.rol_usuario
    ADD CONSTRAINT rol_usuario_usuario_id_fkey
        FOREIGN KEY (usuario_id) REFERENCES public.usuario(id) ON DELETE CASCADE;
ALTER TABLE ONLY public.rol_usuario
    ADD CONSTRAINT rol_usuario_rol_id_fkey
        FOREIGN KEY (rol_id) REFERENCES public.rol(id) ON DELETE CASCADE;
```

> **Notas sobre seguridad**:
> - **No existen tablas `ruta` ni `rutarol` en la BD**. Las rutas permitidas por rol se calculan en código (`services/auth_service.py → calcular_rutas_permitidas`) con las reglas hardcodeadas para los roles `Admin`, `EncargadoProyectos` y `Visitante`.
> - **No hay triggers** definidos en el esquema actual. Toda la lógica transaccional para maestro-detalle vive en los Stored Procedures de la sección 3.

---

## 3. Stored Procedures reales

El proyecto usa los **5 Stored Procedures** definidos en `ProcedimientosAlmacenados.sql`. Todos siguen el mismo contrato: un parámetro `OUT p_resultado` de tipo `JSONB` que la API C# extrae de `resultados[0].p_resultado` y `ApiService.ejecutar_sp()` parsea automáticamente a `dict`.

| # | Stored Procedure | Endpoint del frontend | Comportamiento |
|---|------------------|------------------------|----------------|
| 1 | `sp_consultar_proyecto_y_productos` | `GET /proyecto?accion=editar` | Devuelve el proyecto y sus productos anidados |
| 2 | `sp_insertar_proyecto_y_productos` | `POST /proyecto/crear` | Inserta maestro + detalles en una transacción |
| 3 | `sp_actualizar_proyecto_y_productos` | `POST /proyecto/actualizar` | **SYNC diferencial**: UPDATE existentes, INSERT nuevos, DELETE removidos |
| 4 | `sp_borrar_proyecto_y_productos` | `POST /proyecto/eliminar` | Borra maestro + detalles + limpia tablas puente |
| 5 | `sp_listar_proyecto_y_productos` | (opcional) | Lista proyectos con sus productos anidados |

> **No hay triggers** ni otros SPs definidos. Estos cinco son los únicos creados en el dump.

### 3.1 SP: Consultar proyecto y productos

```sql
DROP FUNCTION IF EXISTS sp_consultar_proyecto_y_productos(INT);

CREATE OR REPLACE FUNCTION sp_consultar_proyecto_y_productos(
    p_id            INT,
    OUT p_resultado JSONB
) AS $$
DECLARE
    v_proyecto  JSONB;
    v_productos JSONB;
BEGIN
    SELECT to_jsonb(p.*)
      INTO v_proyecto
      FROM proyecto p
     WHERE p.id = p_id;

    IF v_proyecto IS NULL THEN
        RAISE EXCEPTION 'Proyecto con id=% no encontrado.', p_id;
    END IF;

    SELECT COALESCE(jsonb_agg(to_jsonb(pr.*) ORDER BY pr.id), '[]'::JSONB)
      INTO v_productos
      FROM producto pr
     WHERE pr.proyecto = p_id;

    p_resultado := jsonb_build_object(
        'proyecto',  v_proyecto,
        'productos', v_productos
    );
END;
$$ LANGUAGE plpgsql;
```

### 3.2 SP: Insertar proyecto y productos

> Si `p_id IS NULL`, se autocalcula con `COALESCE(MAX(id), 0) + 1`. Los IDs de producto también se autocalculan.

```sql
CREATE OR REPLACE FUNCTION sp_insertar_proyecto_y_productos(
    p_id                INT,
    p_titulo            VARCHAR,
    p_resumen           VARCHAR,
    p_presupuesto       DOUBLE PRECISION,
    p_tipo_financiacion VARCHAR,
    p_tipo_fondos       VARCHAR,
    p_fecha_inicio      DATE,
    p_fecha_fin         DATE,
    p_productos         JSON,
    OUT p_resultado     JSONB
) AS $$
DECLARE
    v_id_proyecto   INT;
    v_productos     JSONB;
    v_prod          JSONB;
    v_nuevo_id_prod INT;
    v_insertados    INT := 0;
BEGIN
    -- Determinar ID del proyecto
    IF p_id IS NOT NULL THEN
        IF EXISTS (SELECT 1 FROM proyecto WHERE id = p_id) THEN
            RAISE EXCEPTION 'Ya existe un proyecto con id=%.', p_id;
        END IF;
        v_id_proyecto := p_id;
    ELSE
        SELECT COALESCE(MAX(id), 0) + 1 INTO v_id_proyecto FROM proyecto;
    END IF;

    -- Insertar el maestro
    INSERT INTO proyecto (
        id, titulo, resumen, presupuesto,
        tipo_financiacion, tipo_fondos,
        fecha_inicio, fecha_fin
    )
    VALUES (
        v_id_proyecto, p_titulo, p_resumen, p_presupuesto,
        p_tipo_financiacion, p_tipo_fondos,
        p_fecha_inicio, p_fecha_fin
    );

    -- Validar e insertar detalles
    v_productos := COALESCE(p_productos::JSONB, '[]'::JSONB);

    IF jsonb_typeof(v_productos) <> 'array' THEN
        RAISE EXCEPTION 'p_productos debe ser un JSON array. Recibido: %.',
                        jsonb_typeof(v_productos);
    END IF;

    IF jsonb_array_length(v_productos) > 0 THEN
        SELECT COALESCE(MAX(id), 0) INTO v_nuevo_id_prod FROM producto;

        FOR v_prod IN SELECT * FROM jsonb_array_elements(v_productos)
        LOOP
            v_nuevo_id_prod := v_nuevo_id_prod + 1;
            INSERT INTO producto (
                id, nombre, categoria, fecha_entrega, proyecto, tipo_producto
            )
            VALUES (
                v_nuevo_id_prod,
                v_prod->>'nombre',
                v_prod->>'categoria',
                (v_prod->>'fecha_entrega')::DATE,
                v_id_proyecto,
                (v_prod->>'tipo_producto')::INT
            );
            v_insertados := v_insertados + 1;
        END LOOP;
    END IF;

    p_resultado := jsonb_build_object(
        'mensaje',              'Proyecto creado exitosamente.',
        'id',                   v_id_proyecto,
        'productos_insertados', v_insertados
    );
END;
$$ LANGUAGE plpgsql;
```

### 3.3 SP: Actualizar proyecto y productos (SYNC diferencial)

> A diferencia de un replace-all (DELETE ALL + INSERT), este SP **sincroniza**: UPDATE para productos con `id` ya existente, INSERT para los nuevos, DELETE para los que ya no vienen en la lista. Esto **preserva** las relaciones en `docente_producto` para los productos que no cambian.

```sql
CREATE OR REPLACE FUNCTION sp_actualizar_proyecto_y_productos(
    p_id                INT,
    p_titulo            VARCHAR,
    p_resumen           VARCHAR,
    p_presupuesto       DOUBLE PRECISION,
    p_tipo_financiacion VARCHAR,
    p_tipo_fondos       VARCHAR,
    p_fecha_inicio      DATE,
    p_fecha_fin         DATE,
    p_productos         JSON,
    OUT p_resultado     JSONB
) AS $$
DECLARE
    v_productos     JSONB;
    v_prod          JSONB;
    v_ids_entrantes INT[];
    v_nuevo_id_prod INT;
    v_actualizados  INT := 0;
    v_insertados    INT := 0;
    v_eliminados    INT := 0;
BEGIN
    -- Validar existencia
    IF NOT EXISTS (SELECT 1 FROM proyecto WHERE id = p_id) THEN
        RAISE EXCEPTION 'Proyecto con id=% no encontrado.', p_id;
    END IF;

    -- UPDATE del maestro
    UPDATE proyecto SET
        titulo            = p_titulo,
        resumen           = p_resumen,
        presupuesto       = p_presupuesto,
        tipo_financiacion = p_tipo_financiacion,
        tipo_fondos       = p_tipo_fondos,
        fecha_inicio      = p_fecha_inicio,
        fecha_fin         = p_fecha_fin
    WHERE id = p_id;

    v_productos := COALESCE(p_productos::JSONB, '[]'::JSONB);

    IF jsonb_typeof(v_productos) <> 'array' THEN
        RAISE EXCEPTION 'p_productos debe ser un JSON array. Recibido: %.',
                        jsonb_typeof(v_productos);
    END IF;

    -- IDs de productos que sobreviven
    SELECT COALESCE(array_agg((elem->>'id')::INT), ARRAY[]::INT[])
      INTO v_ids_entrantes
      FROM jsonb_array_elements(v_productos) AS elem
     WHERE elem ? 'id'
       AND elem->>'id' IS NOT NULL
       AND elem->>'id' <> '';

    -- DELETE de removidos: primero docente_producto, luego producto
    DELETE FROM docente_producto
     WHERE producto IN (
         SELECT id FROM producto
          WHERE proyecto = p_id
            AND id <> ALL (v_ids_entrantes)
     );

    WITH eliminados AS (
        DELETE FROM producto
         WHERE proyecto = p_id
           AND id <> ALL (v_ids_entrantes)
        RETURNING id
    )
    SELECT COUNT(*) INTO v_eliminados FROM eliminados;

    -- UPDATE / INSERT segun tenga "id"
    IF jsonb_array_length(v_productos) > 0 THEN
        SELECT COALESCE(MAX(id), 0) INTO v_nuevo_id_prod FROM producto;

        FOR v_prod IN SELECT * FROM jsonb_array_elements(v_productos)
        LOOP
            IF v_prod ? 'id'
               AND (v_prod->>'id') IS NOT NULL
               AND (v_prod->>'id') <> '' THEN
                UPDATE producto SET
                    nombre        = v_prod->>'nombre',
                    categoria     = v_prod->>'categoria',
                    fecha_entrega = (v_prod->>'fecha_entrega')::DATE,
                    tipo_producto = (v_prod->>'tipo_producto')::INT,
                    proyecto      = p_id
                WHERE id = (v_prod->>'id')::INT;

                IF NOT FOUND THEN
                    RAISE EXCEPTION
                        'Producto con id=% no existe para el proyecto=%.',
                        (v_prod->>'id')::INT, p_id;
                END IF;

                v_actualizados := v_actualizados + 1;
            ELSE
                v_nuevo_id_prod := v_nuevo_id_prod + 1;
                INSERT INTO producto (
                    id, nombre, categoria, fecha_entrega, proyecto, tipo_producto
                )
                VALUES (
                    v_nuevo_id_prod,
                    v_prod->>'nombre',
                    v_prod->>'categoria',
                    (v_prod->>'fecha_entrega')::DATE,
                    p_id,
                    (v_prod->>'tipo_producto')::INT
                );
                v_insertados := v_insertados + 1;
            END IF;
        END LOOP;
    END IF;

    p_resultado := jsonb_build_object(
        'mensaje',                'Proyecto actualizado exitosamente.',
        'id',                     p_id,
        'productos_actualizados', v_actualizados,
        'productos_insertados',   v_insertados,
        'productos_eliminados',   v_eliminados
    );
END;
$$ LANGUAGE plpgsql;
```

### 3.4 SP: Borrar proyecto y productos

> Limpia **todas** las tablas puente que referencian al proyecto antes de borrar el maestro, simulando un `ON DELETE CASCADE` que el esquema **no** declara.

```sql
CREATE OR REPLACE FUNCTION sp_borrar_proyecto_y_productos(
    p_id            INT,
    OUT p_resultado JSONB
) AS $$
DECLARE
    v_prods_borrados INT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM proyecto WHERE id = p_id) THEN
        RAISE EXCEPTION 'Proyecto con id=% no encontrado.', p_id;
    END IF;

    -- Referencias de productos en docente_producto
    DELETE FROM docente_producto
     WHERE producto IN (SELECT id FROM producto WHERE proyecto = p_id);

    -- Productos del proyecto
    WITH borrados AS (
        DELETE FROM producto WHERE proyecto = p_id
        RETURNING id
    )
    SELECT COUNT(*) INTO v_prods_borrados FROM borrados;

    -- TABLAS PUENTE DE PROYECTO
    DELETE FROM aa_proyecto     WHERE proyecto = p_id;
    DELETE FROM ac_proyecto     WHERE proyecto = p_id;
    DELETE FROM aliado_proyecto WHERE proyecto = p_id;
    DELETE FROM desarrolla      WHERE proyecto = p_id;
    DELETE FROM ods_proyecto    WHERE proyecto = p_id;
    DELETE FROM palabras_clave  WHERE proyecto = p_id;
    DELETE FROM proyecto_linea  WHERE proyecto = p_id;

    -- Maestro
    DELETE FROM proyecto WHERE id = p_id;

    p_resultado := jsonb_build_object(
        'mensaje',              'Proyecto eliminado exitosamente.',
        'id',                   p_id,
        'productos_eliminados', v_prods_borrados
    );
END;
$$ LANGUAGE plpgsql;
```

### 3.5 SP: Listar proyectos con productos anidados (opcional)

> Útil si se quiere reemplazar el `GET /api/proyecto` por un `ejecutar_sp` que devuelva productos anidados en una sola llamada.

```sql
CREATE OR REPLACE FUNCTION sp_listar_proyecto_y_productos(
    p_limite        INT DEFAULT NULL,
    OUT p_resultado JSONB
) AS $$
BEGIN
    WITH proy AS (
        SELECT p.* FROM proyecto p
        ORDER BY p.id
        LIMIT p_limite                  -- NULL ⇒ sin limite
    ),
    proy_con_prods AS (
        SELECT
            pr.id, pr.titulo, pr.resumen, pr.presupuesto,
            pr.tipo_financiacion, pr.tipo_fondos,
            pr.fecha_inicio, pr.fecha_fin,
            COALESCE(
                (SELECT jsonb_agg(to_jsonb(prd.*) ORDER BY prd.id)
                   FROM producto prd
                  WHERE prd.proyecto = pr.id),
                '[]'::JSONB
            ) AS productos
        FROM proy pr
    )
    SELECT jsonb_build_object(
             'proyectos',
             COALESCE(jsonb_agg(to_jsonb(proy_con_prods.*)), '[]'::JSONB)
           )
      INTO p_resultado
      FROM proy_con_prods;

    IF p_resultado IS NULL THEN
        p_resultado := jsonb_build_object('proyectos', '[]'::JSONB);
    END IF;
END;
$$ LANGUAGE plpgsql;
```

---

## 4. Triggers

**El esquema actual no define ningún trigger** (`CREATE TRIGGER ...`). Toda la lógica transaccional para garantizar consistencia maestro-detalle vive en los 5 Stored Procedures de la sección anterior. Si en una entrega futura se agregan triggers (por ejemplo, para auditoría o cálculo automático de campos derivados), deben documentarse aquí.

---

## 5. Diccionario de tipos PostgreSQL → Python → HTML

| Tipo PostgreSQL | Python | HTML input |
|-----------------|--------|------------|
| `integer` | `int` | `type="number"` |
| `character varying(N)` | `str` | `type="text"` (o `<textarea>` si N grande) |
| `text` | `str` | `<textarea>` |
| `double precision` | `float` | `type="number" step="0.01"` |
| `date` | `datetime.date` | `type="date"` |
| `timestamp without time zone` | `datetime.datetime` | `type="datetime-local"` |
| `boolean` | `bool` | `type="checkbox"` |
| `json` / `jsonb` | `dict` / `list` | — (uso interno SPs) |

---

## 6. Cardinalidades resumen

| Relación | Tipo | Tabla intermedia |
|----------|------|------------------|
| `proyecto` ↔ `producto` | 1:N | No (FK directo, `producto.proyecto` es nullable) |
| `tipo_producto` ↔ `producto` | 1:N | No (FK directo, NOT NULL) |
| `proyecto` ↔ `area_aplicacion` | N:M | `aa_proyecto` |
| `proyecto` ↔ `area_conocimiento` | N:M | `ac_proyecto` |
| `proyecto` ↔ `objetivo_desarrollo_sostenible` | N:M | `ods_proyecto` |
| `proyecto` ↔ `linea_investigacion` | N:M | `proyecto_linea` |
| `proyecto` ↔ `aliado` | N:M | `aliado_proyecto` |
| `proyecto` ↔ `termino_clave` | N:M | `palabras_clave` |
| `proyecto` ↔ `docente` | N:M (con atributos `rol` y `descripcion`) | `desarrolla` |
| `producto` ↔ `docente` | N:M | `docente_producto` |
| `usuario` ↔ `rol` | N:M (con `ON DELETE CASCADE`) | `rol_usuario` |

---

## 7. Integridad referencial

| Acción | Comportamiento real en el dump |
|--------|--------------------------------|
| FKs de `producto` | `producto.proyecto` y `producto.tipo_producto` → `NO ACTION` |
| FKs de tablas puente del proyecto | `NO ACTION` por defecto (no hay `CASCADE`) |
| Borrar un proyecto | **Solo es seguro vía `sp_borrar_proyecto_y_productos`**, que limpia las 7 tablas puente y la tabla `producto` antes de borrar el maestro |
| FKs de `rol_usuario` | `ON DELETE CASCADE` (al borrar un usuario o rol se borran sus asignaciones) |
| FKs de `producto` con `tipo_producto` | `NO ACTION` (no se puede borrar un tipo que tenga productos asociados) |

---

## Referencias

- **Fuente del esquema**: `BdMapaConocimiento.sql` (dump PostgreSQL 18.1)
- **Fuente de los SPs**: `ProcedimientosAlmacenados.sql`
- **Formato data-model**: Spec-Kit estructura de specs
- **Normalización**: [02_especificacion.md](02_especificacion.md), sección 3.3
- **ACID**: [01_constitucion.md](01_constitucion.md), Artículo VIII
- **Plan técnico con SPs**: [04_plan.md](04_plan.md), sección 7.3

---

## Fecha de ratificación

- **Versión**: 1.1
- **Fecha**: 2026-05-21
- **Autores**: Samuel Giraldo, Jostin (Estudiantes Construcción de Software USB)
- **BD**: PostgreSQL 18.1 en Neon Cloud

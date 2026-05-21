# OpenSpec - Instalación, Uso y Comparación con Spec-Kit

**OpenSpec** es el framework open source de **Fission AI** para Spec Driven Development (SDD). Con **30.000+ estrellas** en GitHub, es compatible con 20+ agentes de IA (Claude Code, Cursor, Copilot, Gemini, OpenCode, etc.).

A diferencia de **Spec-Kit** (GitHub) que es para proyectos nuevos (**greenfield**), **OpenSpec** está diseñado para proyectos existentes (**brownfield**) con el concepto de **delta specs** — cambios incrementales que no reescriben toda la spec.

---

## 1. Qué es OpenSpec

OpenSpec convierte el SDD en un **flujo de trabajo con herramientas reales**. No es una plantilla de Markdown — es una CLI que se instala con `npm` y se integra con tu agente de IA.

### 4 principios de OpenSpec

| Principio | Qué significa |
|-----------|---------------|
| **Fluido, no rígido** | No hay puertas de fase. Puedes volver atrás cuando quieras |
| **Iterativo, no waterfall** | Aprende mientras construyes, refina sobre la marcha |
| **Fácil, no complejo** | Configuración mínima, arranque en segundos |
| **Brownfield first** | Diseñado para proyectos existentes, no solo para nuevos |

### 4 conceptos fundamentales

| Concepto | Qué es | Dónde vive |
|----------|--------|------------|
| **Specs** | Fuente de verdad: cómo se comporta el sistema **AHORA** | `openspec/specs/{dominio}/spec.md` |
| **Changes** | Propuestas de cambio (carpeta autocontenida) | `openspec/changes/{nombre}/` |
| **Artefactos** | Documentos dentro de un change (proposal, design, tasks, delta specs) | Dentro de cada change |
| **Delta Specs** | Cambios incrementales a las specs (`ADDED`, `MODIFIED`, `REMOVED`) | `openspec/changes/{nombre}/specs/` |

### Referencias

- **Repositorio**: [github.com/Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec)
- **Documentación**: OpenSpec Getting Started
- **Guía detallada**: [webreactiva.com/blog/openspec](https://webreactiva.com/blog/openspec)
- **npm**: `@fission-ai/openspec`

---

## 2. Instalación paso a paso

### 2.1 Prerrequisitos

| Herramienta | Versión mínima | Cómo verificar |
|-------------|----------------|----------------|
| Node.js | 20.19.0+ | `node --version` |
| npm | (incluido) | `npm --version` |
| Git | cualquiera | `git --version` |

### 2.2 Instalar OpenSpec

```powershell
npm install -g @fission-ai/openspec@latest
openspec --version   # Debe mostrar: 1.3.0 (o superior)
```

### 2.3 Inicializar en el proyecto

```powershell
cd C:\Users\Samue\Desktop\Entrega2-MapaCto\FrontFlask-MapaCto\FrontFlask
openspec init
```

El proceso pregunta qué agente de IA usas. Seleccionar **Claude Code**. OpenSpec crea los skills en `.claude/skills/` y los comandos en `.claude/commands/`.

### 2.4 Qué genera `openspec init`

```
FrontFlask/
├── openspec/
│   ├── specs/              <- Fuente de verdad (vacia al inicio)
│   └── changes/
│       └── archive/        <- Cambios archivados
│
└── .claude/
    ├── commands/opsx        <- Comandos OPSX
    └── skills/
        ├── openspec-propose/     <- /opsx:propose
        ├── openspec-apply-change/ <- /opsx:apply
        ├── openspec-archive-change/ <- /opsx:archive
        └── openspec-explore/     <- /opsx:explore
```

### 2.5 Desactivar telemetría (opcional)

```powershell
$env:OPENSPEC_TELEMETRY = "0"
```

---

## 3. Comandos de OpenSpec (OPSX)

### Comandos principales (perfil core)

| Comando | Qué hace | Cuándo usarlo |
|---------|----------|---------------|
| `/opsx:explore` | Modo exploratorio libre, sin crear artefactos | Cuando no tienes claro el enfoque |
| `/opsx:propose` | Crea un change con **TODOS** los artefactos (proposal, specs, design, tasks) | Inicio rápido, la mayoría de los casos |
| `/opsx:apply` | Implementa las tareas del change | Cuando el plan está listo |
| `/opsx:archive` | Archiva el change y fusiona delta specs | Cuando todas las tareas están completas |

### Comandos avanzados (perfil expandido)

| Comando | Qué hace |
|---------|----------|
| `/opsx:new` | Crea solo la estructura del change (sin artefactos) |
| `/opsx:continue` | Genera el siguiente artefacto según dependencias |
| `/opsx:ff` | Fast-forward: genera todos los artefactos de golpe |
| `/opsx:verify` | Valida implementación contra specs |
| `/opsx:sync` | Fusiona delta specs sin archivar |
| `/opsx:bulk-archive` | Archiva varios changes a la vez |
| `/opsx:onboard` | Tutorial guiado con tu propio código |

> **Nota**: En **Claude Code** se usa dos puntos (`/opsx:propose`). En Cursor, OpenCode, Windsurf se usa guión (`/opsx-propose`).

---

## 4. Flujo completo con ejemplo

### Agregar una feature nueva al proyecto MapaCto

#### Paso 1: Explorar la idea

```
> /opsx:explore
> "Necesito agregar exportación CSV en la pagina de proyecto para
>  reportes institucionales con todos los productos asociados"
> La IA analiza el codigo existente y sugiere enfoques
```

#### Paso 2: Crear el change con artefactos

```
> /opsx:propose exportar-csv-proyecto
> Genera:
>   openspec/changes/exportar-csv-proyecto/
>   ├── proposal.md      <- Por que y que
>   ├── specs/            <- Delta specs (que cambia)
>   ├── design.md         <- Como (enfoque tecnico)
>   └── tasks.md          <- Checklist de implementacion
```

#### Paso 3: Revisar y ajustar

```
> Leer los artefactos, editar si falta algo
> Samuel revisa proposal.md; Jostin revisa design.md
```

#### Paso 4: Implementar

```
> /opsx:apply
> La IA ejecuta tarea por tarea, marcando checkboxes
```

#### Paso 5: Archivar

```
> /opsx:archive
> Delta specs se fusionan con specs principales
> Change se mueve a openspec/changes/archive/2026-05-21-exportar-csv-proyecto/
```

### Delta specs: el concepto clave

En vez de reescribir toda la spec, escribes **SOLO lo que cambia**:

```markdown
# Delta for Proyecto

## ADDED Requirements

### Requirement: CSV Export
El sistema DEBE permitir exportar la lista de proyectos a CSV con todos sus
productos asociados y los nombres de tipo_producto y docentes resueltos.

## MODIFIED Requirements

### Requirement: Listar proyectos
El sistema DEBE mostrar un boton "Exportar CSV" en la tabla de proyectos.
(Previously: solo mostraba la tabla)
```

Al archivar, los deltas se fusionan: `ADDED` se agrega, `MODIFIED` reemplaza, `REMOVED` se elimina.

---

## 5. Estructura de archivos en este proyecto

Ahora el proyecto tiene **3 carpetas** de documentación SDD:

```
FrontFlask-MapaCto/FrontFlask/
├── sdd/                    <- Documentacion manual (educativa, extensa)
│   ├── 00_indice.md
│   ├── 01_constitucion.md   (SOLID, ACID, patrones)
│   ├── 02_especificacion.md (modelo ER, normalizacion)
│   ├── 03_clarificacion.md  (preguntas resueltas)
│   ├── 04_plan.md           (diagramas Mermaid)
│   ├── 05_tareas.md         (por historia, Samuel/Jostin)
│   ├── 06_specify_cli.md    (instalacion Spec-Kit)
│   ├── 07_openspec.md       (ESTE archivo)
│   └── data-model.md        (SQL completo PostgreSQL Neon)
│
├── .specify/               <- Spec-Kit de GitHub (greenfield)
│   ├── memory/constitution.md
│   ├── specs/001-proyecto-maestro-detalle/{spec,plan,tasks}.md
│   ├── specs/002-crud-catalogos/{spec,plan,tasks}.md
│   ├── specs/003-nm-proyecto/{spec,plan,tasks}.md
│   ├── specs/004-relaciones-docente/{spec,plan,tasks}.md
│   ├── specs/005-login-control-acceso/{spec,plan,tasks}.md
│   └── templates/*.md
│
└── openspec/               <- OpenSpec de Fission AI (brownfield)
    ├── specs/               (se llenara con delta specs por dominio)
    │   ├── proyecto/spec.md
    │   ├── producto/spec.md
    │   └── auth/spec.md
    └── changes/
        └── archive/         (changes completados)
```

---

## 6. Comparación detallada: Manual (`sdd/`) vs Spec-Kit vs OpenSpec

### Tabla comparativa de los 3 enfoques

| Aspecto | `sdd/` (Manual) | Spec-Kit (GitHub) | OpenSpec (Fission AI) |
|---------|-----------------|-------------------|------------------------|
| **Quién genera** | El humano escribe todo | La IA llena templates vía `/speckit-*` | La IA genera artefactos vía `/opsx:*` |
| **Instalación** | Ninguna (solo crear `.md`) | Python + uv + uvx | Node.js + npm |
| **Complejidad setup** | Cero | Media (uv puede fallar en Windows) | Baja (npm install y listo) |
| **Formato** | Libre (tú decides la estructura) | Formato fijo (templates oficiales) | Formato fijo (proposal/spec/design/tasks) |
| **Constitución** | Sí ([01_constitucion.md](01_constitucion.md)) | Sí (`constitution.md`, formato oficial) | No (usa `config.yaml` con context) |
| **Diagramas Mermaid** | Sí (secuencia, clases, ER) | No (falta según el video) | No |
| **SOLID, ACID, patrones** | Sí (explicados con ejemplos MapaCto) | No (solo si los escribes) | No |
| **Delta specs** | No | No | Sí (ADDED, MODIFIED, REMOVED) |
| **Archivado** | No | No | Sí (`archive/` con fecha) |
| **Given/When/Then** | No | Sí (`spec-template.md`) | Sí (formato BDD) |
| **Paralelización `[P]`** | Sí (manual) | Sí (`tasks-template.md`) | Sí (automático) |
| **Git extension** | No | Sí (`/speckit-git-*`) | No |
| **Analyze/Checklist** | No | Sí (`/speckit-analyze`) | Sí (`/opsx:verify`) |
| **Multiidioma** | Sí (en el idioma que quieras) | No (inglés) | Sí (ES, PT, ZH, JA, FR, DE) |
| **Brownfield** | Sí (funciona con cualquier proyecto) | Limitado | Diseñado para esto |
| **Educativo** | Muy alto (tutorial detallado) | Medio (formato estándar) | Medio (formato estándar) |
| **Reproducible** | No (cada quien escribe diferente) | Sí (templates + slash commands) | Sí (`propose` genera todo igual) |
| **Agentes IA** | Cualquiera (es solo Markdown) | Claude, Copilot, Gemini, +10 | Claude, Copilot, Cursor, +20 |
| **Estrellas GitHub** | N/A | ~5.000 | 30.000+ |
| **Versión** | N/A | 0.7.2 (pre-release) | 1.3.0 (estable) |

### Tabla comparativa: qué tiene cada uno

| Documento/Feature | `sdd/` (Manual) | `.specify/` (Spec-Kit) | `openspec/` (OpenSpec) |
|-------------------|-----------------|------------------------|-------------------------|
| Constitución / reglas globales | ✅ `01_constitucion.md` | ✅ `constitution.md` | ❌ (usa `config.yaml`) |
| Especificación por feature | ✅ `02_especificacion.md` | ✅ `specs/{feature}/spec.md` | ✅ `specs/{dominio}/spec.md` |
| Clarificación / preguntas | ✅ `03_clarificacion.md` | ✅ `/speckit-clarify` | ✅ `/opsx:explore` |
| Plan técnico | ✅ `04_plan.md` | ✅ `specs/{feature}/plan.md` | ✅ `changes/{nombre}/design.md` |
| Tareas ejecutables | ✅ `05_tareas.md` | ✅ `specs/{feature}/tasks.md` | ✅ `changes/{nombre}/tasks.md` |
| Modelo de datos (SQL) | ✅ `data-model.md` | ❌ (se crea manual) | ❌ (se crea manual) |
| Diagramas secuencia (Mermaid) | ✅ `04_plan.md` secc.7 | ❌ | ❌ |
| Diagrama clases (Mermaid) | ✅ `04_plan.md` secc.8 | ❌ | ❌ |
| SOLID explicado con ejemplos | ✅ `01_constitucion.md` | ❌ | ❌ |
| ACID explicado | ✅ `01_constitucion.md` | ❌ | ❌ |
| Patrones de diseño | ✅ `01_constitucion.md` | ❌ | ❌ |
| Delta specs (cambios incrementales) | ❌ | ❌ | ✅ |
| Archivado de cambios | ❌ | ❌ | ✅ |
| Proposal (por qué + alcance) | ❌ | ❌ | ✅ `changes/{}/proposal.md` |
| Given/When/Then (BDD) | ❌ | ✅ | ✅ |
| Git integration (commits/branches) | ❌ | ✅ `/speckit-git-*` | ❌ |
| Guía de instalación | ✅ `06_specify_cli.md` | ✅ `GUIA_SPECKIT.md` | ✅ `07_openspec.md` |

### Ventajas de cada enfoque

**`sdd/` (Manual) — Lo mejor para enseñar**

| Ventaja | Por qué |
|---------|---------|
| Total libertad de formato | Puedes incluir SOLID, ACID, patrones, diagramas, lo que quieras |
| No requiere instalación | Solo Markdown, funciona en cualquier editor |
| Diagramas Mermaid | Ni Spec-Kit ni OpenSpec los generan |
| Contenido educativo | Explicaciones con ejemplos, comparaciones, narrativas |
| Cualquier idioma | Escribes en español directamente |
| Sin dependencia de herramienta | Si Spec-Kit o OpenSpec desaparecen, tu `sdd/` sigue |

**Spec-Kit — Lo mejor para estructura y validación**

| Ventaja | Por qué |
|---------|---------|
| Constitución como concepto formal | Reglas no negociables que la IA respeta |
| Templates estándar | Todos los specs tienen el mismo formato |
| `/speckit-analyze` | Valida que spec, plan y tasks estén alineados |
| `/speckit-checklist` | Genera checklist de calidad automático |
| Git extension | Commits y branches estandarizados |
| Fases claras | Fácil de enseñar: 1.Constitution 2.Specify 3.Plan 4.Tasks 5.Implement |

**OpenSpec — Lo mejor para proyectos existentes**

| Ventaja | Por qué |
|---------|---------|
| Delta specs | Solo documentas **LO QUE CAMBIA**, no reescribes todo |
| `/opsx:propose` | Genera TODO de una vez (proposal + spec + design + tasks) |
| `/opsx:explore` | Piensas la idea antes de comprometerte |
| Archivado | Trazabilidad completa con fechas |
| `npm install` | Fácil de instalar (Node.js es más común) |
| Multiidioma | Specs en español nativo |
| 30.000+ estrellas | Comunidad activa, actualizaciones frecuentes |

### Desventajas de cada enfoque

| Enfoque | Desventaja | Impacto |
|---------|------------|---------|
| Manual (`sdd/`) | No es reproducible (cada quien escribe diferente) | Difícil estandarizar en equipos grandes |
| Manual (`sdd/`) | No tiene validación automática | No sabes si spec y código están alineados |
| Manual (`sdd/`) | Requiere disciplina del humano | Si no escribes, no existe |
| Spec-Kit | No tiene delta specs | Reescribir spec completa para cada cambio |
| Spec-Kit | Pre-release (v0.7.2) | Posibles cambios breaking |
| Spec-Kit | uv puede fallar en Windows | Instalación complicada para estudiantes |
| Spec-Kit | Sin diagramas Mermaid | Falta visual |
| OpenSpec | No tiene constitución | Reglas globales no tienen lugar dedicado |
| OpenSpec | No tiene Git extension | No integra commits |
| OpenSpec | Requiere Node.js 20.19+ | Versión reciente |

### Tabla comparativa general (Spec-Kit vs OpenSpec)

| Aspecto | Spec-Kit (GitHub) | OpenSpec (Fission AI) |
|---------|-------------------|------------------------|
| Repositorio | github/spec-kit | Fission-AI/OpenSpec |
| Estrellas GitHub | ~5.000 | 30.000+ |
| Licencia | Open source | MIT, open source |
| Instalación | Python (uv/uvx) | Node.js (npm) |
| Versión actual | 0.7.2 | 1.3.0 |
| Tipo de proyecto | Greenfield (nuevo) | Brownfield (existente) |
| Agentes soportados | Claude, Copilot, Gemini, +10 | Claude, Copilot, Cursor, OpenCode, +20 |
| Estructura | `.specify/` | `openspec/` |
| Constitución | Sí (`constitution.md`) | No (usa `config.yaml` con context) |
| Delta specs | No | Sí (ADDED, MODIFIED, REMOVED) |
| Archivado | No | Sí (`archive/` con fecha) |
| Schemas custom | No | Sí (`openspec schema init`) |
| Idiomas | Inglés | Multiidioma (ES, PT, ZH, JA, FR, DE) |
| Git extension | Sí (commits, branches) | No (usa git directo) |
| Workflows | Sí (`workflow.yml`) | No |

### Ventajas de Spec-Kit para este proyecto (MapaCto)

| Ventaja | Por qué importa aquí |
|---------|----------------------|
| Constitución | Define reglas no negociables (SOLID, ACID, "todo va por API REST") que la IA no puede violar |
| Templates oficiales | `spec-template.md`, `plan-template.md`, `tasks-template.md` con formato estándar |
| Git extension | Comandos `/speckit-git-commit`, `/speckit-git-feature` útiles para Samuel y Jostin |
| Analyze + Checklist | Valida consistencia entre spec, plan y tasks. Bueno para evaluación |
| Fases claras | Fácil de explicar al profesor en la sustentación |

### Ventajas de OpenSpec para este proyecto (MapaCto)

| Ventaja | Por qué importa aquí |
|---------|----------------------|
| Delta specs | Cuando agreguemos features nuevas (CSV, dashboard, paginación), solo documentamos LO QUE CAMBIA |
| Brownfield | El proyecto MapaCto ya tiene código. OpenSpec está diseñado para esto |
| Archivado | Cada entrega futura queda archivada con fecha. Trazabilidad completa |
| Explore | `/opsx:explore` permite pensar antes de comprometer cambios |
| Más rápido | `/opsx:propose` genera TODO de una vez |
| npm | Samuel y Jostin pueden tener Node.js fácilmente |
| Multiidioma | Specs en español nativo |

---

## 7. Recomendación para este proyecto y similares

### Usar AMBAS herramientas, cada una para lo que es mejor:

| Fase del proyecto | Herramienta | Por qué |
|-------------------|-------------|---------|
| Inicio (greenfield) | Spec-Kit | Constitution + estructura inicial + fases claras |
| Agregar features (brownfield) | OpenSpec | Delta specs + propose rápido + archivado |
| Evaluación | Spec-Kit | Analyze + Checklist para verificar completitud |
| Trabajo en equipo (Samuel + Jostin) | Spec-Kit | Git extension para commits/branches estándar |
| Exploración de ideas | OpenSpec | `/opsx:explore` sin comprometerse |
| Documentación educativa | `sdd/` (manual) | SOLID, ACID, diagramas Mermaid (ninguna herramienta los genera) |

### Flujo recomendado para nuestro proyecto

```
1. Al inicio del proyecto:
   specify init --here --integration claude    <- Spec-Kit: constitution + estructura
   openspec init                               <- OpenSpec: delta specs + changes

2. Para cada feature nueva (ej: exportar CSV):
   /opsx:explore "quiero agregar exportacion CSV en proyecto"  <- OpenSpec: explorar
   /opsx:propose exportar-csv-proyecto         <- OpenSpec: generar artefactos
   (Samuel y Jostin revisan y ajustan)
   /opsx:apply                                 <- OpenSpec: implementar
   /opsx:archive                               <- OpenSpec: archivar + fusionar

3. Para validar (antes de entregar):
   /speckit-analyze                            <- Spec-Kit: consistencia
   /speckit-checklist                          <- Spec-Kit: calidad

4. Para commitear:
   /speckit-git-commit                         <- Spec-Kit: commit estandar
```

### Para proyectos similares (entregas académicas)

| Escenario | Recomendación |
|-----------|---------------|
| Proyecto nuevo, 1 estudiante | Spec-Kit solo (constitution + specs por feature) |
| Proyecto nuevo, 2-3 estudiantes (como nosotros) | Spec-Kit (constitution + git extension) + OpenSpec (delta specs para cada estudiante) |
| Proyecto existente, agregar features | OpenSpec solo (delta specs + propose + archive) |
| Curso de Diseño de Software | Ambas + `sdd/` manual (para enseñar conceptos: SOLID, ACID, patrones, diagramas) |
| Producción real | OpenSpec (brownfield, rápido, multiidioma) |

---

## 8. Qué instalamos en este proyecto

| Herramienta | Versión | Método | Fecha |
|-------------|---------|--------|-------|
| uv | 0.11.7 | `pip install uv` | 2026-05-21 |
| specify-cli (Spec-Kit) | 0.7.2.dev0 | `uvx --from git+...spec-kit specify init` | 2026-05-21 |
| OpenSpec | 1.3.0 | `npm install -g @fission-ai/openspec@latest` | 2026-05-21 |

### Skills de Claude Code instalados

| De Spec-Kit | De OpenSpec |
|-------------|-------------|
| `/speckit-constitution` | `/opsx:explore` |
| `/speckit-specify` | `/opsx:propose` |
| `/speckit-plan` | `/opsx:apply` |
| `/speckit-tasks` | `/opsx:archive` |
| `/speckit-implement` | |
| `/speckit-clarify` | |
| `/speckit-analyze` | |
| `/speckit-checklist` | |
| `/speckit-git-commit` | |
| `/speckit-git-feature` | |

---

## 9. Referencias

- **OpenSpec repo**: [github.com/Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec)
- **OpenSpec guía**: [webreactiva.com/blog/openspec](https://webreactiva.com/blog/openspec)
- **Spec-Kit repo**: [github.com/github/spec-kit](https://github.com/github/spec-kit)
- **Spec-Kit documentación**: [spec-driven.md](https://github.com/github/spec-kit/blob/main/spec-driven.md)
- **Video SDD conceptual**: youtu.be/p2WA672HrdI
- **Video Spec-Kit tutorial**: youtu.be/QzSCmSFKvko
- **Blog Microsoft**: Diving Into SDD
- **Seguridad vibe coding**: Awesome Agents Report

---

## Fecha de ratificación

- **Versión**: 1.0
- **Fecha**: 2026-05-21
- **Autores**: Samuel Giraldo, Jostin (Estudiantes Diseño de Software USB)
- **Referencia OpenSpec**: [github.com/Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec)
- **Referencia Spec-Kit**: [github.com/github/spec-kit](https://github.com/github/spec-kit)

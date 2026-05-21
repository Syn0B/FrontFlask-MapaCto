# Specify CLI - Instalación y Configuración

Este documento registra todo lo que se hizo para instalar y configurar **specify-cli**, la herramienta oficial de GitHub para Spec-Driven Development (SDD).

---

## 1. Qué es specify-cli

Es la **herramienta de línea de comandos** de GitHub Spec-Kit que automatiza y da estructura al Spec Driven Development. Sirve para:

| Función | Qué hace |
|---------|----------|
| **Scaffolding** | Crea la estructura `.specify/` con templates, scripts, constituciones |
| **Guardrails** | Verifica que el código generado cumpla con la constitución |
| **Ciclo de vida** | Permite moverse entre las 5 etapas del SDD con comandos |

**Referencia**: [github.com/github/spec-kit](https://github.com/github/spec-kit)

---

## 2. Prerrequisitos

| Herramienta | Versión instalada | Para qué |
|-------------|-------------------|----------|
| Python | 3.13.0 | Runtime (ya estaba instalado) |
| Git | (ya instalado) | Control de versiones |
| uv | 0.11.7 | Gestor de paquetes Python (se instaló) |
| specify-cli | 0.7.2.dev0 | CLI de Spec-Kit (se instaló vía `uvx`) |

---

## 3. Instalación paso a paso

### 3.1 Instalar `uv` (gestor de paquetes)

```powershell
pip install uv
```

`uv` es el gestor de paquetes recomendado por GitHub para ejecutar specify-cli.
**Referencia**: [docs.astral.sh/uv](https://docs.astral.sh/uv)

### 3.2 Verificar que specify-cli funciona

```powershell
# En Windows, necesita PYTHONIOENCODING=utf-8 por los emojis del banner
$env:PYTHONIOENCODING = "utf-8"
uvx --from git+https://github.com/github/spec-kit.git specify version
```

**Resultado**:

```
CLI Version    0.7.2.dev0
Python         3.13.0
Platform       Windows
Architecture   AMD64
```

### 3.3 Inicializar en el proyecto

```powershell
cd C:\Users\Samue\Desktop\Entrega2-MapaCto\FrontFlask-MapaCto\FrontFlask
$env:PYTHONIOENCODING = "utf-8"
uvx --from git+https://github.com/github/spec-kit.git specify init --here --ai claude --ignore-agent-tools
```

**Opciones usadas**:

- `--here`: inicializar en el directorio actual (no crear subcarpeta)
- `--ai claude`: configurar para Claude Code como agente IA
- `--ignore-agent-tools`: no validar herramientas del agente

> **Nota**: `--ai` está deprecado en favor de `--integration claude` (desde v1.0.0).

---

## 4. Qué generó `specify init`

### 4.1 Estructura de carpetas creada

```
FrontFlask-MapaCto/FrontFlask/
├── .specify/                              <- Carpeta principal de Spec-Kit
│   ├── memory/
│   │   └── constitution.md               <- Plantilla de constitución (por llenar)
│   ├── templates/
│   │   ├── constitution-template.md      <- Template para constituciones
│   │   ├── spec-template.md              <- Template para especificaciones
│   │   ├── plan-template.md              <- Template para planes
│   │   ├── tasks-template.md             <- Template para tareas
│   │   ├── checklist-template.md         <- Template para checklists
│   │   └── agent-file-template.md        <- Template para CLAUDE.md
│   ├── scripts/powershell/
│   │   ├── check-prerequisites.ps1       <- Verificar herramientas
│   │   ├── common.ps1                    <- Funciones compartidas
│   │   ├── create-new-feature.ps1        <- Crear rama feature/
│   │   ├── setup-plan.ps1                <- Configurar plan
│   │   └── update-agent-context.ps1      <- Actualizar contexto del agente
│   ├── extensions/
│   │   └── git/                          <- Extension Git (commits, branches, etc)
│   │       ├── commands/                 <- Comandos git del spec-kit
│   │       └── scripts/                  <- Scripts bash/powershell para git
│   ├── workflows/
│   │   └── speckit/workflow.yml          <- Workflow de Spec-Kit
│   ├── integrations/
│   │   ├── claude.manifest.json          <- Configuracion para Claude Code
│   │   └── claude/scripts/              <- Scripts de integracion con Claude
│   ├── extensions.yml                    <- Registro de extensiones
│   ├── init-options.json                 <- Opciones usadas en init
│   └── integration.json                  <- Integracion activa (claude)
│
├── .claude/skills/                       <- Skills de Claude Code (nuevas)
│   ├── speckit-constitution/SKILL.md     <- /speckit-constitution
│   ├── speckit-specify/SKILL.md          <- /speckit-specify
│   ├── speckit-plan/SKILL.md             <- /speckit-plan
│   ├── speckit-tasks/SKILL.md            <- /speckit-tasks
│   ├── speckit-implement/SKILL.md        <- /speckit-implement
│   ├── speckit-clarify/SKILL.md          <- /speckit-clarify
│   ├── speckit-analyze/SKILL.md          <- /speckit-analyze
│   ├── speckit-checklist/SKILL.md        <- /speckit-checklist
│   ├── speckit-git-commit/SKILL.md       <- /speckit-git-commit
│   ├── speckit-git-feature/SKILL.md      <- /speckit-git-feature
│   ├── speckit-git-initialize/SKILL.md   <- /speckit-git-initialize
│   ├── speckit-git-remote/SKILL.md       <- /speckit-git-remote
│   ├── speckit-git-validate/SKILL.md     <- /speckit-git-validate
│   └── speckit-taskstoissues/SKILL.md    <- /speckit-taskstoissues
│
└── sdd/                                  <- Nuestra documentacion SDD (NO tocada)
    ├── 00_indice.md
    ├── 01_constitucion.md
    ├── 02_especificacion.md
    ├── 03_clarificacion.md
    ├── 04_plan.md
    ├── 05_tareas.md
    └── data-model.md
```

### 4.2 Archivos clave generados

| Archivo | Qué es | Estado |
|---------|--------|--------|
| `.specify/memory/constitution.md` | Plantilla de constitución con placeholders `[PROJECT_NAME]`, `[PRINCIPLE_1_NAME]` | Por llenar (tiene placeholders) |
| `.specify/templates/spec-template.md` | Template para crear especificaciones con User Stories y Given/When/Then | Listo para usar |
| `.specify/templates/plan-template.md` | Template para planes técnicos | Listo para usar |
| `.specify/templates/tasks-template.md` | Template para listas de tareas con marcadores `[P]` | Listo para usar |
| `.specify/init-options.json` | Opciones usadas en `specify init` | Auto-generado |
| `.specify/integration.json` | Integración activa: `claude` | Auto-generado |

---

## 5. Comandos disponibles (skills de Claude Code)

Después de `specify init --ai claude`, Claude Code tiene estos slash commands:

### Comandos principales (ciclo SDD)

| Comando | Fase SDD | Qué hace |
|---------|----------|----------|
| `/speckit-constitution` | Constitución | Establece principios no negociables del proyecto |
| `/speckit-specify` | Especificación | Define requisitos y historias de usuario |
| `/speckit-clarify` | Clarificación | Hace preguntas para resolver ambigüedades |
| `/speckit-plan` | Plan | Crea plan técnico con stack elegido |
| `/speckit-tasks` | Tareas | Genera desglose de tareas ejecutables |
| `/speckit-implement` | Código | Ejecuta las tareas del plan |

### Comandos de mejora (opcionales)

| Comando | Qué hace |
|---------|----------|
| `/speckit-analyze` | Valida consistencia entre artefactos (spec vs plan vs tasks) |
| `/speckit-checklist` | Genera checklists de calidad para validar requisitos |

### Comandos de Git

| Comando | Qué hace |
|---------|----------|
| `/speckit-git-commit` | Commit con mensaje estandarizado |
| `/speckit-git-feature` | Crear rama `feature/` desde spec |
| `/speckit-git-initialize` | Inicializar repo git |
| `/speckit-git-remote` | Configurar remote |
| `/speckit-git-validate` | Validar estado del repo |

### Comando extra

| Comando | Qué hace |
|---------|----------|
| `/speckit-taskstoissues` | Convertir tareas a GitHub Issues |

---

## 6. Comparación: nuestra carpeta `sdd/` vs `.specify/`

Nuestra carpeta `sdd/` se creó **ANTES** de instalar specify-cli. Ambas coexisten. `sdd/` tiene contenido **real** del proyecto MapaCto; `.specify/` tiene **plantillas y herramientas** del CLI.

| Aspecto | `sdd/` (nuestros docs) | `.specify/` (Spec-Kit CLI) |
|---------|------------------------|----------------------------|
| Contenido | Documentación **REAL** del proyecto MapaCto (llena, con datos concretos) | Plantillas con **PLACEHOLDERS** (por llenar) |
| Constitución | [01_constitucion.md](01_constitucion.md) (SOLID, ACID, patrones, stack real) | `memory/constitution.md` (plantilla vacía) |
| Especificación | [02_especificacion.md](02_especificacion.md) (modelo ER, flujos proyecto-producto, ODS, aliados) | `templates/spec-template.md` (formato Given/When/Then) |
| Plan | [04_plan.md](04_plan.md) (diagramas secuencia y clases, 6 Mermaid) | `templates/plan-template.md` (estructura vacía) |
| Tareas | [05_tareas.md](05_tareas.md) (historias Samuel/Jostin, todas completadas) | `templates/tasks-template.md` (formato con `[P]`) |
| Modelo de datos | [data-model.md](data-model.md) (SQL completo PostgreSQL/Neon) | No tiene (se crea por feature) |
| Clarificación | [03_clarificacion.md](03_clarificacion.md) (preguntas resueltas sobre MapaCto) | No tiene (se genera con `/speckit-clarify`) |
| Skills Claude | No aplica | `.claude/skills/speckit-*/SKILL.md` (14 skills) |
| Scripts | No aplica | `.specify/scripts/powershell/` (5 scripts) |
| Git extension | No aplica | `.specify/extensions/git/` (comandos git) |

### Conclusión

La carpeta `sdd/` es la **documentación viva** del proyecto MapaCto — tiene todo el contenido real (proyectos, productos, docentes, ODS, áreas, aliados). La carpeta `.specify/` es la **infraestructura de Spec-Kit** — tiene templates, scripts y skills para crear nuevas features siguiendo el flujo SDD.

Para features futuras, se puede usar `/speckit-specify` que creará una carpeta `.specify/specs/{feature}/` con `spec.md`, `plan.md`, `tasks.md` siguiendo los templates.

---

## 7. Cómo usar specify-cli en el día a día

### Para crear una nueva feature

```powershell
# 1. Iniciar Claude Code en el proyecto
# 2. Usar el slash command:
/speckit-specify   # Describe la feature, Claude genera spec.md
/speckit-plan      # Claude genera plan tecnico
/speckit-tasks     # Claude genera lista de tareas
/speckit-implement # Claude ejecuta las tareas
```

### Para validar consistencia

```powershell
/speckit-analyze   # Revisa que spec, plan y tasks esten alineados
/speckit-checklist # Genera checklist de calidad
```

### Para crear rama y commit

```powershell
/speckit-git-feature  # Crea rama feature/ desde la spec
/speckit-git-commit   # Commit con mensaje estandarizado
```

---

## 8. Referencias

- **Repositorio oficial**: [github.com/github/spec-kit](https://github.com/github/spec-kit)
- **Documentación SDD**: [spec-driven.md](https://github.com/github/spec-kit/blob/main/spec-driven.md)
- **Guía instalación**: [github.github.com/spec-kit/installation.html](https://github.github.com/spec-kit/installation.html)
- **Blog Microsoft**: [Diving Into SDD With Spec Kit](https://devblogs.microsoft.com/blog/spec-driven-development-spec-kit)
- **Paquete npm**: [@spec-kit/cli](https://www.npmjs.com/package/@spec-kit/cli)
- **Video SDD**: La forma CORRECTA de programar con IA en 2026
- **Video tutorial**: GitHub Spec Kit - Tutorial Completo con ejemplo
- **DeepWiki**: Instalación Spec-Kit

---

## 9. Documentación generada con Spec-Kit (llenada)

Después de `specify init`, las plantillas estaban vacías (con placeholders). Se llenaron manualmente con los datos reales del proyecto MapaCto, siguiendo el formato oficial de Spec-Kit.

### Archivos llenados

| Archivo | Estado anterior | Estado actual |
|---------|-----------------|---------------|
| `.specify/memory/constitution.md` | Placeholders `[PROJECT_NAME]`, `[PRINCIPLE_1]` | Lleno: 6 principios (API-First, Descubrimiento Dinámico, Seguridad 3 Capas, SOLID, ACID, Simplicidad) + stack + convenciones + prohibiciones + patrones |
| `.specify/specs/001-proyecto-maestro-detalle/spec.md` | No existía | Creado: User Stories del CRUD proyecto + productos con SPs (Given/When/Then) |
| `.specify/specs/001-proyecto-maestro-detalle/plan.md` | No existía | Creado: arquitectura SPs, ejecutar_sp en ApiService, atomicidad de transacción |
| `.specify/specs/001-proyecto-maestro-detalle/tasks.md` | No existía | Creado: tareas Samuel para SPs + frontend, todas completadas |
| `.specify/specs/002-login-control-acceso/spec.md` | No existía | Creado: 5 User Stories (login, control acceso por roles Admin/EncargadoProyectos/Visitante, JWT, cambiar pwd, restablecer pwd) |
| `.specify/specs/002-login-control-acceso/plan.md` | No existía | Creado: arquitectura, componentes, endpoints, security design, rationale |
| `.specify/specs/002-login-control-acceso/tasks.md` | No existía | Creado: tareas por story con `[P]`, todas completadas, validación final |

### Relación entre `sdd/` y `.specify/`

```
sdd/                                    .specify/
(creado ANTES de instalar CLI)          (creado por specify init + llenado despues)
(formato libre, contenido extenso)      (formato Spec-Kit oficial)

01_constitucion.md            <->  memory/constitution.md (formato oficial)
02_especificacion.md          <->  specs/002-login/spec.md (Given/When/Then)
03_clarificacion.md                (no tiene equivalente directo)
04_plan.md (diagramas Mermaid)<->  specs/002-login/plan.md (formato oficial)
05_tareas.md                  <->  specs/002-login/tasks.md (formato oficial)
data-model.md (SQL Neon)           (no tiene equivalente - se crea por feature)
06_specify_cli.md (ESTE archivo)   (no tiene equivalente)
```

`sdd/` tiene contenido más extenso y educativo (con SOLID, ACID, diagramas Mermaid de MapaCto). `.specify/` tiene contenido en formato estándar de Spec-Kit (Given/When/Then, componentes, rationale).

**Ambas carpetas coexisten y se complementan. Ninguna se borra.**

---

## 10. Diagramas Mermaid (mejora sobre Spec-Kit)

Según el video *GitHub Spec Kit - Tutorial Completo*:

> *"Como algo malo [de Spec-Kit] es quizá la falta de uso de Mermaid. En mis proyectos siempre tengo un diagrama entidad-relación para facilitarle a la IA que entienda la estructura de mi base de datos, así como diagramas de secuencia para que entienda la arquitectura o un diagrama de flujo para los flujos."*

En este proyecto **SÍ** incluimos diagramas Mermaid (en [sdd/04_plan.md](04_plan.md)):

- **6 diagramas de secuencia** (login, CRUD listar, crear proyecto con SP, acceso denegado, cambiar contraseña, restablecer contraseña)
- **1 diagrama de clases** (`ApiService`, `AuthService`, `BlueprintProyecto`, `BlueprintCatalogo`, `BlueprintNM`, `BlueprintAuth`, `Middleware`)
- **Diagrama ER** en [sdd/data-model.md](data-model.md)

Esto complementa lo que Spec-Kit no incluye por defecto.

---

## 11. Fecha y versión

- **Fecha de instalación**: 2026-05-21
- **specify-cli versión**: 0.7.2.dev0
- **uv version**: 0.11.7
- **Python**: 3.13.0
- **Plataforma**: Windows 10 Pro (AMD64)
- **Integración**: Claude Code
- **Script type**: PowerShell
- **Autores**: Samuel Giraldo, Jostin

---

## Fecha de ratificación

- **Versión**: 1.0
- **Fecha**: 2026-05-21
- **Autores**: Samuel Giraldo, Jostin (Estudiantes Construcción de Software USB)
- **Referencia Spec-Kit**: [github.com/github/spec-kit](https://github.com/github/spec-kit)

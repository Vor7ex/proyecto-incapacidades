# 🏥 Sistema de Gestión de Incapacidades

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![Estado](https://img.shields.io/badge/Estado-En%20Desarrollo-yellow.svg)](docs/GUIA_COMPLETA.md)
[![Licencia](https://img.shields.io/badge/Licencia-MIT-yellow.svg)](LICENSE)

Sistema web para la gestión digital de incapacidades médicas de empleados, desarrollado con Flask. Incluye validación automática de documentos por tipo, notificaciones inteligentes, scheduler de recordatorios y gestión de estados con máquina de transiciones.

**🚀 Release 1.0 en desarrollo** | **16 Casos de Uso** | **3 UC Completados al 100%, 5 UC Funcionales (50-95%), 8 UC Planificados**

---

## 📚 Documentación

La documentación completa está organizada en la carpeta [`/docs`](docs/):

| Documento | Descripción | Para quién |
|-----------|-------------|------------|
| **[📘 GUIA_COMPLETA.md](docs/GUIA_COMPLETA.md)** | Guía principal del sistema | 👨‍💻 Desarrolladores, PM |
| **[⚙️ CONFIGURACION_TECNICA.md](docs/CONFIGURACION_TECNICA.md)** | Setup y deployment completo | 🔧 DevOps, SysAdmins |
| **[📖 MANUAL_USUARIO.md](docs/MANUAL_USUARIO.md)** | Guía paso a paso | 👥 Usuarios finales |
| **[📄 CASOS_DE_USO.md](docs/CASOS_DE_USO.md)** | 16 UC detallados | 📋 Analistas, QA |


> 💡 **¿Nuevo en el proyecto?** Comienza con [GUIA_COMPLETA.md](docs/GUIA_COMPLETA.md)

---

## 📊 Estado del Proyecto

| UC | Caso de Uso | Estado | Descripción |
|----|------------|--------|-------------|
| **UC1** | **Registrar incapacidad** | **✅ 100%** | **Flujo completo con todas las excepciones (E1-E6) + UI moderna** |
| **UC2** | **Notificar RRHH** | **✅ 100%** | **Email automático + notificaciones internas + reintentos (E1-E4)** |
| UC3 | Consultar incapacidades | ⚠️ 70% | Vista moderna con cards, estadísticas y acciones contextuales |
| UC4 | Validar documentación | ⚠️ 80% | Panel funcional, falta manejo de E2-E5 y validación manual |
| **UC5** | **Verificar requisitos por tipo** | **✅ 100%** | **Validación automática completa con todas las excepciones** |
| **UC6** | **Solicitar documentos faltantes** | **✅ 95%** | **Funcional con recordatorios + UI moderna, falta E2 y E4** |
| UC7 | Aprobar/Rechazar | ⚠️ 85% | Aprobación/rechazo funcional, faltan motivos predefinidos y E3 |
| UC8 | Actualizar estado | ⚠️ 70% | Cambios automáticos + historial con timeline moderna |
| UC9 | Consultar estado radicación | 🔴 0% | Release 2.0 - No implementado |
| UC10 | Generar reporte seguimiento | 🔴 0% | Release 2.0 - No implementado |
| UC11 | Ver incapacidades del equipo | 🔴 0% | Release 2.0 - No implementado |
| UC12 | Registrar pago EPS/ARL | 🔴 0% | Release 3.0 - No implementado |
| UC13 | Conciliar pagos mensualmente | 🔴 0% | Release 3.0 - No implementado |
| UC14 | Generar reporte pagos pendientes | 🔴 0% | Release 3.0 - No implementado |
| UC15 | Almacenar documentos | ⚠️ 90% | Almacenamiento seguro implementado, faltan cifrado y E4 |
| UC16 | Descargar incapacidad completa | ⚠️ 15% | Solo descarga individual, falta ZIP organizado y permisos |

### 🎯 Casos de Uso Destacados

#### UC5 - Verificar requisitos por tipo ✅ COMPLETADO 100%
**Sistema inteligente de validación automática según tipo de incapacidad**

- ✅ Servicio `ValidadorRequisitos` robusto (494 líneas, 19 tests unitarios)
- ✅ Reglas condicionales dinámicas por tipo:
  - **Enfermedad General**: Certificado + Epicrisis (solo si días > 2)
  - **Accidente Laboral**: Certificado + Epicrisis obligatorios
  - **Accidente de Tránsito**: Certificado + Epicrisis + FURIPS
  - **Licencia Maternidad**: Certificado + Cert. Nacido Vivo + Registro Civil + Doc. Identidad
  - **Licencia Paternidad**: + Documento Identidad Madre con descripción específica
- ✅ API REST dinámica `/incapacidades/api/documentos-requeridos/<tipo>?dias=X`
- ✅ Integración completa con UC1 (registro) y UC4 (validación)
- ✅ Manejo robusto de excepciones E1 y E2 con fallbacks automáticos
- ✅ Logging detallado para auditoría y troubleshooting

#### UC6 - Solicitud de documentos faltantes ✅ 95% FUNCIONAL
**Sistema automatizado de gestión de documentos pendientes**

- ✅ Scheduler automático con APScheduler (tareas diarias 08:00 AM)
- ✅ Sistema de recordatorios escalados (Día 3: amable, Día 6: urgente)
- ✅ 4 templates HTML profesionales y responsivos para emails
- ✅ Gestión completa de estados con transiciones automáticas
- ✅ Suite de 9 tests automatizados (100% passing)
- ✅ Panel dedicado para carga de documentos solicitados
- ✅ Validación automática post-carga que actualiza estados
- ⚠️ **Pendiente**: Reinicio de solicitud (E2) y extensión manual de plazos (E4)

#### UC2 - Notificar RRHH ✅ 100% IMPLEMENTADO
**Sistema integral de notificaciones por email y notificaciones internas**

- ✅ Envío automático de emails a colaborador y Gestión Humana (pasos 4-5)
- ✅ Creación de notificaciones internas en BD (pasos 6-7)
- ✅ Sistema de reintentos automático (E3): 3 intentos con intervalos de 5 minutos
- ✅ Validación de formato de email (E2): fallback a notificaciones internas
- ✅ Notificación a administrador si no hay usuarios RRHH activos (E4)
- ✅ Registro detallado de logs (paso 8): timestamp, destinatarios, éxito/error
- ✅ Marcado de notificaciones como enviadas/entregadas (paso 9)
- ✅ Template de email para administrador (sin usuarios RRHH)
- ✅ Fallback de email_notificaciones a email de login (E1 implícito)
- ✅ 16 tests unitarios (100% passing)

#### UC1 - Registrar incapacidad ✅ 100% IMPLEMENTADO
**Flujo principal y excepciones completas**

- ✅ Formulario completo con 5 tipos de incapacidad
- ✅ Validación de formato de datos (tipo, fechas, formato archivos)
- ✅ Cálculo automático de días entre fechas
- ✅ Generación de código de radicación único
- ✅ Almacenamiento transaccional (incapacidad + documentos)
- ✅ Integración con UC5 (validación automática de requisitos)
- ✅ Integración con UC2 (notificaciones automáticas)
- ✅ **E1**: Documentos incompletos - Validación opcional (UC6)
- ✅ **E2**: Formato de archivo inválido - Mensaje específico
- ✅ **E3**: Archivo >10MB - Mensaje detallado con sugerencias
- ✅ **E4**: Fechas inválidas - Validación completa
- ✅ **E5**: Sesión expirada - Borrador automático en localStorage
- ✅ **E6**: Pérdida de conexión - Guardado local y recuperación automática

#### UC3 - Consultar incapacidades ⚠️ 70% IMPLEMENTADO
**Vista moderna con cards y acciones contextuales**

- ✅ Listado de incapacidades del colaborador ordenado por fecha
- ✅ **UI modernizada** con cards, gradientes y animaciones
- ✅ **Estadísticas rápidas** visuales (Total, Pendientes, Aprobadas, Rechazadas)
- ✅ Visualización de: código, tipo, fechas, días, estado
- ✅ Acceso a detalle de cada incapacidad
- ✅ **Indicadores visuales** según estado con badges modernos y colores
- ✅ **Botones contextuales** por estado:
  - "Cargar Documentos" para DOCUMENTACION_INCOMPLETA (UC6)
  - "Ver Detalles" para todas las incapacidades
  - Estados visuales distintos (Pendiente, En Revisión, Aprobada, Rechazada)
- ✅ **Empty state** ilustrado cuando no hay incapacidades
- ✅ **Diseño responsive** con grid adaptativo
- ⚠️ **Pendiente**: 
  - Filtros por fecha, tipo y estado (paso 3 del flujo)
  - Paginación de resultados (paso 2 menciona "paginada")
  - Descarga individual de documentos (paso 5)
  - Descarga completa en ZIP (paso 5)
  - Manejo de excepciones E1, E2, E3

#### UC15 - Almacenar documentos ⚠️ 90% IMPLEMENTADO
**Sistema de almacenamiento seguro con metadatos completos**

- ✅ Generación de UUID único por documento
- ✅ Cálculo de hash MD5 para verificación de integridad
- ✅ Estructura organizada `/año/mes/tipo_documento/colaborador_id/UUID.ext`
- ✅ Registro en BD con metadata: nombre, ruta, tamaño, tipo, hash, fecha, usuario
- ✅ Permisos de acceso según rol
- ✅ Generación de miniaturas para imágenes
- ✅ Logging de operaciones de almacenamiento
- ✅ Manejo de excepciones E1 (espacio insuficiente), E2 (error escritura), E3 (corrupto)
- ⚠️ **Pendiente**: 
  - Cifrado adicional para documentos sensibles (epicrisis, historia clínica) - paso 9
  - Respaldo automático en almacenamiento secundario (pasos 11-12)
  - Detección de duplicados E4 con confirmación
  - Manejo de fallo en respaldo E5

---

## 🏗️ Arquitectura del Sistema

### 📁 Estructura del Proyecto

```
proyecto-incapacidades/
├── app/                        # Aplicación principal
│   ├── models/                 # Modelos SQLAlchemy
│   │   ├── incapacidad.py     # Modelo principal de incapacidad
│   │   ├── documento.py       # Documentos adjuntos
│   │   ├── usuario.py         # Gestión de usuarios
│   │   └── ...
│   ├── routes/                # Endpoints Flask
│   │   ├── incapacidades.py   # Rutas principales + API UC5
│   │   ├── auth.py           # Autenticación
│   │   └── documentos.py     # Gestión de archivos
│   ├── services/              # Lógica de negocio
│   │   ├── validacion_requisitos_service.py  # 🎯 UC5 Core
│   │   └── solicitud_documentos_service.py   # 🎯 UC6 Core
│   ├── templates/             # Templates Jinja2
│   │   ├── incapacidades/
│   │   │   └── crear.html     # 🎯 UI Dinámica UC1+UC5
│   │   └── emails/            # Templates de email UC6
│   ├── tasks/                 # Tareas automatizadas
│   │   └── scheduler_uc6.py   # 🎯 Scheduler UC6
│   └── utils/                 # Utilidades
├── docs/                      # Documentación completa
├── tests/                     # Suite de tests
└── migrations/               # Migraciones BD
```

### 🔧 Stack Tecnológico

| Componente | Tecnología | Versión | Propósito |
|------------|------------|---------|-----------|
| **Backend** | Flask | 3.0.0 | Framework web principal |
| **ORM** | SQLAlchemy | 2.0+ | Mapeo objeto-relacional |
| **Base de Datos** | SQLite/PostgreSQL | - | Almacenamiento persistente |
| **Frontend** | Bootstrap | 5.3.0 | Framework CSS/JS responsive |
| **UI/UX** | Custom CSS + Gradients | - | Diseño moderno con animaciones |
| **Scheduler** | APScheduler | 3.10+ | Tareas automatizadas |
| **Email** | Flask-Mail | - | Sistema de notificaciones |
| **Testing** | Unittest | Python std | Tests automatizados |

### 🎨 Sistema de Diseño Moderno

El proyecto implementa un **sistema de diseño consistente y moderno** en todos los templates:

**Características del UI:**
- ✅ **Gradientes modernos** en todos los componentes principales
- ✅ **Animaciones fluidas**: fadeInUp, slideInLeft, fadeInScale, pulse, shake
- ✅ **Paleta de colores coherente**:
  - Azul (#3b82f6 → #2563eb) - Acciones principales
  - Naranja (#f59e0b → #d97706) - Advertencias y alertas
  - Verde (#10b981 → #059669) - Confirmaciones y éxito
  - Rojo (#ef4444 → #dc2626) - Errores y rechazos
  - Púrpura (#8b5cf6 → #7c3aed) - Historial y auditoría
- ✅ **Responsive design** con breakpoints optimizados
- ✅ **Transiciones suaves** (0.3s ease) en todos los elementos interactivos
- ✅ **Sombras y efectos hover** para mejor feedback visual
- ✅ **Espaciado consistente** con padding-bottom en contenedores principales

**Templates modernizados:**
- ✅ `crear.html` - Formulario de registro con UI dinámica (~2400 líneas)
- ✅ `mis_incapacidades.html` - Listado con cards modernos
- ✅ `dashboard_auxiliar.html` - Dashboard con estadísticas visuales
- ✅ `detalle_incapacidad.html` - Vista detallada con iconos y badges
- ✅ `notificaciones.html` - Sistema de notificaciones con filtros (~1070 líneas)
- ✅ `cargar_documentos_solicitados.html` - Panel de carga con timeline (~1080 líneas)
- ✅ `historial_estados.html` - Timeline vertical con auditoría completa
- ✅ `base.html` - Dropdown de notificaciones modernizado (400px, sin scroll horizontal)

**Componentes reutilizables:**
- Breadcrumbs modernos con gradientes
- Cards con hover effects y animaciones
- Badges con gradientes por estado
- Botones con efectos de onda
- Formularios con validación visual
- Timeline vertical para historial
- Empty states ilustrados
- Loaders y spinners animados

---

## ⚡ Funcionalidades Principales

### 🔐 Sistema de Autenticación
- **Login seguro** con validación de credenciales
- **Roles diferenciados**: Empleados, Auxiliares Administrativos, RRHH
- **Sesiones persistentes** con Flask-Login
- ⚠️ **Pendiente**: Logout automático por inactividad

### 📝 Gestión de Incapacidades
- **Registro completo (UC1)** con UI dinámica modernizada (~2400 líneas)
- **Tipos soportados**: Enfermedad General, Accidente Laboral, Accidente de Tránsito, Licencias de Maternidad/Paternidad
- **Cálculo automático** de días de incapacidad con validación
- **Código de radicación** único por incapacidad (formato: INC-YYYYMMDD-XXXX)
- **UI adaptativa** que muestra documentos requeridos según tipo seleccionado
- **Sistema de borradores** automático con localStorage (cada 30s)
- **Recuperación offline** ante pérdida de conexión
- **Validación completa** de formatos, tamaños y fechas

### 📄 Gestión Inteligente de Documentos
- **Validación automática UC5** según tipo y condiciones (100% completo)
- **Carga múltiple** de archivos con validación de formato
- **Metadatos completos** (UUID, hash MD5, tamaño, tipo, fecha, usuario)
- **Almacenamiento estructurado** con organización por año/mes/tipo/colaborador
- **Permisos por rol** para control de acceso
- ⚠️ **Pendiente**: Vista previa de documentos, cifrado de docs sensibles, respaldos automáticos

### 🔔 Sistema de Notificaciones
- **Notificaciones UC2** por email con templates HTML (100% completo)
- **Sistema UC6** de solicitud de documentos automatizado (95% completo)
- **Scheduler inteligente** con recordatorios escalados (Día 3, Día 6)
- **Estados dinámicos** que se actualizan automáticamente
- **Panel moderno** para carga de documentos solicitados
- **Dropdown de notificaciones** en navbar (400px, sin scroll horizontal)
- **Página de notificaciones** con filtros por estado y orden (~1070 líneas)
- **Notificaciones internas** en base de datos con contador en tiempo real
- ⚠️ **Pendiente**: Reinicio de solicitudes (E2), extensión manual de plazos (E4)

### 📊 Dashboards por Rol
- **Empleados**: Listado modernizado de incapacidades con:
  - Cards con gradientes y animaciones
  - Estadísticas visuales rápidas (Total, Pendientes, Aprobadas, Rechazadas)
  - Botones contextuales según estado
  - Vista de detalle completa con historial
  - Empty states ilustrados
- **Auxiliares**: Dashboard con estadísticas y panel de validación:
  - Contadores animados de incapacidades por estado
  - Listado de pendientes con acciones rápidas
  - Vista de detalle con información completa
  - Acceso al historial de estados con timeline moderna
- **Sistema de diseño consistente** en todos los módulos
- ⚠️ **Pendiente**: Filtros avanzados, búsqueda, paginación, reportes gráficos, vista para líderes

---

## 🚀 Inicio Rápido

### 1. Instalación

```bash
# Clonar repositorio
git clone <repo-url>
cd proyecto-incapacidades

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configuración

```bash
# Crear archivo de configuración
copy config.py.template config.py

# Configurar base de datos y email en config.py
# Ver docs/CONFIGURACION_TECNICA.md para detalles
```

### 3. Inicialización

```bash
# Crear usuarios de prueba
python crear_usuarios.py

# Ejecutar aplicación
python run.py
```

### 4. Acceso al Sistema

- **URL**: `http://localhost:5000`
- **Usuario Colaborador**: `empleado@test.com` / `123456`
- **Usuario Auxiliar**: `auxiliar@test.com` / `123456`

---

## 🧪 Testing

El proyecto incluye una suite de tests automatizados enfocada en componentes críticos:

```bash
# Ejecutar todos los tests
python -m pytest tests/ -v

# Tests UC1 (100% cobertura)
python -m unittest tests.test_uc1_excepciones -v

# Tests UC2 (100% cobertura)
python -m unittest tests.test_uc2_notificaciones -v

# Tests específicos UC5 (100% cobertura)
python -m pytest tests/test_validacion_requisitos.py -v

# Tests específicos UC6 (95% cobertura)
python -m pytest tests/test_notificaciones_uc6.py -v
python -m pytest tests/test_solicitud_documentos_service.py -v
python -m pytest tests/test_uc6_completo_e2e.py -v

# Tests de integración
python -m pytest tests/test_integracion_e2e.py -v
python -m pytest tests/test_integracion_uc1_uc5.py -v

# Tests de utilidades
python -m pytest tests/test_maquina_estados.py -v
python -m pytest tests/test_codigo_radicacion.py -v
python -m pytest tests/test_calendario.py -v
```

**Cobertura de Testing:**
- ✅ **UC1**: 100% (19 tests - registro completo con excepciones E1-E6)
- ✅ **UC2**: 100% (16 tests - notificaciones email e internas con E1-E4)
- ✅ **UC5**: 100% (19 tests - validación de requisitos)
- ✅ **UC6**: 95% (9 tests - solicitud de documentos y recordatorios)
- ✅ **Utilidades**: 100% (máquina de estados, calendario, código radicación)
- ✅ **Integración UC1+UC5**: 100% (flujo completo de registro con validación)
- ⚠️ **UC3, UC4, UC7**: Tests parciales (flujos principales, faltan excepciones)
- 🔴 **UC3, UC8, UC15, UC16**: Sin tests automatizados

**Nota**: La cobertura global del proyecto es aproximadamente 70%. Los componentes críticos (UC1, UC2, UC5, UC6, utilidades) tienen 100% de cobertura.

---

## ⚠️ Limitaciones Conocidas y Trabajo Pendiente

### 📋 UC1 - Registrar Incapacidad (100%) ✅
**Implementado:**
- ✅ Flujo normal completo (12 pasos)
- ✅ **E1**: Documentos incompletos - Permitido (UC6 posterior)
- ✅ **E2**: Formato inválido - Mensaje específico por tipo
- ✅ **E3**: Archivo >10MB - Validación frontend y backend con sugerencias
- ✅ **E4**: Fechas inválidas - Validación completa de rangos
- ✅ **E5**: Sesión expirada - Borrador automático cada 30s en localStorage
- ✅ **E6**: Pérdida de conexión - Guardado offline y recuperación automática
- ✅ Integración con UC2, UC5, UC15
- ✅ Tests completos (15 tests unitarios)

### 📧 UC2 - Notificar RRHH (100%) ✅
**Implementado:**
- ✅ Flujo normal completo (9 pasos)
- ✅ Envío de emails a colaborador y Gestión Humana
- ✅ Creación de notificaciones internas en BD (pasos 6-7)
- ✅ Registro detallado de logs (paso 8)
- ✅ Marcado de notificaciones como entregadas (paso 9)
- ✅ **E1**: Líder no asignado - Notifica solo a RRHH (fallback automático)
- ✅ **E2**: Email inválido - Solo envía notificación interna
- ✅ **E3**: Error en servidor de correo - Reintentos automáticos (3x, 5min)
- ✅ **E4**: Sin usuarios RRHH - Notifica a administrador
- ✅ Integración completa con UC1 (registro)
- ✅ Tests completos (16 tests unitarios)

### 🔍 UC3 - Consultar Incapacidades (70%)
**Implementado:**
- ✅ Listado básico con código, tipo, fechas, días, estado
- ✅ **UI modernizada** con sistema de diseño consistente
- ✅ **Estadísticas visuales** en cards (Total, Pendientes, Aprobadas, Rechazadas)
- ✅ Cards de incapacidad con gradientes y animaciones
- ✅ Acceso a detalle de incapacidad con botón "Ver Detalles"
- ✅ **Indicadores visuales** por estado con badges modernos
- ✅ **Botones contextuales** según estado (ej: "Cargar Documentos" si está incompleta)
- ✅ Empty state ilustrado cuando no hay incapacidades
- ✅ Diseño responsive con grid adaptativo

**Pendiente:**
- ❌ **Paso 3**: Filtros por fecha, tipo y estado
- ❌ **Paso 2**: Paginación de resultados
- ❌ **Paso 5**: Descarga individual y en ZIP de documentos
- ❌ **E1-E3**: Todas las excepciones

### ✅ UC4 - Validar Documentación (80%)
**Implementado:**
- ✅ Panel de validación con listado
- ✅ Visualización de documentos adjuntos
- ✅ Integración con UC5 (checklist automático)
- ✅ Cambio de estado a "Documentación Completa"
- ✅ Integración con UC7

**Pendiente:**
- ❌ **Paso 6**: Checklist de verificación manual (coherencia fechas/días)
- ❌ **E2-E5**: Manejo de documentos ilegibles, información incoherente, certificado no original

### 🎯 UC5 - Verificar Requisitos (100%) ✅
**Completamente implementado** según especificación

### 📨 UC6 - Solicitar Documentos (95%)
**Implementado:**
- ✅ Todo el flujo normal (11 pasos)
- ✅ Scheduler automático
- ✅ Recordatorios escalados
- ✅ Templates de email profesionales
- ✅ **UI modernizada** para panel de carga (~1080 líneas)
- ✅ **Timeline visual** con estados por documento
- ✅ **Indicadores de urgencia** con colores (danger, warning, info)
- ✅ **Validación en tiempo real** de archivos
- ✅ **Feedback visual** con animaciones y previews
- ✅ E1 y E3 implementadas

**Pendiente:**
- ❌ **E2**: Reinicio de UC6 con nuevo plazo si documentos siguen incompletos
- ❌ **E4**: Extensión manual de plazo por auxiliar con motivo justificado

### ✔️ UC7 - Aprobar/Rechazar (85%)
**Implementado:**
- ✅ Flujo de aprobación completo
- ✅ Flujo de rechazo con observaciones
- ✅ Cambios de estado
- ✅ Notificaciones al colaborador

**Pendiente:**
- ❌ **Paso 3 (rechazo)**: Lista predefinida de motivos de rechazo
- ❌ **E1**: Notificación adicional a coordinación y área jurídica en caso de falsificación
- ❌ **E3**: Aprobación con observaciones especiales para transcripción

### 🔄 UC8 - Actualizar Estado (70%)
**Implementado:**
- ✅ Cambios automáticos de estado (desde UC4, UC6, UC7)
- ✅ Registro completo en historial de estados
- ✅ **Vista de historial modernizada** con timeline vertical
- ✅ **UI profesional** con gradientes púrpuras y animaciones
- ✅ Acceso al historial desde detalle de incapacidad
- ✅ Información completa: usuario, fecha/hora, estados anterior/nuevo, observaciones
- ✅ Timeline con badges circulares y línea conectora con gradiente
- ✅ Cards de cambio con hover effects
- ✅ Empty state ilustrado si no hay cambios

**Pendiente:**
- ❌ **Pasos 1-6**: Interfaz manual para auxiliar (actualización manual)
- ❌ **Pasos 7-10**: Campos específicos por estado (causal rechazo, valor pago)
- ❌ **Validación de transiciones** (E1)
- ❌ **Campos obligatorios** por estado (E2, E3)

### 📦 UC15 - Almacenar Documentos (90%)
**Implementado:**
- ✅ Pasos 1-8 (UUID, hash, estructura, permisos)
- ✅ Paso 10 (miniaturas)
- ✅ Paso 13 (confirmación)
- ✅ E1, E2, E3 implementadas

**Pendiente:**
- ❌ **Paso 9**: Cifrado adicional para documentos sensibles
- ❌ **Pasos 11-12**: Respaldo automático en almacenamiento secundario
- ❌ **E4**: Detección y confirmación de duplicados
- ❌ **E5**: Manejo de fallo en respaldo con reintento

### 📥 UC16 - Descargar Incapacidad (15%)
**Implementado:**
- ✅ Descarga individual de documentos (pasos 1-8 flujo individual)

**Pendiente:**
- ❌ **Flujo ZIP completo** (pasos 1-10 del flujo alterno)
- ❌ **Estructura organizada** con subcarpetas
- ❌ **Archivo info.txt** con metadatos
- ❌ **Validación de permisos** por rol (E1, E6)
- ❌ **Todas las excepciones** (E2-E5)

---

---

## 📈 Roadmap

### ✅ Completado al 100% (Release 1.0)
- **UC1**: Registro de incapacidades con todas las excepciones (19 tests)
- **UC2**: Notificaciones email e internas con reintentos y excepciones (16 tests)
- **UC5**: Verificación automática de requisitos (494 líneas, 19 tests)

### 🚧 En Desarrollo Activo (Release 1.0 - 70-95%)
- **UC6**: Solicitud automatizada de documentos (95% - falta manejo excepciones E2/E4) + UI moderna
- **UC15**: Almacenamiento de documentos (90% - falta cifrado para docs sensibles)
- **UC7**: Aprobar/Rechazar (85% - falta lista motivos predefinidos)
- **UC4**: Validar documentación (80% - falta validación manual detallada)
- **UC3**: Consultar incapacidades (70% - faltan filtros, búsqueda y paginación) + UI moderna
- **UC8**: Actualizar estado (70% - cambios automáticos + historial visual completo)

### ⏸️ Implementación Parcial (Release 1.0 - <50%)
- **UC16**: Descargar incapacidad (15% - solo individual, falta ZIP organizado)

### 🔄 Planificado (Release 2.0)
- Completar UC3-UC4, UC6-UC8 al 100%
- UC9: Consultar estado radicación (dashboard de seguimiento)
- UC10: Generar reportes seguimiento (con gráficos y métricas)
- UC11: Ver incapacidades del equipo (vista para líderes)
- UC16: Descargar paquete completo (ZIP con estructura organizada)

### 🔮 Planificado (Release 3.0)
- UC12-UC14: Módulo de conciliación y pagos completo
- Dashboard analítico con métricas avanzadas
- API REST completa para integraciones externas
- Módulo móvil responsive (PWA)
- Integración con LDAP/Active Directory
- Sistema de alertas proactivas
- Módulo de reportes personalizables

---

## 🤝 Contribución

Este proyecto sigue las mejores prácticas de desarrollo:

- **Código limpio** con documentación inline
- **Tests automatizados** para cada funcionalidad
- **Commits descriptivos** siguiendo convenciones
- **Documentación actualizada** en `/docs`

Para contribuir, revisa [docs/GUIA_COMPLETA.md](docs/GUIA_COMPLETA.md) y los estándares de código.

---

## 📞 Soporte

- **Documentación**: [`/docs`](docs/)
- **Issues**: Repositorio del proyecto
- **Logs**: `instance/logs/` para troubleshooting

---

**🏥 Sistema de Gestión de Incapacidades** - Digitalizando y automatizando la gestión de incapacidades médicas con inteligencia y eficiencia.
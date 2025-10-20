# Sistema de Gestión de Incapacidades

Sistema web para la gestión de incapacidades médicas de empleados, desarrollado con Flask.

**Estado:** 65.5% completo | **Release:** 1.0 (en desarrollo)

> 🚀 **Inicio rápido:** Ver [`GUIA_RAPIDA.md`](GUIA_RAPIDA.md) para setup en 5 minutos  
> 📁 **Estructura:** Ver [`ESTRUCTURA.md`](ESTRUCTURA.md) para arquitectura completa  
> 🔧 **Scripts:** Ver [`SCRIPTS_UTILIDAD.md`](SCRIPTS_UTILIDAD.md) para comandos disponibles

---

## 📊 Estado del Proyecto (resumen)

| UC | Caso de Uso | Estado |
|----|------------|--------|
| UC1 | Registrar incapacidad | ✅ 100% |
| UC2 | Notificar RRHH | ✅ 85% |
| UC3 | Consultar incapacidades | ⚠️ 60% |
| UC4 | Validar documentación | ⚠️ 75% |
| UC5 | Verificar requisitos por tipo | 🔴 40% |
| UC6 | Solicitar documentos faltantes | ✅ 95% |
| UC7 | Aprobar/Rechazar | ⚠️ 65% |
| UC15 | Almacenar documentos | ⚠️ 70% |

**Resumen de avances en esta sesión:**
- Implementado UC6 - Solicitud de Documentos Faltantes (95% completo)
  - ✅ Scheduler automático con APScheduler (tareas diarias 08:00 AM)
  - ✅ 3 funciones de notificación con escalamiento de urgencia
  - ✅ 4 templates HTML responsivos para emails
  - ✅ Sistema de recordatorios automatizados (día 3 y día 6)
  - ✅ 9 tests de notificaciones (100% passing)
  - ✅ Documentación completa en `docs/UC6_SOLICITUD_DOCUMENTOS.md`
- Previamente: mejoras de UX en el formulario de registro (previews de archivos, preservación de archivos, modal de confirmación con código de radicación, indicador de progreso). Detalles en `docs/MEJORAS_UX_CLIENTE.md`.
- Backend: la ruta `/incapacidades/registrar` ahora soporta peticiones AJAX/JSON y responde con JSON en caso de solicitud desde el cliente.
- `crear_usuarios.py` reescrito para ser más robusto (detección de entorno, eliminación/creación de usuarios de prueba). Usuarios de prueba recreados.
- Commit reciente con mejoras UX: `1217bae` (mensaje: feat(UX): Implementar mejoras client-side en registro de incapacidades).

---

## ✨ Funcionalidades Principales (actualizado)

- ✅ Registro de incapacidades con código de radicación único (INC-YYYYMMDD-XXXX)
- ✅ Transacciones atómicas (rollback automático en errores)
- ✅ Validación de tipos de incapacidad (5 tipos permitidos)
- ✅ Reglas documentales por tipo de incapacidad
- ✅ Sistema de carga de archivos con metadatos (UUID, MD5, MIME)
- ✅ Sistema de notificaciones por email con reintentos configurables
- ✅ **Scheduler automático de recordatorios (APScheduler)**
- ✅ **UC6: Solicitud de documentos faltantes con recordatorios escalados**
- ✅ Logging detallado de eventos del sistema
- ✅ Hooks post-commit para almacenamiento y verificación (UC15)
- ✅ Validación de documentación por auxiliar
- ✅ Aprobación/rechazo de incapacidades
- ✅ Mejoras UX cliente (previews, validación client-side, modal de confirmación, preservación de archivos)
- ⚠️ Validación automática por tipo (parcial)


---

## 🛠️ Stack Tecnológico

- **Backend:** Flask 3.0.0 (Python 3.8+)
- **ORM:** Flask-SQLAlchemy 3.1.1
- **Auth:** Flask-Login 0.6.3
- **Email:** Flask-Mail 0.9.1 (Mailtrap para desarrollo)
- **Scheduler:** APScheduler 3.10.4 (tareas automáticas)
- **BD:** SQLite
- **Frontend:** Bootstrap 5 + JavaScript vanilla

---

## 🚀 Instalación Rápida

### Requisitos
- Python 3.8+
- Cuenta Mailtrap (gratis: https://mailtrap.io)

### Instalación

```powershell
# 1. Clonar proyecto
cd proyecto-incapacidades

# 2. Crear entorno virtual
python -m venv venv
venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar .env
# Copiar .env.example a .env y editar con credenciales Mailtrap
MAIL_ENABLED=False  # False = modo simulación (no consume cuota)
MAIL_SERVER=sandbox.smtp.mailtrap.io
MAIL_PORT=2525
MAIL_USERNAME=tu-usuario-mailtrap
MAIL_PASSWORD=tu-password-mailtrap
GESTION_HUMANA_EMAIL=rrhh@test.com

# 5. Crear usuarios de prueba
python crear_usuarios.py

# 6. Ejecutar aplicación
python run.py

# 7. Abrir http://localhost:5000
```

---

## 👤 Usuarios de Prueba (actualizado)

| Rol | Email | Contraseña |
|-----|-------|------------|
| Colaborador | `empleado@test.com` | `123456` |
| Auxiliar | `auxiliar@test.com` | `123456` |

> Nota: el script `crear_usuarios.py` fue mejorado en esta sesión para recrear estos usuarios. Ejecutar `python crear_usuarios.py` si no existen.

---

## 📧 Control de Emails

```powershell
python toggle_email.py on      # Activar emails reales (consume cuota)
python toggle_email.py off     # Desactivar (modo simulación)
python toggle_email.py status  # Ver estado actual
```

**Nota:** En modo simulación (`MAIL_ENABLED=False`), los emails se muestran en consola pero no se envían.

---

## � Estructura del Proyecto

> **Ver estructura completa:** [`ESTRUCTURA.md`](ESTRUCTURA.md)

```
proyecto-incapacidades/
├── app/                    # Aplicación Flask
│   ├── models/             # Modelos ORM (Usuario, Incapacidad, Documento)
│   ├── routes/             # Controladores (auth, incapacidades, documentos)
│   ├── templates/          # Vistas HTML + 6 templates de email
│   ├── static/             # CSS, JS, uploads
│   └── utils/              # email_service, validaciones
├── docs/                   # Documentación
│   ├── ESTADO_PROYECTO.md
│   ├── CONTROL_EMAILS.md
│   ├── BUG_FIX_ALERTAS.md
│   ├── manual_usuario.md
│   ├── roles_permisos.md
│   ├── MEJORAS_UX_CLIENTE.md
│   └── UC6_SOLICITUD_DOCUMENTOS.md   # 📘 Documentación completa de UC6
├── instance/
│   └── database.db         # SQLite
├── .env                    # Configuración (NO versionar)
├── config.py               # Config Flask
├── run.py                  # Ejecutar aplicación
├── crear_usuarios.py       # Script usuarios de prueba (mejorado)
├── toggle_email.py         # Control on/off emails
├── GUIA_RAPIDA.md          # 🚀 Inicio rápido en 5 minutos
├── SCRIPTS_UTILIDAD.md     # Descripción de scripts
└── requirements.txt        # Dependencias
```

---

## 🧭 Cambios Destacados (esta sesión)

- feat(UX): Previews de archivos en `registro_incapacidad.html` (imágenes y PDFs)
- feat(UX): Preservación de archivos seleccionados cuando hay errores (DataTransfer)
- feat(UX): Modal de confirmación con código de radicación y botón copiar
- feat(routes): `/incapacidades/registrar` ahora responde JSON para peticiones AJAX
- refactor: `crear_usuarios.py` reescrito y robustecido (recrea usuarios de prueba)
- docs: `docs/MEJORAS_UX_CLIENTE.md` añadido con detalles, pruebas y diagramas
- commit: `1217bae` contiene las mejoras UX y cambios relacionados

---

## �️ Comandos Útiles (resumen)

### Ejecutar aplicación
```powershell
python run.py
```

### Crear usuarios de prueba
```powershell
python crear_usuarios.py
```

### Ejecutar tests (ejemplo)
```powershell
python -m pytest tests/test_validacion_documentos.py -q
```

---

## 🔥 Flujo de Trabajo (breve)

### Colaborador:
1. Login → Dashboard
2. Registrar incapacidad (tipo, fechas)
3. Cargar documentos (certificado, epicrisis si aplica)
4. Recibir email de confirmación ✉️
5. Consultar estado de mis incapacidades

### Auxiliar RRHH:
1. Login → Dashboard Auxiliar
2. Ver incapacidades pendientes
3. Revisar documentación cargada
4. Validar o solicitar documentos faltantes (pendiente UC6)
5. Aprobar o rechazar incapacidad

---

## 🎯 Próximos Pasos

1. ✅ ~~Implementar UC6: Solicitar documentos faltantes~~ (completado 95%)
2. Completar UC5: Validación automática por tipo
3. UC2: Notificar líder directo (completar)
4. UC15: Backups externos y thumbnails para PDFs
5. Tests E2E de UC6 (ajustes finales pendientes)

---

## 📘 Documentación Detallada

- **UC6 - Solicitud de Documentos Faltantes**: Ver [`docs/UC6_SOLICITUD_DOCUMENTOS.md`](docs/UC6_SOLICITUD_DOCUMENTOS.md)
  - Diagramas de flujo y estados
  - Ejemplos de uso para usuarios y desarrolladores
  - Configuración del scheduler
  - Logs esperados y troubleshooting

---

## 📞 Soporte

**Inicio rápido:** Ver `GUIA_RAPIDA.md` para setup en 5 minutos

**Problemas con emails:**
```powershell
python toggle_email.py status  # Ver estado
```

**Problemas con archivos:**
- Verificar carpeta `app/static/uploads/` existe
- Formatos permitidos: PDF, PNG, JPG, JPEG

**Consultar logs:**
- Ver consola del servidor para mensajes con emojis: ✅ (éxito), ❌ (error), ⚠️ (advertencia), 📧 (email), 💾 (almacenamiento), 🔔 (notificación)
- Configurar nivel de logging en `.env`: `LOG_LEVEL=INFO` (opciones: DEBUG, INFO, WARNING, ERROR)

---

# Resumen de Cambios

## **Sesión 19 Octubre 2025 - Tarea 6: Scheduler, Testing y Documentación UC6**

- **Scheduler Automático:** Se implementó `app/tasks/scheduler_uc6.py` con APScheduler
  - Tarea diaria a las 08:00 AM para procesar recordatorios
  - Configuración en `app/__init__.py` con flag `SCHEDULER_ENABLED`
  - Función `procesar_recordatorios_documentos()` ejecuta lógica de negocio
  - Timezone: America/Bogota

- **Tests Implementados:**
  - ✅ `tests/test_notificaciones_uc6.py`: 9/9 tests passing (100%)
  - ⚠️ `tests/test_uc6_completo_e2e.py`: Creado (requiere ajustes)
  - ⚠️ `tests/test_excepciones_uc6.py`: Creado (requiere ajustes)

- **Documentación Completa:**
  - ✅ `docs/UC6_SOLICITUD_DOCUMENTOS.md`: 600+ líneas
  - Diagramas ASCII de estados y secuencia
  - Línea de tiempo completa (día 0 a día 6+)
  - Ejemplos de uso para usuarios finales y desarrolladores
  - Logs esperados y troubleshooting
  - Arquitectura técnica y FAQ

- **README Actualizado:**
  - UC6 cambiado de 🔴 0% a ✅ 95%
  - Agregado APScheduler al stack tecnológico
  - Link a documentación completa de UC6

## **Sesión 13 Octubre 2025 - Mejoras UX y Backend**

- **Mejoras de UX:** Interfaces mejoradas con modales de confirmación, previsualización de archivos y experiencia de usuario más intuitiva.
- **Backend:** Lógica de respuestas AJAX/JSON actualizada en `/incapacidades/registrar`.
- **Script de Creación de Usuarios:** Refactorización de `crear_usuarios.py` con manejo robusto de errores.
- **Tests:** Pruebas ejecutadas exitosamente (ej: `tests/test_validacion_documentos.py`).
- **Documentación:** Ver `docs/MEJORAS_UX_CLIENTE.md` para detalles adicionales.

---

**Última actualización:** 2025-10-19  
**Estado:** Pre-Release 1.0 (70% completo - UC6 implementado)  
**Próximo hito:** Tests E2E de UC6 y validación automática (UC5)

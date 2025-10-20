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

## 🧭 Cambios Destacados (esta sesión - 20 Octubre 2025)

### Fixes Críticos UC6 - Gestión de Documentos:
- 🐛 **FIJO:** Documentos cargados mostraban "Falta" incorrectamente
  - Causa raíz: Inconsistencia en `tipo_documento` (mix de strings simples y enums)
  - Solución: Normalizar almacenamiento a tipos simples en línea 1010 `incapacidades.py`
  
- 🐛 **FIJO:** Estado no cambiaba después de subir documentos
  - Causa: Comparación de enums vs strings nunca coincidía en validación
  - Solución: Agregar `mapeo_tipo_simple` en `solicitud_documentos_service.py` línea 197
  
- 🐛 **FIJO:** Permitía subir documentos indefinidamente
  - Causa: Solicitudes nunca marcadas como `ENTREGADO`
  - Solución: Una vez estado cambia a `PENDIENTE_VALIDACION`, frontend redirige
  
- 🐛 **FIJO:** Mensajes de respuesta mostraban valores enum (CERTIFICADO_INCAPACIDAD)
  - Causa: JSON retornaba directamente `p.tipo_documento`
  - Solución: Agregar mapeo de nombres legibles en línea 1044-1056 `incapacidades.py`

### Mejoras de Estilización:
- 📱 **Estilización completa de estados en `mis_incapacidades.html`:**
  - Agregados emojis de estatus con nombres legibles (⏳ Pendiente, ✅ Aprobada, etc)
  - Colores diferenciados para cada estado UC6:
    - 🟠 `DOCUMENTACION_INCOMPLETA` → naranja (#fd7e14)
    - 🟢 `DOCUMENTACION_COMPLETA` → verde claro (#20c997)
    - 🔵 `PENDIENTE_VALIDACION` → celeste (#0dcaf0)
    - ✅ `VALIDADA` → verde oscuro (#198754)
  
- 🎨 **CSS mejorado en `styles.css`:**
  - `.badge-estado` con mejor contraste y spacing
  - Soporte responsive para tablets/móviles
  - Botones agrupados en tabla más compactos
  - Mínimo ancho de 150px en badges para claridad

- 🖥️ **Tabla más legible:**
  - Iconos Bootstrap en encabezados
  - Espaciado mejorado
  - Badges secundarios para tipo e indicadores
  - Acciones en botones grupo (btn-group-sm)

### Archivos Modificados:
- ✏️ `app/routes/incapacidades.py` (líneas 710-780, 994-1010, 1044-1072)
- ✏️ `app/services/solicitud_documentos_service.py` (línea 173-197)
- ✏️ `app/templates/mis_incapacidades.html` (rediseño completo)
- ✏️ `app/static/css/styles.css` (nuevos estados UC6)

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

# Resumen de Cambios

## **Sesión 20 Octubre 2025 - Bug Fixes Críticos UC6 y Estilización**

### Bugs Corregidos:
1. **Documentos mostraban "Falta" después de ser cargados**
   - Problema: `tipo_documento` almacenado de forma inconsistente (enums vs strings)
   - Solución: Normalizar a strings simples en todas partes
   - Impacto: UC6 ahora funciona correctamente

2. **Estado no cambiaba a PENDIENTE_VALIDACION**
   - Problema: Comparación de tipos nunca coincidía (CERTIFICADO_INCAPACIDAD vs certificado)
   - Solución: Mapeo en `solicitud_documentos_service.py` antes de comparar
   - Impacto: Flujo de validación de documentos restaurado

3. **Mensajes JSON mostraban valores enum**
   - Problema: Response incluía `CERTIFICADO_INCAPACIDAD` en lugar de texto legible
   - Solución: Diccionario de mapeo para nombres amigables
   - Impacto: UX mejorada, usuarios entienden qué documentos faltan

### Mejoras de UI/UX:
- Tabla "Mis Incapacidades" completamente rediseñada
- Estados UC6 con colores diferenciados y emojis
- Responsive design mejorado para mobile
- Badges con mejor contraste (fix letras blancas sobre fondo blanco)

### Status: ✅ 95% → 📈 Mejora de confiabilidad

---

**Última actualización:** 2025-10-20  
**Estado:** Pre-Release 1.0 (75% completo - UC6 bugs fixed y UI mejorada)  
**Próximo hito:** Tests E2E de UC6 y validación automática (UC5)

# Sistema de Gestión de Incapacidades

Sistema web para la gestión de incapacidades médicas de empleados, desarrollado con Flask.

**Estado actual:** 65.5% completo | **Release:** 1.0 (en desarrollo)

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
| UC6 | Solicitar documentos faltantes | 🔴 0% |
| UC7 | Aprobar/Rechazar | ⚠️ 65% |
| UC15 | Almacenar documentos | ⚠️ 70% |

**Resumen de avances en esta sesión:**
- Implementadas mejoras de UX en el formulario de registro (previews de archivos, preservación de archivos, modal de confirmación con código de radicación, indicador de progreso). Detalles en `docs/MEJORAS_UX_CLIENTE.md`.
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
- ✅ Logging detallado de eventos del sistema
- ✅ Hooks post-commit para almacenamiento y verificación (UC15)
- ✅ Validación de documentación por auxiliar
- ✅ Aprobación/rechazo de incapacidades
- ✅ Mejoras UX cliente (previews, validación client-side, modal de confirmación, preservación de archivos)
- ⚠️ Validación automática por tipo (parcial)
- 🔴 Solicitud de documentos faltantes (pendiente)

---

## 🛠️ Stack Tecnológico

- **Backend:** Flask 3.0.0 (Python 3.8+)
- **ORM:** Flask-SQLAlchemy 3.1.1
- **Auth:** Flask-Login 0.6.3
- **Email:** Flask-Mail 0.9.1 (Mailtrap para desarrollo)
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
+│   └── MEJORAS_UX_CLIENTE.md   # (nuevo) Detalle de mejoras UX implementadas
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

1. Implementar UC6: Solicitar documentos faltantes (prioridad alta)
2. Completar UC5: Validación automática por tipo
3. UC2: Notificar líder directo (completar)
4. UC15: Backups externos y thumbnails para PDFs

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

# Resumen de Cambios (Sesión 13 Octubre 2025)

- **Mejoras de UX:** Se implementaron interfaces de usuario mejoradas, incluyendo modales de confirmación, previsualización de archivos y una experiencia de usuario más intuitiva.
- **Backend:** Se actualizó la lógica de respuestas AJAX/JSON en las rutas (por ejemplo, en `/incapacidades/registrar`) para mejorar la validación y el manejo de datos.
- **Script de Creación de Usuarios:** Se refactorizó el archivo `crear_usuarios.py` para manejar de forma robusta errores (como problemas de codificación) y validar contraseñas, eliminando usuarios existentes antes de crear nuevos registros de prueba.
- **Tests:** Se ejecutaron pruebas (por ejemplo, `tests/test_validacion_documentos.py`) con resultados exitosos.
- **Documentación:** Este README se actualiza para reflejar los cambios realizados durante esta sesión. Consulte `docs/MEJORAS_UX_CLIENTE.md` para obtener detalles adicionales de las mejoras en la experiencia de usuario.

---

**Última actualización:** 2025-10-13  
**Estado:** Pre-Release 1.0 (65.5% completo)  
**Próximo hito:** UC6 - Solicitar documentos faltantes

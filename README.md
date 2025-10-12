# Sistema de Gestión de Incapacidades

Sistema web para la gestión de incapacidades médicas de empleados, desarrollado con Flask.

**Estado actual:** 55.6% completo | **Release:** 1.0 (en desarrollo)

> 🚀 **Inicio rápido:** Ver [`GUIA_RAPIDA.md`](GUIA_RAPIDA.md) para setup en 5 minutos  
> 📁 **Estructura:** Ver [`ESTRUCTURA.md`](ESTRUCTURA.md) para arquitectura completa  
> 🔧 **Scripts:** Ver [`SCRIPTS_UTILIDAD.md`](SCRIPTS_UTILIDAD.md) para comandos disponibles

---

## 📊 Estado del Proyecto

| UC | Caso de Uso | Estado |
|----|------------|--------|
| UC1 | Registrar incapacidad | ⚠️ 85% |
| UC2 | Notificar RRHH | ⚠️ 70% |
| UC3 | Consultar incapacidades | ⚠️ 60% |
| UC4 | Validar documentación | ⚠️ 75% |
| UC5 | Verificar requisitos por tipo | 🔴 40% |
| UC6 | Solicitar documentos faltantes | 🔴 0% |
| UC7 | Aprobar/Rechazar | ⚠️ 65% |
| UC15 | Almacenar documentos | ⚠️ 50% |

**Bloqueadores críticos:** UC6 (0%), UC5 (40%)  
**Ver detalles:** `docs/ESTADO_PROYECTO.md`

---

## ✨ Funcionalidades Principales

- ✅ Registro de incapacidades con carga de documentos
- ✅ Sistema de notificaciones por email (6 templates)
- ✅ Validación de documentación por auxiliar
- ✅ Aprobación/rechazo de incapacidades
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

```bash
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

## 👤 Usuarios de Prueba

| Rol | Email | Contraseña |
|-----|-------|------------|
| Colaborador | `colaborador@test.com` | `123456` |
| Auxiliar | `auxiliar@test.com` | `123456` |

---

## 📧 Control de Emails

```bash
python toggle_email.py on      # Activar emails reales (consume cuota)
python toggle_email.py off     # Desactivar (modo simulación)
python toggle_email.py status  # Ver estado actual
```

**Nota:** En modo simulación (`MAIL_ENABLED=False`), los emails se muestran en consola pero no se envían.

---

## 📁 Estructura del Proyecto

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
│   ├── ESTADO_PROYECTO.md  # ⭐ Estado detallado (55.6%)
│   ├── CONTROL_EMAILS.md   # Control de cuota emails
│   ├── BUG_FIX_ALERTAS.md  # Fix alertas JavaScript
│   ├── manual_usuario.md   # Manual de usuario
│   └── roles_permisos.md   # Matriz de permisos
├── instance/
│   └── database.db         # SQLite
├── .env                    # Configuración (NO versionar)
├── config.py               # Config Flask
├── run.py                  # Ejecutar aplicación
├── crear_usuarios.py       # Script usuarios de prueba
├── toggle_email.py         # Control on/off emails
├── GUIA_RAPIDA.md         # 🚀 Inicio rápido en 5 minutos
├── SCRIPTS_UTILIDAD.md    # Descripción de scripts
└── requirements.txt        # Dependencias
```

---

## �️ Comandos Útiles

### Ejecutar aplicación
```bash
python run.py
```

### Crear usuarios de prueba
```bash
python crear_usuarios.py
```

### Control de emails
```bash
python toggle_email.py on      # Activar emails reales
python toggle_email.py off     # Desactivar (modo simulación)
python toggle_email.py status  # Ver estado
```

**Nota:** Ver `SCRIPTS_UTILIDAD.md` para más detalles sobre los scripts disponibles.

---

## 🔥 Flujo de Trabajo

### Colaborador:
1. Login → Dashboard
2. Registrar incapacidad (tipo, fechas)
3. Cargar documentos (certificado, epicrisis si aplica)
4. Recibir email de confirmación ✉️
5. Consultar estado de mis incapacidades
6. Recibir notificaciones de validación/aprobación

### Auxiliar RRHH:
1. Login → Dashboard Auxiliar
2. Ver incapacidades pendientes
3. Revisar documentación cargada
4. Validar o solicitar documentos faltantes (⚠️ parcialmente implementado)
5. Aprobar o rechazar incapacidad
6. Sistema envía notificaciones automáticas ✉️

---

## 🎯 Próximos Pasos

**Release 1.0 Completo (14 días):**

1. **Sprint 1** - Implementar UC6: Solicitar documentos faltantes (4 días)
2. **Sprint 2** - Completar UC5: Validación automática por tipo (3 días)
3. **Sprint 3** - Mejoras UC2, UC7, UC15 (3 días)
4. **Sprint 4** - Mejoras UC1, UC3, UC4 (2 días)
5. **Testing final** (2 días)

Ver detalles en `docs/ESTADO_PROYECTO.md`

---

## 🐛 Problemas Conocidos

1. **Rate Limit Mailtrap** - Solo 1 email/segundo (SOLUCIONADO con delay de 2s)
2. **Notificación al líder falta** - Solo notifica a RRHH (pendiente)
3. **Validación automática manual** - UC5 requiere completar validación automática

Ver más en `docs/SOLUCION_PROBLEMAS.md`

---

## 📞 Soporte

**Inicio rápido:** Ver `GUIA_RAPIDA.md` para setup en 5 minutos

**Problemas con emails:**
```bash
python toggle_email.py status  # Ver estado
```

**Problemas con archivos:**
- Verificar carpeta `app/static/uploads/` existe
- Formatos permitidos: PDF, PNG, JPG, JPEG

**Consultar logs:**
- Ver consola del servidor para mensajes con ✅ ❌ 📧

---

**Última actualización:** 2025-10-12  
**Estado:** Pre-Release 1.0 (55.6% completo)  
**Próximo hito:** UC6 - Solicitar documentos faltantes
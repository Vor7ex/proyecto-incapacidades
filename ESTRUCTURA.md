# 📁 Estructura del Proyecto

Estructura limpia y organizada del proyecto después de la limpieza del 2025-10-12.

---

## 🎯 Raíz del Proyecto

```
proyecto-incapacidades/
├── .env                    # Variables de entorno (NO versionar)
├── .env.example            # Ejemplo de configuración
├── .gitignore              # Archivos ignorados por Git
├── config.py               # Configuración de Flask
├── crear_usuarios.py       # Script: crear usuarios de prueba
├── GUIA_RAPIDA.md         # ⭐ Inicio rápido en 5 minutos
├── README.md              # Documentación principal
├── requirements.txt        # Dependencias Python
├── run.py                 # Script: ejecutar aplicación
├── SCRIPTS_UTILIDAD.md    # Descripción de scripts disponibles
├── toggle_email.py        # Script: control on/off emails
└── ESTRUCTURA.md          # Este archivo
```

### 📝 Archivos Clave

- **`GUIA_RAPIDA.md`** - 🚀 Inicio rápido para nuevos desarrolladores
- **`README.md`** - Documentación completa del proyecto
- **`SCRIPTS_UTILIDAD.md`** - Guía de scripts en raíz
- **`config.py`** - Configuración centralizada
- **`.env`** - Variables de entorno (secreto, no versionar)

---

## 📂 Carpeta `app/` - Aplicación Flask

```
app/
├── __init__.py             # Inicialización de Flask
├── models/                 # Modelos de datos (ORM)
│   ├── __init__.py
│   ├── usuario.py          # Modelo Usuario
│   ├── incapacidad.py      # Modelo Incapacidad
│   └── documento.py        # Modelo Documento
├── routes/                 # Rutas/Controladores
│   ├── __init__.py
│   ├── auth.py             # Autenticación (login/logout)
│   ├── incapacidades.py    # CRUD incapacidades
│   └── documentos.py       # Gestión de documentos
├── templates/              # Vistas HTML (Jinja2)
│   ├── base.html           # Template base
│   ├── login.html
│   ├── registro_incapacidad.html
│   ├── mis_incapacidades.html
│   ├── detalle_incapacidad.html
│   ├── dashboard_auxiliar.html
│   ├── validar_incapacidades.html
│   ├── aprobar_rechazar.html
│   ├── info_sistema.html
│   └── emails/             # Templates de email
│       ├── confirmacion_registro.html
│       ├── notificacion_gestion_humana.html
│       ├── validacion_completada.html
│       ├── documentos_faltantes.html
│       ├── incapacidad_aprobada.html
│       └── incapacidad_rechazada.html
├── static/                 # Archivos estáticos
│   ├── css/
│   │   └── styles.css      # Estilos personalizados
│   ├── js/
│   │   └── main.js         # JavaScript (alertas, validaciones)
│   └── uploads/            # Documentos cargados (NO versionar)
└── utils/                  # Utilidades
    ├── email_service.py    # Sistema de notificaciones
    └── validaciones.py     # Validaciones de negocio
```

### 🎨 Frontend
- **Bootstrap 5** - Framework CSS
- **JavaScript vanilla** - Sin frameworks adicionales
- **Jinja2** - Motor de templates

### 🗄️ Backend
- **Flask 3.0.0** - Framework web
- **Flask-Login** - Autenticación
- **Flask-SQLAlchemy** - ORM
- **Flask-Mail** - Emails

---

## 📚 Carpeta `docs/` - Documentación

```
docs/
├── ESTADO_PROYECTO.md          # ⭐ Estado detallado (55.6%)
├── CONTROL_EMAILS.md           # Sistema de control de cuota emails
├── BUG_FIX_ALERTAS.md          # Fix alertas JavaScript
├── manual_usuario.md           # Manual de usuario final
└── roles_permisos.md           # Matriz de permisos por rol
```

### 📖 Documentación Esencial

1. **`ESTADO_PROYECTO.md`** - Estado actual detallado
   - % completitud por caso de uso
   - Bloqueadores críticos
   - Plan de acción con sprints
   - Problemas conocidos

2. **`CONTROL_EMAILS.md`** - Sistema de emails
   - Toggle on/off
   - Ahorro de cuota Mailtrap
   - Modo desarrollo vs producción

3. **`manual_usuario.md`** - Guía para usuarios finales
   - Cómo registrar incapacidad
   - Cómo validar documentos
   - Flujos de trabajo

---

## 🗃️ Carpeta `instance/` - Base de Datos

```
instance/
└── database.db             # SQLite (NO versionar)
```

**Nota:** La BD se crea automáticamente al ejecutar `run.py` por primera vez.

---

## 🧪 Carpeta `tests/` - Pruebas

```
tests/
└── test_basico.py          # Tests unitarios básicos
```

**Pendiente:** Expandir suite de tests (Sprint 4)

---

## 🗑️ Archivos Eliminados (Limpieza 2025-10-12)

### Scripts temporales eliminados:
- ❌ `corregir_rutas.py` - Script de corrección temporal
- ❌ `probar_email.py` - Funcionalidad en `toggle_email.py`
- ❌ `verificar_archivos.py` - Debug temporal
- ❌ `verificar_uc2.py` - Funcionalidad en `toggle_email.py`

### Documentación redundante eliminada:
- ❌ `CHECKLIST_GIT.md` - Checklist temporal
- ❌ `GITIGNORE_CAMBIOS.md` - Doc temporal
- ❌ `docs/checklist_pruebas.md` - Checklist temporal
- ❌ `docs/UC2_NOTIFICACIONES.md` - Info consolidada en ESTADO_PROYECTO.md
- ❌ `docs/UC2_IMPLEMENTACION_COMPLETA.md` - Redundante
- ❌ `docs/CHECKLIST_UC2.md` - Checklist temporal
- ❌ `docs/CONFIGURACION_EMAIL_SEGURA.md` - Info en CONTROL_EMAILS.md
- ❌ `docs/DECISION_ARQUITECTURA_ROLES.md` - Decisión ya tomada
- ❌ `docs/SOLUCION_PROBLEMAS.md` - Info en ESTADO_PROYECTO.md
- ❌ `docs/UC2_RESUMEN_FINAL.md` - Info consolidada

### Cache eliminado:
- ❌ `__pycache__/` (raíz) - Ignorado en .gitignore

---

## 🔒 Archivos NO Versionados

Configurado en `.gitignore`:

```
# NO versionar
.env                        # Credenciales
instance/database.db        # Base de datos
app/static/uploads/*        # Documentos cargados
venv/                       # Entorno virtual
__pycache__/                # Cache Python
*.pyc, *.pyo                # Compilados
```

---

## 📊 Métricas del Proyecto

| Aspecto | Cantidad |
|---------|----------|
| Scripts raíz | 3 (run, crear_usuarios, toggle_email) |
| Modelos | 3 (Usuario, Incapacidad, Documento) |
| Rutas | 3 blueprints (auth, incapacidades, documentos) |
| Templates HTML | 9 vistas + 6 emails = 15 |
| Archivos docs | 5 documentos esenciales |
| Archivos config | 3 (.env.example, config.py, .gitignore) |

---

## 🎯 Convenciones

### Nombres de archivos
- **Scripts:** `verbo_sustantivo.py` (ej: `crear_usuarios.py`)
- **Modelos:** Singular, minúsculas (ej: `usuario.py`)
- **Templates:** `verbo_sustantivo.html` (ej: `registro_incapacidad.html`)
- **Docs:** MAYÚSCULAS_SNAKE_CASE.md (ej: `ESTADO_PROYECTO.md`)

### Estructura de código
- **Models:** ORM con SQLAlchemy
- **Routes:** Blueprints por funcionalidad
- **Templates:** Herencia de `base.html`
- **Utils:** Funciones auxiliares sin estado

---

## 🚀 Comandos Frecuentes

```bash
# Activar entorno
venv\Scripts\activate

# Ver estructura
tree /F  # Windows
ls -R    # Linux/Mac

# Listar docs
dir docs

# Ver scripts raíz
dir *.py

# Limpiar cache
Remove-Item -Recurse -Force **\__pycache__
```

---

**Última actualización:** 2025-10-12  
**Estado:** Proyecto limpio y organizado

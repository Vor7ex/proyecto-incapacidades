# Sistema de Gestion de Incapacidades - Release 1.0

Sistema web para gestionar el ciclo completo de incapacidades medicas,
desde el registro hasta la aprobacion, con notificaciones automaticas por email.

## Caracteristicas

- ✅ Registro digital de incapacidades (UC1)
- ✅ Sistema de notificaciones por email (UC2)
- ✅ Consulta de historial de incapacidades (UC3)
- ✅ Recepcion y validacion de documentacion (UC4)
- ✅ Validacion de requisitos por tipo (UC5)
- ✅ Aprobacion/rechazo de incapacidades (UC7)
- ✅ Almacenamiento digital de documentos (UC15)
- ✅ Sistema de roles (colaborador/auxiliar)
- ✅ Workflow completo de gestion

## Tecnologias

- **Backend**: Python 3.8+ con Flask 3.0.0
- **Frontend**: HTML5, Bootstrap 5, JavaScript
- **Base de Datos**: SQLite
- **Autenticacion**: Flask-Login 0.6.3
- **Email**: Flask-Mail 0.9.1
- **ORM**: Flask-SQLAlchemy 3.1.1

## Instalacion

### Requisitos Previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Cuenta de correo para SMTP (Gmail recomendado)

### Pasos

1. **Clonar o descargar el proyecto**

2. **Crear entorno virtual:**
   ```bash
   python -m venv venv
   venv\Scripts\activate     # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno:**
   - Copiar `.env.example` a `.env`
   - Editar `.env` con tus credenciales SMTP
   
   ```bash
   # Ejemplo para Gmail
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=tu_correo@gmail.com
   MAIL_PASSWORD=tu_contraseña_aplicacion
   GESTION_HUMANA_EMAIL=rrhh@empresa.com
   ```
   
   **Importante:** Para Gmail, debes generar una "Contraseña de aplicación":
   - Ir a https://myaccount.google.com/security
   - Activar "Verificación en 2 pasos"
   - Ir a "Contraseñas de aplicaciones"
   - Generar nueva contraseña para "Mail"
   - Usar esa contraseña en `MAIL_PASSWORD`

5. **Crear usuarios de prueba:**
   ```bash
   python crear_usuarios.py
   ```

6. **Ejecutar aplicacion:**
   ```bash
   python run.py
   ```

7. **Abrir navegador en:** http://localhost:5000

## Usuarios de Prueba

Después de ejecutar `crear_usuarios.py`:

- **Colaborador**: colaborador@test.com / 123456
- **Auxiliar**: auxiliar@test.com / 123456

## Probar Sistema de Notificaciones

Después de configurar el SMTP:

```bash
python probar_email.py
```

Este script verificará la configuración y enviará un email de prueba.

## Estructura del Proyecto

```
proyecto-incapacidades/
├── app/
│   ├── models/          # Modelos de BD (Usuario, Incapacidad, Documento)
│   ├── routes/          # Rutas/Controladores (auth, incapacidades, documentos)
│   ├── templates/       # Vistas HTML
│   │   └── emails/      # Plantillas de email (6 templates)
│   ├── static/          # CSS, JS, uploads
│   └── utils/           # Utilidades (validaciones, email_service)
├── docs/                # Documentacion (UC2, roles, bugs, etc)
├── instance/            # Base de datos SQLite
├── tests/               # Pruebas unitarias
├── config.py            # Configuracion (SMTP, paths, etc)
├── run.py               # Punto de entrada
├── crear_usuarios.py    # Script para crear usuarios de prueba
├── probar_email.py      # Script para probar notificaciones
├── .env.example         # Ejemplo de configuracion de entorno
└── requirements.txt     # Dependencias Python
```

## Casos de Uso Implementados - Release 1.0

| UC | Nombre | Estado |
|----|--------|--------|
| UC1 | Registrar incapacidad y cargar documentos | ✅ 100% |
| UC2 | Notificar al colaborador y Gestión Humana | ✅ 100% |
| UC3 | Consultar mis incapacidades | ✅ 100% |
| UC4 | Recibir y validar documentación | ✅ 100% |
| UC5 | Verificar requisitos según tipo de incapacidad | ⚠️ 70% |
| UC7 | Aprobar o rechazar incapacidad | ✅ 100% |
| UC15 | Almacenar documentos de forma digital | ✅ 100% |

**Leyenda:**
- ✅ Implementado y probado
- ⚠️ Parcialmente implementado (validación manual funciona, automática en desarrollo)

Ver detalles en: `docs/UC2_NOTIFICACIONES.md`

## Sistema de Notificaciones (UC2)

El sistema envía emails automáticamente en los siguientes eventos:

### Al Colaborador:
1. **Confirmación de registro** - Cuando registra una incapacidad
2. **Validación completada** - Cuando RRHH valida la documentación
3. **Documentos faltantes** - Si falta documentación requerida
4. **Aprobación** - Cuando la incapacidad es aprobada
5. **Rechazo** - Cuando la incapacidad es rechazada (con motivo)

### A Gestión Humana:
1. **Nueva solicitud** - Cuando un colaborador registra una incapacidad

**Características:**
- ✉️ Envío asíncrono (no bloquea la aplicación)
- 📧 Templates HTML profesionales y responsive
- 🔒 Configuración segura vía variables de entorno
- ⚡ Reintentos automáticos si falla el SMTP

## Flujo de Trabajo

### Colaborador:
1. Login → Dashboard
2. Registrar incapacidad (tipo, fechas)
3. Cargar documentos (certificado, epicrisis si aplica)
4. Recibir email de confirmación
5. Consultar estado de mis incapacidades
6. Recibir notificaciones de validación/aprobación

### Auxiliar RRHH:
1. Login → Dashboard Auxiliar
2. Ver incapacidades pendientes
3. Revisar documentación
4. Validar o solicitar documentos faltantes
5. Aprobar o rechazar
6. Sistema envía notificaciones automáticas

## Validación Automática de Requisitos

El sistema valida automáticamente:
- ✅ Certificado de incapacidad (obligatorio siempre)
- ✅ Epicrisis (obligatoria si >2 días o accidente laboral)
- ✅ Formato de archivos (PDF, PNG, JPG, JPEG)
- ✅ Rango de fechas válido
- ✅ Nivel de cumplimiento (0-100%)

## Seguridad

- 🔐 Contraseñas hasheadas con Werkzeug
- 🔒 Autenticación basada en sesiones (Flask-Login)
- 🛡️ Control de acceso por roles
- 📁 Validación de archivos subidos
- 🔑 Credenciales SMTP en variables de entorno (no en código)

## Limitaciones Conocidas

- No incluye integración con portales EPS/ARL (Release 2.0)
- No incluye reportes avanzados (Release 2.0)
- No incluye módulo de conciliación de pagos (Release 3.0)
- Validación automática parcial (mejora continua)
- Autenticación básica (OAuth en Release 2.0)

## Trabajo Futuro (Próximas Releases)

### Release 1.1
- [ ] UC6: Solicitar documentos faltantes (mejorado)
- [ ] Cola de emails con Celery + Redis
- [ ] Logs persistentes de notificaciones
- [ ] Dashboard de estado de emails

### Release 2.0
- [ ] UC8-UC14: Integración con EPS/ARL
- [ ] Reportes avanzados (PDF/Excel)
- [ ] Dashboard con gráficos
- [ ] Notificaciones SMS/Push
- [ ] OAuth 2.0

### Release 3.0
- [ ] UC16: Módulo de conciliación financiera
- [ ] Sistema de roles granular
- [ ] API REST
- [ ] Aplicación móvil

## Troubleshooting

### Email no se envía
1. Verificar configuración en `.env`
2. Verificar que MAIL_PASSWORD es contraseña de aplicación (no contraseña normal)
3. Verificar conexión a internet
4. Verificar puerto 587 no bloqueado
5. Ejecutar `python probar_email.py` para diagnóstico

### No puedo subir archivos
1. Verificar que `app/static/uploads/` existe
2. Verificar permisos de escritura
3. Verificar formato de archivo (PDF, PNG, JPG, JPEG)

### Alertas desaparecen
- Presionar Ctrl+F5 para limpiar caché del navegador
- Verificar que `main.js` está actualizado

Ver más soluciones en: `docs/SOLUCION_PROBLEMAS.md`

## Documentación

- `docs/UC2_NOTIFICACIONES.md` - Sistema de notificaciones completo
- `docs/DECISION_ARQUITECTURA_ROLES.md` - Decisión de 2 roles vs 3 roles
- `docs/BUG_FIX_ALERTAS.md` - Solución de alertas que desaparecen
- `docs/SOLUCION_PROBLEMAS.md` - Guía de solución de problemas
- `docs/roles_permisos.md` - Matriz de permisos por rol
- `docs/manual_usuario.md` - Manual de usuario final

## Testing

```bash
# Ejecutar tests unitarios
pytest tests/

# Con coverage
pytest --cov=app tests/

# Test específico
pytest tests/test_basico.py
```

## Autores

- Juan Esteban Agudelo Escobar
- Juan Alejandro Salgado Arcila

## Licencia

Proyecto académico - Universidad Tecnológica de Pereira

---

**Versión:** 1.0.0  
**Fecha:** 2024  
**Estado:** ✅ Release 1.0 Completo
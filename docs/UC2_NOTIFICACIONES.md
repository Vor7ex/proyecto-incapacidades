# UC-2: Notificar al Colaborador y Gestión Humana

## Estado: ✅ IMPLEMENTADO

## Descripción
Sistema de notificaciones por correo electrónico para mantener informados a colaboradores y Gestión Humana sobre el estado de las incapacidades.

## Actores
- Colaborador
- Auxiliar RRHH (Gestión Humana)
- Sistema (automatizado)

## Flujo de Notificaciones

### 1. Registro de Incapacidad (UC1)
**Trigger:** Colaborador registra nueva incapacidad

**Notificaciones:**
- ✉️ **Al Colaborador:** Confirmación de registro
  - Template: `confirmacion_registro.html`
  - Contenido: Detalles de la incapacidad, próximos pasos
  
- ✉️ **A Gestión Humana:** Alerta de nueva solicitud
  - Template: `notificacion_gestion_humana.html`
  - Contenido: Datos del colaborador, tipo, fechas, documentos adjuntos

**Función:** `notificar_nueva_incapacidad(incapacidad, colaborador)`

### 2. Validación de Documentación (UC4)
**Trigger:** Auxiliar RRHH completa revisión

**Escenario A: Documentación Completa**
- ✉️ **Al Colaborador:** Notificación de validación exitosa
  - Template: `validacion_completada.html`
  - Función: `notificar_validacion_completada(incapacidad, colaborador)`

**Escenario B: Documentación Incompleta**
- ✉️ **Al Colaborador:** Solicitud de documentos faltantes
  - Template: `documentos_faltantes.html`
  - Contenido: Observaciones del auxiliar, documentos requeridos
  - Función: `notificar_documentos_faltantes(incapacidad, colaborador, observaciones)`

### 3. Aprobación/Rechazo (UC7)
**Trigger:** Auxiliar RRHH toma decisión final

**Escenario A: Aprobación**
- ✉️ **Al Colaborador:** Confirmación de aprobación
  - Template: `incapacidad_aprobada.html`
  - Función: `notificar_aprobacion(incapacidad, colaborador)`

**Escenario B: Rechazo**
- ✉️ **Al Colaborador:** Notificación de rechazo
  - Template: `incapacidad_rechazada.html`
  - Contenido: Motivo del rechazo, opciones disponibles
  - Función: `notificar_rechazo(incapacidad, colaborador)`

## Componentes Implementados

### 1. Servicio de Email (`app/utils/email_service.py`)
```python
from flask_mail import Mail, Message
from flask import render_template
from threading import Thread

mail = Mail()

def send_async_email(app, msg):
    """Envía email en hilo separado (no bloquea la app)"""
    
def notificar_nueva_incapacidad(incapacidad, colaborador):
    """UC1: Notifica registro de nueva incapacidad"""
    
def notificar_validacion_completada(incapacidad, colaborador):
    """UC4: Notifica validación exitosa"""
    
def notificar_documentos_faltantes(incapacidad, colaborador, observaciones):
    """UC4: Notifica documentos incompletos"""
    
def notificar_aprobacion(incapacidad, colaborador):
    """UC7: Notifica aprobación"""
    
def notificar_rechazo(incapacidad, colaborador):
    """UC7: Notifica rechazo"""
```

### 2. Templates de Email (`app/templates/emails/`)
- `confirmacion_registro.html` - Confirmación al colaborador
- `notificacion_gestion_humana.html` - Alerta a RRHH
- `validacion_completada.html` - Validación exitosa
- `documentos_faltantes.html` - Documentos incompletos
- `incapacidad_aprobada.html` - Aprobación
- `incapacidad_rechazada.html` - Rechazo

**Características:**
- Diseño responsive con CSS inline
- Branding corporativo
- Información clara y estructurada
- Botones de acción (CTAs)

### 3. Configuración SMTP (`config.py`)
```python
MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
GESTION_HUMANA_EMAIL = os.environ.get('GESTION_HUMANA_EMAIL', 'rrhh@empresa.com')
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@empresa.com')
```

### 4. Integración en Rutas (`app/routes/incapacidades.py`)
- ✅ `registrar()` - Llama a `notificar_nueva_incapacidad()`
- ✅ `validar()` - Llama a `notificar_validacion_completada()` o `notificar_documentos_faltantes()`
- ✅ `aprobar_rechazar()` - Llama a `notificar_aprobacion()` o `notificar_rechazo()`

## Configuración Requerida

### Variables de Entorno
Crear archivo `.env` en la raíz del proyecto:

```bash
# SMTP Configuration (Gmail example)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu_correo@gmail.com
MAIL_PASSWORD=tu_contraseña_aplicacion

# Destinatarios
GESTION_HUMANA_EMAIL=rrhh@empresa.com
ADMIN_EMAIL=admin@empresa.com
```

### Contraseña de Aplicación Gmail
1. Ir a https://myaccount.google.com/security
2. Activar "Verificación en 2 pasos"
3. Ir a "Contraseñas de aplicaciones"
4. Generar nueva contraseña para "Mail"
5. Usar esa contraseña en `MAIL_PASSWORD`

### Instalación
```bash
pip install Flask-Mail==0.9.1
```

## Manejo de Errores

### Estrategia de Resiliencia
```python
try:
    notificar_nueva_incapacidad(incapacidad, current_user)
except Exception as e:
    print(f"Error al enviar notificacion: {e}")
    # No interrumpir el flujo si falla el email
```

**Razón:** Si el servicio de correo falla (SMTP caído, credenciales incorrectas, etc.), la incapacidad se registra de todas formas. El error se registra pero no afecta la operación principal.

### Logs
- Los errores de email se imprimen en consola
- No se muestran al usuario (para evitar confusión)
- La operación principal siempre se completa

## Características Técnicas

### Envío Asíncrono
```python
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

# En cada función de notificación:
Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()
```

**Ventajas:**
- No bloquea la respuesta HTTP
- Mejor experiencia de usuario
- Mayor throughput del servidor

### Seguridad
- ✅ Contraseñas en variables de entorno (no en código)
- ✅ TLS habilitado para SMTP
- ✅ Validación de destinatarios
- ✅ Sanitización de contenido HTML

## Testing

### Probar Configuración SMTP
```bash
python -c "from app.utils.email_service import probar_configuracion; probar_configuracion()"
```

### Probar Notificación Manual
```python
from app import create_app
from app.models import Incapacidad, Usuario
from app.utils.email_service import notificar_nueva_incapacidad

app = create_app()
with app.app_context():
    incap = Incapacidad.query.first()
    user = Usuario.query.first()
    notificar_nueva_incapacidad(incap, user)
```

## Criterios de Aceptación

| # | Criterio | Estado |
|---|----------|--------|
| 1 | Al registrar incapacidad, colaborador recibe email de confirmación | ✅ |
| 2 | Al registrar incapacidad, RRHH recibe email de alerta | ✅ |
| 3 | Al completar validación, colaborador recibe notificación | ✅ |
| 4 | Al solicitar documentos, colaborador recibe lista de faltantes | ✅ |
| 5 | Al aprobar incapacidad, colaborador recibe confirmación | ✅ |
| 6 | Al rechazar incapacidad, colaborador recibe motivo | ✅ |
| 7 | Emails no bloquean la aplicación (asíncronos) | ✅ |
| 8 | Si falla email, la operación principal continúa | ✅ |
| 9 | Emails tienen diseño profesional y responsive | ✅ |
| 10 | Configuración SMTP mediante variables de entorno | ✅ |

## Próximos Pasos (Mejoras Futuras)

### Release 1.1
- [ ] Sistema de cola de emails (Celery + Redis)
- [ ] Reintentos automáticos si falla envío
- [ ] Logs persistentes de emails enviados
- [ ] Dashboard de estado de notificaciones

### Release 1.2
- [ ] Notificaciones SMS adicionales
- [ ] Notificaciones push (web)
- [ ] Preferencias de notificación por usuario
- [ ] Plantillas personalizables por empresa

## Referencias
- [Flask-Mail Documentation](https://pythonhosted.org/Flask-Mail/)
- [Gmail SMTP Settings](https://support.google.com/mail/answer/7126229)
- [Sending Email Asynchronously](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xi-email-support)

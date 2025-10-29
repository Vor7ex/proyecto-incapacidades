# ⚙️ Configuración Técnica y Deployment

**Última actualización:** Octubre 2025  
**Versión:** Release 1.0  

---

## 📋 Tabla de Contenidos

1. [Requisitos del Sistema](#requisitos-del-sistema)
2. [Instalación Detallada](#instalación-detallada)
3. [Configuración de Variables de Entorno](#configuración-de-variables-de-entorno)
4. [Base de Datos](#base-de-datos)
5. [Sistema de Emails](#sistema-de-emails)
6. [Scheduler y Tareas Automáticas](#scheduler-y-tareas-automáticas)
7. [Deployment en Producción](#deployment-en-producción)
8. [Monitoreo y Logs](#monitoreo-y-logs)
9. [Seguridad](#seguridad)
10. [Troubleshooting Avanzado](#troubleshooting-avanzado)

---

## 💻 Requisitos del Sistema

### Hardware Mínimo

- **CPU:** 2 cores
- **RAM:** 4 GB
- **Disco:** 10 GB disponibles
- **Red:** Conexión estable para SMTP

### Software Requerido

- **Python:** 3.8 o superior
- **pip:** 20.0 o superior
- **git:** Para clonar repositorio (opcional)
- **PowerShell/CMD:** Terminal Windows
- **Navegador:** Chrome, Firefox, Edge (versiones recientes)

### Servicios Externos

- **SMTP Server:** Mailtrap (desarrollo) o SendGrid/Gmail (producción)
- **Base de Datos:** SQLite (desarrollo) o PostgreSQL/MySQL (producción)

---

## 🔧 Instalación Detallada

### 1. Preparar Entorno

```powershell
# Clonar repositorio (si aplica)
git clone https://github.com/tu-usuario/proyecto-incapacidades.git
cd proyecto-incapacidades

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
venv\Scripts\activate

# Verificar activación (debe mostrar (venv) en prompt)
```

### 2. Instalar Dependencias

```powershell
# Actualizar pip
python -m pip install --upgrade pip

# Instalar dependencias del proyecto
pip install -r requirements.txt

# Verificar instalación
pip list
```

**Dependencias principales:**
```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Flask-Mail==0.9.1
APScheduler==3.10.4
Werkzeug==3.0.1
email-validator==2.1.0
```

### 3. Configurar Variables de Entorno

```powershell
# Copiar archivo de ejemplo
copy .env.example .env

# Editar .env con tu editor preferido
notepad .env
```

### 4. Inicializar Base de Datos

```powershell
# La BD se crea automáticamente al ejecutar
python run.py

# O manualmente
python -c "from app import create_app, db; app=create_app(); app.app_context().push(); db.create_all(); print('BD creada')"
```

### 5. Crear Usuarios de Prueba

```powershell
python crear_usuarios.py
```

**Salida esperada:**
```
✅ Usuario creado: empleado@test.com (colaborador)
✅ Usuario creado: auxiliar@test.com (auxiliar)
✅ 2 usuarios de prueba creados exitosamente
```

---

## 🔑 Configuración de Variables de Entorno

### Archivo `.env` Completo

```bash
# ============================================
# FLASK - Configuración General
# ============================================
SECRET_KEY=genera-una-clave-secreta-aqui-con-secrets-token-hex-32
FLASK_ENV=development                    # production en producción
DEBUG=True                                # False en producción

# ============================================
# BASE DE DATOS
# ============================================
# SQLite (Desarrollo)
SQLALCHEMY_DATABASE_URI=sqlite:///instance/database.db

# PostgreSQL (Producción - ejemplo)
# SQLALCHEMY_DATABASE_URI=postgresql://usuario:password@localhost:5432/incapacidades_db

# MySQL (Producción - ejemplo)
# SQLALCHEMY_DATABASE_URI=mysql+pymysql://usuario:password@localhost:3306/incapacidades_db

SQLALCHEMY_TRACK_MODIFICATIONS=False
SQLALCHEMY_ECHO=False                     # True para ver queries SQL

# ============================================
# EMAILS - Configuración SMTP
# ============================================
MAIL_ENABLED=False                        # False=simulación, True=envío real
MAIL_SERVER=sandbox.smtp.mailtrap.io
MAIL_PORT=2525
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=tu-usuario-mailtrap
MAIL_PASSWORD=tu-password-mailtrap
MAIL_DEFAULT_SENDER=noreply@empresa.com
MAIL_MAX_EMAILS=None                      # Límite de emails por conexión

# Destinatarios
GESTION_HUMANA_EMAIL=rrhh@empresa.com
COLABORADOR_EMAIL=empleado@empresa.com    # Para pruebas

# Reintentos
EMAIL_MAX_REINTENTOS=3
EMAIL_REINTENTO_DELAY=5                   # segundos

# ============================================
# SCHEDULER - Tareas Automáticas (UC6)
# ============================================
SCHEDULER_ENABLED=False                   # True en producción
SCHEDULER_TIMEZONE=America/Bogota
SCHEDULER_JOB_DEFAULTS={
  "coalesce": False,
  "max_instances": 1
}

# UC6 - Solicitud de Documentos
PLAZO_DOCUMENTOS_DIAS_HABILES=3
MAX_RECORDATORIOS=2
HORA_EJECUCION_SCHEDULER=08:00            # Formato HH:MM

# ============================================
# ARCHIVOS Y UPLOADS
# ============================================
UPLOAD_FOLDER=app/static/uploads
MAX_CONTENT_LENGTH=16777216               # 16 MB en bytes
ALLOWED_EXTENSIONS=pdf,jpg,jpeg,png

# ============================================
# LOGGING
# ============================================
LOG_LEVEL=INFO                            # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE=logs/app.log                     # Archivo de logs (opcional)
LOG_MAX_BYTES=10485760                    # 10 MB
LOG_BACKUP_COUNT=5

# ============================================
# SEGURIDAD
# ============================================
SESSION_COOKIE_SECURE=False               # True en producción con HTTPS
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
PERMANENT_SESSION_LIFETIME=3600           # 1 hora en segundos

# ============================================
# DESARROLLO
# ============================================
TESTING=False
```

### Generar SECRET_KEY Segura

```python
# Ejecutar en Python
import secrets
print(secrets.token_hex(32))
# Copiar salida a .env
```

---

## 🗄️ Base de Datos

### Modelos de Datos

#### Usuario
```python
class Usuario(db.Model):
    id: int (PK)
    nombre: str(100)
    apellido: str(100)
    email: str(120) [UNIQUE]
    password_hash: str(200)
    rol: str(20)  # 'colaborador' | 'auxiliar'
    email_notificaciones: bool
    activo: bool
    fecha_registro: datetime
```

#### Incapacidad
```python
class Incapacidad(db.Model):
    id: int (PK)
    codigo_radicacion: str(50) [UNIQUE]
    usuario_id: int (FK → Usuario)
    tipo: str(50)
    fecha_inicio: date
    fecha_fin: date
    dias: int
    diagnostico: text
    estado: str(50)
    motivo_rechazo: text
    fecha_registro: datetime
    fecha_validacion: datetime
    fecha_aprobacion: datetime
```

#### Documento
```python
class Documento(db.Model):
    id: int (PK)
    incapacidad_id: int (FK → Incapacidad)
    tipo_documento: str(50)
    nombre_original: str(200)
    nombre_unico: str(200)
    ruta: str(300)
    mime_type: str(100)
    tamanio_bytes: int
    hash_md5: str(32)
    uuid: str(36) [UNIQUE]
    fecha_carga: datetime
```

#### SolicitudDocumento (UC6)
```python
class SolicitudDocumento(db.Model):
    id: int (PK)
    incapacidad_id: int (FK → Incapacidad)
    tipo_documento: str(50)
    estado: str(30)  # PENDIENTE | ENTREGADO | REQUIERE_CITACION
    fecha_solicitud: datetime
    fecha_vencimiento: datetime
    fecha_entrega: datetime
    ultima_notificacion: datetime
    numero_recordatorios: int
    solicitado_por_id: int (FK → Usuario)
    observaciones_auxiliar: text
    observaciones_colaborador: text
```

### Migraciones (SQLAlchemy)

```python
# Crear nueva migración
from app import create_app, db
app = create_app()
app.app_context().push()

# Crear todas las tablas
db.create_all()

# Eliminar todas las tablas (CUIDADO)
db.drop_all()

# Recrear desde cero
db.drop_all()
db.create_all()
```

### Respaldo y Restauración (SQLite)

```powershell
# Respaldo
copy instance\database.db instance\database_backup_$(Get-Date -Format "yyyyMMdd_HHmmss").db

# Restauración
copy instance\database_backup_20251028_143000.db instance\database.db
```

### Migración a PostgreSQL (Producción)

```bash
# 1. Instalar psycopg2
pip install psycopg2-binary

# 2. Crear base de datos en PostgreSQL
psql -U postgres
CREATE DATABASE incapacidades_db;
CREATE USER incapacidades_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE incapacidades_db TO incapacidades_user;

# 3. Actualizar .env
SQLALCHEMY_DATABASE_URI=postgresql://incapacidades_user:password@localhost:5432/incapacidades_db

# 4. Ejecutar app para crear tablas
python run.py
```

---

## 📧 Sistema de Emails

### Configuración de Mailtrap (Desarrollo)

1. **Crear cuenta:** https://mailtrap.io (plan gratuito: 100 emails/mes)
2. **Obtener credenciales:**
   - Ir a **My Inbox**
   - Click en **Show Credentials**
   - Copiar `Username` y `Password`

3. **Configurar .env:**
```bash
MAIL_ENABLED=True
MAIL_SERVER=sandbox.smtp.mailtrap.io
MAIL_PORT=2525
MAIL_USERNAME=tu-username-aqui
MAIL_PASSWORD=tu-password-aqui
```

### Configuración de SendGrid (Producción)

1. **Crear cuenta:** https://sendgrid.com (100 emails/día gratis)
2. **Generar API Key:**
   - Settings → API Keys → Create API Key
   - Copiar la key generada

3. **Configurar .env:**
```bash
MAIL_ENABLED=True
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=apikey
MAIL_PASSWORD=SG.tu-api-key-aqui
```

### Configuración de Gmail (Alternativa)

1. **Habilitar verificación en 2 pasos** en cuenta Gmail
2. **Generar contraseña de aplicación:**
   - Google Account → Security → App passwords
   - Generar contraseña para "Mail"

3. **Configurar .env:**
```bash
MAIL_ENABLED=True
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu-email@gmail.com
MAIL_PASSWORD=contraseña-de-aplicacion
```

### Control de Emails

```powershell
# Script de control
python toggle_email.py status    # Ver estado actual
python toggle_email.py on        # Activar envío real
python toggle_email.py off       # Modo simulación

# Verificar configuración
python -c "from app.utils.email_service import verificar_configuracion; verificar_configuracion()"
```

### Sistema de Reintentos

Configurado en `app/utils/email_service.py`:

```python
def send_async_email(app, msg, reintentos=EMAIL_MAX_REINTENTOS):
    intento = 1
    while intento <= reintentos:
        try:
            with app.app_context():
                mail.send(msg)
            logger.info(f"✅ Email enviado: {msg.subject}")
            return True
        except Exception as e:
            if intento < reintentos:
                logger.warning(f"⚠️ Reintento {intento}/{reintentos}...")
                time.sleep(EMAIL_REINTENTO_DELAY)
                intento += 1
            else:
                logger.error(f"❌ Error definitivo: {str(e)}")
                return False
```

---

## ⏰ Scheduler y Tareas Automáticas

### Configuración de APScheduler

En `app/tasks/scheduler_uc6.py`:

```python
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.solicitud_documentos_service import SolicitudDocumentosService

def iniciar_scheduler(app):
    """Inicia el scheduler de tareas automáticas"""
    if not app.config.get('SCHEDULER_ENABLED', False):
        print("⚠️ Scheduler DESACTIVADO (SCHEDULER_ENABLED=False)")
        return None
    
    scheduler = BackgroundScheduler(
        timezone=app.config.get('SCHEDULER_TIMEZONE', 'America/Bogota')
    )
    
    # Tarea: Procesar recordatorios de UC6
    hora = app.config.get('HORA_EJECUCION_SCHEDULER', '08:00')
    hora_split = hora.split(':')
    
    scheduler.add_job(
        func=lambda: procesar_recordatorios_job(app),
        trigger='cron',
        hour=int(hora_split[0]),
        minute=int(hora_split[1]),
        id='procesar_recordatorios_documentos',
        name='UC6: Procesar recordatorios de documentos',
        replace_existing=True
    )
    
    scheduler.start()
    print(f"✅ Scheduler iniciado - Tarea diaria a las {hora}")
    return scheduler
```

### Activar en Producción

```bash
# En .env
SCHEDULER_ENABLED=True
HORA_EJECUCION_SCHEDULER=08:00
SCHEDULER_TIMEZONE=America/Bogota
```

### Verificar Ejecución

```python
# Ver tareas programadas
from app.tasks.scheduler_uc6 import scheduler
if scheduler:
    for job in scheduler.get_jobs():
        print(f"Job: {job.name}, Next run: {job.next_run_time}")
```

### Ejecutar Tarea Manualmente (Testing)

```python
from app.tasks.scheduler_uc6 import ejecutar_tarea_manual

# Ejecutar procesamiento de recordatorios
resultado = ejecutar_tarea_manual('procesar_recordatorios')
print(f"Resultado: {resultado}")
```

---

## 🚀 Deployment en Producción

### Opción 1: Gunicorn (Recomendado)

```bash
# 1. Instalar Gunicorn
pip install gunicorn

# 2. Ejecutar
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"

# Opciones:
# -w 4: 4 workers (2 x CPU cores)
# -b: bind address
# --timeout 120: timeout de 120s
# --access-logfile -: logs de acceso
```

**Configurar como servicio (systemd):**

```ini
# /etc/systemd/system/incapacidades.service
[Unit]
Description=Sistema de Incapacidades
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/incapacidades
Environment="PATH=/var/www/incapacidades/venv/bin"
ExecStart=/var/www/incapacidades/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Habilitar e iniciar servicio
sudo systemctl enable incapacidades
sudo systemctl start incapacidades
sudo systemctl status incapacidades
```

### Opción 2: Nginx + Gunicorn

```nginx
# /etc/nginx/sites-available/incapacidades
server {
    listen 80;
    server_name incapacidades.empresa.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/incapacidades/app/static;
        expires 30d;
    }

    client_max_body_size 16M;
}
```

### Opción 3: Docker

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_ENV=production
ENV SCHEDULER_ENABLED=True

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:create_app()"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - SQLALCHEMY_DATABASE_URI=postgresql://user:pass@db:5432/incapacidades
      - MAIL_ENABLED=True
      - SCHEDULER_ENABLED=True
    volumes:
      - ./instance:/app/instance
      - ./app/static/uploads:/app/app/static/uploads
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: incapacidades
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## 📊 Monitoreo y Logs

### Configuración de Logging

En `config.py`:

```python
import logging
from logging.handlers import RotatingFileHandler
import os

def configurar_logging(app):
    """Configurar logging del sistema"""
    if not app.debug:
        # Crear directorio de logs si no existe
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # Handler de archivo con rotación
        file_handler = RotatingFileHandler(
            'logs/incapacidades.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Sistema de Incapacidades iniciado')
```

### Logs Estructurados

```python
# Ejemplo de logging en código
import logging
logger = logging.getLogger(__name__)

# En funciones
logger.info(f"✅ UC1: Incapacidad #{incapacidad.id} registrada")
logger.warning(f"⚠️ UC6: Recordatorio no enviado - Email inválido")
logger.error(f"❌ UC2: Error al enviar email: {str(e)}")
```

### Monitoreo de Tareas Programadas

```python
# Script de monitoreo
from app.tasks.scheduler_uc6 import scheduler

if scheduler:
    print("📊 Estado del Scheduler:")
    print(f"  Running: {scheduler.running}")
    print(f"  Jobs: {len(scheduler.get_jobs())}")
    
    for job in scheduler.get_jobs():
        print(f"\n  📋 Job: {job.name}")
        print(f"     ID: {job.id}")
        print(f"     Next run: {job.next_run_time}")
        print(f"     Trigger: {job.trigger}")
```

### Métricas en Tiempo Real

```python
# Dashboard de métricas (ejemplo)
from app.models import Incapacidad, Usuario, SolicitudDocumento
from sqlalchemy import func

def obtener_metricas():
    return {
        'total_incapacidades': Incapacidad.query.count(),
        'pendientes_validacion': Incapacidad.query.filter_by(
            estado='PENDIENTE_VALIDACION'
        ).count(),
        'doc_incompletas': Incapacidad.query.filter_by(
            estado='DOCUMENTACION_INCOMPLETA'
        ).count(),
        'solicitudes_activas': SolicitudDocumento.query.filter_by(
            estado='PENDIENTE'
        ).count(),
        'usuarios_activos': Usuario.query.filter_by(activo=True).count()
    }
```

---

## 🔒 Seguridad

### HTTPS en Producción

```bash
# Instalar Certbot (Let's Encrypt)
sudo apt install certbot python3-certbot-nginx

# Obtener certificado SSL
sudo certbot --nginx -d incapacidades.empresa.com

# Renovación automática
sudo certbot renew --dry-run
```

### Headers de Seguridad

En `app/__init__.py`:

```python
from flask_talisman import Talisman

def create_app():
    app = Flask(__name__)
    
    if app.config['ENV'] == 'production':
        # Configurar HTTPS y headers de seguridad
        Talisman(app, 
            force_https=True,
            strict_transport_security=True,
            content_security_policy={
                'default-src': "'self'",
                'script-src': ["'self'", "'unsafe-inline'", 'cdn.jsdelivr.net'],
                'style-src': ["'self'", "'unsafe-inline'", 'cdn.jsdelivr.net'],
            }
        )
    
    return app
```

### Rate Limiting

```python
# Instalar
pip install Flask-Limiter

# Configurar
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Aplicar a rutas específicas
@incapacidades_bp.route('/registrar', methods=['POST'])
@limiter.limit("10 per hour")
def registrar():
    # ...
```

### Validación de Archivos

```python
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16 MB

def archivo_permitido(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validar_tamano(file):
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    return size <= MAX_FILE_SIZE
```

---

## 🛠️ Troubleshooting Avanzado

### Problema: Base de datos bloqueada (SQLite)

```python
# Solución temporal
import sqlite3
conn = sqlite3.connect('instance/database.db', timeout=30)
conn.close()

# Solución permanente: Migrar a PostgreSQL
```

### Problema: Scheduler ejecuta múltiples veces

```python
# En scheduler_uc6.py, verificar:
scheduler.add_job(
    # ...
    coalesce=True,  # Combinar ejecuciones perdidas
    max_instances=1  # Solo 1 instancia a la vez
)
```

### Problema: Emails en spam

**Configurar SPF, DKIM, DMARC:**

```dns
; SPF Record
@ IN TXT "v=spf1 include:_spf.google.com ~all"

; DKIM (desde SendGrid)
default._domainkey IN TXT "v=DKIM1; k=rsa; p=..."

; DMARC
_dmarc IN TXT "v=DMARC1; p=quarantine; rua=mailto:dmarc@empresa.com"
```

### Problema: Archivos grandes provocan timeout

```python
# Usar streaming para archivos grandes
from werkzeug.wsgi import FileWrapper

@app.route('/download/<int:doc_id>')
def download(doc_id):
    # ...
    return send_file(
        ruta,
        as_attachment=True,
        download_name=documento.nombre_original,
        max_age=0
    )
```

### Problema: Sesiones expiran muy rápido

```python
# En .env
PERMANENT_SESSION_LIFETIME=86400  # 24 horas

# En login
@auth_bp.route('/login', methods=['POST'])
def login():
    # ...
    login_user(usuario, remember=True)
    session.permanent = True
```

---

## 📚 Recursos Adicionales

### Documentación Oficial

- Flask: https://flask.palletsprojects.com/
- SQLAlchemy: https://www.sqlalchemy.org/
- APScheduler: https://apscheduler.readthedocs.io/
- Bootstrap 5: https://getbootstrap.com/

### Herramientas Recomendadas

- **DB Browser for SQLite:** Explorar base de datos
- **Postman:** Testing de API
- **PM2:** Gestor de procesos (alternativa a systemd)
- **Sentry:** Monitoreo de errores
- **Prometheus + Grafana:** Métricas y dashboards

---

**🎉 Sistema configurado y listo para deployment!**

Para guía de usuario, ver `MANUAL_USUARIO.md`

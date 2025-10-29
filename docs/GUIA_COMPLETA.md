# 📘 Guía Completa del Sistema de Incapacidades

**Última actualización:** Octubre 2025  
**Versión:** Release 1.0  
**Estado:** 95% Completo

---

## 📋 Tabla de Contenidos

1. [Inicio Rápido](#inicio-rápido)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Casos de Uso Implementados](#casos-de-uso-implementados)
4. [Roles y Permisos](#roles-y-permisos)
5. [Manual de Usuario](#manual-de-usuario)
6. [Configuración](#configuración)

---

## 🚀 Inicio Rápido

### Instalación en 5 Minutos

```powershell
# 1. Activar entorno virtual
venv\Scripts\activate

# 2. Instalar dependencias (solo primera vez)
pip install -r requirements.txt

# 3. Crear usuarios de prueba
python crear_usuarios.py

# 4. Desactivar emails para desarrollo
python toggle_email.py off

# 5. Ejecutar aplicación
python run.py

# 6. Abrir navegador: http://localhost:5000
```

### Credenciales de Acceso

| Rol | Email | Contraseña | Permisos |
|-----|-------|------------|----------|
| Colaborador | `empleado@test.com` | `123456` | Registrar y consultar propias incapacidades |
| Auxiliar RRHH | `auxiliar@test.com` | `123456` | Validar, aprobar/rechazar todas las incapacidades |

---

## 🏗️ Arquitectura del Sistema

### Stack Tecnológico

- **Backend:** Flask 3.0.0 (Python 3.8+)
- **ORM:** Flask-SQLAlchemy 3.1.1
- **Autenticación:** Flask-Login 0.6.3
- **Notificaciones:** Flask-Mail 0.9.1
- **Tareas programadas:** APScheduler 3.10.4
- **Base de Datos:** SQLite
- **Frontend:** Bootstrap 5 + JavaScript vanilla

### Estructura del Proyecto

```
proyecto-incapacidades/
├── app/
│   ├── models/                 # Modelos de datos
│   │   ├── usuario.py          # Usuario con roles
│   │   ├── incapacidad.py      # Incapacidad principal
│   │   ├── documento.py        # Documentos adjuntos
│   │   ├── solicitud_documento.py  # UC6: Solicitudes de docs
│   │   └── notificacion.py     # Sistema de notificaciones
│   ├── routes/                 # Controladores
│   │   ├── auth.py             # Login/Logout
│   │   ├── incapacidades.py    # CRUD incapacidades
│   │   └── documentos.py       # Gestión de archivos
│   ├── services/               # Lógica de negocio
│   │   └── solicitud_documentos_service.py  # UC6
│   ├── tasks/                  # Tareas programadas
│   │   └── scheduler_uc6.py    # Recordatorios automáticos
│   ├── utils/                  # Utilidades
│   │   ├── email_service.py    # Sistema de emails
│   │   ├── validaciones.py     # Validaciones de negocio
│   │   ├── maquina_estados.py  # Transiciones de estado
│   │   └── calendario.py       # Días hábiles
│   ├── templates/              # Vistas HTML
│   │   └── emails/             # 7 templates de email
│   └── static/
│       ├── css/styles.css      # Estilos personalizados
│       ├── js/main.js          # Validaciones client-side
│       └── uploads/            # Documentos (NO versionar)
├── docs/
│   ├── CASOS_DE_USO.md         # 16 casos de uso detallados
│   ├── GUIA_COMPLETA.md        # Este archivo
│   ├── CONFIGURACION_TECNICA.md  # Setup y deployment
│   └── MANUAL_USUARIO.md       # Guía para usuarios finales
├── instance/
│   └── database.db             # SQLite (NO versionar)
├── .env                        # Variables de entorno
├── config.py                   # Configuración Flask
├── run.py                      # Ejecutar aplicación
└── requirements.txt            # Dependencias
```

---

## 📊 Casos de Uso Implementados

### Release 1.0 (Actual)

| UC | Nombre | Estado | % | Descripción |
|----|--------|--------|---|-------------|
| **UC1** | Registrar incapacidad | ✅ | 100% | Registro con documentos, código de radicación, validación client-side |
| **UC2** | Notificar RRHH y líder | ✅ | 85% | Sistema de emails con reintentos, logging detallado |
| **UC3** | Consultar incapacidades | ✅ | 100% | Vista colaborador de sus incapacidades con filtros |
| **UC4** | Validar documentación | ✅ | 100% | Checklist automático + validación manual |
| **UC5** | Verificar requisitos por tipo | ✅ | 100% | Reglas automáticas según tipo de incapacidad |
| **UC6** | Solicitar documentos faltantes | ✅ | 95% | Scheduler automático, recordatorios escalados |
| **UC7** | Aprobar/Rechazar | ✅ | 100% | Aprobación con motivos, notificaciones |
| **UC15** | Almacenar documentos | ✅ | 70% | Almacenamiento con metadatos (UUID, MD5) |

### Módulo de Seguimiento (Release 2.0)

| UC | Nombre | Estado | Descripción |
|----|--------|--------|-------------|
| **UC8** | Actualizar estado | 📄 | Transiciones de estado con trazabilidad |
| **UC9** | Consultar radicación | 📄 | Dashboard de seguimiento por entidad |
| **UC10** | Generar reporte | 📄 | Reportes de seguimiento con filtros |
| **UC11** | Ver incapacidades del equipo | 📄 | Vista para líder inmediato |

### Módulo de Conciliación (Release 3.0)

| UC | Nombre | Estado | Descripción |
|----|--------|--------|-------------|
| **UC12** | Registrar pago EPS/ARL | 📄 | Registro de pagos recibidos |
| **UC13** | Conciliar pagos | 📄 | Conciliación mensual |
| **UC14** | Reporte pagos pendientes | 📄 | Dashboard financiero |

### Módulo de Gestión Documental

| UC | Nombre | Estado | Descripción |
|----|--------|--------|-------------|
| **UC16** | Descargar incapacidad completa | 📄 | Descarga individual o ZIP organizado |

---

## 🔐 Roles y Permisos

### 👤 Colaborador

**Casos de uso:**
- ✅ Registrar incapacidad (UC1)
- ✅ Consultar mis incapacidades (UC3)
- ✅ Ver detalle de incapacidad (solo propias)
- ✅ Cargar documentos solicitados (UC6)

**Restricciones:**
- ❌ No puede ver incapacidades de otros colaboradores
- ❌ No puede cambiar estados
- ❌ No puede acceder a dashboard auxiliar

### 👨‍💼 Auxiliar de Gestión Humana

**Casos de uso:**
- ✅ Validar documentación (UC4, UC5)
- ✅ Solicitar documentos faltantes (UC6)
- ✅ Aprobar/Rechazar incapacidades (UC7)
- ✅ Ver todas las incapacidades
- ✅ Dashboard con estadísticas
- ✅ Descargar documentos

**Permisos especiales:**
- ✅ Acceso completo a todas las incapacidades
- ✅ Cambiar estados de incapacidades
- ✅ Generar reportes
- ✅ Ver métricas del sistema

---

## 📱 Manual de Usuario

### Para Colaboradores

#### 1. Registrar una Incapacidad

1. **Acceder al sistema:**
   - Ir a http://localhost:5000
   - Login con `empleado@test.com` / `123456`

2. **Ir a "Registrar Incapacidad"**

3. **Completar el formulario:**
   - **Tipo:** Seleccionar (Enfermedad general, Accidente laboral, etc.)
   - **Fechas:** Inicio y fin de la incapacidad
   - **Días:** Se calculan automáticamente
   - **Certificado:** PDF o imagen (obligatorio)
   - **Epicrisis:** Solo si es >2 días o accidente
   - **FURIPS:** Solo para accidentes de tránsito

4. **Verificar previews:**
   - Se muestran miniaturas de archivos cargados
   - Validación en tiempo real (tamaño, formato)

5. **Enviar formulario:**
   - Clic en "Registrar Incapacidad"
   - Ver modal con código de radicación
   - **Guardar código:** `INC-YYYYMMDD-XXXX`

6. **Confirmaciones:**
   - ✅ Email de confirmación
   - ✅ Notificación a Gestión Humana
   - ✅ Incapacidad visible en "Mis Incapacidades"

#### 2. Consultar Mis Incapacidades

1. Ir a "Mis Incapacidades"
2. Ver tabla con todas tus incapacidades
3. **Estados posibles:**
   - ⏳ **Pendiente Validación:** RRHH revisando documentos
   - 📄 **Documentación Incompleta:** Faltan documentos (ver email)
   - ✅ **Pendiente Validación** (después de cargar): RRHH re-validando
   - ✅ **Aprobada:** Incapacidad aprobada
   - ❌ **Rechazada:** No cumple requisitos (ver motivo)

4. **Acciones disponibles:**
   - 👁️ **Ver Detalle:** Información completa
   - 📄 **Descargar Documentos:** PDFs adjuntos

#### 3. Cargar Documentos Solicitados (UC6)

**Cuando RRHH solicita documentos faltantes:**

1. **Recibir email:**
   ```
   📄 Documentos Solicitados - Incapacidad #INC-20251028-A3F2
   
   Para continuar con la validación, necesitamos:
   - FURIPS
   - Epicrisis actualizada
   
   Plazo: 3 días hábiles (hasta 31/10/2025)
   ```

2. **Cargar documentos:**
   - Clic en enlace del email
   - O ir a "Mis Incapacidades" → "Cargar Documentos"
   - Subir archivos solicitados
   - **Importante:** Cargar TODOS los documentos antes del plazo

3. **Recordatorios automáticos:**
   - **Día 3:** Recordatorio si no has cargado
   - **Día 6:** Segunda notificación (última llamada)
   - **Después de día 6:** Requiere citación presencial

4. **Confirmación:**
   - Email de "Documentación Completada"
   - Estado regresa a "Pendiente Validación"
   - RRHH re-valida documentos

---

### Para Auxiliares de Gestión Humana

#### 1. Dashboard

1. Login con `auxiliar@test.com` / `123456`
2. **Ver dashboard con:**
   - 📊 Total de incapacidades pendientes
   - 📝 Incapacidades en revisión
   - ✅ Aprobadas este mes
   - ❌ Rechazadas este mes

#### 2. Validar Documentación (UC4, UC5)

1. **Ir a "Validar Incapacidades"**
2. **Seleccionar incapacidad "Pendiente Validación"**
3. **Checklist automático (UC5):**
   - ✅ Certificado de incapacidad (obligatorio)
   - ✅/❌ Epicrisis (según tipo y días)
   - ✅/❌ FURIPS (si es accidente de tránsito)
   - ✅/❌ Documentos de maternidad/paternidad

4. **Revisión manual:**
   - Descargar y abrir cada documento
   - Verificar legibilidad
   - Verificar coherencia de fechas
   - Verificar que sean documentos originales

5. **Decisión:**
   - **Documentación completa:**
     - Marcar como "Documentación Completa"
     - Pasar a aprobar/rechazar (UC7)
   - **Documentación incompleta:**
     - Ir a "Solicitar Documentos" (UC6)

#### 3. Solicitar Documentos Faltantes (UC6)

1. **En vista de validación:**
   - Clic en "Solicitar Documentos Faltantes"

2. **Formulario de solicitud:**
   - Seleccionar documentos faltantes del checklist
   - Agregar observaciones específicas:
     ```
     FURIPS: Requerido para accidente de tránsito
     Epicrisis: Documento ilegible, enviar copia clara
     ```

3. **Confirmar solicitud:**
   - Sistema calcula plazo de 3 días hábiles
   - Email automático al colaborador
   - Estado cambia a "Documentación Incompleta"

4. **Seguimiento automático:**
   - **Día 3:** Sistema envía recordatorio (08:00 AM)
   - **Día 6:** Sistema envía 2da notificación (08:00 AM)
   - **Si no responde:** Estado → "Requiere Citación"

5. **Cuando colaborador carga documentos:**
   - Recibes email "Documentación Completada"
   - Incapacidad regresa a "Pendiente Validación"
   - Re-validar documentos

#### 4. Aprobar o Rechazar (UC7)

1. **Ir a "Aprobar/Rechazar"**
2. **Solo incapacidades "Documentación Completa"**

3. **Aprobar:**
   - Clic en "Aprobar Incapacidad"
   - Estado → "Aprobada - Pendiente Transcripción"
   - Email de aprobación al colaborador

4. **Rechazar:**
   - Clic en "Rechazar Incapacidad"
   - **Seleccionar motivo:**
     - Certificado no original
     - Fechas incoherentes
     - Documentación falsa
     - Extemporánea (fuera de plazo)
     - Otro (especificar)
   - Agregar observaciones detalladas
   - Confirmar rechazo
   - Estado → "Rechazada"
   - Email de rechazo al colaborador con motivo

---

## ⚙️ Configuración

### Variables de Entorno (.env)

```bash
# === Flask ===
SECRET_KEY=tu-clave-secreta-generada
FLASK_ENV=development

# === Base de Datos ===
SQLALCHEMY_DATABASE_URI=sqlite:///instance/database.db

# === Emails ===
MAIL_ENABLED=False                      # False = simulación, True = envío real
MAIL_SERVER=sandbox.smtp.mailtrap.io
MAIL_PORT=2525
MAIL_USE_TLS=True
MAIL_USERNAME=tu-usuario-mailtrap
MAIL_PASSWORD=tu-password-mailtrap
MAIL_DEFAULT_SENDER=noreply@empresa.com
GESTION_HUMANA_EMAIL=rrhh@empresa.com

# === Reintentos de Email ===
EMAIL_MAX_REINTENTOS=3                  # Número de reintentos
EMAIL_REINTENTO_DELAY=5                 # Segundos entre reintentos

# === Scheduler (UC6) ===
SCHEDULER_ENABLED=False                 # True en producción
PLAZO_DOCUMENTOS_DIAS_HABILES=3
MAX_RECORDATORIOS=2

# === Logging ===
LOG_LEVEL=INFO                          # DEBUG, INFO, WARNING, ERROR

# === Archivos ===
MAX_CONTENT_LENGTH=16777216             # 16MB
UPLOAD_FOLDER=app/static/uploads
```

### Control de Emails

```powershell
# Ver estado actual
python toggle_email.py status

# Desactivar (modo desarrollo - recomendado)
python toggle_email.py off

# Activar (pruebas reales)
python toggle_email.py on
```

**Modo OFF (desarrollo):**
- ❌ No envía emails reales
- ✅ Muestra logs en consola
- ✅ Ahorra cuota de Mailtrap (100 emails/mes)
- ✅ Desarrollo más rápido

**Modo ON (testing/producción):**
- ✅ Envía emails reales
- 📧 Consume cuota

---

## 🔥 Flujos Completos

### Flujo Exitoso (Sin Documentos Faltantes)

```
1. Colaborador registra incapacidad
   ├─ Carga: certificado + epicrisis
   ├─ Recibe código: INC-20251028-A3F2
   └─ Email de confirmación
   
2. Auxiliar valida (mismo día)
   ├─ Checklist automático: ✅ Todo completo
   ├─ Revisión manual: ✅ Documentos válidos
   └─ Estado → "Documentación Completa"
   
3. Auxiliar aprueba
   ├─ Estado → "Aprobada"
   └─ Email de aprobación al colaborador
   
⏱️ Tiempo total: < 1 día
```

### Flujo con Documentos Faltantes (UC6)

```
1. Colaborador registra incapacidad
   ├─ Carga: solo certificado
   ├─ Falta: FURIPS (accidente de tránsito)
   └─ Email de confirmación
   
2. Auxiliar valida (día 0)
   ├─ Checklist automático: ❌ Falta FURIPS
   ├─ Solicita FURIPS con plazo 3 días
   └─ Estado → "Documentación Incompleta"
   
3. Colaborador recibe email (día 0)
   ├─ "Documentos Solicitados"
   └─ Plazo: hasta día 3
   
4. Colaborador NO carga (día 1-2)
   └─ Sin acción
   
5. Sistema envía recordatorio (día 3, 08:00 AM)
   ├─ Email: "RECORDATORIO - Urgente"
   └─ Plazo vencido
   
6. Colaborador carga FURIPS (día 4)
   ├─ Estado → "Pendiente Validación"
   └─ Email "Documentación Completada" a auxiliar
   
7. Auxiliar re-valida (día 4)
   ├─ Checklist: ✅ FURIPS ahora presente
   └─ Estado → "Documentación Completa"
   
8. Auxiliar aprueba (día 5)
   ├─ Estado → "Aprobada"
   └─ Email de aprobación
   
⏱️ Tiempo total: 5 días
```

### Flujo de Rechazo

```
1. Colaborador registra incapacidad
   └─ Carga: certificado con fecha alterada
   
2. Auxiliar valida
   ├─ Detecta: fechas incoherentes
   └─ Rechaza con motivo: "Fechas incoherentes en certificado"
   
3. Colaborador recibe email
   ├─ Motivo: "Fechas incoherentes"
   ├─ Observaciones: "La fecha de inicio no coincide..."
   └─ Estado: "Rechazada"
   
⏱️ Tiempo total: 1-2 días
```

---

## 📧 Sistema de Notificaciones

### Templates de Email

| Template | Trigger | Destinatarios |
|----------|---------|---------------|
| **confirmacion_registro.html** | UC1: Registro exitoso | Colaborador |
| **notificacion_gestion_humana.html** | UC1: Registro exitoso | RRHH + Líder |
| **validacion_completada.html** | UC4: Documentación completa | Colaborador |
| **documentos_faltantes.html** | UC6: Solicitud inicial | Colaborador |
| **recordatorio_documentos_dia2.html** | UC6: Día 3 (1er recordatorio) | Colaborador |
| **segunda_notificacion_documentos.html** | UC6: Día 6 (última llamada) | Colaborador |
| **documentacion_completada.html** | UC6: Colaborador carga docs | Auxiliar |
| **incapacidad_aprobada.html** | UC7: Aprobación | Colaborador |
| **incapacidad_rechazada.html** | UC7: Rechazo | Colaborador |

### Características del Sistema de Emails

- ✅ **Reintentos automáticos:** 3 intentos con delay de 5s
- ✅ **Logging detallado:** Registro de envíos exitosos y fallidos
- ✅ **Batch con delay:** 10s entre emails para evitar rate limit
- ✅ **Validación de destinatarios:** No envía sin email válido
- ✅ **Modo simulación:** Ver emails en consola sin enviar
- ✅ **Código de radicación:** Incluido en subjects para trazabilidad

---

## 🛠️ Comandos Útiles

### Desarrollo

```powershell
# Activar entorno
venv\Scripts\activate

# Ejecutar aplicación
python run.py

# Crear/Recrear usuarios de prueba
python crear_usuarios.py

# Ver estado de emails
python toggle_email.py status
```

### Testing

```powershell
# Ejecutar todos los tests
python -m pytest tests/ -v

# Tests específicos
python -m pytest tests/test_notificaciones_uc6.py -v
python -m pytest tests/test_uc6_completo_e2e.py -v

# Con cobertura
python -m pytest tests/ --cov=app --cov-report=html
```

### Mantenimiento

```powershell
# Limpiar cache
Remove-Item -Recurse -Force **\__pycache__

# Ver logs en tiempo real (filtrados)
python run.py | Select-String "UC2|UC6|UC15"

# Verificar estructura de BD
python -c "from app import create_app, db; app=create_app(); app.app_context().push(); print(db.metadata.tables.keys())"
```

---

## 📊 Métricas del Proyecto

### Completitud por Módulo

| Módulo | UC's | Completitud | Estado |
|--------|------|-------------|--------|
| **Registro** | UC1, UC2, UC3 | 95% | ✅ Completo |
| **Validación** | UC4, UC5, UC6, UC7 | 98% | ✅ Completo |
| **Seguimiento** | UC8, UC9, UC10, UC11 | 0% | 📄 Documentado |
| **Conciliación** | UC12, UC13, UC14 | 0% | 📄 Documentado |
| **Gestión Documental** | UC15, UC16 | 70% | ⚠️ Parcial |

### Estadísticas de Código

- **Líneas de código Python:** ~8,500
- **Templates HTML:** 15 archivos
- **Tests:** 40+ tests pasando
- **Cobertura:** ~75%
- **Modelos de datos:** 7 modelos
- **Rutas:** 25+ endpoints

---

## 🐛 Troubleshooting

### Problema: No se envían emails

**Solución:**
```powershell
# 1. Verificar estado
python toggle_email.py status

# 2. Si está OFF, activar
python toggle_email.py on

# 3. Verificar credenciales en .env
# MAIL_USERNAME y MAIL_PASSWORD correctos

# 4. Reiniciar aplicación
python run.py
```

### Problema: Archivos no se cargan

**Verificar:**
1. Carpeta `app/static/uploads/` existe
2. Permisos de escritura
3. Tamaño < 16MB
4. Formato: PDF, JPG, PNG

### Problema: Scheduler no ejecuta tareas

**Solución:**
```python
# En .env
SCHEDULER_ENABLED=True

# Verificar logs en consola
# Buscar: "🔄 Iniciando tarea programada"
```

### Problema: Base de datos corrupta

**Recrear BD:**
```powershell
# 1. Respaldar datos si es necesario
copy instance\database.db instance\database.db.backup

# 2. Eliminar BD
Remove-Item instance\database.db

# 3. Ejecutar app (recrea BD automáticamente)
python run.py

# 4. Recrear usuarios
python crear_usuarios.py
```

---

## 📚 Recursos Adicionales

### Documentación

- **CASOS_DE_USO.md:** Especificación completa de 16 casos de uso
- **CONFIGURACION_TECNICA.md:** Setup detallado y deployment
- **MANUAL_USUARIO.md:** Guía paso a paso para usuarios finales

### Scripts Disponibles

- `run.py` - Ejecutar aplicación
- `crear_usuarios.py` - Crear usuarios de prueba
- `toggle_email.py` - Control on/off de emails
- `migrate_*.py` - Scripts de migración de datos

---

## ✅ Checklist de Deployment

### Pre-Producción

- [ ] Tests pasando (100%)
- [ ] `.env` configurado para producción
- [ ] `MAIL_ENABLED=True`
- [ ] `SCHEDULER_ENABLED=True`
- [ ] `FLASK_ENV=production`
- [ ] `SECRET_KEY` segura generada
- [ ] Credenciales SMTP de producción
- [ ] Base de datos en servidor externo (no SQLite)

### Producción

- [ ] HTTPS configurado
- [ ] Backups automáticos de BD
- [ ] Monitoring de logs
- [ ] Rate limiting configurado
- [ ] CORS configurado si aplica
- [ ] Firewall configurado
- [ ] Dominio configurado
- [ ] Certificado SSL válido

---

**🎉 ¡Sistema listo para usar!**

Para más información técnica, ver `CONFIGURACION_TECNICA.md`

# ✅ Checklist de Instalación y Configuración - UC2

Usa este checklist para verificar que el sistema de notificaciones está correctamente configurado.

---

## 📦 1. Dependencias

### Instalar Flask-Mail
```bash
pip install Flask-Mail==0.9.1
```

**Verificar:**
```bash
pip list | grep Flask-Mail
```

✅ Debería mostrar: `Flask-Mail 0.9.1`

---

## 🔧 2. Configuración SMTP

### Crear archivo `.env`

1. **Copiar plantilla:**
   ```bash
   copy .env.example .env
   ```

2. **Editar `.env` con credenciales reales:**
   ```bash
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=tu_correo@gmail.com
   MAIL_PASSWORD=xxxx xxxx xxxx xxxx
   GESTION_HUMANA_EMAIL=rrhh@empresa.com
   ADMIN_EMAIL=admin@empresa.com
   ```

### Generar Contraseña de Aplicación Gmail

1. ✅ Ir a: https://myaccount.google.com/security
2. ✅ Activar "Verificación en 2 pasos"
3. ✅ Ir a "Contraseñas de aplicaciones"
4. ✅ Seleccionar "Correo" y "Otro"
5. ✅ Copiar la contraseña de 16 caracteres
6. ✅ Pegar en `.env` como `MAIL_PASSWORD`

**Ejemplo de contraseña de aplicación:** `abcd efgh ijkl mnop`

---

## 🧪 3. Verificar Configuración

### Ejecutar script de prueba:
```bash
python probar_email.py
```

**Salida esperada:**
```
============================================================
PRUEBA DE SISTEMA DE NOTIFICACIONES - UC2
============================================================

1. Verificando configuración SMTP...
   MAIL_SERVER: smtp.gmail.com
   MAIL_PORT: 587
   MAIL_USE_TLS: True
   MAIL_USERNAME: tu_correo@gmail.com
   MAIL_PASSWORD: ***
   ✅ Configuración SMTP OK

2. Buscando datos de prueba...
   ✅ Colaborador encontrado: Juan Perez (colaborador@test.com)
   ✅ Incapacidad encontrada: #1 (Enfermedad General)

3. Enviando email de prueba...
   Destinatario colaborador: colaborador@test.com
   Destinatario RRHH: rrhh@empresa.com
   ✅ Email enviado exitosamente (proceso asíncrono)

4. Revisa las bandejas de entrada:
   - colaborador@test.com (confirmación de registro)
   - rrhh@empresa.com (notificación a RRHH)

✅ PRUEBA COMPLETADA
============================================================
```

---

## 📁 4. Verificar Archivos

### Archivos nuevos creados:

- [ ] ✅ `app/utils/email_service.py` - Servicio de email
- [ ] ✅ `app/templates/emails/confirmacion_registro.html`
- [ ] ✅ `app/templates/emails/notificacion_gestion_humana.html`
- [ ] ✅ `app/templates/emails/validacion_completada.html`
- [ ] ✅ `app/templates/emails/documentos_faltantes.html`
- [ ] ✅ `app/templates/emails/incapacidad_aprobada.html`
- [ ] ✅ `app/templates/emails/incapacidad_rechazada.html`
- [ ] ✅ `.env` - Configuración de entorno
- [ ] ✅ `.env.example` - Plantilla de configuración

### Archivos modificados:

- [ ] ✅ `app/__init__.py` - Inicialización de Flask-Mail
- [ ] ✅ `app/routes/incapacidades.py` - Llamadas a notificaciones
- [ ] ✅ `requirements.txt` - Flask-Mail agregado
- [ ] ✅ `config.py` - Configuración SMTP
- [ ] ✅ `README.md` - Instrucciones actualizadas

---

## 🎯 5. Test de Flujo Completo

### Prueba 1: Registro de Incapacidad (UC1)

1. **Login como colaborador:**
   - Email: `colaborador@test.com`
   - Password: `123456`

2. **Registrar nueva incapacidad:**
   - Ir a "Registrar Incapacidad"
   - Tipo: "Enfermedad General"
   - Fechas: Cualquier rango válido
   - Subir certificado (PDF)
   - Click "Registrar"

3. **Verificar emails recibidos:**
   - [ ] ✅ Colaborador recibe confirmación
   - [ ] ✅ RRHH recibe notificación de nueva solicitud

**Checklist:**
- [ ] Flash message: "Incapacidad registrada exitosamente"
- [ ] Email 1: `confirmacion_registro.html` a colaborador
- [ ] Email 2: `notificacion_gestion_humana.html` a RRHH
- [ ] Emails contienen datos correctos (tipo, fechas, documentos)

---

### Prueba 2: Validación Completa (UC4)

1. **Login como auxiliar:**
   - Email: `auxiliar@test.com`
   - Password: `123456`

2. **Validar incapacidad:**
   - Dashboard Auxiliar → Ver incapacidad pendiente
   - Click "Validar Documentación"
   - Verificar documentos
   - Click "Marcar como Completa"

3. **Verificar email:**
   - [ ] ✅ Colaborador recibe notificación de validación completada

**Checklist:**
- [ ] Estado cambia a "En revisión"
- [ ] Flash message: "Documentación marcada como completa"
- [ ] Email: `validacion_completada.html` a colaborador

---

### Prueba 3: Solicitar Documentos (UC4)

1. **Login como auxiliar**

2. **Validar incapacidad con docs incompletos:**
   - Dashboard Auxiliar → Ver incapacidad
   - Click "Validar Documentación"
   - Click "Solicitar Documentos Faltantes"
   - Escribir observaciones: "Falta Epicrisis"
   - Enviar

3. **Verificar email:**
   - [ ] ✅ Colaborador recibe solicitud de documentos

**Checklist:**
- [ ] Estado permanece "Pendiente"
- [ ] Flash message: "Solicitud registrada... Notificación enviada"
- [ ] Email: `documentos_faltantes.html` con observaciones

---

### Prueba 4: Aprobación (UC7)

1. **Login como auxiliar**

2. **Aprobar incapacidad:**
   - Dashboard Auxiliar → Incapacidad en revisión
   - Click "Aprobar/Rechazar"
   - Seleccionar "Aprobar"
   - Click "Confirmar"

3. **Verificar email:**
   - [ ] ✅ Colaborador recibe notificación de aprobación

**Checklist:**
- [ ] Estado cambia a "Aprobada"
- [ ] Flash message: "Incapacidad #X aprobada exitosamente"
- [ ] Email: `incapacidad_aprobada.html` a colaborador

---

### Prueba 5: Rechazo (UC7)

1. **Login como auxiliar**

2. **Rechazar incapacidad:**
   - Dashboard Auxiliar → Incapacidad en revisión
   - Click "Aprobar/Rechazar"
   - Seleccionar "Rechazar"
   - Escribir motivo: "Documentación inconsistente"
   - Click "Confirmar"

3. **Verificar email:**
   - [ ] ✅ Colaborador recibe notificación de rechazo

**Checklist:**
- [ ] Estado cambia a "Rechazada"
- [ ] Flash message: "Incapacidad #X rechazada"
- [ ] Email: `incapacidad_rechazada.html` con motivo
- [ ] Motivo del rechazo visible en el email

---

## 🐛 6. Troubleshooting

### Problema: Email no se envía

**Síntomas:**
- No llegan emails
- No hay errores visibles en la UI

**Diagnóstico:**

1. **Verificar consola del servidor:**
   ```
   # Buscar:
   "Error al enviar notificacion: ..."
   ```

2. **Causas comunes:**

   **A) Credenciales incorrectas:**
   ```bash
   # Verificar .env
   MAIL_USERNAME=tu_correo@gmail.com
   MAIL_PASSWORD=contraseña_aplicacion_16_caracteres
   ```
   
   **B) Verificación en 2 pasos no activada:**
   - Activar en https://myaccount.google.com/security
   
   **C) Puerto bloqueado:**
   - Verificar firewall permite puerto 587
   - Probar con `telnet smtp.gmail.com 587`
   
   **D) Conexión a internet:**
   - Verificar conectividad

3. **Test manual:**
   ```bash
   python probar_email.py
   ```

---

### Problema: Flask-Mail no encontrado

**Síntoma:**
```
ModuleNotFoundError: No module named 'flask_mail'
```

**Solución:**
```bash
pip install Flask-Mail==0.9.1
```

---

### Problema: Variables de entorno no se cargan

**Síntoma:**
- `MAIL_USERNAME` es None
- Script dice "Configuración SMTP incompleta"

**Solución:**

**Opción A: python-dotenv (recomendado)**
```bash
pip install python-dotenv
```

En `config.py`, agregar al inicio:
```python
from dotenv import load_dotenv
load_dotenv()
```

**Opción B: Configurar manualmente en Windows:**
```powershell
$env:MAIL_USERNAME="tu_correo@gmail.com"
$env:MAIL_PASSWORD="contraseña_aplicacion"
```

---

### Problema: Email va a spam

**Soluciones:**

1. **Marcar como "No es spam"** en el primer email
2. **Agregar remitente a contactos**
3. **Configurar SPF/DKIM** (producción)

---

## ✅ 7. Checklist Final

Antes de considerar UC2 completo:

### Instalación
- [ ] Flask-Mail instalado (`pip list | grep Flask-Mail`)
- [ ] `.env` creado con credenciales correctas
- [ ] Contraseña de aplicación Gmail generada
- [ ] `python probar_email.py` ejecuta sin errores

### Funcionalidad
- [ ] UC1: Email de confirmación y alerta a RRHH
- [ ] UC4: Email de validación completada
- [ ] UC4: Email de documentos faltantes
- [ ] UC7: Email de aprobación
- [ ] UC7: Email de rechazo con motivo

### Calidad
- [ ] Emails tienen diseño profesional
- [ ] Emails contienen datos correctos
- [ ] Emails no bloquean la aplicación
- [ ] Si falla SMTP, app continúa funcionando

### Documentación
- [ ] README.md actualizado con instrucciones
- [ ] `docs/UC2_NOTIFICACIONES.md` leído
- [ ] `.env.example` documentado

---

## 🎉 Confirmación Final

Si todas las casillas están marcadas:

✅ **UC-2 está correctamente implementado y funcionando**

Puedes proceder con:
1. Testing de integración
2. UAT (User Acceptance Testing)
3. Deploy a staging/producción

---

**Última actualización:** 2024  
**Versión:** 1.0.0

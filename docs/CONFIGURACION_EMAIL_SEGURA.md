# 📧 Configuración Segura de Email

## 🎯 Opciones de Configuración

### Opción 1: Mailtrap (RECOMENDADO para Desarrollo) ⭐

**Ventajas:**
- ✅ 100% seguro - No expone credenciales personales
- ✅ Gratis - 100 emails/mes
- ✅ Perfecto para testing
- ✅ Interfaz web para ver emails
- ✅ No envía emails reales (evita spam accidental)

**Configuración:**

1. **Crear cuenta:**
   - Ir a https://mailtrap.io/
   - Registrarse con email

2. **Obtener credenciales:**
   - Dashboard → "Email Testing" → "Inboxes"
   - Click en "My Inbox"
   - Ver "SMTP Settings" → "Show Credentials"

3. **Configurar `.env`:**
   ```bash
   MAIL_SERVER=sandbox.smtp.mailtrap.io
   MAIL_PORT=2525
   MAIL_USE_TLS=True
   MAIL_USERNAME=abc123def456  # Tu username de Mailtrap
   MAIL_PASSWORD=xyz789uvw012  # Tu password de Mailtrap
   MAIL_DEFAULT_SENDER=noreply@incapacidades.com
   GESTION_HUMANA_EMAIL=rrhh@test.com
   ```

4. **Probar:**
   ```bash
   python probar_email.py
   ```

5. **Ver email enviado:**
   - Ir a tu inbox en Mailtrap
   - Ver el email recibido con formato HTML

---

### Opción 2: SendGrid (Para Producción) 🚀

**Ventajas:**
- ✅ 100 emails/día gratis permanentemente
- ✅ API Key (más seguro que contraseñas)
- ✅ Profesional
- ✅ Analytics incluidos

**Configuración:**

1. **Crear cuenta:**
   - Ir a https://sendgrid.com/
   - Registrarse

2. **Generar API Key:**
   - Dashboard → Settings → API Keys
   - "Create API Key"
   - Nombre: "Incapacidades App"
   - Permisos: "Full Access"
   - Copiar API Key (solo se muestra una vez)

3. **Configurar `.env`:**
   ```bash
   MAIL_SERVER=smtp.sendgrid.net
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=apikey  # Literal "apikey"
   MAIL_PASSWORD=SG.xxxxxxxxxxxxxx  # Tu API Key
   MAIL_DEFAULT_SENDER=noreply@tudominio.com
   GESTION_HUMANA_EMAIL=rrhh@tudominio.com
   ```

4. **Verificar dominio (opcional pero recomendado):**
   - Settings → Sender Authentication
   - Verificar email o dominio

---

### Opción 3: Gmail (Solo si no hay alternativa) ⚠️

**⚠️ NO RECOMENDADO para producción**

**Si debes usarlo:**

1. **Crear cuenta Gmail dedicada:**
   - Crear nuevo Gmail: `incapacidades.notificaciones@gmail.com`
   - NO usar cuenta personal

2. **Activar 2FA:**
   - https://myaccount.google.com/security
   - "Verificación en 2 pasos" → Activar

3. **Generar Contraseña de Aplicación:**
   - https://myaccount.google.com/apppasswords
   - Seleccionar app: "Mail"
   - Seleccionar dispositivo: "Otro" → "Incapacidades App"
   - Copiar contraseña de 16 caracteres (sin espacios)

4. **Configurar `.env`:**
   ```bash
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=incapacidades.notificaciones@gmail.com
   MAIL_PASSWORD=abcdefghijklmnop  # Contraseña de aplicación
   MAIL_DEFAULT_SENDER=incapacidades.notificaciones@gmail.com
   GESTION_HUMANA_EMAIL=rrhh@empresa.com
   ```

**Limitaciones:**
- ⚠️ Máximo 500 emails/día
- ⚠️ Puede marcar como spam
- ⚠️ Menos profesional

---

## 🔒 Buenas Prácticas de Seguridad

1. **NUNCA subir `.env` a Git:**
   ```bash
   # Ya está en .gitignore
   .env
   ```

2. **Usar `.env.example` como plantilla:**
   ```bash
   cp .env.example .env
   # Editar .env con tus credenciales reales
   ```

3. **Rotar credenciales regularmente:**
   - Cambiar API Keys cada 3-6 meses
   - Especialmente si el repositorio es público

4. **Diferentes configuraciones por ambiente:**
   ```bash
   .env.development   # Mailtrap
   .env.production    # SendGrid
   ```

---

## 🧪 Testing

```bash
# Probar configuración
python probar_email.py

# Si usas Mailtrap:
# - Ir a https://mailtrap.io/inboxes
# - Ver email recibido

# Si usas SendGrid/Gmail:
# - Revisar inbox del destinatario
```

---

## ❓ Troubleshooting

### Error: "SMTPAuthenticationError"
- ✅ Verificar usuario/password en `.env`
- ✅ En Gmail: verificar contraseña de aplicación
- ✅ En SendGrid: verificar API Key

### Error: "SMTPServerDisconnected"
- ✅ Verificar MAIL_SERVER y MAIL_PORT
- ✅ Verificar firewall/antivirus

### Emails no llegan (SendGrid/Gmail)
- ✅ Revisar carpeta de spam
- ✅ Verificar email del remitente
- ✅ En SendGrid: verificar dominio

---

## 📊 Comparación de Servicios

| Servicio | Gratis/Mes | Seguridad | Uso Recomendado |
|----------|-----------|-----------|-----------------|
| **Mailtrap** | 100 emails | ⭐⭐⭐⭐⭐ | Desarrollo/Testing |
| **SendGrid** | 100/día | ⭐⭐⭐⭐⭐ | Producción |
| **Mailgun** | 5000 (3 meses) | ⭐⭐⭐⭐ | Producción |
| **Gmail** | 500/día | ⭐⭐ | Solo desarrollo |

---

## 🎯 Recomendación Final

**Para tu proyecto:**

1. **Desarrollo/Testing:** Usa Mailtrap ⭐
2. **Producción futura:** Migra a SendGrid
3. **Evita Gmail** a menos que sea absolutamente necesario

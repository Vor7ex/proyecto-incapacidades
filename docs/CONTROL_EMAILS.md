# 🔴 Control de Envío de Emails - Modo Desarrollo

## Problema

Al desarrollar y probar el sistema, cada acción envía emails a Mailtrap, consumiendo rápidamente la cuota gratuita:
- ⚠️ **Mailtrap Plan Gratuito:** Solo 100 emails/mes
- 🔥 Cada prueba completa consume ~4 emails
- 📉 25 pruebas = Cuota agotada

## Solución: Switch On/Off para Emails

### ✅ Implementado

Sistema de activación/desactivación de envío de emails mediante variable de entorno `MAIL_ENABLED`.

---

## Uso Rápido

### **Ver Estado Actual:**
```bash
python toggle_email.py status
```

### **Desactivar Envío (Modo Desarrollo):**
```bash
python toggle_email.py off
```

**Resultado:**
- ❌ No envía emails reales
- ✅ Muestra logs en consola simulando el envío
- ✅ Ahorra cuota de Mailtrap
- ✅ El sistema funciona normalmente

### **Activar Envío (Pruebas Reales):**
```bash
python toggle_email.py on
```

**Resultado:**
- ✅ Envía emails reales a Mailtrap/SMTP
- 📧 Consume cuota de emails

---

## Configuración Manual

### **Archivo `.env`:**

```bash
# Desactivado (modo desarrollo - recomendado)
MAIL_ENABLED=False

# Activado (pruebas reales)
MAIL_ENABLED=True
```

**⚠️ IMPORTANTE:** Reiniciar la aplicación después de cambiar:
```bash
# Detener servidor (Ctrl+C)
python run.py
```

---

## Comportamiento por Modo

### **MAIL_ENABLED=False (Modo Desarrollo)**

**Al registrar una incapacidad:**
```
📧 [SIMULADO] Email NO enviado (MAIL_ENABLED=False)
   Subject: Incapacidad #4 registrada exitosamente
   To: empleado@test.com
   (Cambia MAIL_ENABLED=True en .env para enviar emails reales)

📧 [SIMULADO] Email NO enviado (MAIL_ENABLED=False)
   Subject: Nueva incapacidad para validar - Juan Perez
   To: rrhh@test.com
   (Cambia MAIL_ENABLED=True en .env para enviar emails reales)

✅ UC2: 2 notificaciones enviadas para incapacidad #4
```

**Ventajas:**
- ✅ No consume cuota de Mailtrap
- ✅ Desarrollo más rápido (no espera a SMTP)
- ✅ Logs claros en consola
- ✅ Verifica lógica sin envío real

---

### **MAIL_ENABLED=True (Modo Producción/Testing)**

**Al registrar una incapacidad:**
```
✅ UC2: 2 notificaciones enviadas para incapacidad #4
```

**Resultado:**
- 📧 2 emails reales enviados a Mailtrap
- 📬 Visibles en https://mailtrap.io/inboxes

**Cuándo usar:**
- ✅ Verificar templates HTML
- ✅ Probar contenido de emails
- ✅ Demo al cliente/profesor
- ✅ Testing final antes de release

---

## Script de Control

### **`toggle_email.py`**

Script de utilidad para cambiar fácilmente entre modos.

#### **Comandos:**

| Comando | Acción |
|---------|--------|
| `python toggle_email.py on` | Activar envío de emails |
| `python toggle_email.py off` | Desactivar envío de emails |
| `python toggle_email.py status` | Ver estado actual |

#### **Aliases:**
- **Activar:** `on`, `enable`, `activar`, `true`
- **Desactivar:** `off`, `disable`, `desactivar`, `false`
- **Estado:** `status`, `estado`, `ver`

---

## Verificación

### **Script de Verificación Actualizado:**

```bash
python verificar_uc2.py
```

**Salida con MAIL_ENABLED=False:**
```
4. Verificando inicialización de Flask-Mail...
   ✅ Flask-Mail inicializado
      Server: sandbox.smtp.mailtrap.io
      Port: 2525
      📧 Estado: MODO SIMULACIÓN (sin envío real)
      💡 Cambia MAIL_ENABLED=True en .env para activar
```

**Salida con MAIL_ENABLED=True:**
```
4. Verificando inicialización de Flask-Mail...
   ✅ Flask-Mail inicializado
      Server: sandbox.smtp.mailtrap.io
      Port: 2525
      📧 Estado: ENVÍO ACTIVO (emails reales)
```

---

## Flujo de Trabajo Recomendado

### **Durante Desarrollo:**

1. **Configurar modo simulación:**
   ```bash
   python toggle_email.py off
   ```

2. **Desarrollar y probar:**
   ```bash
   python run.py
   # Registrar incapacidades, validar, aprobar, etc.
   # Ver logs en consola sin gastar cuota
   ```

3. **Verificar logs en consola:**
   - Revisar que se llamen las funciones correctas
   - Verificar destinatarios y asuntos
   - Confirmar lógica de notificaciones

### **Para Testing Real:**

1. **Activar envío:**
   ```bash
   python toggle_email.py on
   ```

2. **Reiniciar app:**
   ```bash
   python run.py
   ```

3. **Ejecutar caso de prueba específico:**
   - Registrar 1 incapacidad (2 emails)
   - Validar (1 email)
   - Aprobar (1 email)
   - **Total: 4 emails**

4. **Verificar en Mailtrap:**
   - Revisar formato HTML
   - Verificar contenido
   - Validar destinatarios

5. **Desactivar nuevamente:**
   ```bash
   python toggle_email.py off
   ```

---

## Gestión de Cuota Mailtrap

### **Plan Gratuito:**
- 📊 **Límite:** 100 emails/mes
- 📧 **Reseteo:** 1 de cada mes
- ⚡ **Rate Limit:** 1 email/segundo

### **Estimación de Consumo:**

| Acción | Emails | Consumo |
|--------|--------|---------|
| Registro completo (UC1) | 2 | 2 emails |
| Validación (UC4) | 1 | 1 email |
| Aprobación/Rechazo (UC7) | 1 | 1 email |
| **Flujo completo** | **4** | **4 emails** |

**Pruebas posibles:** 100 ÷ 4 = **25 flujos completos/mes**

### **Recomendaciones:**

1. **Modo Desarrollo (80% del tiempo):**
   - `MAIL_ENABLED=False`
   - Solo logs en consola
   - 0 emails consumidos

2. **Testing Puntual (20% del tiempo):**
   - `MAIL_ENABLED=True`
   - Solo para verificaciones específicas
   - ~20 emails/mes

3. **Demo/Presentación:**
   - Activar justo antes
   - Ejecutar 1-2 flujos completos
   - Desactivar inmediatamente

---

## Alternativas para Producción

Si se agota la cuota de Mailtrap:

### **Opción 1: SendGrid (Recomendado)**
```bash
# .env
MAIL_ENABLED=True
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=apikey
MAIL_PASSWORD=SG.tu_api_key
```

**Ventajas:**
- ✅ 100 emails/día gratis (permanente)
- ✅ Sin rate limits estrictos
- ✅ Analytics incluidos

### **Opción 2: Gmail Dedicado**
```bash
# .env
MAIL_ENABLED=True
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=proyecto.incapacidades@gmail.com
MAIL_PASSWORD=contraseña_aplicacion
```

**Ventajas:**
- ✅ 500 emails/día
- ✅ Familiar y fácil de configurar

---

## Troubleshooting

### **Problema: Cambié .env pero sigue enviando emails**

**Solución:** Reiniciar la aplicación
```bash
# Detener servidor (Ctrl+C)
python run.py
```

### **Problema: No sé si está activado o desactivado**

**Solución:**
```bash
python toggle_email.py status
```

### **Problema: Los logs no aparecen en consola**

**Verificar:**
1. Que `.env` tenga `MAIL_ENABLED=False`
2. Que reiniciaste la app
3. Ver consola del servidor Flask

---

## Resumen

### **Comandos Esenciales:**

```bash
# Modo desarrollo (sin emails)
python toggle_email.py off
python run.py

# Ver estado
python toggle_email.py status

# Prueba real (con emails)
python toggle_email.py on
python run.py

# Verificar configuración
python verificar_uc2.py
```

### **Archivo .env:**
```bash
# Desarrollo (recomendado por defecto)
MAIL_ENABLED=False

# Producción/Testing
MAIL_ENABLED=True
```

---

## Beneficios

✅ **Ahorro de cuota:** 0 emails consumidos en desarrollo  
✅ **Desarrollo más rápido:** Sin esperar a SMTP  
✅ **Logs claros:** Ver qué emails se enviarían  
✅ **Control total:** On/Off con 1 comando  
✅ **Verificación:** Ver estado actual fácilmente  

---

**Última actualización:** 2025-10-12  
**Versión:** 1.0.1  
**Estado:** ✅ IMPLEMENTADO

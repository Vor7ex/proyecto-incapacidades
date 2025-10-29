# 📖 Manual de Usuario - Sistema de Incapacidades

**Última actualización:** Octubre 2025  
**Versión:** 1.0  
**Dirigido a:** Colaboradores y Personal de Gestión Humana

---

## 📘 Introducción

El Sistema de Gestión de Incapacidades permite gestionar de forma digital todo el proceso de registro, validación y aprobación de incapacidades médicas.

**Beneficios:**
- ✅ Digital, rápido y trazable
- ✅ Notificaciones automáticas
- ✅ Consulta de estado en tiempo real

**Tipos soportados:** Enfermedad general, Accidente laboral, Accidente de tránsito, Licencias de maternidad/paternidad

---

## 🔐 Acceso al Sistema

**URL:** http://localhost:5000

**Credenciales de prueba:**
- Colaborador: `empleado@test.com` / `123456`
- Auxiliar RRHH: `auxiliar@test.com` / `123456`

---

## 👤 Guía para Colaboradores

### 1. Registrar Incapacidad

1. Login → "Registrar Incapacidad"
2. **Seleccionar tipo** de incapacidad
3. **Ingresar fechas** (inicio y fin)
4. **Cargar documentos:**
   - Certificado (obligatorio) - PDF/JPG/PNG, max 10MB
   - Epicrisis (si >2 días o accidente)
   - FURIPS (solo accidente tránsito)
5. **Enviar** y guardar código: `INC-YYYYMMDD-XXXX`

### 2. Consultar Incapacidades

- Menú → "Mis Incapacidades"
- Ver estado, descargar documentos

### 3. Estados

| Estado | Significado | Acción |
|--------|-------------|--------|
| ⏳ Pendiente Validación | RRHH revisando | Esperar |
| 📄 Documentación Incompleta | Faltan docs | Cargar en 3 días |
| ✅ Aprobada | Aprobada | Ninguna |
| ❌ Rechazada | No cumple | Ver motivo |

### 4. Cargar Documentos Solicitados

**Cuando recibes solicitud:**
1. Click en enlace del email
2. Subir archivos solicitados
3. Enviar antes de 3 días hábiles

**Recordatorios:** Día 3 y Día 6 automáticos

---

## 👨‍💼 Guía para Auxiliares RRHH

### 1. Validar Documentación

1. "Validar Incapacidades" → Seleccionar
2. **Revisar checklist automático**
3. Descargar y verificar documentos
4. **Decisión:**
   - ✅ Completa → "Marcar Documentación Completa"
   - ❌ Incompleta → "Solicitar Documentos"

**Checklist por tipo:**
- Enfermedad ≤2 días: Certificado
- Enfermedad >2 días: Certificado + Epicrisis
- Accidente laboral: Certificado + Epicrisis
- Accidente tránsito: + FURIPS
- Maternidad/Paternidad: + Docs nacimiento

### 2. Solicitar Documentos Faltantes

1. "Solicitar Documentos" desde validación
2. Marcar documentos faltantes
3. **Agregar observaciones específicas**
4. Confirmar → email automático

**Sistema automático:**
- Email inmediato
- Recordatorio día 3 (08:00 AM)
- 2da notificación día 6
- Si no responde: "Requiere Citación"

### 3. Aprobar/Rechazar

**Aprobar:**
- "Aprobar/Rechazar" → Revisar → "Aprobar"
- Email automático → Estado "Aprobada"

**Rechazar:**
- Seleccionar motivo + observaciones
- Confirmar (definitivo)

---

## ❓ Preguntas Frecuentes

**Colaboradores:**

**P: ¿Cuánto tarda validación?**
R: 1-2 días hábiles

**P: ¿Qué si me equivoqué?**
R: Contacta RRHH inmediatamente

**P: ¿Qué si no cargo en 3 días?**
R: Recordatorios automáticos. Día 6+: citación

**Auxiliares:**

**P: ¿Cancelar solicitud?**
R: Dashboard solicitudes → "Cancelar" con motivo

**P: ¿Modificar plazo?**
R: No. Estándar 3 días. Casos especiales: administrador

---

## 📚 Glosario

| Término | Definición |
|---------|-----------|
| Código Radicación | ID único (INC-YYYYMMDD-XXXX) |
| Epicrisis | Resumen clínico médico |
| FURIPS | Formato Accidente Tránsito |
| EPS | Entidad Promotora de Salud |
| ARL | Administradora Riesgos Laborales |
| Días Hábiles | Lunes-viernes (sin festivos) |

---

## 📞 Soporte

**Gestión Humana:** `rrhh@empresa.com`  
**Soporte TI:** `soporte.ti@empresa.com`

**Problemas comunes:**
- No inicio sesión → Recuperar contraseña
- No emails → Revisar spam
- No cargar archivos → Verificar <10MB, PDF/JPG/PNG
- Página no carga → Ctrl+F5, limpiar caché

---

**🎉 ¡Gracias por usar el Sistema de Incapacidades!**

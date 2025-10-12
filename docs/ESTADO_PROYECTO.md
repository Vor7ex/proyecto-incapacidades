# Estado del Proyecto - Sistema de Incapacidades

**Última actualización:** 2025-10-12  
**Versión:** Release 1.0 (En desarrollo)  
**Completitud general:** 55.6%

---

## 📊 Estado por Caso de Uso

| UC | Nombre | Estado | % | Prioridad |
|----|--------|--------|---|-----------|
| UC1 | Registrar incapacidad con documentos | ⚠️ Parcial | 85% | ✅ Completar |
| UC2 | Notificar a líder y Gestión Humana | ⚠️ Parcial | 70% | 🟡 Mejorar |
| UC3 | Consultar mis incapacidades | ⚠️ Parcial | 60% | 🟢 Mejorar |
| UC4 | Recibir y validar documentación | ⚠️ Parcial | 75% | ✅ Completar |
| UC5 | Verificar requisitos por tipo | 🔴 Crítico | 40% | 🔴 URGENTE |
| UC6 | Solicitar documentos faltantes | 🔴 No implementado | 0% | 🔴 URGENTE |
| UC7 | Aprobar/Rechazar incapacidad | ⚠️ Parcial | 65% | 🟡 Mejorar |
| UC15 | Almacenar documentos digitalmente | ⚠️ Parcial | 50% | 🟡 Mejorar |

---

## 🔴 Bloqueadores Críticos

### 1. UC6 - Solicitar documentos faltantes (0%)
**Falta implementar:**
- Formulario para marcar documentos faltantes
- Cálculo de 3 días hábiles
- Notificación automática al colaborador
- Recordatorio automático día 2
- Sistema de re-carga de documentos
- Estado "Documentación incompleta"

### 2. UC5 - Verificación automática por tipo (40%)
**Falta implementar:**
- Sistema de reglas automáticas por tipo de incapacidad
- Validación: Epicrisis si días ≥2 (Enfermedad general)
- Validación: FURIPS (Accidente tránsito)
- Validación: Documentos maternidad/paternidad

---

## ✅ Funcionalidades Implementadas

### UC1 - Registrar incapacidad (85%)
- ✅ Formulario de registro
- ✅ Carga de documentos (certificado, epicrisis)
- ✅ Validación de formatos (PDF, JPG, PNG)
- ✅ Cálculo automático de días
- ✅ Código de radicación
- ❌ Borrador automático en pérdida de conexión
- ❌ Validación de fechas futuras con justificación

### UC2 - Notificar a líder y RRHH (70%)
- ✅ Email al colaborador (confirmación)
- ✅ Email a Gestión Humana
- ✅ 6 templates HTML profesionales
- ✅ Sistema on/off de emails (`MAIL_ENABLED`)
- ✅ Delay anti-rate-limit (2s entre emails)
- ❌ Notificación al líder inmediato
- ❌ Notificaciones internas (en sistema)
- ❌ Logs de notificaciones
- ❌ 3 reintentos SMTP automáticos

### UC3 - Consultar incapacidades (60%)
- ✅ Listado de incapacidades del colaborador
- ✅ Vista de detalle
- ❌ Filtros (por fecha, tipo, estado)
- ❌ Paginación
- ❌ Descarga múltiple en ZIP
- ❌ Línea de tiempo de estados

### UC4 - Validar documentación (75%)
- ✅ Vista de validación para auxiliar
- ✅ Checklist visual de documentos
- ✅ Cambio de estado "En revisión"
- ✅ Notificación de validación completada
- ❌ Marcar documentos como ilegibles
- ❌ Registrar incoherencias específicas
- ❌ Log de validación con usuario y fecha

### UC7 - Aprobar/Rechazar (65%)
- ✅ Vista aprobar/rechazar
- ✅ Campo de motivo de rechazo
- ✅ Cambio de estados
- ✅ Notificación al colaborador
- ❌ Lista predefinida de motivos
- ❌ Validación de estado previo
- ❌ Alerta especial para certificados falsos

### UC15 - Almacenar documentos (50%)
- ✅ Almacenamiento local en `/static/uploads`
- ✅ Relación con BD
- ✅ Validación de formatos
- ❌ UUID por documento
- ❌ Hash MD5 para integridad
- ❌ Estructura `/año/mes/tipo/colaborador/`
- ❌ Cifrado de documentos sensibles
- ❌ Respaldos automáticos

---

## 🛠️ Configuración Actual

### Email (UC2)
```bash
MAIL_ENABLED=False  # Cambiar a True para enviar emails reales
MAIL_SERVER=sandbox.smtp.mailtrap.io
MAIL_PORT=2525
```

**Control de emails:**
```bash
python toggle_email.py on      # Activar envío
python toggle_email.py off     # Desactivar (modo simulación)
python toggle_email.py status  # Ver estado
```

### Base de Datos
- SQLite: `instance/database.db`
- 2 usuarios de prueba (colaborador, auxiliar)

### Usuarios de Prueba
- **Colaborador:** `colaborador@test.com` / `123456`
- **Auxiliar:** `auxiliar@test.com` / `123456`

---

## 📋 Plan de Acción - Próximos Pasos

### Sprint 1: UC6 - Solicitar documentos faltantes (CRÍTICO)
**Tiempo estimado:** 3-4 días

1. Crear formulario en vista de validación
2. Lógica de cálculo 3 días hábiles
3. Sistema de notificaciones
4. Recordatorio automático
5. Re-carga de documentos
6. Estado "Documentación incompleta"

### Sprint 2: UC5 - Verificación automática (CRÍTICO)
**Tiempo estimado:** 2-3 días

1. Sistema de reglas por tipo
2. Validación automática en registro
3. Checklist dinámico
4. Alertas de documentos faltantes

### Sprint 3: Completar UC2, UC7, UC15
**Tiempo estimado:** 2-3 días

1. Notificación a líder inmediato (UC2)
2. Notificaciones internas (UC2)
3. Motivos predefinidos rechazo (UC7)
4. Hash MD5 y estructura carpetas (UC15)

### Sprint 4: Mejorar UC1, UC3, UC4
**Tiempo estimado:** 2 días

1. Filtros en consulta (UC3)
2. Borrador automático (UC1)
3. Logs de validación (UC4)

---

## 📁 Estructura del Proyecto

```
proyecto-incapacidades/
├── app/
│   ├── models/           # Usuario, Incapacidad, Documento
│   ├── routes/           # auth, incapacidades, documentos
│   ├── templates/        # Vistas HTML + emails
│   ├── static/           # CSS, JS, uploads
│   └── utils/            # validaciones, email_service
├── docs/                 # Documentación
├── instance/             # BD SQLite
├── .env                  # Configuración (NO subir a git)
├── config.py             # Config de Flask
├── run.py                # Punto de entrada
├── crear_usuarios.py     # Script de usuarios de prueba
├── toggle_email.py       # Control de emails
└── verificar_uc2.py      # Verificar config emails
```

---

## 🚀 Comandos Útiles

### Ejecutar aplicación
```bash
python run.py
```

### Crear usuarios de prueba
```bash
python crear_usuarios.py
```

### Verificar emails
```bash
python verificar_uc2.py       # Ver configuración
python toggle_email.py status  # Estado actual
```

### Verificar errores
```bash
# Ver consola del servidor para logs
# Buscar mensajes con ✅ ❌ 📧
```

---

## 🐛 Problemas Conocidos

### 1. Rate Limit Mailtrap
**Problema:** Solo 1 email/segundo en plan gratuito  
**Solución:** Delay de 10s entre emails (implementado)  
**Alternativa:** SendGrid (100 emails/día gratis)

### 2. Notificación al líder falta
**Problema:** Solo notifica a RRHH, no al líder  
**Estado:** Pendiente UC2 completar  

### 3. Validación automática manual
**Problema:** UC5 no valida automáticamente por tipo  
**Estado:** Pendiente Sprint 2

---

## 📊 Métricas de Calidad

| Aspecto | Estado | Meta |
|---------|--------|------|
| Flujos principales | 6/8 implementados | 8/8 |
| Flujos excepciones | ~30% | 100% |
| Validaciones automáticas | ~10% | 100% |
| Notificaciones | ~60% | 100% |
| Seguridad documentos | ~20% | 100% |

---

## 📚 Documentación de Referencia

### Técnica
- `CONTROL_EMAILS.md` - Sistema de control de emails
- `UC2_RESUMEN_FINAL.md` - Estado final UC2
- `BUG_FIX_ALERTAS.md` - Fix de alertas JavaScript

### Usuario
- `manual_usuario.md` - Manual de uso
- `roles_permisos.md` - Matriz de permisos

### Arquitectura
- `DECISION_ARQUITECTURA_ROLES.md` - 2 vs 3 roles
- `SOLUCION_PROBLEMAS.md` - Troubleshooting

---

## ⏱️ Tiempo Estimado para Release 1.0 Completo

| Fase | Días |
|------|------|
| Sprint 1 (UC6) | 4 días |
| Sprint 2 (UC5) | 3 días |
| Sprint 3 (Completar) | 3 días |
| Sprint 4 (Mejoras) | 2 días |
| Testing final | 2 días |
| **TOTAL** | **14 días** |

---

**Estado actual:** 55.6% completo  
**Bloqueadores críticos:** UC6 (0%), UC5 (40%)  
**Próximo paso recomendado:** Implementar UC6

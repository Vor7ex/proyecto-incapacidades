# UC6: Solicitud de Documentos Faltantes

## Resumen

**UC6 - Solicitud de Documentos Faltantes** es el caso de uso que permite a los Auxiliares de Recursos Humanos solicitar documentos adicionales a los colaboradores cuando la documentación inicial de una incapacidad está incompleta.

### Objetivos
- Solicitar documentos faltantes de manera formal y trazable
- Establecer plazos claros para la entrega (3 días hábiles)
- Enviar recordatorios automáticos escalonados
- Gestionar el ciclo completo: solicitud → recordatorios → entrega → validación

### Actores
- **Auxiliar de RRHH**: Solicita documentos, define plazos, valida entregas
- **Colaborador**: Recibe notificaciones, carga documentos solicitados
- **Sistema (Scheduler)**: Envía recordatorios automáticos según plazos

---

## Diagrama de Estados

```
┌─────────────────────────────────────────────────────────────────┐
│                    ESTADOS DE INCAPACIDAD                        │
└─────────────────────────────────────────────────────────────────┘

    PENDIENTE_VALIDACION
            │
            │ Auxiliar solicita documentos
            ▼
    DOCUMENTACION_INCOMPLETA ◄──┐
            │                    │
            │ Colaborador        │ Auxiliar solicita
            │ carga todos        │ nuevos documentos
            │ los documentos     │ (reinicio de UC6)
            ▼                    │
    PENDIENTE_VALIDACION ────────┘
            │
            │ Auxiliar valida
            │ y aprueba
            ▼
    APROBADA_PENDIENTE_TRANSCRIPCION


┌─────────────────────────────────────────────────────────────────┐
│              ESTADOS DE SOLICITUD DE DOCUMENTO                   │
└─────────────────────────────────────────────────────────────────┘

    PENDIENTE
        │
        ├──> Colaborador carga ────> ENTREGADO
        │
        ├──> Vence plazo (+3 días) ──> PENDIENTE (+ recordatorio)
        │
        ├──> Vence 2da vez (+6 días) ──> REQUIERE_CITACION
        │
        └──> Auxiliar cancela ──────> (Solicitud eliminada)
```

---

## Diagrama de Secuencia

### Flujo Principal

```
Colaborador          Auxiliar RRHH       Sistema/Scheduler         Email
    │                      │                    │                   │
    │                      │                    │                   │
    │  1. Carga           │                    │                   │
    │  incapacidad        │                    │                   │
    │────────────────────>│                    │                   │
    │                      │                    │                   │
    │                      │ 2. Detecta docs    │                   │
    │                      │    faltantes       │                   │
    │                      │                    │                   │
    │                      │ 3. Solicita docs   │                   │
    │                      │    (UC6 inicio)    │                   │
    │                      │────────────────────┤                   │
    │                      │                    │ 4. Envía notif    │
    │                      │                    │   inicial         │
    │                      │                    │──────────────────>│
    │                      │                    │                   │
    │<──────────────────────────────────────────────────────────────┤
    │  5. Email: "Documentos Solicitados"      │                   │
    │                      │                    │                   │
    │  6. Carga docs       │                    │                   │
    │─────────────────────>│                    │                   │
    │                      │                    │                   │
    │                      │ 7. Valida          │                   │
    │                      │    (si completa)   │                   │
    │                      │                    │                   │
    │                      │                    │                   │
    │  [FLUJO ALTERNO: NO CARGA A TIEMPO]      │                   │
    │                      │                    │                   │
    │                      │              8. Día 3: Scheduler       │
    │                      │                 ejecuta 08:00 AM       │
    │                      │                    │                   │
    │                      │                    │ 9. Recordatorio   │
    │                      │                    │    (tono urgente) │
    │                      │                    │──────────────────>│
    │<──────────────────────────────────────────────────────────────┤
    │  10. Email: "RECORDATORIO"               │                   │
    │                      │                    │                   │
    │                      │              11. Día 6: Scheduler      │
    │                      │                 ejecuta 08:00 AM       │
    │                      │                    │                   │
    │                      │                    │ 12. 2da notif     │
    │                      │                    │     (MUY urgente) │
    │                      │                    │──────────────────>│
    │<──────────────────────────────────────────────────────────────┤
    │  13. Email: "URGENTE - Última llamada"   │                   │
    │                      │                    │                   │
    │                      │                    │ 14. Marca como    │
    │                      │                    │     REQUIERE_     │
    │                      │                    │     CITACION      │
    │                      │<───────────────────┤                   │
    │                      │                    │                   │
```

---

## Tiempos y Recordatorios

### Línea de Tiempo del Flujo UC6

| Día | Evento | Actor | Acción |
|-----|--------|-------|--------|
| **Día 0** | Solicitud creada | Auxiliar | Crea solicitud con plazo de 3 días hábiles |
| Día 0 | Email enviado | Sistema | Notifica al colaborador con lista de docs |
| Día 1-2 | Ventana de carga | Colaborador | Puede cargar documentos sin presión |
| **Día 3** | Vencimiento | Sistema | Plazo original vence |
| Día 3 | 1er recordatorio | Scheduler (08:00 AM) | Email con tono urgente |
| Día 4-5 | Última oportunidad | Colaborador | Puede cargar para evitar citación |
| **Día 6** | 2da notificación | Scheduler (08:00 AM) | Email MUY urgente "Última llamada" |
| Día 6+ | Requiere citación | Sistema | Estado → `REQUIERE_CITACION` |

### Cálculo de Días Hábiles

- **Días hábiles**: Lunes a Viernes (excluyendo sábados, domingos y festivos)
- **Festivos**: Se consulta archivo `app/utils/calendario.py`
- **Plazo estándar**: 3 días hábiles desde la solicitud
- **Ejemplo**: 
  - Solicitud: Lunes 9:00 AM
  - Vencimiento: Jueves 23:59:59
  - 1er recordatorio: Viernes 08:00 AM
  - 2da notificación: Lunes siguiente 08:00 AM (día hábil 6)

---

## Tono de los Recordatorios

### Primera Notificación (Día 0)
- **Asunto**: 📄 Documentos Solicitados - Incapacidad #{codigo_radicacion}
- **Tono**: Informativo, neutro
- **Contenido**: Lista de documentos, plazo, enlace para cargar

### Primer Recordatorio (Día 3)
- **Asunto**: 🔔 RECORDATORIO: Documentos Pendientes - #{codigo_radicacion}
- **Tono**: Urgente pero respetuoso
- **Contenido**: Recordatorio del plazo vencido, urgencia de entrega

### Segunda Notificación (Día 6)
- **Asunto**: ⚠️ MUY URGENTE: Última Llamada Documentos - #{codigo_radicacion}
- **Tono**: Muy urgente, última oportunidad
- **Contenido**: Advertencia de que requiere citación presencial

---

## Ejemplos de Uso

### Ejemplo 1: Solicitud Exitosa (Usuario Final)

**Escenario**: Colaborador olvida adjuntar FURIPS al registrar incapacidad

1. **Día 0 - 10:00 AM**: Auxiliar María revisa incapacidad y detecta falta de FURIPS
2. **Día 0 - 10:05 AM**: María usa UC6 para solicitar FURIPS con plazo de 3 días
3. **Día 0 - 10:06 AM**: Juan (colaborador) recibe email:
   ```
   Asunto: 📄 Documentos Solicitados - Incapacidad #INC-2024-001
   
   Estimado Juan,
   
   Para continuar con la validación de tu incapacidad, necesitamos el siguiente documento:
   
   - FURIPS
   
   Por favor cárgalo antes del 22/10/2025 a las 23:59.
   
   [Botón: Cargar Documentos]
   ```

4. **Día 1 - 14:30 PM**: Juan ingresa al sistema y carga el FURIPS
5. **Día 1 - 14:31 PM**: María recibe notificación: "Documentación Completada"
6. **Día 1 - 14:35 PM**: María valida el FURIPS y aprueba la incapacidad

**Resultado**: ✅ Proceso completado en 1 día, sin recordatorios necesarios

---

### Ejemplo 2: Con Recordatorios (Usuario Final)

**Escenario**: Colaborador no responde inmediatamente

1. **Día 0** (Lunes): Solicitud de EPICRISIS enviada
2. **Día 3** (Jueves 08:00 AM): Sistema envía 1er recordatorio automáticamente
   ```
   Asunto: 🔔 RECORDATORIO: Documentos Pendientes - #INC-2024-001
   
   Estimado Juan,
   
   Te recordamos que el plazo para entregar EPICRISIS venció ayer.
   Por favor cárgalo lo antes posible.
   ```

3. **Día 5** (Sábado): Juan intenta cargar pero el sistema no cuenta fines de semana
4. **Día 6** (Lunes 08:00 AM): Sistema envía 2da notificación (última llamada)
5. **Día 6** (Lunes 10:00 AM): Juan carga el documento
6. **Día 6** (Lunes 10:01 AM): Estado regresa a PENDIENTE_VALIDACION

**Resultado**: ⚠️ Proceso completado con retrasos pero sin citación

---

### Ejemplo 3: Requiere Citación (Usuario Final)

**Escenario**: Colaborador no responde después de 6 días

1. **Día 0-6**: Colaborador ignora 2 notificaciones
2. **Día 6 (08:00 AM)**: Sistema marca solicitud como `REQUIERE_CITACION`
3. **Día 6 (09:00 AM)**: Auxiliar ve estado "Requiere Citación" en el dashboard
4. **Día 6 (10:00 AM)**: Auxiliar contacta al colaborador por teléfono
5. **Día 6 (15:00 PM)**: Colaborador se presenta presencialmente con el documento

**Resultado**: ⚠️ Completado presencialmente después de escalamiento

---

## Ejemplos para Desarrolladores

### Ejemplo 1: Crear Solicitud de Documentos

```python
from app.services.solicitud_documentos_service import SolicitudDocumentosService
from app.models.usuario import Usuario
from app.models.incapacidad import Incapacidad

# Obtener datos
auxiliar = Usuario.query.filter_by(email='auxiliar@empresa.com').first()
incapacidad = Incapacidad.query.get(123)

# Crear solicitud
exito, mensaje, solicitudes = SolicitudDocumentosService.crear_solicitud_documentos(
    incapacidad_id=incapacidad.id,
    documentos_a_solicitar=['EPICRISIS', 'FURIPS'],
    observaciones_por_tipo={
        'EPICRISIS': 'Requerido para validar diagnóstico',
        'FURIPS': 'Formato de accidente de trabajo'
    },
    usuario_auxiliar=auxiliar
)

if exito:
    print(f"✅ {mensaje}")
    print(f"📄 Solicitudes creadas: {len(solicitudes)}")
else:
    print(f"❌ Error: {mensaje}")
```

### Ejemplo 2: Procesar Recordatorios Manualmente

```python
from app.services.solicitud_documentos_service import SolicitudDocumentosService

# Ejecutar procesamiento de recordatorios (normalmente automático)
resultado = SolicitudDocumentosService.procesar_recordatorios()

print(f"Exito: {resultado['exito']}")
print(f"Total procesados: {resultado['total_procesados']}")
print(f"Recordatorios enviados: {resultado['recordatorios_enviados']}")
print(f"Requieren citación: {resultado['requieren_citacion']}")
```

### Ejemplo 3: Validar Respuesta del Colaborador

```python
from app.services.solicitud_documentos_service import SolicitudDocumentosService
from app.models.documento import Documento

# Obtener documentos recién cargados
documentos_nuevos = Documento.query.filter_by(
    incapacidad_id=123,
    fecha_carga=datetime.utcnow().date()
).all()

# Validar respuesta
completo, errores, pendientes = SolicitudDocumentosService.validar_respuesta_colaborador(
    incapacidad_id=123,
    documentos_entregados=documentos_nuevos
)

if completo:
    print("✅ Documentación completa")
else:
    print(f"⚠️ Aún pendientes: {[s.tipo_documento for s in pendientes]}")
```

### Ejemplo 4: Configurar Scheduler en Producción

```python
# En config.py
class ProductionConfig(Config):
    SCHEDULER_ENABLED = True  # Habilitar tareas automáticas
    
# En app/__init__.py (ya configurado automáticamente)
# El scheduler se inicia automáticamente si SCHEDULER_ENABLED=True
```

### Ejemplo 5: Ejecutar Tarea Manual (Testing/Debugging)

```python
from app.tasks.scheduler_uc6 import ejecutar_tarea_manual

# Ejecutar manualmente para testing
resultado = ejecutar_tarea_manual('procesar_recordatorios')

if resultado:
    print("✅ Tarea ejecutada correctamente")
else:
    print("❌ Error en la tarea")
```

---

## Logs Esperados

### Logs de Solicitud

```
2025-10-19 10:05:23 INFO [solicitud_documentos_service.py:125] 
✅ UC6: Solicitud creada para incapacidad #INC-2024-001 - 2 documentos solicitados

2025-10-19 10:05:24 INFO [email_service.py:475] 
📧 UC6: Notificación de solicitud enviada a colaborador@empresa.com (#INC-2024-001)
```

### Logs de Scheduler

```
2025-10-22 08:00:00 INFO [scheduler_uc6.py:32] 
🔄 Iniciando tarea programada: procesar_recordatorios_documentos()

2025-10-22 08:00:05 INFO [solicitud_documentos_service.py:310] 
📊 UC6: Procesando recordatorios - Solicitudes vencidas: 3

2025-10-22 08:00:06 INFO [email_service.py:560] 
📧 UC6: Recordatorio enviado a colaborador@empresa.com (solicitud #45)

2025-10-22 08:00:10 INFO [scheduler_uc6.py:45] 
✅ Tarea de recordatorios ejecutada correctamente - Procesados: 3, Recordatorios enviados: 2
```

### Logs de Completitud

```
2025-10-22 14:30:45 INFO [solicitud_documentos_service.py:235] 
✅ UC6: Documentación completada para #INC-2024-001 - Notificando a auxiliar

2025-10-22 14:30:46 INFO [email_service.py:610] 
📧 UC6: Notificación de completitud enviada a auxiliar@empresa.com
```

### Logs de Error

```
2025-10-22 08:00:15 ERROR [email_service.py:630] 
❌ UC6: Error al notificar documentación completada para #INC-2024-001: 
Could not build url for endpoint 'incapacidades.validar_incapacidades'

2025-10-22 08:00:15 WARNING [solicitud_documentos_service.py:130] 
⚠️ UC6: No se pudo enviar notificación de solicitud: Error en plantilla de email
```

---

## Arquitectura Técnica

### Componentes

```
┌──────────────────────────────────────────────────────────┐
│                    ARQUITECTURA UC6                       │
└──────────────────────────────────────────────────────────┘

┌─────────────────┐       ┌──────────────────┐       ┌─────────────────┐
│  Rutas (Flask)  │◄──────│  Servicios (BL)  │──────►│   Modelos (ORM) │
│                 │       │                  │       │                 │
│ - solicitar     │       │ - crear_solicitud│       │ - Incapacidad   │
│ - cargar        │       │ - validar_resp   │       │ - Solicitud_Doc │
│ - validar       │       │ - proc_record    │       │ - Documento     │
└─────────────────┘       └──────────────────┘       └─────────────────┘
        │                          │                          │
        │                          ▼                          │
        │                  ┌──────────────┐                  │
        │                  │ Email Service│                  │
        │                  │              │                  │
        │                  │ - notificar_ │                  │
        │                  │   solicitud  │                  │
        │                  │ - notificar_ │                  │
        │                  │   recordatorio                  │
        │                  └──────────────┘                  │
        │                          │                          │
        ▼                          ▼                          ▼
┌──────────────────────────────────────────────────────────────┐
│                       BASE DE DATOS                           │
└──────────────────────────────────────────────────────────────┘

                     ┌──────────────────┐
                     │  APScheduler     │
                     │  (Background)    │
                     │                  │
                     │  Ejecuta 08:00 AM│
                     │  procesar_record │
                     └──────────────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │ Scheduler UC6    │
                     │ - registrar_tarea│
                     │ - procesar_record│
                     └──────────────────┘
```

### Modelos de Datos

**SolicitudDocumento**
```python
{
    "id": int,
    "incapacidad_id": int,
    "tipo_documento": str,  # EPICRISIS, FURIPS, etc.
    "estado": str,  # PENDIENTE, ENTREGADO, REQUIERE_CITACION
    "fecha_solicitud": datetime,
    "fecha_vencimiento": datetime,
    "fecha_entrega": datetime | None,
    "ultima_notificacion": datetime | None,
    "numero_recordatorios": int,
    "solicitado_por_id": int,  # ID del auxiliar
    "observaciones_auxiliar": str,
    "observaciones_colaborador": str
}
```

---

## Configuración y Deployment

### Variables de Entorno

```python
# En config.py
class Config:
    # Scheduler
    SCHEDULER_ENABLED = False  # Cambiar a True en producción
    
    # Email
    MAIL_ENABLED = True
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'noreply@empresa.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # UC6 Específico
    PLAZO_DOCUMENTOS_DIAS_HABILES = 3
    MAX_RECORDATORIOS = 2
```

### Deployment Checklist

- [ ] APScheduler instalado (`pip install APScheduler==3.10.4`)
- [ ] `SCHEDULER_ENABLED = True` en producción
- [ ] Configuración de email (SMTP) validada
- [ ] Timezone configurado: `America/Bogota`
- [ ] Logs configurados para capturar eventos del scheduler
- [ ] Monitoreo de tareas programadas (verificar ejecución diaria 08:00 AM)

---

## Preguntas Frecuentes (FAQ)

**P: ¿Qué pasa si el colaborador carga solo algunos documentos?**
R: El sistema permite carga parcial. La incapacidad permanece en `DOCUMENTACION_INCOMPLETA` hasta que todos los documentos solicitados estén entregados.

**P: ¿Se pueden solicitar más documentos después de que el colaborador cargó todos?**
R: Sí. El auxiliar puede reiniciar UC6 si detecta problemas en los documentos entregados, iniciando un nuevo ciclo de 3 días.

**P: ¿Qué sucede si el plazo vence en fin de semana o festivo?**
R: Los recordatorios solo se envían en días hábiles. Si el plazo vence un sábado, el recordatorio se envía el lunes siguiente.

**P: ¿Se puede extender el plazo?**
R: Actualmente la funcionalidad de extensión está fuera del scope básico. El auxiliar debe crear una nueva solicitud si necesita dar más tiempo.

**P: ¿Cómo se desactiva el scheduler en desarrollo?**
R: Configurar `SCHEDULER_ENABLED = False` en `config.py`. Por defecto está desactivado.

---

## Versionamiento

- **Versión**: 1.0.0
- **Fecha**: Octubre 2025
- **Autor**: Equipo de Desarrollo - Sistema de Incapacidades
- **Estado**: Implementado al 95%

### Cambios Futuros
- [ ] Funcionalidad de extensión de plazo (solicitud del colaborador)
- [ ] Dashboard de métricas de cumplimiento
- [ ] Notificaciones por SMS/WhatsApp (adicional a email)
- [ ] Firma digital de documentos
- [ ] Validación automática de documentos con IA

---

## Referencias

- **Código Fuente**: 
  - `app/services/solicitud_documentos_service.py`
  - `app/tasks/scheduler_uc6.py`
  - `app/utils/email_service.py`
  
- **Tests**:
  - `tests/test_notificaciones_uc6.py`
  - `tests/test_uc6_completo_e2e.py`
  - `tests/test_excepciones_uc6.py`

- **Templates de Email**:
  - `app/templates/emails/solicitud_documentos.html`
  - `app/templates/emails/recordatorio_documentos_dia2.html`
  - `app/templates/emails/segunda_notificacion_documentos.html`
  - `app/templates/emails/documentacion_completada.html`

- **Rutas Web**:
  - GET/POST `/incapacidades/<id>/solicitar-documentos`
  - GET/POST `/documentos/cargar-solicitados/<id>`

---

**Última actualización**: 19 de Octubre de 2025

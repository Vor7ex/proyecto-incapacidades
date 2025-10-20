# Tarea 2 - UC6: Utilidades Completadas ✅

## Resumen de Implementación

**Fecha:** 19 de octubre de 2025  
**Commit:** 815eb22  
**Tests:** 41/41 pasando (100%)

---

## Archivos Creados

### 1. `app/utils/calendario.py`
**Funcionalidades:**
- ✅ Constante `FESTIVOS_COLOMBIA` con festivos 2025-2026
- ✅ `es_dia_habil(fecha)` - Detecta fines de semana y festivos
- ✅ `sumar_dias_habiles(fecha_inicio, dias=3)` - Suma días hábiles saltando festivos
- ✅ `dias_habiles_restantes(fecha_inicio, fecha_vencimiento)` - Calcula días restantes
- ✅ `formatar_fecha_legible(fecha)` - Formato en español (ej: "viernes 17 de octubre de 2025")

**Tests:** 20/20 pasando
- Validación de días hábiles vs festivos
- Suma de días hábiles con salto de fines de semana
- Suma de días hábiles con salto de festivos
- Cálculo de días restantes (positivos y negativos)
- Formato de fechas en español

---

### 2. `app/utils/maquina_estados.py`
**Funcionalidades:**
- ✅ Matriz de transiciones válidas `TRANSICIONES_VALIDAS`
- ✅ `es_transicion_valida(estado_actual, estado_nuevo)` - Valida transiciones
- ✅ `obtener_transiciones_posibles(estado_actual)` - Lista estados permitidos
- ✅ `validar_cambio_estado(estado_nuevo, incapacidad, verificar_precondiciones)` - Validación completa

**Estados soportados:**
```
PENDIENTE_VALIDACION → DOCUMENTACION_INCOMPLETA | DOCUMENTACION_COMPLETA | RECHAZADA
DOCUMENTACION_INCOMPLETA → PENDIENTE_VALIDACION | DOCUMENTACION_COMPLETA | RECHAZADA
DOCUMENTACION_COMPLETA → APROBADA_PENDIENTE_TRANSCRIPCION | RECHAZADA
APROBADA_PENDIENTE_TRANSCRIPCION → TRANSCRITA
TRANSCRITA → COBRADA | RECHAZADA_ENTIDAD
COBRADA → PAGADA
RECHAZADA_ENTIDAD → TRANSCRITA (reintentos)
PAGADA → (estado final)
RECHAZADA → (estado final)
```

**Precondiciones validadas:**
- DOCUMENTACION_COMPLETA: requiere documentos cargados y solicitudes respondidas
- RECHAZADA: requiere motivo_rechazo
- APROBADA_PENDIENTE_TRANSCRIPCION: requiere documentación completa

**Tests:** 21/21 pasando
- Transiciones válidas e inválidas
- Estados finales sin transiciones
- Precondiciones de cambio de estado
- Validación de matriz completa

---

### 3. `app/utils/eventos_uc6.py`
**Funcionalidades:**
- ✅ Sistema de eventos de dominio (patrón Observer)
- ✅ Gestor centralizado `GestorEventos`
- ✅ 5 eventos de UC6:
  - `SolicitudDocumentosCreada`
  - `DocumentosEntregados`
  - `SolicitudVencida`
  - `RecordatorioEnviado`
  - `RequerimientoCitacion`

**API del Gestor:**
```python
gestor_eventos_uc6.suscribir(tipo_evento, handler)
gestor_eventos_uc6.emitir(evento)
gestor_eventos_uc6.desuscribir(tipo_evento, handler)
gestor_eventos_uc6.limpiar_suscriptores(tipo_evento)
```

**Funciones de conveniencia:**
- `emitir_solicitud_documentos_creada(...)`
- `emitir_documentos_entregados(...)`
- `emitir_solicitud_vencida(...)`
- `emitir_recordatorio_enviado(...)`
- `emitir_requerimiento_citacion(...)`

---

## Tests Creados

### `tests/test_calendario.py`
**20 test cases:**
- TestEsDiaHabil (5 tests)
- TestSumarDiasHabiles (5 tests)
- TestDiasHabilesRestantes (5 tests)
- TestFormatarFechaLegible (5 tests)

### `tests/test_maquina_estados.py`
**21 test cases:**
- TestEsTransicionValida (7 tests)
- TestObtenerTransicionesPosibles (5 tests)
- TestValidarCambioEstado (6 tests)
- TestMatrizTransiciones (3 tests)

---

## Ejemplos de Uso

### Calendario
```python
from datetime import date
from app.utils.calendario import sumar_dias_habiles, formatar_fecha_legible

# Calcular vencimiento (3 días hábiles)
hoy = date(2025, 10, 20)  # Lunes
vencimiento = sumar_dias_habiles(hoy, 3)  # 2025-10-23 (Jueves)

# Formatear para email
texto = formatar_fecha_legible(vencimiento)
# "jueves 23 de octubre de 2025"
```

### Máquina de Estados
```python
from app.utils.maquina_estados import validar_cambio_estado
from app.models.enums import EstadoIncapacidadEnum

# Validar cambio de estado
valido, mensaje = validar_cambio_estado(
    EstadoIncapacidadEnum.DOCUMENTACION_COMPLETA.value,
    incapacidad,
    verificar_precondiciones=True
)

if not valido:
    print(f"Error: {mensaje}")
```

### Eventos
```python
from app.utils.eventos_uc6 import gestor_eventos_uc6, SolicitudDocumentosCreada

# Suscribir handler
def mi_handler(evento):
    print(f"Solicitud creada para incapacidad {evento.incapacidad_id}")

gestor_eventos_uc6.suscribir(SolicitudDocumentosCreada, mi_handler)

# Emitir evento
from app.utils.eventos_uc6 import emitir_solicitud_documentos_creada
from datetime import datetime

emitir_solicitud_documentos_creada(
    incapacidad_id=123,
    documentos_solicitados=['EPICRISIS', 'FURIPS'],
    observaciones={'EPICRISIS': 'Documento ilegible'},
    fecha_vencimiento=datetime.now(),
    auxiliar_id=1
)
```

---

## Integración con Tarea 1

Las utilidades creadas se integran perfectamente con los modelos de la Tarea 1:

1. **`SolicitudDocumento`** usa `calendario.py`:
   - `dias_restantes()` → `dias_habiles_restantes()`
   - `esta_vencida()` → usa fechas calculadas con días hábiles

2. **`Incapacidad`** usa `maquina_estados.py`:
   - `cambiar_estado()` → valida con `validar_cambio_estado()`

3. **Servicios UC6** usarán `eventos_uc6.py`:
   - Emisión de eventos en cada operación
   - Logging y auditoría vía suscriptores

---

## Verificación

```bash
# Tests
python -m pytest tests/test_calendario.py tests/test_maquina_estados.py -v
# 41 passed in 1.00s

# Compilación
python -m compileall -q app/utils
# OK

# Importación
python -c "from app.utils.calendario import sumar_dias_habiles; print('OK')"
python -c "from app.utils.maquina_estados import es_transicion_valida; print('OK')"
python -c "from app.utils.eventos_uc6 import gestor_eventos_uc6; print('OK')"
```

---

## Próximos Pasos (Tarea 3)

Con las utilidades completadas, la Tarea 3 implementará:
- `SolicitudDocumentosService` que usará:
  - `calendario.py` para calcular fechas de vencimiento
  - `maquina_estados.py` para validar cambios de estado
  - `eventos_uc6.py` para emitir eventos de dominio
- Lógica de negocio de UC6
- Integración con modelos de Tarea 1

---

## Criterios de Aceptación ✅

- ✅ `sumar_dias_habiles()` calcula correctamente (3 días hábiles)
- ✅ Festivos se respetan
- ✅ Fines de semana se saltan
- ✅ Tests 41/41 pasando (100%)
- ✅ Máquina de estados valida transiciones
- ✅ Eventos de dominio emitibles y suscribibles
- ✅ Código compilable sin errores
- ✅ Documentación completa con ejemplos

**Estado:** ✅ COMPLETADA  
**Tiempo:** ~2 horas (según estimación)

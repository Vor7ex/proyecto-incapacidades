# 🔐 Roles y Permisos del Sistema

## ⚡ Decisión de Diseño: 2 Roles en lugar de 3

**Por qué eliminamos el rol "Jefe RRHH":**
- ✅ **Simplicidad**: Menos complejidad para Release 1.0
- ✅ **Funcionalidad completa**: Auxiliar RRHH puede validar Y aprobar/rechazar
- ✅ **Flujo más ágil**: No requiere aprobación multinivel innecesaria
- ✅ **Escalable**: Se puede agregar el rol "Jefe" en versiones futuras si se requiere
- ✅ **Casos de uso cumplidos**: CU-006 y CU-007 son realizados por Auxiliar RRHH

---

## Basado en Casos de Uso del Documento PDF

### 👤 **Colaborador** (`rol='colaborador'`)

**Casos de Uso:**
- ✅ **CU-001**: Iniciar Sesión
- ✅ **CU-002**: Cerrar Sesión
- ✅ **CU-003**: Registrar Incapacidad
- ✅ **CU-004**: Consultar Mis Incapacidades
- ✅ **CU-005**: Ver Detalle de Incapacidad (solo propias)

**Permisos:**
- Ver y gestionar **solo sus propias** incapacidades
- Registrar nuevas incapacidades
- Subir documentos (certificado, epicrisis)
- Ver el estado de sus solicitudes

**Rutas Accesibles:**
- `/incapacidades/registrar` - Registrar nueva incapacidad
- `/incapacidades/mis-incapacidades` - Ver mis incapacidades
- `/incapacidades/detalle/<id>` - Ver detalle (solo propias)

---

### 👨‍💼 **Auxiliar RRHH** (`rol='auxiliar'`)

**Casos de Uso:**
- ✅ **CU-001**: Iniciar Sesión
- ✅ **CU-002**: Cerrar Sesión
- ✅ **CU-006**: Validar Incapacidad
  - Verificar documentación completa
  - Solicitar documentos faltantes
  - Marcar como "En revisión" si está completa
- ✅ **CU-007**: Aprobar/Rechazar Incapacidad
  - Aprobar incapacidades validadas
  - Rechazar con motivo justificado
  - Solo incapacidades en estado "En revisión"

**Permisos:**
- Ver **todas** las incapacidades
- Validar documentación de incapacidades
- Aprobar/Rechazar incapacidades
- Ver estadísticas y reportes
- Descargar cualquier documento

**Rutas Accesibles:**
- `/incapacidades/dashboard-auxiliar` - Dashboard principal
- `/incapacidades/validar/<id>` - Validar documentación
- `/incapacidades/aprobar-rechazar/<id>` - Aprobar/Rechazar
- `/incapacidades/detalle/<id>` - Ver cualquier incapacidad
- `/incapacidades/estadisticas` - Ver estadísticas

---

## 🔄 Flujo de Trabajo Simplificado

```
1. Colaborador → Registra Incapacidad (CU-003)
   ↓ Estado: "Pendiente"
   
2. Auxiliar RRHH → Valida Documentación (CU-006)
   ↓ Opciones:
   │  • Documentación completa → Estado: "En revisión"
   │  • Documentación incompleta → Solicita documentos → Mantiene "Pendiente"
   
3. Auxiliar RRHH → Aprueba o Rechaza (CU-007)
   ↓ Decisión:
   │  • Aprobar → Estado: "Aprobada"
   │  • Rechazar → Estado: "Rechazada" (con motivo)
   
4. Colaborador → Consulta Estado (CU-004)
```

---

## 📋 Matriz de Permisos

| Funcionalidad | Colaborador | Auxiliar RRHH |
|--------------|-------------|---------------|
| Registrar incapacidad | ✅ | ❌ |
| Ver mis incapacidades | ✅ | - |
| Ver todas las incapacidades | ❌ | ✅ |
| Validar documentación | ❌ | ✅ |
| Aprobar/Rechazar | ❌ | ✅ |
| Ver estadísticas | ❌ | ✅ |
| Descargar documentos propios | ✅ | - |
| Descargar cualquier documento | ❌ | ✅ |

---

## 🔑 Credenciales de Prueba

```
Colaborador:
  Email: empleado@test.com
  Password: 123456
  Rol: colaborador

Auxiliar RRHH:
  Email: auxiliar@test.com
  Password: 123456
  Rol: auxiliar
```

---

## 🚀 Mejoras Futuras (Release 2.0)

### Posible incorporación de rol "Jefe RRHH":
- [ ] Separar validación (Auxiliar) de aprobación (Jefe)
- [ ] Flujo de aprobación multinivel
- [ ] Agregar rol Admin para gestión de usuarios
- [ ] Sistema de notificaciones por email
- [ ] Logs de auditoría de todas las acciones
- [ ] Firma digital para aprobaciones

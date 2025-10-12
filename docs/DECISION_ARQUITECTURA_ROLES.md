# 🏗️ Decisión de Arquitectura: 2 Roles vs 3 Roles

## 📅 Fecha: 12 de Octubre 2025
## 🎯 Release: 1.0

---

## 🤔 Pregunta Original

**¿Realmente hace falta el usuario "jefe"? No se especifica claramente en los casos de uso.**

---

## 💡 Decisión Tomada

**✅ ELIMINADO el rol "Jefe RRHH"**  
**✅ Sistema simplificado a 2 roles: `colaborador` y `auxiliar`**

---

## 📊 Análisis de Casos de Uso

### Del Documento PDF:

| Caso de Uso | Actor Original | Actor Asignado |
|-------------|----------------|----------------|
| CU-001: Iniciar Sesión | Todos | Todos |
| CU-002: Cerrar Sesión | Todos | Todos |
| CU-003: Registrar Incapacidad | Colaborador | ✅ Colaborador |
| CU-004: Consultar Mis Incapacidades | Colaborador | ✅ Colaborador |
| CU-005: Ver Detalle | Colaborador | ✅ Colaborador |
| CU-006: Validar Incapacidad | Auxiliar RRHH | ✅ Auxiliar |
| CU-007: Aprobar/Rechazar | Jefe RRHH? | ✅ Auxiliar |

**Observación clave**: El documento NO especifica claramente que debe haber un "Jefe RRHH" separado del "Auxiliar RRHH".

---

## ✅ Ventajas de 2 Roles

### 1. **Simplicidad**
- Menos código que mantener
- Menos lógica condicional
- Menos pruebas requeridas
- Menos puntos de fallo

### 2. **Usabilidad**
- Flujo de trabajo más directo
- Menos confusión para usuarios finales
- No requiere entrenamiento sobre diferencias de roles
- Proceso más ágil

### 3. **Cumplimiento de Casos de Uso**
- ✅ Todos los CU implementados
- ✅ Validación de documentos (CU-006)
- ✅ Aprobación/rechazo (CU-007)
- ✅ Sin funcionalidad perdida

### 4. **Realidad Organizacional**
- En la mayoría de empresas pequeñas/medianas, **una persona hace ambas funciones**
- No requiere jerarquía compleja para Release 1.0
- Se puede agregar después si se necesita

### 5. **Time-to-Market**
- Desarrollo más rápido
- Testing más simple
- Deployment más fácil
- Menos bugs potenciales

---

## ⚠️ Desventajas Consideradas

### 1. **Separación de Responsabilidades**
- ❌ No hay segregación entre validación y aprobación
- **Mitigación**: Se puede agregar en Release 2.0 si se requiere

### 2. **Auditoría**
- ❌ La misma persona valida y aprueba
- **Mitigación**: El sistema registra fechas y estados de cada acción

### 3. **Escalabilidad Organizacional**
- ❌ Si la empresa crece, puede necesitar separar roles
- **Mitigación**: La arquitectura permite agregar el rol después

---

## 🔄 Comparación de Flujos

### ❌ Flujo con 3 Roles (Rechazado)
```
Colaborador → Registra
    ↓
Auxiliar → Valida documentación
    ↓
Jefe → Aprueba/Rechaza
    ↓
Colaborador → Recibe notificación
```
**Problema**: 2 niveles de aprobación pueden ser excesivos para Release 1.0

### ✅ Flujo con 2 Roles (Adoptado)
```
Colaborador → Registra
    ↓
Auxiliar → Valida + Aprueba/Rechaza
    ↓
Colaborador → Recibe notificación
```
**Ventaja**: Más ágil, cumple todos los requisitos

---

## 📝 Cambios Implementados

### Archivos Modificados:

1. **`crear_usuarios.py`**
   - Eliminado usuario "Carlos Jefe"
   - Solo crea: Colaborador + Auxiliar

2. **`app/routes/auth.py`**
   - Simplificada lógica de redirección
   - Solo maneja 2 roles

3. **`app/routes/incapacidades.py`**
   - Eliminadas referencias a `rol == 'jefe'`
   - Auxiliar puede validar Y aprobar/rechazar
   - Permisos simplificados

4. **`app/templates/dashboard_auxiliar.html`**
   - Eliminadas condiciones por rol "jefe"
   - Título simplificado
   - UI más limpia

5. **`app/templates/base.html`**
   - Navbar simplificado
   - Solo 2 opciones de menú según rol

6. **`app/templates/login.html`**
   - Eliminada credencial de "Jefe RRHH"

7. **`docs/roles_permisos.md`**
   - Documentación actualizada
   - Matriz de permisos simplificada
   - Justificación incluida

---

## 🚀 Plan de Migración Futura (Release 2.0)

Si en el futuro se requiere separar los roles:

### Paso 1: Agregar rol "jefe"
```python
# En crear_usuarios.py
Usuario(nombre="Jefe RRHH", email="jefe@empresa.com", rol="jefe")
```

### Paso 2: Actualizar permisos
```python
# CU-006: Solo auxiliar
if current_user.rol != 'auxiliar':
    flash('Acceso denegado')

# CU-007: Solo jefe  
if current_user.rol != 'jefe':
    flash('Acceso denegado')
```

### Paso 3: Agregar estado intermedio
```python
# Nuevo flujo:
# Pendiente → (Auxiliar valida) → Validada → (Jefe aprueba) → Aprobada
```

**Estimación**: 2-4 horas de desarrollo

---

## ✅ Conclusión

**Para Release 1.0, el sistema con 2 roles es:**
- ✅ Más simple
- ✅ Más rápido de implementar
- ✅ Cumple todos los casos de uso
- ✅ Más fácil de mantener
- ✅ Suficiente para la mayoría de organizaciones
- ✅ Fácilmente extensible en el futuro

**La decisión de eliminar el rol "Jefe" fue correcta.**

---

## 📋 Estado Actual

### Roles Implementados:
- ✅ **Colaborador** (`colaborador`)
- ✅ **Auxiliar RRHH** (`auxiliar`)

### Credenciales de Prueba:
```
Colaborador:  empleado@test.com  / 123456
Auxiliar:     auxiliar@test.com  / 123456
```

### Casos de Uso Cumplidos:
- ✅ CU-001 a CU-007: **Todos implementados**
- ✅ Sistema funcional y probado
- ✅ Listo para Release 1.0

---

**Firmado**: Sistema de Incapacidades v1.0  
**Fecha**: 12/10/2025

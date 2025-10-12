# 🐛 Bug Fix: Alertas que Desaparecen en Validación de Documentos

## 📋 Problema Reportado

**Síntoma:**
La sección de "Validación Automática de Requisitos" en la página de validación de documentos desaparece después de unos segundos.

**Contenido que desaparece:**
```
Validación Automática de Requisitos
Checklist de Documentos Obligatorios:
✅ Certificado de Incapacidad: Presente
✅ Epicrisis: No requerida para este caso (Presente de todas formas)
✓ Estado:
✅ Certificado presente
✅ Documentación completa
✅ Todos los documentos obligatorios están presentes
```

---

## 🔍 Causa Raíz

### Código Problemático en `app/static/js/main.js`:

```javascript
// ❌ PROBLEMA: Cierra TODAS las alertas después de 5 segundos
document.addEventListener('DOMContentLoaded', function() {
  const alertas = document.querySelectorAll('.alert:not(.alert-warning):not(.alert-info)');
  alertas.forEach(alerta => {
    setTimeout(() => {
      const bsAlert = new bootstrap.Alert(alerta);
      bsAlert.close();  // ← Esto cierra las alertas de validación también!
    }, 5000);
  });
});
```

**Explicación:**
- El script selecciona **todas** las alertas de la página (excepto warning e info)
- Después de 5 segundos, las cierra automáticamente
- Esto incluye las alertas de validación de documentos en el formulario
- Las alertas de validación **NO deberían cerrarse** porque son parte del contenido permanente

---

## ✅ Solución Implementada

### Código Corregido en `app/static/js/main.js`:

```javascript
// ✅ SOLUCIÓN: Solo cerrar alertas de mensajes flash (temporales)
document.addEventListener('DOMContentLoaded', function() {
  // Solo cerrar alertas que estén en el contenedor de mensajes flash
  const alertasFlash = document.querySelectorAll('.container > .alert');
  alertasFlash.forEach(alerta => {
    // No cerrar alertas dentro de cards o formularios (son parte del contenido)
    if (!alerta.closest('.card-body') && !alerta.closest('form')) {
      setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alerta);
        bsAlert.close();
      }, 5000);
    }
  });
});
```

**Cambios:**
1. ✅ Selector más específico: `.container > .alert` (solo hijos directos del container)
2. ✅ Verificación adicional: `!alerta.closest('.card-body')` (no cerrar alertas dentro de cards)
3. ✅ Verificación adicional: `!alerta.closest('form')` (no cerrar alertas dentro de formularios)

---

## 🎯 Comportamiento Esperado

### Alertas que SÍ se cierran (mensajes flash):
```html
<!-- En base.html, fuera de .card-body -->
<div class="container mt-3">
  <div class="alert alert-success">
    ✅ Incapacidad registrada exitosamente  ← Se cierra a los 5s
  </div>
</div>
```

### Alertas que NO se cierran (contenido permanente):
```html
<!-- En validar_incapacidades.html, dentro de .card-body -->
<div class="card-body">
  <div class="alert alert-success">
    ✅ Validación Automática de Requisitos  ← NO se cierra, es permanente
  </div>
</div>
```

---

## 🧪 Cómo Probar

### Paso 1: Limpiar caché del navegador
```
1. Presiona Ctrl + Shift + Delete
2. Selecciona "Caché de imágenes y archivos"
3. Limpia los datos
```

O simplemente:
```
Ctrl + F5 (recarga forzada sin caché)
```

### Paso 2: Acceder a validación de documentos
```
1. Iniciar sesión como Auxiliar RRHH
2. Dashboard → Validar incapacidad
3. Observar que la sección de "Validación Automática" NO desaparece
```

### Paso 3: Verificar mensajes flash
```
1. Registrar una nueva incapacidad
2. El mensaje "Incapacidad registrada exitosamente" debe desaparecer a los 5s
```

---

## 📝 Notas Técnicas

### ¿Por qué Flask no recarga archivos JS automáticamente?

Flask en modo debug solo recarga:
- ✅ Archivos Python (`.py`)
- ✅ Templates HTML (`.html`)
- ❌ Archivos estáticos (`.js`, `.css`, `.jpg`, etc.)

Para forzar recarga de archivos estáticos:
1. **Limpia caché del navegador**: Ctrl + F5
2. **Versiona los archivos**: `main.js?v=2`
3. **Usa herramientas de desarrollo**: Desactiva caché en DevTools

### Alternativa: Versionado de archivos estáticos

```html
<!-- En base.html -->
<script src="{{ url_for('static', filename='js/main.js') }}?v={{ config.VERSION }}"></script>
```

```python
# En config.py
VERSION = '1.0.1'
```

---

## ✅ Verificación

**Antes del fix:**
- ❌ Alertas de validación desaparecen a los 5s
- ✅ Mensajes flash desaparecen a los 5s

**Después del fix:**
- ✅ Alertas de validación NO desaparecen (permanentes)
- ✅ Mensajes flash desaparecen a los 5s (comportamiento correcto)

---

## 🚀 Estado

- ✅ Bug identificado
- ✅ Código corregido en `main.js`
- ✅ Documentación creada
- ⏳ Requiere: Ctrl + F5 en el navegador para aplicar cambios

---

**Fecha:** 12/10/2025  
**Archivo afectado:** `app/static/js/main.js`  
**Tipo de fix:** JavaScript - Selector de alertas  
**Severidad:** Media (afecta UX pero no funcionalidad)

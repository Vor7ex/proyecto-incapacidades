# ✅ Checklist Git - Estado del Repositorio

## 📋 Archivos Listos para Commit

### ✅ Modificados (10 archivos):
- `.gitignore` - Actualizado con más exclusiones
- `app/__init__.py` - Creación automática de carpeta uploads
- `app/routes/auth.py` - Simplificado a 2 roles
- `app/routes/incapacidades.py` - Permisos corregidos
- `app/static/js/main.js` - Fix de alertas que desaparecen
- `app/templates/base.html` - Navbar actualizado
- `app/templates/dashboard_auxiliar.html` - Simplificado
- `app/templates/login.html` - Credenciales actualizadas
- `config.py` - Rutas absolutas para uploads
- `requirements.txt` - Dependencias actualizadas

### ✨ Nuevos (8 archivos):
- `app/static/uploads/.gitkeep` - Mantiene carpeta en Git
- `corregir_rutas.py` - Script para migrar rutas de BD
- `crear_usuarios.py` - Script para crear usuarios de prueba
- `verificar_archivos.py` - Script de diagnóstico
- `docs/BUG_FIX_ALERTAS.md` - Documentación de fix
- `docs/DECISION_ARQUITECTURA_ROLES.md` - Decisión de diseño
- `docs/SOLUCION_PROBLEMAS.md` - Guía de troubleshooting
- `docs/roles_permisos.md` - Matriz de permisos

---

## ❌ Archivos Correctamente Ignorados

### Base de datos:
- ✅ `instance/database.db`

### Archivos subidos:
- ✅ `app/static/uploads/*.pdf` (7 archivos PDF ignorados)

### Cache de Python:
- ✅ `__pycache__/`
- ✅ `*.pyc`, `*.pyo`, `*.pyd`

### Entorno virtual:
- ✅ `venv/`

---

## 🚀 Comandos Sugeridos

```bash
# Ver estado
git status

# Agregar todos los cambios
git add .

# Commit
git commit -m "feat: Simplificación a 2 roles y correcciones varias

- Eliminado rol 'jefe' (solo colaborador y auxiliar)
- Corregidas rutas absolutas para uploads
- Fix: alertas de validación que desaparecían
- Agregados scripts de utilidad
- Actualizada documentación completa
- Mejorado .gitignore"

# Push
git push origin main
```

---

## 📊 Resumen

| Categoría | Cantidad | Estado |
|-----------|----------|--------|
| Modificados | 10 | ✅ Listos |
| Nuevos | 8 | ✅ Listos |
| Ignorados | ~15+ | ✅ Correcto |
| **Total** | **18** | ✅ **Listo para commit** |

---

**Estado:** ✅ Repositorio listo para commit y push

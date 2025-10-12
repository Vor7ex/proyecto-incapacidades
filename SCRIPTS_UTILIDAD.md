# Scripts de Utilidad

Este documento describe los scripts disponibles en la raíz del proyecto.

## 🚀 Scripts Principales

### `run.py`
**Uso:** Ejecutar la aplicación Flask

```bash
python run.py
```

Inicia el servidor en http://localhost:5000

---

### `crear_usuarios.py`
**Uso:** Crear usuarios de prueba en la base de datos

```bash
python crear_usuarios.py
```

**Crea:**
- Colaborador: `colaborador@test.com` / `123456`
- Auxiliar: `auxiliar@test.com` / `123456`

**Cuándo usar:**
- Primera vez que ejecutas el proyecto
- Después de eliminar la base de datos
- Para resetear usuarios de prueba

---

### `toggle_email.py`
**Uso:** Controlar el envío de emails (on/off/status)

```bash
python toggle_email.py on      # Activar envío real de emails
python toggle_email.py off     # Desactivar (modo simulación)
python toggle_email.py status  # Ver estado actual
```

**Cuándo usar:**
- Para ahorrar cuota de emails en desarrollo (off)
- Para probar emails reales antes de producción (on)
- Para verificar configuración actual (status)

**Funcionamiento:**
- Modifica `MAIL_ENABLED` en el archivo `.env`
- En modo OFF: logs en consola, no envía emails
- En modo ON: envía emails reales vía SMTP

---

## 📋 Flujo de Trabajo Recomendado

### Setup Inicial
```bash
# 1. Activar entorno virtual
venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar .env
# Copiar .env.example a .env y editar

# 4. Crear usuarios de prueba
python crear_usuarios.py

# 5. Desactivar emails para desarrollo
python toggle_email.py off

# 6. Ejecutar aplicación
python run.py
```

### Desarrollo Diario
```bash
# Activar entorno
venv\Scripts\activate

# Verificar estado de emails
python toggle_email.py status

# Ejecutar app
python run.py
```

### Antes de Probar Emails
```bash
# Activar emails
python toggle_email.py on

# Ejecutar app y probar flujo
python run.py

# Desactivar emails después de probar
python toggle_email.py off
```

---

## 🗑️ Scripts Eliminados

Los siguientes scripts fueron eliminados por ser temporales o redundantes:

- ❌ `corregir_rutas.py` - Script de corrección temporal
- ❌ `probar_email.py` - Funcionalidad incorporada en `toggle_email.py`
- ❌ `verificar_archivos.py` - Script de debug temporal
- ❌ `verificar_uc2.py` - Funcionalidad incorporada en `toggle_email.py`

---

## 💡 Tips

1. **Siempre desactiva emails en desarrollo** para ahorrar cuota
2. **Usa `crear_usuarios.py`** cada vez que borres la BD
3. **Verifica el estado** con `toggle_email.py status` antes de probar
4. **Lee los logs** en consola para ver emails simulados

---

**Última actualización:** 2025-10-12

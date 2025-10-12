# 🚀 Guía Rápida - Sistema de Incapacidades

**Última actualización:** 2025-10-12  
**Estado:** 55.6% completo

---

## ⚡ Inicio Rápido (5 minutos)

```bash
# 1. Activar entorno virtual
venv\Scripts\activate

# 2. Instalar dependencias (solo primera vez)
pip install -r requirements.txt

# 3. Crear usuarios de prueba (solo primera vez)
python crear_usuarios.py

# 4. Desactivar emails para desarrollo
python toggle_email.py off

# 5. Ejecutar aplicación
python run.py

# 6. Abrir navegador: http://localhost:5000
```

---

## 👤 Credenciales de Acceso

| Rol | Email | Contraseña |
|-----|-------|------------|
| Colaborador | `colaborador@test.com` | `123456` |
| Auxiliar RRHH | `auxiliar@test.com` | `123456` |

---

## 📧 Control de Emails

```bash
# Ver estado actual
python toggle_email.py status

# Desactivar (desarrollo) - NO consume cuota
python toggle_email.py off

# Activar (pruebas) - SÍ consume cuota Mailtrap
python toggle_email.py on
```

**Modo OFF (recomendado en desarrollo):**
- ✅ Logs en consola
- ✅ No consume cuota
- ✅ Ver contenido de emails

**Modo ON (pruebas antes de producción):**
- 📧 Envío real vía Mailtrap
- 📉 Consume cuota (100/mes gratis)

---

## 🧪 Flujo de Prueba Completo

### Como Colaborador:
1. Login: `colaborador@test.com` / `123456`
2. Ir a "Registrar Incapacidad"
3. Llenar formulario:
   - Tipo: "Enfermedad general"
   - Fecha inicio: Hoy
   - Fecha fin: +3 días
   - Cargar certificado PDF
4. Enviar
5. Ver mensaje de confirmación ✅
6. Ver email en consola (si MAIL_ENABLED=False)

### Como Auxiliar RRHH:
1. Login: `auxiliar@test.com` / `123456`
2. Ir a "Validar Incapacidades"
3. Seleccionar incapacidad
4. Revisar documentos
5. Marcar validación completada
6. Aprobar o rechazar

---

## 📂 Archivos Importantes

### Configuración
- `.env` - Variables de entorno (NO subir a git)
- `config.py` - Configuración de Flask
- `.gitignore` - Archivos ignorados

### Scripts
- `run.py` - Ejecutar aplicación
- `crear_usuarios.py` - Crear usuarios de prueba
- `toggle_email.py` - Control on/off emails

### Documentación
- `README.md` - Documentación principal
- `SCRIPTS_UTILIDAD.md` - Descripción de scripts
- `docs/ESTADO_PROYECTO.md` - Estado detallado
- `docs/CONTROL_EMAILS.md` - Sistema de emails

---

## 🐛 Problemas Comunes

### 1. Error al ejecutar `python run.py`
```bash
# Verificar entorno virtual activado
venv\Scripts\activate

# Reinstalar dependencias
pip install -r requirements.txt
```

### 2. No aparecen usuarios
```bash
# Recrear usuarios
python crear_usuarios.py
```

### 3. Emails no se ven en consola
```bash
# Verificar modo desactivado
python toggle_email.py status

# Si está ON, desactivar
python toggle_email.py off
```

### 4. No puedo subir archivos
- Verificar carpeta `app/static/uploads/` existe
- Formatos permitidos: PDF, PNG, JPG, JPEG
- Tamaño máximo: 16MB

---

## 📊 Estado del Proyecto

| Caso de Uso | Estado | Prioridad |
|-------------|--------|-----------|
| UC1 - Registrar incapacidad | 85% | ✅ Completar |
| UC2 - Notificar RRHH | 70% | 🟡 Mejorar |
| UC3 - Consultar incapacidades | 60% | 🟢 Mejorar |
| UC4 - Validar documentación | 75% | ✅ Completar |
| UC5 - Verificar requisitos | 40% | 🔴 URGENTE |
| UC6 - Solicitar documentos | 0% | 🔴 URGENTE |
| UC7 - Aprobar/Rechazar | 65% | 🟡 Mejorar |
| UC15 - Almacenar documentos | 50% | 🟡 Mejorar |

**Bloqueadores:** UC6 (0%), UC5 (40%)

---

## 🎯 Próximos Pasos

1. **Implementar UC6** - Solicitar documentos faltantes (4 días)
2. **Completar UC5** - Validación automática por tipo (3 días)
3. **Testing integral** - Casos excepcionales (2 días)

**Tiempo estimado para Release 1.0:** 14 días

---

## 📞 Ayuda

- **Documentación completa:** Ver `README.md`
- **Estado detallado:** Ver `docs/ESTADO_PROYECTO.md`
- **Troubleshooting:** Ver `docs/SOLUCION_PROBLEMAS.md`
- **Scripts:** Ver `SCRIPTS_UTILIDAD.md`

---

**Tip:** Mantén `MAIL_ENABLED=False` durante desarrollo y actívalo solo para pruebas finales.

# 🔧 Solución de Problemas Comunes

## ❌ Error: "El sistema no puede encontrar la ruta especificada"

### Síntomas:
```
Error al descargar el archivo: [WinError 3] El sistema no puede encontrar la ruta especificada: 
'C:\\Users\\Juan\\dev\\proyecto-incapacidades\\app\\app/static/uploads\\archivo.pdf'
```

### Causa:
- Las rutas en la base de datos están mal formadas (relativas en lugar de absolutas)
- La carpeta `uploads` no existe

### ✅ Solución:

#### 1. Ejecutar el script de corrección de rutas:
```bash
python corregir_rutas.py
```

Esto corregirá todas las rutas en la base de datos a rutas absolutas.

#### 2. Verificar que la carpeta existe:
```bash
# Windows PowerShell
if (!(Test-Path "app\static\uploads")) { New-Item -ItemType Directory -Path "app\static\uploads" }

# CMD
if not exist "app\static\uploads" mkdir "app\static\uploads"
```

#### 3. Reiniciar el servidor:
La aplicación ahora crea automáticamente la carpeta al iniciar.

---

## 📝 Cambios Realizados en el Código

### `config.py`
**Antes:**
```python
UPLOAD_FOLDER = 'app/static/uploads'  # Ruta relativa ❌
```

**Después:**
```python
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads')  # Ruta absoluta ✅
```

### `app/__init__.py`
**Agregado:**
```python
# Crear carpeta de uploads si no existe
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
```

---

## 🔍 Verificación Manual

### Ver las rutas actuales en la base de datos:
```python
from app import create_app, db
from app.models.documento import Documento

app = create_app()
with app.app_context():
    docs = Documento.query.all()
    for doc in docs:
        print(f"ID {doc.id}: {doc.ruta}")
```

### Verificar archivos en el sistema:
```bash
dir app\static\uploads
```

---

## 🚀 Prevención Futura

El sistema ahora:
1. ✅ Usa rutas absolutas en `config.py`
2. ✅ Crea automáticamente la carpeta `uploads` al iniciar
3. ✅ Guarda rutas absolutas en la base de datos
4. ✅ El script `corregir_rutas.py` está disponible para migraciones

---

## 📋 Otros Problemas Comunes

### Archivo no se sube:
- Verificar que el formulario tenga `enctype="multipart/form-data"`
- Verificar que el tamaño no exceda 10MB
- Verificar que la extensión sea permitida: `.pdf`, `.png`, `.jpg`, `.jpeg`

### Error de permisos:
```bash
# Dar permisos de escritura a la carpeta uploads (Linux/Mac)
chmod 755 app/static/uploads
```

### Limpiar archivos huérfanos:
```bash
# Listar archivos que no están en la base de datos
python -c "import os; from app import create_app, db; from app.models.documento import Documento; app = create_app(); app.app_context().push(); archivos = set(os.listdir('app/static/uploads')); docs_bd = set([os.path.basename(d.ruta) for d in Documento.query.all()]); huerfanos = archivos - docs_bd; print('Archivos huérfanos:', huerfanos)"
```

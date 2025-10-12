"""
Script de verificación del sistema de archivos
"""
from app import create_app, db
from app.models.documento import Documento
from config import Config
import os

app = create_app()

print("=" * 70)
print("🔍 VERIFICACIÓN DEL SISTEMA DE ARCHIVOS")
print("=" * 70)

# 1. Verificar configuración
print(f"\n1️⃣ Configuración:")
print(f"   UPLOAD_FOLDER: {Config.UPLOAD_FOLDER}")
print(f"   Existe: {'✅ SÍ' if os.path.exists(Config.UPLOAD_FOLDER) else '❌ NO'}")

# 2. Verificar documentos en la base de datos
with app.app_context():
    documentos = Documento.query.all()
    print(f"\n2️⃣ Documentos en la base de datos: {len(documentos)}")
    
    archivos_ok = 0
    archivos_error = 0
    
    for doc in documentos:
        existe = os.path.exists(doc.ruta)
        if existe:
            tamaño = os.path.getsize(doc.ruta)
            print(f"   ✅ ID {doc.id}: {os.path.basename(doc.ruta)} ({tamaño} bytes)")
            archivos_ok += 1
        else:
            print(f"   ❌ ID {doc.id}: {os.path.basename(doc.ruta)} - ARCHIVO NO ENCONTRADO")
            print(f"      Ruta: {doc.ruta}")
            archivos_error += 1

# 3. Verificar archivos en el sistema
print(f"\n3️⃣ Archivos en el sistema:")
if os.path.exists(Config.UPLOAD_FOLDER):
    archivos = os.listdir(Config.UPLOAD_FOLDER)
    print(f"   Total de archivos: {len(archivos)}")
    for archivo in archivos:
        ruta_completa = os.path.join(Config.UPLOAD_FOLDER, archivo)
        tamaño = os.path.getsize(ruta_completa)
        print(f"   📄 {archivo} ({tamaño} bytes)")
else:
    print(f"   ❌ La carpeta no existe")

# 4. Resumen
print(f"\n" + "=" * 70)
print(f"📊 RESUMEN:")
print(f"   Documentos en BD: {len(documentos)}")
print(f"   Archivos OK: {archivos_ok}")
print(f"   Archivos con error: {archivos_error}")
print(f"   Estado: {'✅ TODO OK' if archivos_error == 0 else '⚠️ HAY ERRORES'}")
print("=" * 70)

"""
Script para corregir las rutas de documentos en la base de datos
"""
from app import create_app, db
from app.models.documento import Documento
import os

app = create_app()

with app.app_context():
    # Obtener todos los documentos
    documentos = Documento.query.all()
    
    print(f"📄 Encontrados {len(documentos)} documentos en la base de datos\n")
    
    # Ruta base correcta
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads')
    
    corregidos = 0
    
    for doc in documentos:
        # Extraer solo el nombre del archivo de la ruta antigua
        nombre_archivo_guardado = os.path.basename(doc.ruta)
        
        # Construir la nueva ruta correcta
        nueva_ruta = os.path.join(UPLOAD_FOLDER, nombre_archivo_guardado)
        
        # Verificar si el archivo existe
        if os.path.exists(nueva_ruta):
            print(f"✅ ID {doc.id}: {nombre_archivo_guardado}")
            print(f"   Antigua: {doc.ruta}")
            print(f"   Nueva:   {nueva_ruta}")
            
            doc.ruta = nueva_ruta
            corregidos += 1
        else:
            print(f"❌ ID {doc.id}: {nombre_archivo_guardado} - ARCHIVO NO ENCONTRADO")
        
        print()
    
    # Guardar cambios
    db.session.commit()
    
    print(f"\n🎉 Se corrigieron {corregidos} rutas de {len(documentos)} documentos")
    print(f"📁 Carpeta de uploads: {UPLOAD_FOLDER}")

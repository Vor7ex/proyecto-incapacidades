"""
Script de migración para agregar metadatos a la tabla documentos.

Nuevos campos:
- nombre_unico: Nombre único generado (UUID + timestamp)
- tamaño_bytes: Tamaño del archivo en bytes
- checksum_md5: Hash MD5 del archivo
- mime_type: Tipo MIME del archivo

Ejecutar: python migrate_documentos.py
"""
import os
import sys

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models.documento import Documento

def migrar_documentos():
    """Agregar columnas nuevas a la tabla documentos"""
    app = create_app()
    
    with app.app_context():
        print("🔄 Iniciando migración de tabla 'documentos'...\n")
        
        try:
            # Verificar si las columnas ya existen
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columnas_existentes = [col['name'] for col in inspector.get_columns('documentos')]
            
            print(f"📋 Columnas actuales: {', '.join(columnas_existentes)}\n")
            
            nuevas_columnas = ['nombre_unico', 'tamaño_bytes', 'checksum_md5', 'mime_type']
            columnas_faltantes = [col for col in nuevas_columnas if col not in columnas_existentes]
            
            if not columnas_faltantes:
                print("✅ Todas las columnas ya existen. No se requiere migración.\n")
                return
            
            print(f"➕ Columnas a agregar: {', '.join(columnas_faltantes)}\n")
            
            # Agregar columnas usando ALTER TABLE
            with db.engine.connect() as conn:
                if 'nombre_unico' in columnas_faltantes:
                    conn.execute(db.text(
                        "ALTER TABLE documentos ADD COLUMN nombre_unico VARCHAR(255)"
                    ))
                    print("  ✓ Agregada columna: nombre_unico")
                
                if 'tamaño_bytes' in columnas_faltantes:
                    conn.execute(db.text(
                        "ALTER TABLE documentos ADD COLUMN tamaño_bytes INTEGER"
                    ))
                    print("  ✓ Agregada columna: tamaño_bytes")
                
                if 'checksum_md5' in columnas_faltantes:
                    conn.execute(db.text(
                        "ALTER TABLE documentos ADD COLUMN checksum_md5 VARCHAR(32)"
                    ))
                    print("  ✓ Agregada columna: checksum_md5")
                
                if 'mime_type' in columnas_faltantes:
                    conn.execute(db.text(
                        "ALTER TABLE documentos ADD COLUMN mime_type VARCHAR(100)"
                    ))
                    print("  ✓ Agregada columna: mime_type")
                
                conn.commit()
            
            print("\n✅ Migración completada exitosamente!")
            print("\n📌 Nota: Los documentos existentes tendrán estos campos en NULL.")
            print("   Puedes ejecutar un script de actualización para calcular metadatos de archivos existentes.\n")
            
        except Exception as e:
            print(f"\n❌ Error durante la migración: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

def actualizar_metadatos_existentes():
    """Actualizar metadatos de documentos existentes (opcional)"""
    import hashlib
    
    app = create_app()
    
    with app.app_context():
        print("\n🔄 Actualizando metadatos de documentos existentes...\n")
        
        documentos = Documento.query.all()
        actualizados = 0
        
        for doc in documentos:
            try:
                # Verificar si el archivo existe
                if not os.path.exists(doc.ruta):
                    print(f"  ⚠️  Archivo no encontrado: {doc.ruta}")
                    continue
                
                # Si ya tiene nombre_unico, saltar
                if doc.nombre_unico:
                    continue
                
                # Generar nombre_unico basado en el nombre actual
                doc.nombre_unico = os.path.basename(doc.ruta)
                
                # Calcular tamaño
                doc.tamaño_bytes = os.path.getsize(doc.ruta)
                
                # Calcular checksum
                with open(doc.ruta, 'rb') as f:
                    md5_hash = hashlib.md5()
                    for chunk in iter(lambda: f.read(4096), b""):
                        md5_hash.update(chunk)
                    doc.checksum_md5 = md5_hash.hexdigest()
                
                # Detectar MIME type
                extension = doc.nombre_archivo.rsplit('.', 1)[1].lower() if '.' in doc.nombre_archivo else ''
                mime_types = {
                    'pdf': 'application/pdf',
                    'png': 'image/png',
                    'jpg': 'image/jpeg',
                    'jpeg': 'image/jpeg'
                }
                doc.mime_type = mime_types.get(extension, 'application/octet-stream')
                
                actualizados += 1
                print(f"  ✓ Actualizado: {doc.nombre_archivo} ({doc.tamaño_mb} MB)")
                
            except Exception as e:
                print(f"  ❌ Error actualizando {doc.nombre_archivo}: {e}")
        
        if actualizados > 0:
            db.session.commit()
            print(f"\n✅ {actualizados} documentos actualizados con metadatos.\n")
        else:
            print("\n✅ No hay documentos para actualizar.\n")

if __name__ == '__main__':
    import sys
    
    print("\n" + "="*70)
    print("MIGRACIÓN DE TABLA DOCUMENTOS - AGREGAR METADATOS")
    print("="*70)
    
    migrar_documentos()
    
    # Preguntar si se desea actualizar documentos existentes
    if len(sys.argv) > 1 and sys.argv[1] == '--actualizar':
        actualizar_metadatos_existentes()
    else:
        print("💡 Tip: Ejecuta con --actualizar para calcular metadatos de archivos existentes:")
        print("   python migrate_documentos.py --actualizar\n")

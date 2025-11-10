"""
Script de migración para agregar campo fecha_lectura al modelo Notificacion.

Este script debe ejecutarse UNA SOLA VEZ para actualizar la base de datos existente.
"""

from app import create_app
from app.models import db

def migrar_notificaciones():
    """Agrega el campo fecha_lectura a la tabla notificaciones."""
    app = create_app()
    
    with app.app_context():
        try:
            # Verificar si la columna ya existe
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('notificaciones')]
            
            if 'fecha_lectura' in columns:
                print("✅ La columna 'fecha_lectura' ya existe. No se requiere migración.")
                return
            
            # Agregar columna fecha_lectura (nullable)
            with db.engine.connect() as conn:
                conn.execute(db.text(
                    "ALTER TABLE notificaciones ADD COLUMN fecha_lectura DATETIME"
                ))
                conn.commit()
            
            print("✅ Migración completada: columna 'fecha_lectura' agregada exitosamente")
            
        except Exception as e:
            print(f"❌ Error durante la migración: {str(e)}")
            raise

if __name__ == "__main__":
    migrar_notificaciones()

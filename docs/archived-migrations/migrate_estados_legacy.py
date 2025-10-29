#!/usr/bin/env python3
"""
Script de migración: Convertir estados legacy a nuevos enums
Usa: python migrate_estados.py
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db
from app.models.incapacidad import Incapacidad
from app.models.enums import EstadoIncapacidadEnum

# Estados legacy a nuevos
MAPEO_ESTADOS = {
    'Pendiente': EstadoIncapacidadEnum.PENDIENTE_VALIDACION.value,
    'En revision': EstadoIncapacidadEnum.DOCUMENTACION_COMPLETA.value,
    'Aprobada': EstadoIncapacidadEnum.APROBADA_PENDIENTE_TRANSCRIPCION.value,
    'Rechazada': EstadoIncapacidadEnum.RECHAZADA.value,
}

def migrate_estados():
    """Migra todos los estados legacy a nuevos enums"""
    app = create_app()
    
    with app.app_context():
        print("🔄 Iniciando migración de estados...")
        print(f"Mapeo de conversión:")
        for legacy, nuevo in MAPEO_ESTADOS.items():
            print(f"  {legacy:20} → {nuevo}")
        print()
        
        total_migrados = 0
        
        for estado_legacy, estado_nuevo in MAPEO_ESTADOS.items():
            # Buscar todas las incapacidades con este estado legacy
            incapacidades = Incapacidad.query.filter_by(estado=estado_legacy).all()
            
            if incapacidades:
                print(f"Migrando '{estado_legacy}' ({len(incapacidades)} registros):")
                for inc in incapacidades:
                    print(f"  - Incapacidad #{inc.id} ({inc.codigo_radicacion}): {estado_legacy} → {estado_nuevo}")
                    inc.estado = estado_nuevo
                    total_migrados += 1
                
                print()
        
        if total_migrados > 0:
            try:
                db.session.commit()
                print(f"✅ Migración completada: {total_migrados} incapacidad(es) actualizada(s)")
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error durante la migración: {e}")
                sys.exit(1)
        else:
            print("ℹ️ No hay incapacidades con estados legacy para migrar")

if __name__ == '__main__':
    migrate_estados()

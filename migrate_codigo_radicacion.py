"""
Migración: Agregar columna codigo_radicacion a tabla incapacidades
Ejecutar: python migrate_codigo_radicacion.py
"""
from app import create_app, db
from app.models.incapacidad import Incapacidad, generar_codigo_radicacion_unico
from sqlalchemy import text

app = create_app()

def migrar_codigo_radicacion():
    with app.app_context():
        print("=" * 60)
        print("MIGRACIÓN: Agregar codigo_radicacion a incapacidades")
        print("=" * 60)
        
        # Verificar si la columna ya existe
        inspector = db.inspect(db.engine)
        columnas = [col['name'] for col in inspector.get_columns('incapacidades')]
        
        if 'codigo_radicacion' in columnas:
            print("✅ La columna 'codigo_radicacion' ya existe")
        else:
            print("📝 Agregando columna 'codigo_radicacion'...")
            
            # Agregar columna
            with db.engine.connect() as conn:
                conn.execute(text(
                    "ALTER TABLE incapacidades ADD COLUMN codigo_radicacion VARCHAR(50)"
                ))
                conn.commit()
            
            print("✅ Columna agregada exitosamente")
        
        # Generar códigos para incapacidades existentes sin código
        incapacidades_sin_codigo = Incapacidad.query.filter(
            (Incapacidad.codigo_radicacion == None) | 
            (Incapacidad.codigo_radicacion == '')
        ).all()
        
        if incapacidades_sin_codigo:
            print(f"\n📋 Generando códigos para {len(incapacidades_sin_codigo)} incapacidad(es) existente(s)...")
            
            for incapacidad in incapacidades_sin_codigo:
                try:
                    # Usar el método de instancia
                    incapacidad.asignar_codigo_radicacion()
                    print(f"  ✅ ID {incapacidad.id}: {incapacidad.codigo_radicacion}")
                    
                except Exception as e:
                    print(f"  ❌ Error en ID {incapacidad.id}: {e}")
            
            # Guardar cambios
            db.session.commit()
            print(f"\n✅ Códigos generados y guardados exitosamente")
        else:
            print("\n✅ Todas las incapacidades ya tienen código de radicación")
        
        # Crear índice único (si no existe)
        print("\n📝 Verificando índice único...")
        indices = inspector.get_indexes('incapacidades')
        existe_indice = any(
            idx.get('unique') and 'codigo_radicacion' in idx.get('column_names', [])
            for idx in indices
        )
        
        if not existe_indice:
            print("📝 Creando índice único...")
            with db.engine.connect() as conn:
                try:
                    conn.execute(text(
                        "CREATE UNIQUE INDEX ix_incapacidades_codigo_radicacion "
                        "ON incapacidades (codigo_radicacion)"
                    ))
                    conn.commit()
                    print("✅ Índice único creado")
                except Exception as e:
                    print(f"⚠️ Error creando índice (puede ser normal si ya existe): {e}")
        else:
            print("✅ Índice único ya existe")
        
        # Resumen final
        print("\n" + "=" * 60)
        print("RESUMEN DE MIGRACIÓN")
        print("=" * 60)
        total = Incapacidad.query.count()
        con_codigo = Incapacidad.query.filter(
            Incapacidad.codigo_radicacion != None,
            Incapacidad.codigo_radicacion != ''
        ).count()
        
        print(f"Total de incapacidades: {total}")
        print(f"Con código de radicación: {con_codigo}")
        print(f"Sin código: {total - con_codigo}")
        
        if con_codigo == total:
            print("\n✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        else:
            print("\n⚠️ ADVERTENCIA: Algunas incapacidades no tienen código")
        
        print("=" * 60)

if __name__ == '__main__':
    migrar_codigo_radicacion()

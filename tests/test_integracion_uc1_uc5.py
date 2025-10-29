#!/usr/bin/env python3
"""
Test de integración UC1 + UC5
Verificar que la validación automática funciona en el registro de incapacidades.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import date
from app import create_app, db
from app.models.usuario import Usuario
from app.models.incapacidad import Incapacidad
from app.models.documento import Documento
from app.models.enums import TipoDocumentoEnum

def test_integracion_uc1_uc5():
    """Test de integración UC1 + UC5"""
    app = create_app()
    
    with app.app_context():
        print("🧪 Iniciando test de integración UC1 + UC5...")
        
        # 1. Crear usuario de prueba
        usuario = Usuario.query.filter_by(email='test@test.com').first()
        if not usuario:
            usuario = Usuario(
                nombre='Test Usuario',
                email='test@test.com',
                rol='colaborador'
            )
            usuario.set_password('test123')
            db.session.add(usuario)
            db.session.commit()
            print("✅ Usuario de prueba creado")
        
        # 2. Crear incapacidad de prueba (Enfermedad General, 5 días - requiere epicrisis)
        incapacidad = Incapacidad(
            usuario_id=usuario.id,
            tipo='Enfermedad General',
            fecha_inicio=date.today(),
            fecha_fin=date.today(),
            dias=5  # > 2 días, requiere epicrisis
        )
        
        db.session.add(incapacidad)
        db.session.flush()
        
        print(f"✅ Incapacidad creada: ID {incapacidad.id}, Tipo: {incapacidad.tipo}, Días: {incapacidad.dias}")
        
        # 3. Ejecutar validación UC5 manualmente
        from app.services.validacion_requisitos_service import ValidadorRequisitos
        
        validador = ValidadorRequisitos()
        resultado = validador.validar(incapacidad)
        
        print(f"\n📋 Resultado UC5:")
        print(f"   Completo: {resultado['completo']}")
        print(f"   Faltantes: {len(resultado['faltantes'])}")
        print(f"   Presentes: {len(resultado['presentes'])}")
        
        if resultado['faltantes']:
            print("   Documentos faltantes:")
            for doc in resultado['faltantes']:
                print(f"     - {doc['nombre']}: {doc['motivo']}")
        
        # 4. Agregar certificado (obligatorio)
        documento1 = Documento(
            incapacidad_id=incapacidad.id,
            tipo_documento='CERTIFICADO_INCAPACIDAD',  # Usar valor del enum
            nombre_archivo='certificado_test.pdf',
            nombre_unico='cert_123.pdf',
            ruta='uploads/cert_123.pdf',
            mime_type='application/pdf',
            tamaño_bytes=1024
        )
        db.session.add(documento1)
        db.session.commit()  # Commit para que UC5 vea el documento
        
        # 5. Ejecutar validación nuevamente (refrescar incapacidad)
        db.session.refresh(incapacidad)  # Refrescar relación documentos
        
        # Debug: verificar documentos cargados
        print(f"   Documentos en relación: {len(incapacidad.documentos)}")
        for doc in incapacidad.documentos:
            print(f"     - {doc.tipo_documento}: {doc.nombre_archivo}")
        
        resultado2 = validador.validar(incapacidad)
        
        print(f"\n📋 Resultado UC5 (después de agregar certificado):")
        print(f"   Completo: {resultado2['completo']}")
        print(f"   Faltantes: {len(resultado2['faltantes'])}")
        print(f"   Presentes: {len(resultado2['presentes'])}")
        
        # 6. Agregar epicrisis (requerida para > 2 días)
        documento2 = Documento(
            incapacidad_id=incapacidad.id,
            tipo_documento='EPICRISIS',  # Usar valor del enum
            nombre_archivo='epicrisis_test.pdf',
            nombre_unico='epi_123.pdf',
            ruta='uploads/epi_123.pdf',
            mime_type='application/pdf',
            tamaño_bytes=2048
        )
        db.session.add(documento2)
        db.session.commit()  # Commit para que UC5 vea el documento
        
        # 7. Validación final (refrescar incapacidad)
        db.session.refresh(incapacidad)  # Refrescar relación documentos
        resultado3 = validador.validar(incapacidad)
        
        print(f"\n📋 Resultado UC5 (después de agregar epicrisis):")
        print(f"   Completo: {resultado3['completo']}")
        print(f"   Faltantes: {len(resultado3['faltantes'])}")
        print(f"   Presentes: {len(resultado3['presentes'])}")
        
        # 8. Guardar resultado en BD (simular integración UC1)
        incapacidad.validacion_uc5 = resultado3
        db.session.commit()
        
        print(f"\n💾 Resultado UC5 guardado en BD:")
        print(f"   Campo validacion_uc5: {incapacidad.validacion_uc5 is not None}")
        
        # 9. Verificar que se guardó correctamente
        incapacidad_bd = Incapacidad.query.get(incapacidad.id)
        if incapacidad_bd.validacion_uc5:
            print(f"   ✅ Validación UC5 persistida correctamente")
            print(f"   Completo en BD: {incapacidad_bd.validacion_uc5.get('completo', False)}")
        else:
            print(f"   ❌ Error: Validación UC5 no se guardó")
        
        # 10. Cleanup
        db.session.delete(incapacidad)
        db.session.delete(usuario)
        db.session.commit()
        
        print("\n🎉 Test de integración UC1 + UC5 completado exitosamente!")
        
        return True

if __name__ == '__main__':
    test_integracion_uc1_uc5()
#!/usr/bin/env python3
"""
Test específico para verificar corrección de documentos requeridos
para Licencia de Maternidad y Licencia de Paternidad.

Validación: UC5 debe solicitar TODOS los documentos especificados
en CASOS_DE_USO.md líneas 294-295.
"""

from app.services.validacion_requisitos_service import ValidadorRequisitos
from app.models.enums import TipoDocumentoEnum


def test_licencias_documentos_completos():
    """
    Verifica que se soliciten TODOS los documentos según UC5.
    
    Licencia de Maternidad debe incluir:
    - Certificado de Incapacidad
    - Epicrisis  
    - Certificado de Nacido Vivo
    - Registro Civil
    - Documento de Identidad
    
    Licencia de Paternidad debe incluir:
    - Certificado de Incapacidad
    - Epicrisis con semanas de gestación
    - Certificado de Nacido Vivo
    - Registro Civil  
    - Documento de Identidad de la Madre
    """
    print("🔍 Verificando documentos requeridos para licencias...")
    
    validador = ValidadorRequisitos()
    
    # ================================================================
    # TEST 1: LICENCIA DE MATERNIDAD
    # ================================================================
    print("\n📋 LICENCIA DE MATERNIDAD:")
    requisitos_maternidad = validador.obtener_requisitos_para_tipo('Licencia de Maternidad')
    
    documentos_esperados_maternidad = [
        TipoDocumentoEnum.CERTIFICADO_INCAPACIDAD.value,
        TipoDocumentoEnum.EPICRISIS.value,
        TipoDocumentoEnum.CERTIFICADO_NACIDO_VIVO.value,
        TipoDocumentoEnum.REGISTRO_CIVIL.value,
        TipoDocumentoEnum.DOCUMENTO_IDENTIDAD.value
    ]
    
    print(f"✅ Documentos esperados: {len(documentos_esperados_maternidad)}")
    for doc in documentos_esperados_maternidad:
        print(f"   - {doc}")
    
    print(f"📝 Documentos obtenidos: {len(requisitos_maternidad['obligatorios'])}")
    for doc in requisitos_maternidad['obligatorios']:
        print(f"   - {doc}")
    
    # Verificar que todos estén presentes
    faltantes_maternidad = set(documentos_esperados_maternidad) - set(requisitos_maternidad['obligatorios'])
    if faltantes_maternidad:
        print(f"❌ FALTANTES EN MATERNIDAD: {faltantes_maternidad}")
        return False
    else:
        print("✅ MATERNIDAD: Todos los documentos presentes")
    
    # ================================================================
    # TEST 2: LICENCIA DE PATERNIDAD
    # ================================================================
    print("\n👨‍👶 LICENCIA DE PATERNIDAD:")
    requisitos_paternidad = validador.obtener_requisitos_para_tipo('Licencia de Paternidad')
    
    documentos_esperados_paternidad = [
        TipoDocumentoEnum.CERTIFICADO_INCAPACIDAD.value,
        TipoDocumentoEnum.EPICRISIS.value,
        TipoDocumentoEnum.CERTIFICADO_NACIDO_VIVO.value,
        TipoDocumentoEnum.REGISTRO_CIVIL.value,
        TipoDocumentoEnum.DOCUMENTO_IDENTIDAD.value  # de la madre
    ]
    
    print(f"✅ Documentos esperados: {len(documentos_esperados_paternidad)}")
    for doc in documentos_esperados_paternidad:
        print(f"   - {doc}")
    
    print(f"📝 Documentos obtenidos: {len(requisitos_paternidad['obligatorios'])}")
    for doc in requisitos_paternidad['obligatorios']:
        print(f"   - {doc}")
    
    # Verificar que todos estén presentes
    faltantes_paternidad = set(documentos_esperados_paternidad) - set(requisitos_paternidad['obligatorios'])
    if faltantes_paternidad:
        print(f"❌ FALTANTES EN PATERNIDAD: {faltantes_paternidad}")
        return False
    else:
        print("✅ PATERNIDAD: Todos los documentos presentes")
    
    # ================================================================
    # RESUMEN FINAL
    # ================================================================
    print("\n" + "="*60)
    print("📊 RESUMEN DE CORRECCIÓN:")
    print("="*60)
    print(f"✅ Licencia de Maternidad: {len(requisitos_maternidad['obligatorios'])}/5 documentos")
    print(f"✅ Licencia de Paternidad: {len(requisitos_paternidad['obligatorios'])}/5 documentos")
    print("✅ Certificado de Incapacidad incluido en ambas")
    print("✅ Documento de Identidad incluido en ambas")
    print("🎉 CORRECCIÓN COMPLETADA EXITOSAMENTE")
    
    return True


if __name__ == "__main__":
    import sys
    sys.path.append('.')
    
    try:
        resultado = test_licencias_documentos_completos()
        exit_code = 0 if resultado else 1
        sys.exit(exit_code)
        
    except Exception as e:
        print(f"❌ ERROR EN TEST: {e}")
        sys.exit(1)
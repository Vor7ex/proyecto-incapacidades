#!/usr/bin/env python3
"""
Test final de la corrección de la regla condicional Epicrisis
"""

import sys
import os

# Configurar path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app.services.validacion_requisitos_service import ValidadorRequisitos

def test_correccion_completa():
    print("🧪 TEST FINAL: Corrección de regla condicional Epicrisis")
    print("=" * 60)
    
    validador = ValidadorRequisitos()
    
    # Casos de prueba según el caso de uso
    casos_prueba = [
        (1, False, "1 día - Epicrisis NO obligatoria"),
        (2, False, "2 días - Epicrisis NO obligatoria (límite)"),
        (3, True, "3 días - Epicrisis SÍ obligatoria"),
        (5, True, "5 días - Epicrisis SÍ obligatoria"),
        (10, True, "10 días - Epicrisis SÍ obligatoria")
    ]
    
    print("\n📋 Pruebas para ENFERMEDAD GENERAL:")
    print("-" * 40)
    
    todos_correctos = True
    
    for dias, debe_ser_obligatoria, descripcion in casos_prueba:
        requisitos = validador.obtener_requisitos_por_tipo_y_dias('Enfermedad General', dias)
        epicrisis_obligatoria = 'EPICRISIS' in requisitos['obligatorios']
        
        estado = "✅" if epicrisis_obligatoria == debe_ser_obligatoria else "❌"
        if epicrisis_obligatoria != debe_ser_obligatoria:
            todos_correctos = False
        
        print(f"{estado} {descripcion}")
        print(f"    Obligatorios: {requisitos['obligatorios']}")
        print(f"    Condicionales: {requisitos['condicionales']}")
        print()
    
    # Verificar que otros tipos no se vean afectados
    print("📋 Verificación otros tipos (no deben cambiar):")
    print("-" * 40)
    
    otros_tipos = [
        ('Accidente Laboral', True),
        ('Accidente de Tránsito', True),
        ('Licencia de Maternidad', True),
        ('Licencia de Paternidad', True)
    ]
    
    for tipo, debe_tener_epicrisis in otros_tipos:
        requisitos = validador.obtener_requisitos_por_tipo_y_dias(tipo, 1)
        tiene_epicrisis = 'EPICRISIS' in requisitos['obligatorios']
        
        estado = "✅" if tiene_epicrisis == debe_tener_epicrisis else "❌"
        if tiene_epicrisis != debe_tener_epicrisis:
            todos_correctos = False
        
        print(f"{estado} {tipo}: {'SÍ' if tiene_epicrisis else 'NO'} incluye Epicrisis")
    
    print("\n" + "=" * 60)
    if todos_correctos:
        print("🎉 ¡CORRECCIÓN COMPLETAMENTE EXITOSA!")
        print("\n✅ La regla condicional ahora funciona correctamente:")
        print("   • Enfermedad General + días <= 2: Solo Certificado")
        print("   • Enfermedad General + días > 2: Certificado + Epicrisis")
        print("   • Otros tipos mantienen sus reglas originales")
        print("\n🔧 Cambios implementados:")
        print("   • Corregida lógica en obtener_requisitos_por_tipo_y_dias()")
        print("   • Corregida URL de API en template JavaScript")
        print("   • Validación funciona según casos de uso UC5")
    else:
        print("❌ AÚN HAY PROBLEMAS EN LA IMPLEMENTACIÓN")
    
    print("\n📝 Próximo paso:")
    print("   Probar en navegador: /incapacidades/registrar")
    print("   Seleccionar 'Enfermedad General' y cambiar fechas")
    print("   Verificar que badges cambien según días calculados")

if __name__ == '__main__':
    test_correccion_completa()
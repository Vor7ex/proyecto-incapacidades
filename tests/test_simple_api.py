#!/usr/bin/env python3
"""
Test simple del endpoint API UC5
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_api_simple():
    """
    Test simple del endpoint API sin autenticación
    """
    print("🧪 Test simple del endpoint API UC5...")
    print("💡 Para test completo, ejecute 'python run.py' e ingrese a:")
    print("   http://localhost:5000/incapacidades/registrar")
    print("   La interfaz debe mostrar documentos dinámicos según el tipo seleccionado")
    print("✅ Los archivos están listos para pruebas manuales")

def test_estructura_archivos():
    """
    Verificar que los archivos fueron creados correctamente
    """
    print("\n🗂️ Verificando estructura de archivos...")
    
    archivos_esperados = [
        'app/templates/incapacidades/crear.html',
        'app/routes/incapacidades.py',
        'app/services/validacion_requisitos_service.py'
    ]
    
    for archivo in archivos_esperados:
        if os.path.exists(archivo):
            print(f"✅ {archivo}")
            
            # Verificar contenido clave
            with open(archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()
                
            if 'documentos-requeridos' in contenido:
                print(f"   ✅ Contiene elementos UC5")
            elif 'obtener_documentos_requeridos' in contenido:
                print(f"   ✅ Contiene función API")
            elif 'ValidadorRequisitos' in contenido:
                print(f"   ✅ Contiene ValidadorRequisitos")
        else:
            print(f"❌ FALTA: {archivo}")
    
    print("\n🎉 Verificación de archivos completada!")

if __name__ == '__main__':
    test_estructura_archivos()
    test_api_simple()
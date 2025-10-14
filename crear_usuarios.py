#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para crear usuarios de prueba en la base de datos.
Ejecutar: python crear_usuarios.py
"""
import sys
import os

# Asegurar que no se ejecute el servidor Flask
os.environ['FLASK_RUN_FROM_CLI'] = 'false'

from app import create_app, db
from app.models.usuario import Usuario

def crear_usuarios():
    """Crea usuarios de prueba en la base de datos."""
    app = create_app()
    
    with app.app_context():
        try:
            # Verificar usuarios existentes
            usuarios_existentes = Usuario.query.all()
            print(f"Usuarios actuales en BD: {len(usuarios_existentes)}")
            
            # Limpiar usuarios existentes
            if usuarios_existentes:
                print("Eliminando usuarios existentes...")
                Usuario.query.delete()
                db.session.commit()
                print("Usuarios anteriores eliminados")
            
            # Crear usuarios de prueba
            print("\nCreando nuevos usuarios de prueba...")
            usuarios = [
                Usuario(
                    nombre="Juan Empleado",
                    email="empleado@test.com",
                    rol="colaborador"
                ),
                Usuario(
                    nombre="Maria Garcia",
                    email="auxiliar@test.com",
                    rol="auxiliar"
                )
            ]
            
            for usuario in usuarios:
                usuario.set_password("123456")
                db.session.add(usuario)
                print(f"  + {usuario.nombre} ({usuario.rol})")
            
            db.session.commit()
            
            # Verificar creación
            total = Usuario.query.count()
            print(f"\nTotal de usuarios en BD: {total}")
            
            print("\n" + "="*50)
            print("USUARIOS CREADOS EXITOSAMENTE")
            print("="*50)
            print("\nCredenciales de acceso:")
            print("  - Colaborador: empleado@test.com / 123456")
            print("  - Auxiliar RRHH: auxiliar@test.com / 123456")
            print("="*50)
            
            return True
            
        except Exception as e:
            print(f"\nERROR al crear usuarios: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = crear_usuarios()
    sys.exit(0 if success else 1)
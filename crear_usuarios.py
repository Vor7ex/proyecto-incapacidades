"""
Script para crear usuarios de prueba con los nuevos campos email_notificaciones.
Usa COLABORADOR_EMAIL del .env para las notificaciones.
"""

import os
from dotenv import load_dotenv
from app import create_app
from app.models import db
from app.models.usuario import Usuario

# Cargar .env
load_dotenv()

# Crear app
app = create_app()

with app.app_context():
    # Limpiar base de datos existente
    print("🗑️  Limpiando base de datos existente...")
    db.drop_all()
    
    # Crear las tablas
    print("📦 Creando tablas de BD...")
    db.create_all()
    
    # Obtener email de notificaciones desde .env
    email_notificaciones = os.getenv('COLABORADOR_EMAIL', 'noreply@test.com')
    
    # Crear usuario colaborador
    print("\n👤 Creando usuario colaborador...")
    usuario_colaborador = Usuario(
        nombre='Juan Empleado',
        email='empleado@test.com',
        email_notificaciones=email_notificaciones,
        rol='colaborador'
    )
    usuario_colaborador.set_password('123456')
    
    # Crear usuario auxiliar
    print("👤 Creando usuario auxiliar...")
    usuario_auxiliar = Usuario(
        nombre='Maria Garcia',
        email='auxiliar@test.com',
        email_notificaciones=email_notificaciones,
        rol='auxiliar'
    )
    usuario_auxiliar.set_password('123456')
    
    # Guardar usuarios
    db.session.add(usuario_colaborador)
    db.session.add(usuario_auxiliar)
    db.session.commit()
    
    print("\n✅ Usuarios creados exitosamente:")
    print(f"  Colaborador: empleado@test.com / 123456")
    print(f"  - Email notificaciones: {email_notificaciones}")
    print(f"  Auxiliar: auxiliar@test.com / 123456")
    print(f"  - Email notificaciones: {email_notificaciones}")
    print(f"\n📧 Todos los emails de notificación van a: {email_notificaciones}")

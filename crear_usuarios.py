from app import create_app, db
from app.models.usuario import Usuario

app = create_app()

with app.app_context():
    # Limpiar usuarios existentes (opcional)
    Usuario.query.delete()
    
    # Crear usuarios de prueba
    usuarios = [
        Usuario(
            nombre="Juan Empleado",
            email="empleado@test.com",
            rol="colaborador"
        ),
        Usuario(
            nombre="María García",
            email="auxiliar@test.com",
            rol="auxiliar"
        )
    ]
    
    for usuario in usuarios:
        usuario.set_password("123456")
        db.session.add(usuario)
    
    db.session.commit()
    print("✅ Usuarios creados exitosamente")
    print("\nCredenciales de acceso:")
    print("- Colaborador: empleado@test.com / 123456")
    print("- Auxiliar RRHH: auxiliar@test.com / 123456")
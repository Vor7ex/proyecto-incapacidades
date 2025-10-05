"""
Tests basicos para verificar funcionamiento del sistema
Ejecutar: python -m pytest tests/
"""

def test_imports():
    """Verificar que todos los modulos se importen correctamente"""
    try:
        from app import create_app
        from app.models.usuario import Usuario
        from app.models.incapacidad import Incapacidad
        from app.models.documento import Documento
        assert True
    except ImportError as e:
        assert False, f"Error de importacion: {e}"

def test_crear_app():
    """Verificar que la aplicacion se cree correctamente"""
    from app import create_app
    app = create_app()
    assert app is not None
    assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///database.db'

def test_modelos():
    """Verificar que los modelos esten bien definidos"""
    from app.models.usuario import Usuario
    from app.models.incapacidad import Incapacidad
    from app.models.documento import Documento
    
    # Verificar atributos de Usuario
    assert hasattr(Usuario, 'nombre')
    assert hasattr(Usuario, 'email')
    assert hasattr(Usuario, 'rol')
    
    # Verificar atributos de Incapacidad
    assert hasattr(Incapacidad, 'tipo')
    assert hasattr(Incapacidad, 'fecha_inicio')
    assert hasattr(Incapacidad, 'estado')
    
    # Verificar atributos de Documento
    assert hasattr(Documento, 'nombre_archivo')
    assert hasattr(Documento, 'ruta')

if __name__ == '__main__':
    test_imports()
    test_crear_app()
    test_modelos()
    print("✅ Todos los tests basicos pasaron correctamente")
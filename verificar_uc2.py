"""
Script de verificación de configuración UC2
Verifica que todo esté correctamente configurado antes de probar
"""
import os
import sys

def verificar_configuracion():
    print("=" * 60)
    print("🔍 VERIFICACIÓN DE CONFIGURACIÓN UC2")
    print("=" * 60)
    
    errores = []
    warnings = []
    
    # 1. Verificar archivo .env
    print("\n1. Verificando archivo .env...")
    if os.path.exists('.env'):
        print("   ✅ Archivo .env existe")
        
        # Cargar y verificar variables
        from dotenv import load_dotenv
        load_dotenv()
        
        required_vars = [
            'MAIL_SERVER',
            'MAIL_PORT',
            'MAIL_USERNAME',
            'MAIL_PASSWORD',
            'MAIL_DEFAULT_SENDER'
        ]
        
        for var in required_vars:
            value = os.environ.get(var)
            if value:
                print(f"   ✅ {var} configurado")
            else:
                errores.append(f"Variable {var} no encontrada en .env")
                print(f"   ❌ {var} NO configurado")
    else:
        errores.append("Archivo .env no existe")
        print("   ❌ Archivo .env NO existe")
    
    # 2. Verificar dependencias
    print("\n2. Verificando dependencias Python...")
    try:
        import flask_mail
        print("   ✅ Flask-Mail instalado")
    except ImportError:
        errores.append("Flask-Mail no instalado")
        print("   ❌ Flask-Mail NO instalado")
    
    try:
        import dotenv
        print("   ✅ python-dotenv instalado")
    except ImportError:
        warnings.append("python-dotenv no instalado (opcional pero recomendado)")
        print("   ⚠️  python-dotenv NO instalado")
    
    # 3. Verificar archivos del sistema
    print("\n3. Verificando archivos del sistema...")
    
    archivos_requeridos = [
        'app/utils/email_service.py',
        'app/templates/emails/confirmacion_registro.html',
        'app/templates/emails/notificacion_gestion_humana.html',
        'app/templates/emails/validacion_completada.html',
        'app/templates/emails/documentos_faltantes.html',
        'app/templates/emails/incapacidad_aprobada.html',
        'app/templates/emails/incapacidad_rechazada.html'
    ]
    
    for archivo in archivos_requeridos:
        if os.path.exists(archivo):
            print(f"   ✅ {archivo}")
        else:
            errores.append(f"Archivo {archivo} no encontrado")
            print(f"   ❌ {archivo} NO encontrado")
    
    # 4. Verificar que Flask-Mail esté inicializado
    print("\n4. Verificando inicialización de Flask-Mail...")
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            mail_server = app.config.get('MAIL_SERVER')
            mail_enabled = app.config.get('MAIL_ENABLED', True)
            
            if mail_server:
                print(f"   ✅ Flask-Mail inicializado")
                print(f"      Server: {mail_server}")
                print(f"      Port: {app.config.get('MAIL_PORT')}")
                
                if mail_enabled:
                    print(f"      📧 Estado: ENVÍO ACTIVO (emails reales)")
                else:
                    print(f"      📧 Estado: MODO SIMULACIÓN (sin envío real)")
                    print(f"      💡 Cambia MAIL_ENABLED=True en .env para activar")
            else:
                errores.append("Flask-Mail no inicializado correctamente")
                print("   ❌ Flask-Mail NO inicializado")
    except Exception as e:
        errores.append(f"Error al crear app: {e}")
        print(f"   ❌ Error al crear app: {e}")
    
    # 5. Verificar base de datos
    print("\n5. Verificando base de datos...")
    try:
        from app import create_app
        from app.models.usuario import Usuario
        app = create_app()
        
        with app.app_context():
            count_usuarios = Usuario.query.count()
            if count_usuarios > 0:
                print(f"   ✅ Base de datos OK ({count_usuarios} usuarios)")
            else:
                warnings.append("No hay usuarios en la BD. Ejecuta: python crear_usuarios.py")
                print("   ⚠️  No hay usuarios en la BD")
    except Exception as e:
        errores.append(f"Error al acceder BD: {e}")
        print(f"   ❌ Error al acceder BD: {e}")
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN")
    print("=" * 60)
    
    if not errores and not warnings:
        print("✅ TODO OK - Sistema listo para enviar notificaciones")
        print("\n🚀 Próximos pasos:")
        print("   1. Ejecuta: python run.py")
        print("   2. Registra una incapacidad")
        print("   3. Verifica emails en https://mailtrap.io/inboxes")
        return True
    
    if warnings:
        print(f"\n⚠️  ADVERTENCIAS ({len(warnings)}):")
        for w in warnings:
            print(f"   - {w}")
    
    if errores:
        print(f"\n❌ ERRORES ({len(errores)}):")
        for e in errores:
            print(f"   - {e}")
        print("\n🔧 Acciones requeridas:")
        
        if any('dotenv' in e.lower() for e in errores):
            print("   pip install python-dotenv")
        
        if any('flask-mail' in e.lower() for e in errores):
            print("   pip install Flask-Mail==0.9.1")
        
        if any('.env' in e for e in errores):
            print("   Crea archivo .env con credenciales SMTP")
            print("   (Usa .env.example como plantilla)")
        
        print("\n📚 Consulta: docs/FIX_NOTIFICACIONES.md")
        return False
    
    return True

if __name__ == '__main__':
    try:
        success = verificar_configuracion()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error durante verificación: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

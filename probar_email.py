"""
Script para probar la configuración de email del sistema

Uso:
    python probar_email.py

Antes de ejecutar:
    1. Configurar variables de entorno en .env
    2. pip install python-dotenv Flask-Mail
"""

import os
from dotenv import load_dotenv
from flask import Flask
from flask_mail import Mail, Message

def main():
    print("=" * 60)
    print("PRUEBA DE SISTEMA DE NOTIFICACIONES - UC2")
    print("=" * 60)
    
    # Cargar variables de entorno
    load_dotenv()
    
    # Crear app Flask mínima
    app = Flask(__name__)
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'False') == 'True'
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@incapacidades.com')
    app.config['GESTION_HUMANA_EMAIL'] = os.environ.get('GESTION_HUMANA_EMAIL', 'rrhh@test.com')
    
    mail = Mail(app)
    
    # Verificar configuración SMTP
    print("\n1. Verificando configuración SMTP...")
    print(f"   MAIL_SERVER: {app.config['MAIL_SERVER']}")
    print(f"   MAIL_PORT: {app.config['MAIL_PORT']}")
    print(f"   MAIL_USE_TLS: {app.config['MAIL_USE_TLS']}")
    print(f"   MAIL_USERNAME: {app.config['MAIL_USERNAME']}")
    print(f"   MAIL_PASSWORD: {'***' if app.config['MAIL_PASSWORD'] else 'NO CONFIGURADA'}")
    print(f"   MAIL_DEFAULT_SENDER: {app.config['MAIL_DEFAULT_SENDER']}")
    
    if not app.config['MAIL_USERNAME'] or not app.config['MAIL_PASSWORD']:
        print("\n❌ ERROR: Configuración SMTP incompleta")
        print("\n📋 Configura las variables de entorno en .env:")
        print("  MAIL_SERVER=sandbox.smtp.mailtrap.io")
        print("  MAIL_PORT=2525")
        print("  MAIL_USE_TLS=True")
        print("  MAIL_USERNAME=tu_username_mailtrap")
        print("  MAIL_PASSWORD=tu_password_mailtrap")
        print("  MAIL_DEFAULT_SENDER=noreply@incapacidades.com")
        print("  GESTION_HUMANA_EMAIL=rrhh@test.com")
        print("\n💡 Para Mailtrap:")
        print("  1. Ve a https://mailtrap.io/inboxes")
        print("  2. Copia Username y Password de SMTP Settings")
        return
    
    print("   ✅ Configuración SMTP OK")
    
    # Enviar email de prueba
    print("\n2. Enviando email de prueba...")
    
    with app.app_context():
        try:
            # Email de prueba
            msg = Message(
                subject="✅ [PRUEBA] Sistema de Notificaciones - Configuración OK",
                sender=app.config['MAIL_DEFAULT_SENDER'],
                recipients=["colaborador@test.com"]
            )
            
            msg.html = """
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <style>
                    body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background: #28a745; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }
                    .content { background: #f8f9fa; padding: 30px; border: 1px solid #dee2e6; border-radius: 0 0 5px 5px; }
                    .success-box { background: #d4edda; border-left: 4px solid #28a745; padding: 15px; margin: 15px 0; }
                    .info-box { background: white; padding: 15px; margin: 15px 0; border: 1px solid #dee2e6; border-radius: 5px; }
                    .footer { text-align: center; margin-top: 20px; color: #6c757d; font-size: 12px; }
                    ul { line-height: 1.8; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>✅ Configuración Exitosa</h1>
                </div>
                <div class="content">
                    <div class="success-box">
                        <h2>🎉 ¡El sistema de notificaciones está funcionando!</h2>
                        <p>Has configurado correctamente UC2 - Sistema de Notificaciones por Email</p>
                    </div>
                    
                    <div class="info-box">
                        <h3>📧 Tipos de Notificaciones Disponibles:</h3>
                        <ul>
                            <li><strong>UC1:</strong> Confirmación de registro (colaborador + RRHH)</li>
                            <li><strong>UC4:</strong> Validación completada / Documentos faltantes</li>
                            <li><strong>UC7:</strong> Aprobación / Rechazo de incapacidad</li>
                        </ul>
                    </div>
                    
                    <div class="info-box">
                        <h3>🚀 Próximos Pasos:</h3>
                        <ol>
                            <li>Ejecuta la aplicación: <code>python run.py</code></li>
                            <li>Registra una incapacidad como colaborador</li>
                            <li>Verifica que lleguen 2 emails a Mailtrap</li>
                            <li>Valida y aprueba como auxiliar RRHH</li>
                            <li>Verifica las notificaciones en cada paso</li>
                        </ol>
                    </div>
                    
                    <p><strong>✅ Todo está listo para usar el sistema completo.</strong></p>
                </div>
                <div class="footer">
                    <p>Sistema de Gestión de Incapacidades - Release 1.0</p>
                    <p>Universidad Tecnológica de Pereira</p>
                </div>
            </body>
            </html>
            """
            
            mail.send(msg)
            print("   ✅ Email enviado exitosamente")
            
            print("\n3. ✅ CONFIGURACIÓN SMTP VALIDADA")
            print("\n📬 Revisa tu inbox de Mailtrap:")
            print("   👉 https://mailtrap.io/inboxes")
            print("\n📧 Deberías ver 1 email:")
            print("   • colaborador@test.com - Prueba de configuración")
            print("\n🚀 Próximos pasos:")
            print("   1. Ejecuta: python run.py")
            print("   2. Registra una incapacidad (verás 2 emails en Mailtrap)")
            print("   3. Valida y aprueba (verás más notificaciones)")
            print("\n✅ PRUEBA COMPLETADA")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ ERROR al enviar email: {e}")
            print("\n🔍 Verifica:")
            print("  1. Credenciales SMTP correctas en .env")
            print("  2. MAIL_USERNAME y MAIL_PASSWORD sin espacios extra")
            print("  3. Conexión a internet activa")
            print("\n💡 Si usas Mailtrap, las credenciales están en:")
            print("   https://mailtrap.io/inboxes → SMTP Settings")
            print("=" * 60)

if __name__ == '__main__':
    main()

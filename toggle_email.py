"""
Script para activar/desactivar el envío de emails

Uso:
    python toggle_email.py on     # Activar envío de emails
    python toggle_email.py off    # Desactivar envío de emails
    python toggle_email.py status # Ver estado actual
"""

import os
import sys

def leer_env():
    """Lee el archivo .env y retorna un diccionario"""
    env_vars = {}
    if os.path.exists('.env'):
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    return env_vars

def escribir_env(env_vars):
    """Escribe el diccionario al archivo .env manteniendo comentarios"""
    if not os.path.exists('.env'):
        print("❌ Archivo .env no encontrado")
        return False
    
    with open('.env', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    with open('.env', 'w', encoding='utf-8') as f:
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#') and '=' in stripped:
                key = stripped.split('=', 1)[0]
                if key in env_vars:
                    f.write(f"{key}={env_vars[key]}\n")
                else:
                    f.write(line)
            else:
                f.write(line)
    
    return True

def mostrar_estado():
    """Muestra el estado actual del envío de emails"""
    env_vars = leer_env()
    mail_enabled = env_vars.get('MAIL_ENABLED', 'True')
    
    print("\n" + "=" * 60)
    print("📧 ESTADO DEL SISTEMA DE NOTIFICACIONES")
    print("=" * 60)
    
    if mail_enabled.lower() in ['true', 'on', '1']:
        print("\n✅ ENVÍO DE EMAILS: ACTIVADO")
        print("   📬 Los emails se envían a Mailtrap/SMTP configurado")
        print("\n💡 Para desactivar:")
        print("   python toggle_email.py off")
    else:
        print("\n🔴 ENVÍO DE EMAILS: DESACTIVADO")
        print("   📝 Solo se simula el envío (logs en consola)")
        print("   ⚡ Ahorra cuota de Mailtrap para pruebas reales")
        print("\n💡 Para activar:")
        print("   python toggle_email.py on")
    
    print("\n📊 Configuración actual:")
    print(f"   MAIL_SERVER: {env_vars.get('MAIL_SERVER', 'No configurado')}")
    print(f"   MAIL_PORT: {env_vars.get('MAIL_PORT', 'No configurado')}")
    print(f"   MAIL_USERNAME: {env_vars.get('MAIL_USERNAME', 'No configurado')}")
    print("=" * 60 + "\n")

def activar_emails():
    """Activa el envío de emails"""
    env_vars = leer_env()
    env_vars['MAIL_ENABLED'] = 'True'
    
    if escribir_env(env_vars):
        print("\n✅ Envío de emails ACTIVADO")
        print("   📬 Los emails se enviarán a SMTP configurado")
        print("\n⚠️  IMPORTANTE: Reinicia la aplicación (python run.py)")
        print("   para que los cambios surtan efecto\n")
        return True
    return False

def desactivar_emails():
    """Desactiva el envío de emails"""
    env_vars = leer_env()
    env_vars['MAIL_ENABLED'] = 'False'
    
    if escribir_env(env_vars):
        print("\n🔴 Envío de emails DESACTIVADO")
        print("   📝 Solo se simularán los envíos (logs en consola)")
        print("   ⚡ No se gastará cuota de Mailtrap")
        print("\n⚠️  IMPORTANTE: Reinicia la aplicación (python run.py)")
        print("   para que los cambios surtan efecto\n")
        return True
    return False

def main():
    if len(sys.argv) < 2:
        print("\n📧 Script de Control de Emails\n")
        print("Uso:")
        print("  python toggle_email.py on      # Activar envío")
        print("  python toggle_email.py off     # Desactivar envío")
        print("  python toggle_email.py status  # Ver estado actual\n")
        sys.exit(1)
    
    comando = sys.argv[1].lower()
    
    if comando in ['on', 'enable', 'activar', 'true']:
        activar_emails()
    elif comando in ['off', 'disable', 'desactivar', 'false']:
        desactivar_emails()
    elif comando in ['status', 'estado', 'ver']:
        mostrar_estado()
    else:
        print(f"\n❌ Comando '{comando}' no reconocido")
        print("\nComandos válidos: on, off, status\n")
        sys.exit(1)

if __name__ == '__main__':
    main()

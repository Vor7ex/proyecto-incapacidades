"""
UC2: Servicio de Notificaciones por Email
Notifica a líder y Gestión Humana sobre eventos del sistema
"""
from flask import render_template
from flask_mail import Mail, Message
from threading import Thread
from config import Config
import time

mail = Mail()

def send_async_email(app, msg):
    """Envía email de forma asíncrona para no bloquear el request"""
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Error al enviar email: {str(e)}")

def send_email(subject, recipients, html_body, text_body=None):
    """
    Envía un email
    
    Args:
        subject: Asunto del email
        recipients: Lista de destinatarios
        html_body: Cuerpo del email en HTML
        text_body: Cuerpo del email en texto plano (opcional)
    """
    from flask import current_app
    
    # Verificar si el envío de emails está habilitado
    if not current_app.config.get('MAIL_ENABLED', True):
        print(f"📧 [SIMULADO] Email NO enviado (MAIL_ENABLED=False)")
        print(f"   Subject: {subject}")
        print(f"   To: {', '.join(recipients)}")
        print(f"   (Cambia MAIL_ENABLED=True en .env para enviar emails reales)")
        return
    
    msg = Message(
        subject=subject,
        recipients=recipients,
        html=html_body,
        body=text_body or html_body
    )
    
    # Enviar en segundo plano para no bloquear
    Thread(
        target=send_async_email,
        args=(current_app._get_current_object(), msg)
    ).start()


def send_multiple_emails(emails_data):
    """
    Envía múltiples emails con delay entre ellos para evitar rate limit
    
    Args:
        emails_data: Lista de diccionarios con keys: subject, recipients, html_body
    """
    from flask import current_app
    
    def send_batch(app, emails_list):
        with app.app_context():
            for i, email_data in enumerate(emails_list):
                # Verificar si el envío está habilitado
                if not app.config.get('MAIL_ENABLED', True):
                    print(f"📧 [SIMULADO] Email {i+1}/{len(emails_list)} NO enviado (MAIL_ENABLED=False)")
                    print(f"   Subject: {email_data['subject']}")
                    print(f"   To: {', '.join(email_data['recipients'])}")
                    print(f"   (Cambia MAIL_ENABLED=True en .env para enviar emails reales)")
                else:
                    try:
                        msg = Message(
                            subject=email_data['subject'],
                            recipients=email_data['recipients'],
                            html=email_data['html_body'],
                            body=email_data.get('text_body', email_data['html_body'])
                        )
                        mail.send(msg)
                        print(f"✅ Email {i+1}/{len(emails_list)} enviado: {email_data['subject']}")
                    except Exception as e:
                        print(f"❌ Error enviando email {i+1}: {e}")
                
                # Delay entre emails (excepto después del último)
                if i < len(emails_list) - 1:
                    time.sleep(10.0)  # 10 segundos para evitar rate limit de Mailtrap
    
    # Enviar en thread separado
    Thread(
        target=send_batch,
        args=(current_app._get_current_object(), emails_data)
    ).start()


# ============================================================================
# UC2: Notificaciones de Incapacidades
# ============================================================================

def notificar_nueva_incapacidad(incapacidad):
    """
    UC2: Notifica al registrar una nueva incapacidad
    Destinatarios: Colaborador (confirmación) + Gestión Humana
    """
    from flask import current_app, url_for
    
    # Usar send_multiple_emails para enviar con delay
    emails = [
        {
            'subject': f'Incapacidad #{incapacidad.id} registrada exitosamente',
            'recipients': [incapacidad.usuario.email],
            'html_body': render_template(
                'emails/confirmacion_registro.html',
                incapacidad=incapacidad,
                colaborador=incapacidad.usuario
            )
        },
        {
            'subject': f'Nueva incapacidad para validar - {incapacidad.usuario.nombre}',
            'recipients': [Config.GESTION_HUMANA_EMAIL],
            'html_body': render_template(
                'emails/notificacion_gestion_humana.html',
                incapacidad=incapacidad,
                colaborador=incapacidad.usuario,
                tipo_notificacion='nueva'
            )
        }
    ]
    
    send_multiple_emails(emails)
    print(f"✅ UC2: 2 notificaciones programadas para incapacidad #{incapacidad.id}")


def notificar_validacion_completada(incapacidad):
    """
    UC2: Notifica cuando se completa la validación de documentos
    Destinatarios: Colaborador
    """
    send_email(
        subject=f'Incapacidad #{incapacidad.id} - Documentación validada',
        recipients=[incapacidad.usuario.email],
        html_body=render_template(
            'emails/validacion_completada.html',
            incapacidad=incapacidad,
            colaborador=incapacidad.usuario
        )
    )
    
    print(f"✅ UC2: Notificación de validación enviada para incapacidad #{incapacidad.id}")


def notificar_documentos_faltantes(incapacidad, observaciones):
    """
    UC2 + UC6: Notifica cuando faltan documentos
    Destinatarios: Colaborador
    """
    send_email(
        subject=f'Incapacidad #{incapacidad.id} - Documentos faltantes',
        recipients=[incapacidad.usuario.email],
        html_body=render_template(
            'emails/documentos_faltantes.html',
            incapacidad=incapacidad,
            colaborador=incapacidad.usuario,
            observaciones=observaciones
        )
    )
    
    print(f"✅ UC2: Notificación de documentos faltantes enviada para incapacidad #{incapacidad.id}")


def notificar_aprobacion(incapacidad):
    """
    UC2: Notifica aprobación de incapacidad
    Destinatarios: Colaborador
    """
    send_email(
        subject=f'✅ Incapacidad #{incapacidad.id} APROBADA',
        recipients=[incapacidad.usuario.email],
        html_body=render_template(
            'emails/incapacidad_aprobada.html',
            incapacidad=incapacidad,
            colaborador=incapacidad.usuario
        )
    )
    
    print(f"✅ UC2: Notificación de aprobación enviada para incapacidad #{incapacidad.id}")


def notificar_rechazo(incapacidad):
    """
    UC2: Notifica rechazo de incapacidad
    Destinatarios: Colaborador
    """
    send_email(
        subject=f'❌ Incapacidad #{incapacidad.id} RECHAZADA',
        recipients=[incapacidad.usuario.email],
        html_body=render_template(
            'emails/incapacidad_rechazada.html',
            incapacidad=incapacidad,
            colaborador=incapacidad.usuario
        )
    )
    
    print(f"✅ UC2: Notificación de rechazo enviada para incapacidad #{incapacidad.id}")

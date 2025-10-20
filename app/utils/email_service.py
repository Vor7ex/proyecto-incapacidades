"""
UC2: Servicio de Notificaciones por Email
Notifica a líder y Gestión Humana sobre eventos del sistema
Incluye logging, reintentos y hooks de almacenamiento
"""
from flask import render_template
from flask_mail import Mail, Message
from threading import Thread
from config import Config
import time
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

mail = Mail()

# Configuración de reintentos (se puede sobrescribir desde Config)
def get_max_reintentos():
    """Obtiene el número máximo de reintentos desde Config o usa default"""
    try:
        from config import Config
        return getattr(Config, 'EMAIL_MAX_REINTENTOS', 3)
    except:
        return 3

def get_reintento_delay():
    """Obtiene el delay entre reintentos desde Config o usa default"""
    try:
        from config import Config
        return getattr(Config, 'EMAIL_REINTENTO_DELAY', 5)
    except:
        return 5

MAX_REINTENTOS = get_max_reintentos()
REINTENTO_DELAY = get_reintento_delay()

def send_async_email(app, msg, reintentos=MAX_REINTENTOS):
    """
    Envía email de forma asíncrona con sistema de reintentos
    
    Args:
        app: Instancia de Flask
        msg: Mensaje a enviar
        reintentos: Número máximo de reintentos
    """
    with app.app_context():
        intento = 1
        while intento <= reintentos:
            try:
                mail.send(msg)
                logger.info(f"✅ Email enviado exitosamente: {msg.subject} → {', '.join(msg.recipients)}")
                return True
            except Exception as e:
                if intento < reintentos:
                    logger.warning(
                        f"⚠️ Error en intento {intento}/{reintentos} al enviar email: {str(e)}. "
                        f"Reintentando en {REINTENTO_DELAY}s..."
                    )
                    time.sleep(REINTENTO_DELAY)
                    intento += 1
                else:
                    logger.error(
                        f"❌ Error definitivo al enviar email tras {reintentos} intentos: {str(e)}. "
                        f"Subject: {msg.subject}, Recipients: {', '.join(msg.recipients)}"
                    )
                    return False

def send_email(subject, recipients, html_body, text_body=None, reintentos=MAX_REINTENTOS):
    """
    Envía un email con logging y manejo de errores
    
    Args:
        subject: Asunto del email
        recipients: Lista de destinatarios
        html_body: Cuerpo del email en HTML
        text_body: Cuerpo del email en texto plano (opcional)
        reintentos: Número de reintentos en caso de fallo
    
    Returns:
        bool: True si el email se programó exitosamente
    """
    from flask import current_app
    
    # Validar destinatarios
    if not recipients or not any(recipients):
        logger.error(f"❌ No se puede enviar email sin destinatarios. Subject: {subject}")
        return False
    
    # Verificar si el envío de emails está habilitado
    if not current_app.config.get('MAIL_ENABLED', True):
        logger.info(f"📧 [SIMULADO] Email NO enviado (MAIL_ENABLED=False)")
        logger.info(f"   Subject: {subject}")
        logger.info(f"   To: {', '.join(recipients)}")
        logger.info(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"   💡 Cambia MAIL_ENABLED=True en .env para enviar emails reales")
        return True  # Retornar True porque la simulación fue exitosa
    
    try:
        msg = Message(
            subject=subject,
            recipients=recipients,
            html=html_body,
            body=text_body or html_body
        )
        
        # Enviar en segundo plano para no bloquear
        Thread(
            target=send_async_email,
            args=(current_app._get_current_object(), msg, reintentos)
        ).start()
        
        logger.info(f"📤 Email programado para envío: {subject}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error al programar envío de email: {str(e)}")
        return False


def send_multiple_emails(emails_data, delay=10.0):
    """
    Envía múltiples emails con delay entre ellos para evitar rate limit
    Incluye logging detallado y manejo de errores por email
    
    Args:
        emails_data: Lista de diccionarios con keys: subject, recipients, html_body
        delay: Segundos entre envíos (default: 10s)
    
    Returns:
        None (procesa en background)
    """
    from flask import current_app
    
    def send_batch(app, emails_list, batch_delay):
        with app.app_context():
            enviados = 0
            fallidos = 0
            
            logger.info(f"📬 Iniciando envío de batch: {len(emails_list)} emails")
            
            for i, email_data in enumerate(emails_list):
                # Validar datos del email
                if not email_data.get('recipients'):
                    logger.warning(f"⚠️ Email {i+1}/{len(emails_list)} omitido: sin destinatarios")
                    fallidos += 1
                    continue
                
                # Verificar si el envío está habilitado
                if not app.config.get('MAIL_ENABLED', True):
                    logger.info(f"📧 [SIMULADO] Email {i+1}/{len(emails_list)}")
                    logger.info(f"   Subject: {email_data['subject']}")
                    logger.info(f"   To: {', '.join(email_data['recipients'])}")
                    logger.info(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    enviados += 1
                else:
                    # Enviar email real con reintentos
                    intento = 1
                    exito = False
                    
                    while intento <= MAX_REINTENTOS and not exito:
                        try:
                            msg = Message(
                                subject=email_data['subject'],
                                recipients=email_data['recipients'],
                                html=email_data['html_body'],
                                body=email_data.get('text_body', email_data['html_body'])
                            )
                            mail.send(msg)
                            logger.info(f"✅ Email {i+1}/{len(emails_list)} enviado: {email_data['subject']}")
                            enviados += 1
                            exito = True
                        except Exception as e:
                            if intento < MAX_REINTENTOS:
                                logger.warning(
                                    f"⚠️ Error en intento {intento}/{MAX_REINTENTOS} "
                                    f"(Email {i+1}/{len(emails_list)}): {str(e)}. Reintentando..."
                                )
                                time.sleep(REINTENTO_DELAY)
                                intento += 1
                            else:
                                logger.error(
                                    f"❌ Error definitivo en email {i+1}/{len(emails_list)}: {str(e)}"
                                )
                                fallidos += 1
                
                # Delay entre emails (excepto después del último)
                if i < len(emails_list) - 1:
                    time.sleep(batch_delay)
            
            # Resumen del batch
            logger.info(
                f"📊 Batch completado: {enviados} enviados, {fallidos} fallidos de {len(emails_list)} totales"
            )
    
    # Enviar en thread separado
    Thread(
        target=send_batch,
        args=(current_app._get_current_object(), emails_data, delay)
    ).start()


# ============================================================================
# UC2: Notificaciones de Incapacidades
# ============================================================================

def notificar_nueva_incapacidad(incapacidad):
    """
    UC2: Notifica al registrar una nueva incapacidad
    Destinatarios: Colaborador (confirmación) + Gestión Humana
    
    Args:
        incapacidad: Instancia de Incapacidad
        
    Returns:
        bool: True si las notificaciones se programaron exitosamente
    """
    from flask import current_app, url_for
    
    logger.info(f"🔔 UC2: Iniciando notificaciones para incapacidad #{incapacidad.id} ({incapacidad.codigo_radicacion})")
    
    try:
        # Validar datos necesarios
        if not incapacidad.usuario or not incapacidad.usuario.email:
            logger.error(f"❌ No se puede notificar incapacidad #{incapacidad.id}: usuario sin email")
            return False
        
        # Verificar email de Gestión Humana
        email_gestion = Config.GESTION_HUMANA_EMAIL
        if not email_gestion or email_gestion == 'gestionhumana@empresa.com':
            logger.warning(
                f"⚠️ GESTION_HUMANA_EMAIL no configurado correctamente. "
                f"Usando valor por defecto: {email_gestion}"
            )
        
        # Preparar emails con información detallada
        emails = [
            {
                'subject': f'✅ Incapacidad {incapacidad.codigo_radicacion} registrada exitosamente',
                'recipients': [incapacidad.usuario.email],
                'html_body': render_template(
                    'emails/confirmacion_registro.html',
                    incapacidad=incapacidad,
                    colaborador=incapacidad.usuario
                )
            },
            {
                'subject': f'🔔 Nueva incapacidad {incapacidad.codigo_radicacion} - {incapacidad.usuario.nombre}',
                'recipients': [email_gestion],
                'html_body': render_template(
                    'emails/notificacion_gestion_humana.html',
                    incapacidad=incapacidad,
                    colaborador=incapacidad.usuario,
                    tipo_notificacion='nueva'
                )
            }
        ]
        
        # Enviar batch de emails
        send_multiple_emails(emails, delay=10.0)
        
        logger.info(
            f"✅ UC2: 2 notificaciones programadas para incapacidad #{incapacidad.id} "
            f"({incapacidad.codigo_radicacion})"
        )
        
        return True
        
    except Exception as e:
        logger.error(
            f"❌ Error crítico al programar notificaciones para incapacidad #{incapacidad.id}: {str(e)}"
        )
        import traceback
        logger.error(traceback.format_exc())
        return False


def notificar_validacion_completada(incapacidad):
    """
    UC2: Notifica cuando se completa la validación de documentos
    Destinatarios: Colaborador
    
    Args:
        incapacidad: Instancia de Incapacidad
        
    Returns:
        bool: True si la notificación se envió exitosamente
    """
    logger.info(f"🔔 UC2: Notificando validación completada para #{incapacidad.id}")
    
    exito = send_email(
        subject=f'✅ Incapacidad {incapacidad.codigo_radicacion} - Documentación validada',
        recipients=[incapacidad.usuario.email],
        html_body=render_template(
            'emails/validacion_completada.html',
            incapacidad=incapacidad,
            colaborador=incapacidad.usuario
        )
    )
    
    if exito:
        logger.info(f"✅ UC2: Notificación de validación enviada para #{incapacidad.id}")
    
    return exito


def notificar_documentos_faltantes(incapacidad, observaciones):
    """
    UC2 + UC6: Notifica cuando faltan documentos
    Destinatarios: Colaborador
    
    Args:
        incapacidad: Instancia de Incapacidad
        observaciones: String con observaciones sobre documentos faltantes
        
    Returns:
        bool: True si la notificación se envió exitosamente
    """
    logger.info(f"🔔 UC2: Notificando documentos faltantes para #{incapacidad.id}")
    
    exito = send_email(
        subject=f'📄 Incapacidad {incapacidad.codigo_radicacion} - Documentos faltantes',
        recipients=[incapacidad.usuario.email],
        html_body=render_template(
            'emails/documentos_faltantes.html',
            incapacidad=incapacidad,
            colaborador=incapacidad.usuario,
            observaciones=observaciones
        )
    )
    
    if exito:
        logger.info(f"✅ UC2: Notificación de documentos faltantes enviada para #{incapacidad.id}")
    
    return exito


def notificar_aprobacion(incapacidad):
    """
    UC2: Notifica aprobación de incapacidad
    Destinatarios: Colaborador
    
    Args:
        incapacidad: Instancia de Incapacidad
        
    Returns:
        bool: True si la notificación se envió exitosamente
    """
    logger.info(f"🔔 UC2: Notificando aprobación para #{incapacidad.id}")
    
    exito = send_email(
        subject=f'✅ Incapacidad {incapacidad.codigo_radicacion} APROBADA',
        recipients=[incapacidad.usuario.email],
        html_body=render_template(
            'emails/incapacidad_aprobada.html',
            incapacidad=incapacidad,
            colaborador=incapacidad.usuario
        )
    )
    
    if exito:
        logger.info(f"✅ UC2: Notificación de aprobación enviada para #{incapacidad.id}")
    
    return exito


def notificar_rechazo(incapacidad):
    """
    UC2: Notifica rechazo de incapacidad
    Destinatarios: Colaborador
    
    Args:
        incapacidad: Instancia de Incapacidad
        
    Returns:
        bool: True si la notificación se envió exitosamente
    """
    logger.info(f"🔔 UC2: Notificando rechazo para #{incapacidad.id}")
    
    exito = send_email(
        subject=f'❌ Incapacidad {incapacidad.codigo_radicacion} RECHAZADA',
        recipients=[incapacidad.usuario.email],
        html_body=render_template(
            'emails/incapacidad_rechazada.html',
            incapacidad=incapacidad,
            colaborador=incapacidad.usuario
        )
    )
    
    if exito:
        logger.info(f"✅ UC2: Notificación de rechazo enviada para #{incapacidad.id}")
    
    return exito


# ============================================================================
# UC6: Notificaciones de Solicitud de Documentos
# ============================================================================

def notificar_solicitud_documentos(incapacidad, solicitudes, usuario_auxiliar):
    """
    UC6: Notifica al colaborador sobre documentos faltantes solicitados
    
    Args:
        incapacidad: Instancia de Incapacidad
        solicitudes: Lista de SolicitudDocumento creadas
        usuario_auxiliar: Usuario auxiliar que realizó la solicitud
        
    Returns:
        bool: True si la notificación se envió exitosamente
    """
    from flask import current_app
    from app.utils.calendario import dias_habiles_restantes, formatar_fecha_legible
    
    logger.info(f"🔔 UC6: Notificando solicitud de documentos para #{incapacidad.id} ({incapacidad.codigo_radicacion})")
    
    try:
        # Validar MAIL_ENABLED
        if not current_app.config.get('MAIL_ENABLED', True):
            logger.info(f"📧 [SIMULADO] Solicitud de documentos NO enviada (MAIL_ENABLED=False)")
            logger.info(f"   Destinatario: {incapacidad.usuario.email}")
            logger.info(f"   Documentos solicitados: {len(solicitudes)}")
            return True
        
        # Validar email del colaborador
        if not incapacidad.usuario or not incapacidad.usuario.email:
            logger.error(f"❌ UC6: No se puede notificar #{incapacidad.id}: colaborador sin email")
            return False
        
        # Construir datos para template
        documentos_solicitados = []
        for sol in solicitudes:
            documentos_solicitados.append({
                'tipo': sol.tipo_documento.replace('_', ' ').title(),
                'tipo_raw': sol.tipo_documento,
                'observaciones': sol.observaciones_auxiliar or 'Sin observaciones adicionales',
                'fecha_vencimiento': formatar_fecha_legible(sol.fecha_vencimiento)
            })
        
        # Obtener fecha de vencimiento (todas las solicitudes tienen el mismo plazo)
        fecha_vencimiento = solicitudes[0].fecha_vencimiento
        dias_restantes = dias_habiles_restantes(datetime.utcnow().date(), fecha_vencimiento)
        
        # Renderizar template
        html_body = render_template(
            'emails/solicitud_documentos.html',
            incapacidad=incapacidad,
            colaborador=incapacidad.usuario,
            documentos_solicitados=documentos_solicitados,
            fecha_vencimiento_str=formatar_fecha_legible(fecha_vencimiento),
            dias_restantes=dias_restantes,
            auxiliar_nombre=usuario_auxiliar.nombre if usuario_auxiliar else 'Gestión Humana'
        )
        
        # Enviar email con reintentos
        exito = send_email(
            subject=f'📄 Documentos faltantes - Incapacidad {incapacidad.codigo_radicacion}',
            recipients=[incapacidad.usuario.email],
            html_body=html_body,
            reintentos=3
        )
        
        if exito:
            # Actualizar ultima_notificacion en todas las solicitudes
            for sol in solicitudes:
                sol.ultima_notificacion = datetime.utcnow()
            
            logger.info(
                f"✅ UC6: Solicitud de documentos enviada a {incapacidad.usuario.email} "
                f"({len(solicitudes)} documentos, vence en {dias_restantes} días hábiles)"
            )
        
        return exito
        
    except Exception as e:
        logger.error(f"❌ UC6: Error al notificar solicitud de documentos para #{incapacidad.id}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def notificar_recordatorio_documentos(incapacidad, numero_recordatorio, solicitudes_pendientes):
    """
    UC6: Envía recordatorio urgente sobre documentos pendientes
    
    Args:
        incapacidad: Instancia de Incapacidad
        numero_recordatorio: int (1 = día antes, 2 = día de vencimiento)
        solicitudes_pendientes: Lista de SolicitudDocumento pendientes
        
    Returns:
        bool: True si la notificación se envió exitosamente
    """
    from flask import current_app
    from app.utils.calendario import formatar_fecha_legible
    
    logger.info(
        f"🔔 UC6: Enviando recordatorio #{numero_recordatorio} para #{incapacidad.id} "
        f"({incapacidad.codigo_radicacion})"
    )
    
    try:
        # Validar MAIL_ENABLED
        if not current_app.config.get('MAIL_ENABLED', True):
            logger.info(f"📧 [SIMULADO] Recordatorio #{numero_recordatorio} NO enviado (MAIL_ENABLED=False)")
            logger.info(f"   Destinatario: {incapacidad.usuario.email}")
            return True
        
        # Validar email
        if not incapacidad.usuario or not incapacidad.usuario.email:
            logger.error(f"❌ UC6: No se puede enviar recordatorio para #{incapacidad.id}: sin email")
            return False
        
        # Preparar datos de documentos
        documentos_pendientes = []
        for sol in solicitudes_pendientes:
            documentos_pendientes.append({
                'tipo': sol.tipo_documento.replace('_', ' ').title(),
                'tipo_raw': sol.tipo_documento,
                'observaciones': sol.observaciones_auxiliar or '',
                'fecha_vencimiento': formatar_fecha_legible(sol.fecha_vencimiento),
                'vencida': sol.esta_vencida()
            })
        
        # Seleccionar template según número de recordatorio
        if numero_recordatorio == 1:
            template = 'emails/recordatorio_documentos_dia2.html'
            asunto = f'⏰ RECORDATORIO: Documentos vencen mañana - {incapacidad.codigo_radicacion}'
        else:  # numero_recordatorio == 2
            template = 'emails/segunda_notificacion_documentos.html'
            asunto = f'🚨 URGENTE: Vencimiento de plazo - {incapacidad.codigo_radicacion}'
        
        # Renderizar template
        html_body = render_template(
            template,
            incapacidad=incapacidad,
            colaborador=incapacidad.usuario,
            documentos_pendientes=documentos_pendientes,
            numero_recordatorio=numero_recordatorio
        )
        
        # Enviar con reintentos
        exito = send_email(
            subject=asunto,
            recipients=[incapacidad.usuario.email],
            html_body=html_body,
            reintentos=3
        )
        
        if exito:
            # Actualizar ultima_notificacion
            for sol in solicitudes_pendientes:
                sol.ultima_notificacion = datetime.utcnow()
            
            logger.info(
                f"✅ UC6: Recordatorio #{numero_recordatorio} enviado a {incapacidad.usuario.email} "
                f"({len(solicitudes_pendientes)} documentos pendientes)"
            )
        
        return exito
        
    except Exception as e:
        logger.error(
            f"❌ UC6: Error al enviar recordatorio #{numero_recordatorio} para #{incapacidad.id}: {str(e)}"
        )
        import traceback
        logger.error(traceback.format_exc())
        return False


def notificar_documentacion_completada(incapacidad, email_auxiliar=None):
    """
    UC6: Notifica a auxiliar que el colaborador completó la carga de documentos
    
    Args:
        incapacidad: Instancia de Incapacidad
        email_auxiliar: Email del auxiliar (opcional, usa Config.GESTION_HUMANA_EMAIL si no se provee)
        
    Returns:
        bool: True si la notificación se envió exitosamente
    """
    from flask import current_app
    from config import Config
    
    logger.info(f"🔔 UC6: Notificando documentación completada para #{incapacidad.id} ({incapacidad.codigo_radicacion})")
    
    try:
        # Validar MAIL_ENABLED
        if not current_app.config.get('MAIL_ENABLED', True):
            logger.info(f"📧 [SIMULADO] Documentación completada NO enviada (MAIL_ENABLED=False)")
            logger.info(f"   Destinatario: auxiliar/RRHH")
            return True
        
        # Determinar destinatario
        destinatario = email_auxiliar or Config.GESTION_HUMANA_EMAIL
        
        if not destinatario:
            logger.error(f"❌ UC6: No se puede notificar documentación completada: sin email de auxiliar")
            return False
        
        # Renderizar template
        html_body = render_template(
            'emails/documentacion_completada.html',
            incapacidad=incapacidad,
            colaborador=incapacidad.usuario
        )
        
        # Enviar email
        exito = send_email(
            subject=f'✅ Documentación completada - {incapacidad.codigo_radicacion}',
            recipients=[destinatario],
            html_body=html_body,
            reintentos=3
        )
        
        if exito:
            logger.info(
                f"✅ UC6: Notificación de documentación completada enviada a {destinatario}"
            )
        
        return exito
        
    except Exception as e:
        logger.error(f"❌ UC6: Error al notificar documentación completada para #{incapacidad.id}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


# ============================================================================
# UC15: Hook de Almacenamiento Definitivo
# ============================================================================

def confirmar_almacenamiento_definitivo(incapacidad):
    """
    UC15: Hook para confirmar almacenamiento definitivo de documentos
    
    Este hook se ejecuta después del commit exitoso y puede:
    - Mover archivos de carpeta temporal a definitiva
    - Crear respaldo de seguridad
    - Registrar en sistema de auditoría
    - Actualizar índices de búsqueda
    
    Args:
        incapacidad: Instancia de Incapacidad con documentos
        
    Returns:
        bool: True si el almacenamiento se confirmó exitosamente
    """
    import os
    from config import Config
    
    logger.info(
        f"💾 UC15: Confirmando almacenamiento definitivo para incapacidad #{incapacidad.id} "
        f"({incapacidad.codigo_radicacion})"
    )
    
    try:
        # Verificar que hay documentos
        if not incapacidad.documentos or len(incapacidad.documentos) == 0:
            logger.warning(f"⚠️ UC15: No hay documentos para almacenar en #{incapacidad.id}")
            return True  # No es error, simplemente no hay nada que hacer
        
        # Log de documentos almacenados
        logger.info(f"📄 UC15: Documentos a confirmar: {len(incapacidad.documentos)}")
        
        for doc in incapacidad.documentos:
            ruta_completa = os.path.join(Config.UPLOAD_FOLDER, doc.ruta)
            
            # Verificar que el archivo físico existe
            if os.path.exists(ruta_completa):
                tamaño_kb = doc.tamaño_bytes / 1024 if doc.tamaño_bytes else 0
                logger.info(
                    f"  ✅ {doc.tipo_documento}: {doc.nombre_unico} "
                    f"({tamaño_kb:.2f} KB, MD5: {doc.checksum_md5[:8] if doc.checksum_md5 else 'N/A'}...)"
                )
            else:
                logger.error(
                    f"  ❌ Archivo físico NO encontrado: {ruta_completa} "
                    f"(documento #{doc.id}, tipo: {doc.tipo_documento})"
                )
                return False
        
        # TODO: Implementar lógica adicional de UC15 según necesidades
        # Por ejemplo:
        # - Mover a carpeta de archivo definitivo
        # - Crear backup en storage externo (S3, Azure Blob, etc.)
        # - Indexar en sistema de búsqueda (Elasticsearch)
        # - Generar thumbnails para PDFs
        # - Escanear con antivirus
        
        logger.info(
            f"✅ UC15: Almacenamiento definitivo confirmado para #{incapacidad.id} "
            f"- {len(incapacidad.documentos)} documento(s) verificados"
        )
        
        return True
        
    except Exception as e:
        logger.error(
            f"❌ UC15: Error al confirmar almacenamiento definitivo para #{incapacidad.id}: {str(e)}"
        )
        import traceback
        logger.error(traceback.format_exc())
        return False

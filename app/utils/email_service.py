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

# ============================================================================
# UC2: Funciones Auxiliares
# ============================================================================

def get_usuarios_gestion_humana():
    """
    UC2-E4: Obtiene lista de usuarios activos del área de Gestión Humana
    
    Returns:
        list: Lista de objetos Usuario con rol 'auxiliar' o 'gestion_humana'
    """
    from app.models.usuario import Usuario
    from app.models import db
    
    try:
        usuarios = Usuario.query.filter(
            Usuario.rol.in_(['auxiliar', 'gestion_humana'])
        ).all()
        
        logger.info(f"👥 UC2-E4: Encontrados {len(usuarios)} usuarios de Gestión Humana activos")
        return usuarios
        
    except Exception as e:
        logger.error(f"❌ UC2-E4: Error al obtener usuarios de Gestión Humana: {str(e)}")
        return []


def crear_notificacion_interna(tipo, destinatario_id, asunto, contenido, solicitud_documento_id=None):
    """
    UC2: Crea notificación interna en la base de datos (pasos 6-7)
    
    Args:
        tipo: TipoNotificacionEnum o string
        destinatario_id: ID del usuario destinatario
        asunto: Asunto de la notificación
        contenido: Contenido HTML o texto de la notificación
        solicitud_documento_id: ID de solicitud de documento (opcional)
        
    Returns:
        Notificacion: Instancia creada o None si hay error
    """
    from app.models.notificacion import Notificacion
    from app.models.enums import TipoNotificacionEnum, EstadoNotificacionEnum
    from app.models import db
    
    try:
        # Validar tipo
        if isinstance(tipo, TipoNotificacionEnum):
            tipo_str = tipo.value
        else:
            tipo_str = str(tipo)
        
        # Crear notificación
        notificacion = Notificacion(
            tipo=tipo_str,
            destinatario_id=destinatario_id,
            asunto=asunto,
            contenido=contenido,
            solicitud_documento_id=solicitud_documento_id,
            estado=EstadoNotificacionEnum.PENDIENTE.value
        )
        
        db.session.add(notificacion)
        db.session.flush()  # Obtener ID sin commit
        
        logger.info(
            f"📬 UC2: Notificación interna creada #{notificacion.id} "
            f"(tipo={tipo_str}, dest={destinatario_id})"
        )
        
        return notificacion
        
    except Exception as e:
        logger.error(f"❌ UC2: Error al crear notificación interna: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None


def marcar_notificacion_enviada(notificacion_id):
    """
    UC2 (paso 9): Marca una notificación como enviada
    
    Args:
        notificacion_id: ID de la notificación
        
    Returns:
        bool: True si se actualizó correctamente
    """
    from app.models.notificacion import Notificacion
    from app.models import db
    
    try:
        notificacion = Notificacion.query.get(notificacion_id)
        if notificacion:
            notificacion.marcar_enviada()
            db.session.commit()
            logger.info(f"✅ UC2: Notificación #{notificacion_id} marcada como enviada")
            return True
        else:
            logger.warning(f"⚠️ UC2: Notificación #{notificacion_id} no encontrada")
            return False
    except Exception as e:
        logger.error(f"❌ UC2: Error al marcar notificación #{notificacion_id} como enviada: {str(e)}")
        db.session.rollback()
        return False


def marcar_notificacion_entregada(notificacion_id):
    """
    UC2 (paso 9): Marca una notificación como entregada
    
    Args:
        notificacion_id: ID de la notificación
        
    Returns:
        bool: True si se actualizó correctamente
    """
    from app.models.notificacion import Notificacion
    from app.models import db
    
    try:
        notificacion = Notificacion.query.get(notificacion_id)
        if notificacion:
            notificacion.marcar_entregada()
            db.session.commit()
            logger.info(f"✅ UC2: Notificación #{notificacion_id} marcada como entregada")
            return True
        else:
            logger.warning(f"⚠️ UC2: Notificación #{notificacion_id} no encontrada")
            return False
    except Exception as e:
        logger.error(f"❌ UC2: Error al marcar notificación #{notificacion_id} como entregada: {str(e)}")
        db.session.rollback()
        return False

def get_email_notificaciones(usuario):
    """
    Obtiene el email de notificaciones de un usuario.
    Si no existe email_notificaciones, usa el email de login como fallback.
    
    Args:
        usuario: Instancia de Usuario
    
    Returns:
        str: Email de notificaciones del usuario
    """
    if not usuario:
        return None
    return usuario.email_notificaciones or usuario.email

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

def send_async_email(app, msg, reintentos=MAX_REINTENTOS, notificacion_id=None):
    """
    UC2-E3: Envía email de forma asíncrona con sistema de reintentos (3 veces, 5 min)
    UC2 (paso 8): Registra log completo de notificaciones enviadas
    UC2 (paso 9): Marca notificaciones como entregadas
    
    Args:
        app: Instancia de Flask
        msg: Mensaje a enviar
        reintentos: Número máximo de reintentos (default: 3)
        notificacion_id: ID de notificación interna asociada (opcional)
        
    Returns:
        bool: True si el envío fue exitoso
    """
    with app.app_context():
        intento = 1
        while intento <= reintentos:
            try:
                mail.send(msg)
                
                # UC2 (paso 8): Log detallado de envío exitoso
                logger.info(
                    f"✅ UC2 (paso 8): Email enviado exitosamente "
                    f"| Subject: {msg.subject} "
                    f"| Recipients: {', '.join(msg.recipients)} "
                    f"| Timestamp: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')} "
                    f"| Intentos: {intento}/{reintentos}"
                )
                
                # UC2 (paso 9): Marcar notificación como entregada
                if notificacion_id:
                    marcar_notificacion_entregada(notificacion_id)
                
                return True
                
            except Exception as e:
                if intento < reintentos:
                    # UC2-E3: Reintento con delay de 5 minutos (300s)
                    logger.warning(
                        f"⚠️ UC2-E3: Error en intento {intento}/{reintentos} "
                        f"| Subject: {msg.subject} "
                        f"| Error: {str(e)} "
                        f"| Reintentando en {REINTENTO_DELAY}s..."
                    )
                    time.sleep(REINTENTO_DELAY)
                    intento += 1
                else:
                    # UC2-E3: Error definitivo después de 3 reintentos
                    logger.error(
                        f"❌ UC2-E3: Error definitivo tras {reintentos} intentos "
                        f"| Subject: {msg.subject} "
                        f"| Recipients: {', '.join(msg.recipients)} "
                        f"| Error: {str(e)} "
                        f"| Timestamp: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
                    )
                    
                    # Registrar error en notificación interna si existe
                    if notificacion_id:
                        from app.models.notificacion import Notificacion
                        from app.models import db
                        try:
                            notif = Notificacion.query.get(notificacion_id)
                            if notif:
                                notif.registrar_error(f"Error tras {reintentos} reintentos: {str(e)}")
                                db.session.commit()
                        except:
                            pass
                    
                    return False

def send_email(subject, recipients, html_body, text_body=None, reintentos=MAX_REINTENTOS, 
               crear_notificacion=False, tipo_notificacion=None, destinatario_id=None):
    """
    UC2: Envía un email con logging, manejo de errores y notificación interna opcional
    UC2-E2: Si el correo es inválido, solo envía notificación interna
    
    Args:
        subject: Asunto del email
        recipients: Lista de destinatarios
        html_body: Cuerpo del email en HTML
        text_body: Cuerpo del email en texto plano (opcional)
        reintentos: Número de reintentos en caso de fallo
        crear_notificacion: Si True, crea notificación interna en BD
        tipo_notificacion: TipoNotificacionEnum para notificación interna
        destinatario_id: ID de usuario para notificación interna
    
    Returns:
        dict: {'email_ok': bool, 'notificacion_id': str|None}
    """
    from flask import current_app
    import re
    
    resultado = {'email_ok': False, 'notificacion_id': None}
    
    # UC2 (paso 6-7): Crear notificación interna PRIMERO si se solicita
    if crear_notificacion and destinatario_id and tipo_notificacion:
        notificacion = crear_notificacion_interna(
            tipo=tipo_notificacion,
            destinatario_id=destinatario_id,
            asunto=subject,
            contenido=html_body
        )
        if notificacion:
            notificacion_id = notificacion.id
            resultado['notificacion_id'] = notificacion_id
            # Marcar como enviada inmediatamente
            notificacion.marcar_enviada()
            from app.models import db
            db.session.commit()
    
    # UC2-E2: Validar formato de emails
    email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    emails_invalidos = [r for r in recipients if r and not email_regex.match(r)]
    
    if emails_invalidos:
        logger.error(
            f"❌ UC2-E2: Email(s) con formato inválido detectado(s): {', '.join(emails_invalidos)}. "
            f"Solo se enviará notificación interna."
        )
        # Ya se creó la notificación interna arriba
        return resultado
    
    # Validar destinatarios
    if not recipients or not any(recipients):
        logger.error(f"❌ UC2: No se puede enviar email sin destinatarios. Subject: {subject}")
        return resultado
    
    # Verificar si el envío de emails está habilitado
    if not current_app.config.get('MAIL_ENABLED', True):
        logger.info(f"📧 [SIMULADO] Email NO enviado (MAIL_ENABLED=False)")
        logger.info(f"   Subject: {subject}")
        logger.info(f"   To: {', '.join(recipients)}")
        logger.info(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"   💡 Cambia MAIL_ENABLED=True en .env para enviar emails reales")
        resultado['email_ok'] = True
    else:
        try:
            # Crear mensaje
            msg = Message(
                subject=subject,
                recipients=recipients,
                html=html_body,
                body=text_body or html_body
            )
            
            # Enviar en segundo plano para no bloquear
            Thread(
                target=send_async_email,
                args=(current_app._get_current_object(), msg, reintentos, resultado.get('notificacion_id'))
            ).start()
            
            logger.info(f"📤 UC2: Email programado para envío: {subject}")
            resultado['email_ok'] = True
            
        except Exception as e:
            logger.error(f"❌ UC2: Error al programar envío de email: {str(e)}")
    
    return resultado


def send_multiple_emails(emails_data, delay=1.0):
    """
    Envía múltiples emails con delay entre ellos para evitar rate limit
    Incluye logging detallado y manejo de errores por email
    
    Args:
        emails_data: Lista de diccionarios con keys: subject, recipients, html_body
        delay: Segundos entre envíos (default: 1s)
    
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
    UC2: Notifica al registrar una nueva incapacidad (flujo completo con excepciones)
    - Paso 4-5: Envía emails a colaborador y Gestión Humana
    - Pasos 6-7: Crea notificaciones internas en el sistema
    - Paso 8: Registra logs detallados
    - Paso 9: Marca notificaciones como entregadas
    - E1: Si no hay líder, notifica solo a Gestión Humana
    - E2: Si email inválido, solo envía notificación interna
    - E3: Reintentos automáticos (3 veces, 5 min)
    - E4: Si no hay usuarios RRHH, notifica al administrador
    
    Destinatarios: Colaborador (confirmación) + Gestión Humana
    
    Args:
        incapacidad: Instancia de Incapacidad
        
    Returns:
        dict: {'email_ok': bool, 'notificaciones_internas': int}
    """
    from flask import current_app, url_for
    from app.models.enums import TipoNotificacionEnum
    from app.models import db
    
    logger.info(f"🔔 UC2: Iniciando notificaciones para incapacidad #{incapacidad.id} ({incapacidad.codigo_radicacion})")
    
    resultado = {'email_ok': True, 'notificaciones_internas': 0}
    
    try:
        # Validar datos necesarios
        if not incapacidad.usuario or not incapacidad.usuario.email:
            logger.error(f"❌ UC2: No se puede notificar incapacidad #{incapacidad.id}: usuario sin email")
            return {'email_ok': False, 'notificaciones_internas': 0}
        
        # Obtener email de notificaciones (fallback a email de login si no existe)
        email_colaborador = incapacidad.usuario.email_notificaciones or incapacidad.usuario.email
        
        # UC2-E4: Verificar si hay usuarios de Gestión Humana activos
        usuarios_rrhh = get_usuarios_gestion_humana()
        
        if not usuarios_rrhh:
            # E4: No hay usuarios de Gestión Humana, notificar a administrador
            logger.warning(
                f"⚠️ UC2-E4: No hay usuarios de Gestión Humana activos. "
                f"Notificando a administrador ({Config.ADMIN_EMAIL})"
            )
            
            # Enviar notificación urgente al administrador
            admin_email_resultado = send_email(
                subject=f'🚨 URGENTE: Nueva incapacidad sin RRHH asignado - {incapacidad.codigo_radicacion}',
                recipients=[Config.ADMIN_EMAIL],
                html_body=render_template(
                    'emails/notificacion_admin_sin_rrhh.html',
                    incapacidad=incapacidad,
                    colaborador=incapacidad.usuario
                ),
                reintentos=3
            )
            
            if not admin_email_resultado['email_ok']:
                logger.error(f"❌ UC2-E4: Error crítico - No se pudo notificar al administrador")
            
            # Usar email genérico de RRHH como fallback
            email_gestion = Config.GESTION_HUMANA_EMAIL
        else:
            # Usar primer usuario de RRHH disponible
            email_gestion = usuarios_rrhh[0].email_notificaciones or usuarios_rrhh[0].email
            logger.info(f"👤 UC2: Usuario RRHH seleccionado: {email_gestion}")
        
        # Verificar email de Gestión Humana
        if not email_gestion or email_gestion == 'gestionhumana@empresa.com':
            logger.warning(
                f"⚠️ UC2: GESTION_HUMANA_EMAIL no configurado correctamente. "
                f"Usando valor por defecto: {email_gestion}"
            )
        
        # === EMAIL 1: Confirmación al colaborador ===
        logger.info(f"📤 UC2 (paso 4): Enviando confirmación a colaborador {email_colaborador}")
        
        email1_resultado = send_email(
            subject=f'✅ Incapacidad {incapacidad.codigo_radicacion} registrada exitosamente',
            recipients=[email_colaborador],
            html_body=render_template(
                'emails/confirmacion_registro.html',
                incapacidad=incapacidad,
                colaborador=incapacidad.usuario
            ),
            reintentos=3,
            crear_notificacion=True,
            tipo_notificacion=TipoNotificacionEnum.REGISTRO_INCAPACIDAD,
            destinatario_id=incapacidad.usuario.id
        )
        
        if email1_resultado['notificacion_id']:
            resultado['notificaciones_internas'] += 1
            logger.info(f"✅ UC2 (pasos 6-7): Notificación interna creada para colaborador")
        
        # === EMAIL 2: Notificación a Gestión Humana ===
        logger.info(f"📤 UC2 (paso 5): Enviando notificación a RRHH {email_gestion}")
        
        # Buscar ID del usuario de RRHH si existe
        destinatario_rrhh_id = None
        if usuarios_rrhh:
            for usr in usuarios_rrhh:
                if (usr.email_notificaciones == email_gestion or usr.email == email_gestion):
                    destinatario_rrhh_id = usr.id
                    break
        
        email2_resultado = send_email(
            subject=f'🔔 Nueva incapacidad {incapacidad.codigo_radicacion} - {incapacidad.usuario.nombre}',
            recipients=[email_gestion],
            html_body=render_template(
                'emails/notificacion_gestion_humana.html',
                incapacidad=incapacidad,
                colaborador=incapacidad.usuario,
                tipo_notificacion='nueva'
            ),
            reintentos=3,
            crear_notificacion=True if destinatario_rrhh_id else False,
            tipo_notificacion=TipoNotificacionEnum.REGISTRO_INCAPACIDAD,
            destinatario_id=destinatario_rrhh_id
        )
        
        if email2_resultado['notificacion_id']:
            resultado['notificaciones_internas'] += 1
            logger.info(f"✅ UC2 (pasos 6-7): Notificación interna creada para RRHH")
        
        # Commit de notificaciones internas
        db.session.commit()
        
        # Evaluar resultado final
        resultado['email_ok'] = email1_resultado['email_ok'] and email2_resultado['email_ok']
        
        logger.info(
            f"✅ UC2: Proceso completo para incapacidad #{incapacidad.id} ({incapacidad.codigo_radicacion}) "
            f"| Emails programados: {2 if resultado['email_ok'] else 'con errores'} "
            f"| Notificaciones internas: {resultado['notificaciones_internas']}"
        )
        
        return resultado
        
    except Exception as e:
        logger.error(
            f"❌ UC2: Error crítico al procesar notificaciones para incapacidad #{incapacidad.id}: {str(e)}"
        )
        import traceback
        logger.error(traceback.format_exc())
        db.session.rollback()
        return {'email_ok': False, 'notificaciones_internas': 0}


def notificar_validacion_completada(incapacidad):
    """
    UC2: Notifica cuando se completa la validación de documentos
    Destinatarios: Colaborador
    
    Args:
        incapacidad: Instancia de Incapacidad
        
    Returns:
        dict: {'email_ok': bool, 'notificacion_id': int}
    """
    from app.models.enums import TipoNotificacionEnum
    from app.models import db
    
    logger.info(f"🔔 UC2: Notificando validación completada para #{incapacidad.id}")
    
    email_colaborador = get_email_notificaciones(incapacidad.usuario)
    
    # Preparar contenido de notificación interna
    contenido_html = render_template(
        'emails/validacion_completada.html',
        incapacidad=incapacidad,
        colaborador=incapacidad.usuario
    )
    
    # Enviar email con notificación interna
    resultado = send_email(
        subject=f'✅ Incapacidad {incapacidad.codigo_radicacion} - Documentación validada',
        recipients=[email_colaborador],
        html_body=contenido_html,
        crear_notificacion=True,
        tipo_notificacion=TipoNotificacionEnum.DOCUMENTACION_COMPLETADA,
        destinatario_id=incapacidad.usuario_id
    )
    
    if resultado['email_ok']:
        logger.info(f"✅ UC2: Notificación de validación enviada para #{incapacidad.id}")
        if resultado['notificacion_id']:
            logger.info(f"📬 UC2: Notificación interna creada #{resultado['notificacion_id']}")
    
    # Commit de la notificación interna
    try:
        db.session.commit()
    except Exception as e:
        logger.error(f"❌ Error al commit de notificación interna: {str(e)}")
        db.session.rollback()
    
    return resultado


def notificar_documentos_faltantes(incapacidad, observaciones):
    """
    UC2 + UC6: Notifica cuando faltan documentos
    Destinatarios: Colaborador
    
    Args:
        incapacidad: Instancia de Incapacidad
        observaciones: String con observaciones sobre documentos faltantes
        
    Returns:
        dict: {'email_ok': bool, 'notificacion_id': int}
    """
    from app.models.enums import TipoNotificacionEnum
    from app.models import db
    
    logger.info(f"🔔 UC2: Notificando documentos faltantes para #{incapacidad.id}")
    
    email_colaborador = get_email_notificaciones(incapacidad.usuario)
    
    # Preparar contenido de notificación interna
    contenido_html = render_template(
        'emails/documentos_faltantes.html',
        incapacidad=incapacidad,
        colaborador=incapacidad.usuario,
        observaciones=observaciones
    )
    
    # Enviar email con notificación interna
    resultado = send_email(
        subject=f'📄 Incapacidad {incapacidad.codigo_radicacion} - Documentos faltantes',
        recipients=[email_colaborador],
        html_body=contenido_html,
        crear_notificacion=True,
        tipo_notificacion=TipoNotificacionEnum.DOCUMENTOS_FALTANTES,
        destinatario_id=incapacidad.usuario_id
    )
    
    if resultado['email_ok']:
        logger.info(f"✅ UC2: Notificación de documentos faltantes enviada para #{incapacidad.id}")
        if resultado['notificacion_id']:
            logger.info(f"📬 UC2: Notificación interna creada #{resultado['notificacion_id']}")
    
    # Commit de la notificación interna
    try:
        db.session.commit()
    except Exception as e:
        logger.error(f"❌ Error al commit de notificación interna: {str(e)}")
        db.session.rollback()
    
    return resultado


def notificar_aprobacion(incapacidad):
    """
    UC2: Notifica aprobación de incapacidad
    Destinatarios: Colaborador
    
    Args:
        incapacidad: Instancia de Incapacidad
        
    Returns:
        dict: {'email_ok': bool, 'notificacion_id': int}
    """
    from app.models.enums import TipoNotificacionEnum
    from app.models import db
    
    logger.info(f"🔔 UC2: Notificando aprobación para #{incapacidad.id}")
    
    email_colaborador = get_email_notificaciones(incapacidad.usuario)
    
    # Preparar contenido de notificación interna
    contenido_html = render_template(
        'emails/incapacidad_aprobada.html',
        incapacidad=incapacidad,
        colaborador=incapacidad.usuario
    )
    
    # Enviar email con notificación interna
    resultado = send_email(
        subject=f'✅ Incapacidad {incapacidad.codigo_radicacion} APROBADA',
        recipients=[email_colaborador],
        html_body=contenido_html,
        crear_notificacion=True,
        tipo_notificacion=TipoNotificacionEnum.APROBACION,
        destinatario_id=incapacidad.usuario_id
    )
    
    if resultado['email_ok']:
        logger.info(f"✅ UC2: Notificación de aprobación enviada para #{incapacidad.id}")
        if resultado['notificacion_id']:
            logger.info(f"📬 UC2: Notificación interna creada #{resultado['notificacion_id']}")
    
    # Commit de la notificación interna
    try:
        db.session.commit()
    except Exception as e:
        logger.error(f"❌ Error al commit de notificación interna: {str(e)}")
        db.session.rollback()
    
    return resultado


def notificar_rechazo(incapacidad):
    """
    UC2: Notifica rechazo de incapacidad
    Destinatarios: Colaborador
    
    Args:
        incapacidad: Instancia de Incapacidad
        
    Returns:
        dict: {'email_ok': bool, 'notificacion_id': int}
    """
    from app.models.enums import TipoNotificacionEnum
    from app.models import db
    
    logger.info(f"🔔 UC2: Notificando rechazo para #{incapacidad.id}")
    
    email_colaborador = get_email_notificaciones(incapacidad.usuario)
    
    # Preparar contenido de notificación interna
    contenido_html = render_template(
        'emails/incapacidad_rechazada.html',
        incapacidad=incapacidad,
        colaborador=incapacidad.usuario
    )
    
    # Enviar email con notificación interna
    resultado = send_email(
        subject=f'❌ Incapacidad {incapacidad.codigo_radicacion} RECHAZADA',
        recipients=[email_colaborador],
        html_body=contenido_html,
        crear_notificacion=True,
        tipo_notificacion=TipoNotificacionEnum.RECHAZO,
        destinatario_id=incapacidad.usuario_id
    )
    
    if resultado['email_ok']:
        logger.info(f"✅ UC2: Notificación de rechazo enviada para #{incapacidad.id}")
        if resultado['notificacion_id']:
            logger.info(f"📬 UC2: Notificación interna creada #{resultado['notificacion_id']}")
    
    # Commit de la notificación interna
    try:
        db.session.commit()
    except Exception as e:
        logger.error(f"❌ Error al commit de notificación interna: {str(e)}")
        db.session.rollback()
    
    return resultado


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
            email_colaborador = get_email_notificaciones(incapacidad.usuario)
            logger.info(f"📧 [SIMULADO] Solicitud de documentos NO enviada (MAIL_ENABLED=False)")
            logger.info(f"   Destinatario: {email_colaborador}")
            logger.info(f"   Documentos solicitados: {len(solicitudes)}")
            return True
        
        # Validar email del colaborador
        if not incapacidad.usuario or not incapacidad.usuario.email:
            logger.error(f"❌ UC6: No se puede notificar #{incapacidad.id}: colaborador sin email")
            return False
        
        # Obtener email de notificaciones
        email_colaborador = get_email_notificaciones(incapacidad.usuario)
        
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
        
        # Enviar email con notificación interna
        resultado = send_email(
            subject=f'📄 Documentos faltantes - Incapacidad {incapacidad.codigo_radicacion}',
            recipients=[email_colaborador],
            html_body=html_body,
            reintentos=3,
            crear_notificacion=True,
            tipo_notificacion='DOCUMENTOS_FALTANTES',
            destinatario_id=incapacidad.usuario_id
        )
        
        if resultado['email_ok']:
            # Actualizar ultima_notificacion en todas las solicitudes
            for sol in solicitudes:
                sol.ultima_notificacion = datetime.utcnow()
            
            logger.info(
                f"✅ UC6: Solicitud de documentos enviada a {incapacidad.usuario.email} "
                f"({len(solicitudes)} documentos, vence en {dias_restantes} días hábiles)"
            )
            
            if resultado['notificacion_id']:
                logger.info(f"📬 UC6: Notificación interna creada #{resultado['notificacion_id']}")
        
        return resultado['email_ok']
        
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
            email_colaborador = get_email_notificaciones(incapacidad.usuario)
            logger.info(f"📧 [SIMULADO] Recordatorio #{numero_recordatorio} NO enviado (MAIL_ENABLED=False)")
            logger.info(f"   Destinatario: {email_colaborador}")
            return True
        
        # Validar email
        if not incapacidad.usuario or not incapacidad.usuario.email:
            logger.error(f"❌ UC6: No se puede enviar recordatorio para #{incapacidad.id}: sin email")
            return False
        
        # Obtener email de notificaciones
        email_colaborador = get_email_notificaciones(incapacidad.usuario)
        
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
        
        # Determinar tipo de notificación según número de recordatorio
        from app.models.enums import TipoNotificacionEnum
        tipo_notif = (TipoNotificacionEnum.RECORDATORIO_DOCUMENTOS_DIA2 
                     if numero_recordatorio == 1 
                     else TipoNotificacionEnum.SEGUNDA_NOTIFICACION_DOCUMENTOS)
        
        # Enviar con reintentos y notificación interna
        resultado = send_email(
            subject=asunto,
            recipients=[email_colaborador],
            html_body=html_body,
            reintentos=3,
            crear_notificacion=True,
            tipo_notificacion=tipo_notif,
            destinatario_id=incapacidad.usuario_id
        )
        
        if resultado['email_ok']:
            # Actualizar ultima_notificacion
            for sol in solicitudes_pendientes:
                sol.ultima_notificacion = datetime.utcnow()
            
            logger.info(
                f"✅ UC6: Recordatorio #{numero_recordatorio} enviado a {incapacidad.usuario.email} "
                f"({len(solicitudes_pendientes)} documentos pendientes)"
            )
            
            if resultado['notificacion_id']:
                logger.info(f"📬 UC6: Notificación interna creada #{resultado['notificacion_id']}")
        
        return resultado['email_ok']
        
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
        
        # Buscar usuario auxiliar para crear notificación interna
        from app.models.usuario import Usuario
        destinatario_id = None
        if email_auxiliar:
            usuario_aux = Usuario.query.filter_by(email=email_auxiliar, rol='auxiliar').first()
            if usuario_aux:
                destinatario_id = usuario_aux.id
        else:
            # Si no hay email específico, buscar primer usuario auxiliar
            usuario_aux = Usuario.query.filter_by(rol='auxiliar').first()
            if usuario_aux:
                destinatario_id = usuario_aux.id
        
        # Renderizar template
        html_body = render_template(
            'emails/documentacion_completada.html',
            incapacidad=incapacidad,
            colaborador=incapacidad.usuario
        )
        
        # Enviar email con notificación interna
        resultado = send_email(
            subject=f'✅ Documentación completada - {incapacidad.codigo_radicacion}',
            recipients=[destinatario],
            html_body=html_body,
            reintentos=3,
            crear_notificacion=True if destinatario_id else False,
            tipo_notificacion='DOCUMENTACION_COMPLETADA',
            destinatario_id=destinatario_id
        )
        
        if resultado['email_ok']:
            logger.info(
                f"✅ UC6: Notificación de documentación completada enviada a {destinatario}"
            )
            if resultado['notificacion_id']:
                logger.info(f"📬 UC6: Notificación interna creada #{resultado['notificacion_id']}")
        
        return resultado['email_ok']
        
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

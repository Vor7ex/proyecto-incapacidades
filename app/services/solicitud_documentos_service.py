"""Servicio de negocio para UC6 - Solicitud de Documentos Faltantes."""
import logging
from datetime import datetime
from typing import List, Dict, Tuple, Optional

from app.models import db
from app.models.documento import Documento
from app.models.enums import (
    EstadoIncapacidadEnum,
    EstadoSolicitudDocumentoEnum,
    TipoDocumentoEnum,
)
from app.models.incapacidad import Incapacidad
from app.models.solicitud_documento import SolicitudDocumento
from app.models.usuario import Usuario
from app.utils.calendario import sumar_dias_habiles
from app.utils.eventos_uc6 import (
    emitir_documentos_entregados,
    emitir_recordatorio_enviado,
    emitir_requerimiento_citacion,
    emitir_solicitud_documentos_creada,
    emitir_solicitud_vencida,
)
from app.utils.maquina_estados import validar_cambio_estado

# Logger
logger = logging.getLogger(__name__)


class SolicitudDocumentosService:
    """Servicio de negocio para gestión de solicitudes de documentos faltantes."""

    @staticmethod
    def crear_solicitud_documentos(
        incapacidad_id: int,
        documentos_a_solicitar: List[str],
        observaciones_por_tipo: Dict[str, str],
        usuario_auxiliar: Usuario
    ) -> Tuple[bool, str, Optional[List[SolicitudDocumento]]]:
        """
        Crea una solicitud de documentos faltantes para una incapacidad.
        
        Args:
            incapacidad_id: ID de la incapacidad
            documentos_a_solicitar: Lista de tipos de documentos a solicitar
            observaciones_por_tipo: Observaciones específicas por cada documento
            usuario_auxiliar: Usuario auxiliar que crea la solicitud
        
        Returns:
            Tuple[bool, str, Optional[List[SolicitudDocumento]]]:
                - bool: True si se creó correctamente
                - str: Mensaje de éxito o error
                - List[SolicitudDocumento]: Lista de solicitudes creadas o None
        """
        try:
            # a) Validar precondiciones
            
            # Validar que el usuario es auxiliar
            if not usuario_auxiliar or usuario_auxiliar.rol != 'auxiliar':
                return False, "Solo auxiliares de RRHH pueden crear solicitudes", None
            
            # Obtener incapacidad
            incapacidad = Incapacidad.query.get(incapacidad_id)
            if not incapacidad:
                return False, f"Incapacidad {incapacidad_id} no encontrada", None
            
            # Validar que el estado es PENDIENTE_VALIDACION (o legacy 'Pendiente')
            # Aceptar ambos para retrocompatibilidad con datos legacy
            estados_validos = [
                EstadoIncapacidadEnum.PENDIENTE_VALIDACION.value,
                'Pendiente'  # Estado legacy
            ]
            
            if incapacidad.estado not in estados_validos:
                return False, f"Incapacidad debe estar en PENDIENTE_VALIDACION (actual: {incapacidad.estado})", None
            
            # Validar que hay documentos a solicitar
            if not documentos_a_solicitar:
                return False, "Debe seleccionar al menos un documento a solicitar", None
            
            # Validar que los documentos son válidos
            documentos_validos = [doc.value for doc in TipoDocumentoEnum]
            for doc in documentos_a_solicitar:
                if doc not in documentos_validos:
                    return False, f"Tipo de documento '{doc}' no es válido", None
            
            # c) Crear solicitudes de documentos
            solicitudes_creadas = []
            fecha_actual = datetime.utcnow()
            fecha_vencimiento = sumar_dias_habiles(fecha_actual.date(), 3)
            
            for tipo_doc in documentos_a_solicitar:
                solicitud = SolicitudDocumento(
                    incapacidad_id=incapacidad_id,
                    tipo_documento=tipo_doc,
                    estado=EstadoSolicitudDocumentoEnum.PENDIENTE.value,
                    fecha_solicitud=fecha_actual,
                    fecha_vencimiento=datetime.combine(fecha_vencimiento, datetime.min.time()),
                    observaciones_auxiliar=observaciones_por_tipo.get(tipo_doc, ""),
                    intentos_notificacion=0,
                    extension_solicitada=False,
                    numero_reintentos=0
                )
                db.session.add(solicitud)
                solicitudes_creadas.append(solicitud)
            
            # d) Cambiar estado de incapacidad a DOCUMENTACION_INCOMPLETA
            incapacidad.cambiar_estado(
                EstadoIncapacidadEnum.DOCUMENTACION_INCOMPLETA.value,
                usuario_auxiliar,
                observaciones=f"Solicitud de {len(documentos_a_solicitar)} documento(s) faltante(s)",
                documento=None
            )
            
            # Guardar cambios en BD
            db.session.commit()
            
            # e) Emitir evento de dominio
            emitir_solicitud_documentos_creada(
                incapacidad_id=incapacidad_id,
                documentos_solicitados=documentos_a_solicitar,
                observaciones=observaciones_por_tipo,
                fecha_vencimiento=datetime.combine(fecha_vencimiento, datetime.min.time()),
                auxiliar_id=usuario_auxiliar.id
            )
            
            # f) Enviar notificación al colaborador
            try:
                from app.utils.email_service import notificar_solicitud_documentos
                notificar_solicitud_documentos(
                    incapacidad=incapacidad,
                    solicitudes=solicitudes_creadas,
                    usuario_auxiliar=usuario_auxiliar
                )
            except Exception as email_error:
                logger.warning(f"No se pudo enviar notificación de solicitud: {email_error}")
            
            # g) Retornar éxito
            return True, f"Solicitud creada exitosamente. Vencimiento: {fecha_vencimiento}", solicitudes_creadas
        
        except Exception as e:
            # g) Rollback en caso de error
            db.session.rollback()
            return False, f"Error al crear solicitud: {str(e)}", None

    @staticmethod
    def validar_respuesta_colaborador(
        incapacidad_id: int,
        documentos_entregados: List[Documento]
    ) -> Tuple[bool, List[str], List[SolicitudDocumento]]:
        """
        Valida y procesa los documentos entregados por el colaborador.
        
        Args:
            incapacidad_id: ID de la incapacidad
            documentos_entregados: Lista de documentos cargados
        
        Returns:
            Tuple[bool, List[str], List[SolicitudDocumento]]:
                - bool: True si todas las solicitudes fueron respondidas
                - List[str]: Lista de errores de validación (vacía si todo OK)
                - List[SolicitudDocumento]: Solicitudes aún pendientes
        """
        try:
            # a) Obtener incapacidad y solicitudes pendientes
            incapacidad = Incapacidad.query.get(incapacidad_id)
            if not incapacidad:
                return False, ["Incapacidad no encontrada"], []
            
            solicitudes_pendientes = incapacidad.obtener_solicitudes_pendientes()
            if not solicitudes_pendientes:
                return True, [], []
            
            # b) Validar y procesar cada documento entregado
            errores = []
            tipos_entregados = set()
            
            # MAPEO: Convertir tipos enum a simples para coincidencia
            mapeo_tipo_simple = {
                'CERTIFICADO_INCAPACIDAD': 'certificado',
                'EPICRISIS': 'epicrisis',
                'FURIPS': 'furips',
                'CERTIFICADO_NACIDO_VIVO': 'certificado_nacido_vivo',
                'REGISTRO_CIVIL': 'registro_civil',
                'DOCUMENTO_IDENTIDAD': 'documento_identidad_madre',
            }
            
            for doc in documentos_entregados:
                # Validar formato
                extensiones_validas = ['.pdf', '.jpg', '.jpeg', '.png']
                extension = '.' + doc.extension.lower() if doc.extension else ''
                if extension not in extensiones_validas:
                    errores.append(f"{doc.nombre_archivo}: formato no válido (solo PDF, JPG, PNG)")
                    continue
                
                # Validar tamaño (< 10MB)
                if doc.tamaño_bytes and doc.tamaño_bytes > 10 * 1024 * 1024:
                    errores.append(f"{doc.nombre_archivo}: tamaño excede 10MB")
                    continue
                
                # Marcar tipo como entregado
                # IMPORTANTE: Agregar tanto el tipo simple (como se guarda en BD)
                # como cualquier enum correspondiente para compatibilidad
                tipos_entregados.add(doc.tipo_documento)
            
            # c) Si hay documentos inválidos, retornar errores
            if errores:
                return False, errores, solicitudes_pendientes
            
            # Marcar solicitudes como entregadas según documentos válidos
            # IMPORTANTE: Comparar convertiendo enum a simple
            for solicitud in solicitudes_pendientes:
                # Convertir el tipo enum de la solicitud a simple
                tipo_solicitud_simple = mapeo_tipo_simple.get(
                    solicitud.tipo_documento, 
                    solicitud.tipo_documento
                )
                
                # Verificar si algún documento entregado coincide
                # Buscar por tipo simple (como se guarda en BD)
                if tipo_solicitud_simple in tipos_entregados:
                    solicitud.estado = EstadoSolicitudDocumentoEnum.ENTREGADO.value
                    solicitud.fecha_entrega = datetime.utcnow()
            
            db.session.commit()
            
            # d) Verificar si TODAS las solicitudes fueron respondidas
            # ⚠️ IMPORTANTE: Refrescar solicitudes_pendientes desde BD para asegurar datos actualizados
            # No usar la lista en memoria que puede estar desincronizada
            db.session.refresh(incapacidad)
            solicitudes_aun_pendientes = incapacidad.obtener_solicitudes_pendientes()
            
            if not solicitudes_aun_pendientes:
                # Todas respondidas: cambiar estado a PENDIENTE_VALIDACION
                incapacidad.cambiar_estado(
                    EstadoIncapacidadEnum.PENDIENTE_VALIDACION.value,
                    incapacidad.usuario,  # El colaborador
                    observaciones="Documentos solicitados entregados",
                    documento=None
                )
                db.session.commit()
                
                # Emitir evento
                emitir_documentos_entregados(
                    incapacidad_id=incapacidad_id,
                    documentos_entregados=list(tipos_entregados),
                    fecha_entrega=datetime.utcnow(),
                    colaborador_id=incapacidad.usuario_id,
                    solicitud_completa=True
                )
                
                # Notificar al auxiliar que se completó la documentación
                try:
                    from app.utils.email_service import notificar_documentacion_completada
                    # Buscar email del auxiliar que creó la solicitud
                    solicitud_ejemplo = solicitudes_pendientes[0] if solicitudes_pendientes else None
                    email_auxiliar = None
                    if solicitud_ejemplo and solicitud_ejemplo.historial_estados:
                        for historial in solicitud_ejemplo.historial_estados:
                            if historial.usuario and historial.usuario.rol.value in ['AUXILIAR', 'GESTION_HUMANA']:
                                email_auxiliar = historial.usuario.email
                                break
                    
                    notificar_documentacion_completada(
                        incapacidad=incapacidad,
                        email_auxiliar=email_auxiliar
                    )
                except Exception as email_error:
                    logger.warning(f"No se pudo notificar documentación completada: {email_error}")
                
                return True, [], []
            
            # e) Algunas pendientes
            emitir_documentos_entregados(
                incapacidad_id=incapacidad_id,
                documentos_entregados=list(tipos_entregados),
                fecha_entrega=datetime.utcnow(),
                colaborador_id=incapacidad.usuario_id,
                solicitud_completa=False
            )
            
            return False, [], solicitudes_aun_pendientes
        
        except Exception as e:
            db.session.rollback()
            return False, [f"Error al procesar documentos: {str(e)}"], []

    @staticmethod
    def procesar_recordatorios() -> Dict[str, int]:
        """
        Procesa recordatorios automáticos para solicitudes vencidas.
        Debe ejecutarse diariamente por un scheduler.
        
        Returns:
            Dict[str, int]: Estadísticas de procesamiento
                - recordatorios_dia2: Cantidad de primeros recordatorios enviados
                - recordatorios_urgentes: Cantidad de segundas notificaciones
                - requieren_citacion: Cantidad marcadas para citación
        """
        fecha_hoy = datetime.utcnow().date()
        stats = {
            'recordatorios_dia2': 0,
            'recordatorios_urgentes': 0,
            'requieren_citacion': 0,
            'errores': 0
        }
        
        try:
            # Buscar solicitudes pendientes con fecha de vencimiento <= hoy
            solicitudes = SolicitudDocumento.query.filter(
                SolicitudDocumento.estado == EstadoSolicitudDocumentoEnum.PENDIENTE.value,
                SolicitudDocumento.fecha_vencimiento <= datetime.combine(fecha_hoy, datetime.max.time())
            ).all()
            
            for solicitud in solicitudes:
                try:
                    fecha_venc = solicitud.fecha_vencimiento.date()
                    dias_vencido = (fecha_hoy - fecha_venc).days
                    
                    # b) Procesar según días de retraso
                    if dias_vencido == 0:
                        # Vence hoy: primer recordatorio
                        if solicitud.intentos_notificacion == 0:
                            solicitud.intentos_notificacion = 1
                            solicitud.ultima_notificacion = datetime.utcnow()
                            
                            # Agrupar solicitudes pendientes por incapacidad
                            incapacidad = solicitud.incapacidad
                            solicitudes_pendientes_inc = incapacidad.obtener_solicitudes_pendientes()
                            
                            # Enviar recordatorio
                            try:
                                from app.utils.email_service import notificar_recordatorio_documentos
                                notificar_recordatorio_documentos(
                                    incapacidad=incapacidad,
                                    numero_recordatorio=1,
                                    solicitudes_pendientes=solicitudes_pendientes_inc
                                )
                            except Exception as email_error:
                                logger.warning(f"Error al enviar recordatorio #1 para #{incapacidad.id}: {email_error}")
                            
                            emitir_recordatorio_enviado(
                                incapacidad_id=solicitud.incapacidad_id,
                                numero_recordatorio=1,
                                fecha_envio=datetime.utcnow(),
                                destinatario_email=solicitud.incapacidad.usuario.email
                            )
                            
                            stats['recordatorios_dia2'] += 1
                    
                    elif 1 <= dias_vencido <= 3:
                        # 1-3 días vencido: segunda notificación (urgente)
                        if solicitud.numero_reintentos == 0:
                            solicitud.numero_reintentos = 1
                            solicitud.intentos_notificacion += 1
                            solicitud.ultima_notificacion = datetime.utcnow()
                            
                            # Agrupar solicitudes pendientes por incapacidad
                            incapacidad = solicitud.incapacidad
                            solicitudes_pendientes_inc = incapacidad.obtener_solicitudes_pendientes()
                            
                            # Enviar recordatorio urgente
                            try:
                                from app.utils.email_service import notificar_recordatorio_documentos
                                notificar_recordatorio_documentos(
                                    incapacidad=incapacidad,
                                    numero_recordatorio=2,
                                    solicitudes_pendientes=solicitudes_pendientes_inc
                                )
                            except Exception as email_error:
                                logger.warning(f"Error al enviar recordatorio #2 para #{incapacidad.id}: {email_error}")
                            
                            emitir_recordatorio_enviado(
                                incapacidad_id=solicitud.incapacidad_id,
                                numero_recordatorio=2,
                                fecha_envio=datetime.utcnow(),
                                destinatario_email=solicitud.incapacidad.usuario.email
                            )
                            
                            stats['recordatorios_urgentes'] += 1
                    
                    elif dias_vencido > 6:
                        # Más de 6 días: requiere citación
                        if solicitud.estado != EstadoSolicitudDocumentoEnum.REQUIERE_CITACION.value:
                            solicitud.estado = EstadoSolicitudDocumentoEnum.REQUIERE_CITACION.value
                            
                            # Cambiar estado de incapacidad
                            incapacidad = solicitud.incapacidad
                            incapacidad.cambiar_estado(
                                EstadoIncapacidadEnum.RECHAZADA.value,
                                incapacidad.usuario,
                                observaciones="Solicitud de documentos vencida sin respuesta",
                                documento=None
                            )
                            
                            emitir_requerimiento_citacion(
                                incapacidad_id=solicitud.incapacidad_id,
                                motivo=f"Documentos no entregados después de {dias_vencido} días",
                                fecha_requerimiento=datetime.utcnow(),
                                intentos_notificacion=solicitud.intentos_notificacion
                            )
                            
                            stats['requieren_citacion'] += 1
                
                except Exception as e:
                    print(f"⚠️ Error procesando solicitud {solicitud.id}: {e}")
                    stats['errores'] += 1
                    continue
            
            db.session.commit()
            return stats
        
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error en procesar_recordatorios: {e}")
            stats['errores'] += 1
            return stats

    @staticmethod
    def permitir_extension_plazo(
        solicitud_documento_id: str,
        motivo_extension: str,
        usuario_auxiliar: Usuario
    ) -> Tuple[bool, str]:
        """
        Permite extender el plazo de una solicitud de documentos.
        
        Args:
            solicitud_documento_id: ID de la solicitud
            motivo_extension: Razón de la extensión
            usuario_auxiliar: Usuario auxiliar que autoriza
        
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            # a) Validar que usuario es AUXILIAR_GH
            if not usuario_auxiliar or usuario_auxiliar.rol != 'auxiliar':
                return False, "Solo auxiliares de RRHH pueden extender plazos"
            
            # b) Validar que solicitud existe
            solicitud = SolicitudDocumento.query.get(solicitud_documento_id)
            if not solicitud:
                return False, "Solicitud no encontrada"
            
            # c) Validar que no tiene extensión previa
            if solicitud.extension_solicitada:
                return False, "La solicitud ya tiene una extensión previa"
            
            # Validar que está pendiente
            if solicitud.estado != EstadoSolicitudDocumentoEnum.PENDIENTE.value:
                return False, f"Solo se pueden extender solicitudes pendientes (actual: {solicitud.estado})"
            
            # d) Extender fecha de vencimiento
            fecha_venc_actual = solicitud.fecha_vencimiento.date()
            nueva_fecha_venc = sumar_dias_habiles(fecha_venc_actual, 3)
            solicitud.fecha_vencimiento = datetime.combine(nueva_fecha_venc, datetime.min.time())
            
            # e) Registrar extensión
            solicitud.extension_solicitada = True
            solicitud.motivo_extension = motivo_extension
            
            # g) Registrar en HistorialEstado
            incapacidad = solicitud.incapacidad
            incapacidad.cambiar_estado(
                incapacidad.estado,  # Mismo estado
                usuario_auxiliar,
                observaciones=f"Extensión de plazo: {motivo_extension}. Nueva fecha: {nueva_fecha_venc}",
                documento=None
            )
            
            db.session.commit()
            
            # h) Retornar éxito
            return True, f"Plazo extendido hasta {nueva_fecha_venc}"
        
        except Exception as e:
            db.session.rollback()
            return False, f"Error al extender plazo: {str(e)}"

"""Eventos de dominio para UC6 - Solicitud de Documentos Faltantes."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Callable, Dict, Any, Optional


# ============================================
# Eventos de dominio
# ============================================

@dataclass
class EventoDominio:
    """Clase base para eventos de dominio."""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SolicitudDocumentosCreada(EventoDominio):
    """Evento emitido cuando el auxiliar crea una solicitud de documentos faltantes."""
    incapacidad_id: int = 0
    documentos_solicitados: List[str] = field(default_factory=list)
    observaciones: Dict[str, str] = field(default_factory=dict)
    fecha_vencimiento: datetime = field(default_factory=datetime.utcnow)
    auxiliar_id: int = 0


@dataclass
class DocumentosEntregados(EventoDominio):
    """Evento emitido cuando el colaborador entrega documentos solicitados."""
    incapacidad_id: int = 0
    documentos_entregados: List[str] = field(default_factory=list)
    fecha_entrega: datetime = field(default_factory=datetime.utcnow)
    colaborador_id: int = 0
    solicitud_completa: bool = False


@dataclass
class SolicitudVencida(EventoDominio):
    """Evento emitido cuando una solicitud de documentos vence sin respuesta."""
    incapacidad_id: int = 0
    documentos_pendientes: List[str] = field(default_factory=list)
    fecha_vencimiento: datetime = field(default_factory=datetime.utcnow)
    dias_retraso: int = 0


@dataclass
class RecordatorioEnviado(EventoDominio):
    """Evento emitido cuando se envía un recordatorio al colaborador."""
    incapacidad_id: int = 0
    numero_recordatorio: int = 1  # 1 o 2
    fecha_envio: datetime = field(default_factory=datetime.utcnow)
    destinatario_email: str = ""


@dataclass
class RequerimientoCitacion(EventoDominio):
    """Evento emitido cuando se requiere citación del colaborador por falta de respuesta."""
    incapacidad_id: int = 0
    motivo: str = ""
    fecha_requerimiento: datetime = field(default_factory=datetime.utcnow)
    intentos_notificacion: int = 0


# ============================================
# Sistema de suscripción a eventos (Observer)
# ============================================

class GestorEventos:
    """Gestor centralizado de eventos de dominio (patrón Observer)."""
    
    def __init__(self):
        self._suscriptores: Dict[type, List[Callable]] = {}
    
    def suscribir(self, tipo_evento: type, handler: Callable[[EventoDominio], None]) -> None:
        """
        Suscribe un handler a un tipo de evento específico.
        
        Args:
            tipo_evento: Clase del evento a escuchar
            handler: Función que se ejecutará cuando ocurra el evento
        
        Examples:
            >>> gestor = GestorEventos()
            >>> def mi_handler(evento):
            ...     print(f"Solicitud creada: {evento.incapacidad_id}")
            >>> gestor.suscribir(SolicitudDocumentosCreada, mi_handler)
        """
        if tipo_evento not in self._suscriptores:
            self._suscriptores[tipo_evento] = []
        self._suscriptores[tipo_evento].append(handler)
    
    def desuscribir(self, tipo_evento: type, handler: Callable) -> None:
        """
        Elimina un handler de la lista de suscriptores.
        
        Args:
            tipo_evento: Clase del evento
            handler: Función a desuscribir
        """
        if tipo_evento in self._suscriptores:
            try:
                self._suscriptores[tipo_evento].remove(handler)
            except ValueError:
                pass
    
    def emitir(self, evento: EventoDominio) -> None:
        """
        Emite un evento a todos los suscriptores registrados.
        
        Args:
            evento: Instancia del evento a emitir
        
        Examples:
            >>> gestor = GestorEventos()
            >>> evento = SolicitudDocumentosCreada(
            ...     incapacidad_id=123,
            ...     documentos_solicitados=['EPICRISIS', 'FURIPS'],
            ...     observaciones={'EPICRISIS': 'Documento ilegible'},
            ...     fecha_vencimiento=datetime.now(),
            ...     auxiliar_id=1
            ... )
            >>> gestor.emitir(evento)
        """
        tipo_evento = type(evento)
        if tipo_evento in self._suscriptores:
            for handler in self._suscriptores[tipo_evento]:
                try:
                    handler(evento)
                except Exception as e:
                    # Log error pero no interrumpir otros handlers
                    print(f"⚠️ Error en handler de evento {tipo_evento.__name__}: {e}")
    
    def limpiar_suscriptores(self, tipo_evento: Optional[type] = None) -> None:
        """
        Limpia todos los suscriptores de un tipo de evento o de todos los eventos.
        
        Args:
            tipo_evento: Si se especifica, solo limpia ese tipo. Si es None, limpia todos.
        """
        if tipo_evento is None:
            self._suscriptores.clear()
        elif tipo_evento in self._suscriptores:
            self._suscriptores[tipo_evento].clear()


# ============================================
# Instancia global del gestor de eventos
# ============================================

gestor_eventos_uc6 = GestorEventos()


# ============================================
# Funciones de conveniencia para emitir eventos
# ============================================

def emitir_solicitud_documentos_creada(
    incapacidad_id: int,
    documentos_solicitados: List[str],
    observaciones: Dict[str, str],
    fecha_vencimiento: datetime,
    auxiliar_id: int
) -> None:
    """Emite el evento SolicitudDocumentosCreada."""
    evento = SolicitudDocumentosCreada(
        incapacidad_id=incapacidad_id,
        documentos_solicitados=documentos_solicitados,
        observaciones=observaciones,
        fecha_vencimiento=fecha_vencimiento,
        auxiliar_id=auxiliar_id
    )
    gestor_eventos_uc6.emitir(evento)


def emitir_documentos_entregados(
    incapacidad_id: int,
    documentos_entregados: List[str],
    fecha_entrega: datetime,
    colaborador_id: int,
    solicitud_completa: bool = False
) -> None:
    """Emite el evento DocumentosEntregados."""
    evento = DocumentosEntregados(
        incapacidad_id=incapacidad_id,
        documentos_entregados=documentos_entregados,
        fecha_entrega=fecha_entrega,
        colaborador_id=colaborador_id,
        solicitud_completa=solicitud_completa
    )
    gestor_eventos_uc6.emitir(evento)


def emitir_solicitud_vencida(
    incapacidad_id: int,
    documentos_pendientes: List[str],
    fecha_vencimiento: datetime,
    dias_retraso: int
) -> None:
    """Emite el evento SolicitudVencida."""
    evento = SolicitudVencida(
        incapacidad_id=incapacidad_id,
        documentos_pendientes=documentos_pendientes,
        fecha_vencimiento=fecha_vencimiento,
        dias_retraso=dias_retraso
    )
    gestor_eventos_uc6.emitir(evento)


def emitir_recordatorio_enviado(
    incapacidad_id: int,
    numero_recordatorio: int,
    fecha_envio: datetime,
    destinatario_email: str
) -> None:
    """Emite el evento RecordatorioEnviado."""
    evento = RecordatorioEnviado(
        incapacidad_id=incapacidad_id,
        numero_recordatorio=numero_recordatorio,
        fecha_envio=fecha_envio,
        destinatario_email=destinatario_email
    )
    gestor_eventos_uc6.emitir(evento)


def emitir_requerimiento_citacion(
    incapacidad_id: int,
    motivo: str,
    fecha_requerimiento: datetime,
    intentos_notificacion: int
) -> None:
    """Emite el evento RequerimientoCitacion."""
    evento = RequerimientoCitacion(
        incapacidad_id=incapacidad_id,
        motivo=motivo,
        fecha_requerimiento=fecha_requerimiento,
        intentos_notificacion=intentos_notificacion
    )
    gestor_eventos_uc6.emitir(evento)

"""Máquina de estados para el ciclo de vida de incapacidades."""
from typing import List, Tuple, Optional

from app.models.enums import EstadoIncapacidadEnum


# Matriz de transiciones válidas
# Formato: estado_origen -> [lista de estados destino válidos]
TRANSICIONES_VALIDAS = {
    EstadoIncapacidadEnum.PENDIENTE_VALIDACION: [
        EstadoIncapacidadEnum.DOCUMENTACION_INCOMPLETA,
        EstadoIncapacidadEnum.DOCUMENTACION_COMPLETA,
        EstadoIncapacidadEnum.RECHAZADA,
    ],
    EstadoIncapacidadEnum.DOCUMENTACION_INCOMPLETA: [
        EstadoIncapacidadEnum.PENDIENTE_VALIDACION,
        EstadoIncapacidadEnum.DOCUMENTACION_COMPLETA,
        EstadoIncapacidadEnum.RECHAZADA,
    ],
    EstadoIncapacidadEnum.DOCUMENTACION_COMPLETA: [
        EstadoIncapacidadEnum.APROBADA_PENDIENTE_TRANSCRIPCION,
        EstadoIncapacidadEnum.RECHAZADA,
    ],
    EstadoIncapacidadEnum.APROBADA_PENDIENTE_TRANSCRIPCION: [
        EstadoIncapacidadEnum.TRANSCRITA,
    ],
    EstadoIncapacidadEnum.TRANSCRITA: [
        EstadoIncapacidadEnum.COBRADA,
        EstadoIncapacidadEnum.RECHAZADA_ENTIDAD,
    ],
    EstadoIncapacidadEnum.COBRADA: [
        EstadoIncapacidadEnum.PAGADA,
    ],
    EstadoIncapacidadEnum.RECHAZADA_ENTIDAD: [
        EstadoIncapacidadEnum.TRANSCRITA,  # Permitir reintentos
    ],
    EstadoIncapacidadEnum.PAGADA: [],  # Estado final
    EstadoIncapacidadEnum.RECHAZADA: [],  # Estado final
}


def es_transicion_valida(estado_actual: str, estado_nuevo: str) -> bool:
    """
    Verifica si una transición de estado es válida según la máquina de estados.
    
    Args:
        estado_actual: Estado actual de la incapacidad
        estado_nuevo: Estado al que se quiere transitar
    
    Returns:
        bool: True si la transición es válida, False en caso contrario
    
    Examples:
        >>> es_transicion_valida(
        ...     EstadoIncapacidadEnum.PENDIENTE_VALIDACION.value,
        ...     EstadoIncapacidadEnum.DOCUMENTACION_INCOMPLETA.value
        ... )
        True
        
        >>> es_transicion_valida(
        ...     EstadoIncapacidadEnum.PAGADA.value,
        ...     EstadoIncapacidadEnum.PENDIENTE_VALIDACION.value
        ... )
        False
    """
    # Si el estado es el mismo, siempre es válido (sin cambio)
    if estado_actual == estado_nuevo:
        return True
    
    # Convertir strings a enums si es necesario
    try:
        if isinstance(estado_actual, str):
            estado_actual = EstadoIncapacidadEnum(estado_actual)
        if isinstance(estado_nuevo, str):
            estado_nuevo = EstadoIncapacidadEnum(estado_nuevo)
    except ValueError:
        return False
    
    # Verificar si el estado actual existe en la matriz
    if estado_actual not in TRANSICIONES_VALIDAS:
        return False
    
    # Verificar si el estado nuevo está en las transiciones permitidas
    return estado_nuevo in TRANSICIONES_VALIDAS[estado_actual]


def obtener_transiciones_posibles(estado_actual: str) -> List[EstadoIncapacidadEnum]:
    """
    Obtiene la lista de estados a los que se puede transitar desde el estado actual.
    
    Args:
        estado_actual: Estado actual de la incapacidad
    
    Returns:
        List[EstadoIncapacidadEnum]: Lista de estados posibles
    
    Examples:
        >>> obtener_transiciones_posibles(
        ...     EstadoIncapacidadEnum.PENDIENTE_VALIDACION.value
        ... )
        [EstadoIncapacidadEnum.DOCUMENTACION_INCOMPLETA, 
         EstadoIncapacidadEnum.DOCUMENTACION_COMPLETA,
         EstadoIncapacidadEnum.RECHAZADA]
    """
    # Convertir string a enum si es necesario
    try:
        if isinstance(estado_actual, str):
            estado_actual = EstadoIncapacidadEnum(estado_actual)
    except ValueError:
        return []
    
    # Retornar lista de transiciones válidas
    return TRANSICIONES_VALIDAS.get(estado_actual, [])


def validar_cambio_estado(
    estado_nuevo: str, 
    incapacidad,
    verificar_precondiciones: bool = True
) -> Tuple[bool, str]:
    """
    Valida si un cambio de estado es posible, considerando precondiciones.
    
    Args:
        estado_nuevo: Estado al que se quiere cambiar
        incapacidad: Instancia de Incapacidad a validar
        verificar_precondiciones: Si True, valida precondiciones adicionales
    
    Returns:
        Tuple[bool, str]: (es_valido, mensaje_error)
            - (True, "") si el cambio es válido
            - (False, "razón del error") si el cambio no es válido
    
    Examples:
        >>> validar_cambio_estado(
        ...     EstadoIncapacidadEnum.DOCUMENTACION_COMPLETA.value,
        ...     incapacidad
        ... )
        (True, "")
    """
    # Convertir strings a enums si es necesario
    try:
        if isinstance(estado_nuevo, str):
            estado_nuevo_enum = EstadoIncapacidadEnum(estado_nuevo)
        else:
            estado_nuevo_enum = estado_nuevo
    except ValueError:
        return False, f"Estado '{estado_nuevo}' no es válido"
    
    estado_actual = incapacidad.estado
    
    # Verificar si la transición es válida según la máquina de estados
    if not es_transicion_valida(estado_actual, estado_nuevo_enum.value):
        return False, (
            f"Transición no válida: {estado_actual} -> {estado_nuevo_enum.value}"
        )
    
    # Si no se requiere verificar precondiciones, retornar válido
    if not verificar_precondiciones:
        return True, ""
    
    # Precondiciones específicas por estado destino
    if estado_nuevo_enum == EstadoIncapacidadEnum.DOCUMENTACION_COMPLETA:
        # Verificar que todas las solicitudes de documentos están respondidas
        if hasattr(incapacidad, 'todas_solicitudes_respondidas'):
            if not incapacidad.todas_solicitudes_respondidas():
                return False, "Aún hay solicitudes de documentos pendientes"
        
        # Verificar que hay documentos cargados
        if not incapacidad.documentos or len(incapacidad.documentos) == 0:
            return False, "No hay documentos cargados"
    
    elif estado_nuevo_enum == EstadoIncapacidadEnum.APROBADA_PENDIENTE_TRANSCRIPCION:
        # Verificar que la documentación está completa
        if estado_actual != EstadoIncapacidadEnum.DOCUMENTACION_COMPLETA.value:
            return False, "La documentación debe estar completa antes de aprobar"
    
    elif estado_nuevo_enum == EstadoIncapacidadEnum.TRANSCRITA:
        # Verificar que está aprobada
        if estado_actual != EstadoIncapacidadEnum.APROBADA_PENDIENTE_TRANSCRIPCION.value:
            if estado_actual != EstadoIncapacidadEnum.RECHAZADA_ENTIDAD.value:
                return False, "Debe estar aprobada o rechazada por entidad para transcribir"
    
    elif estado_nuevo_enum == EstadoIncapacidadEnum.RECHAZADA:
        # Verificar que hay motivo de rechazo
        if not incapacidad.motivo_rechazo:
            return False, "Se requiere especificar el motivo de rechazo"
    
    # Todas las validaciones pasaron
    return True, ""


def obtener_estado_enum(estado: str) -> Optional[EstadoIncapacidadEnum]:
    """
    Convierte un string a EstadoIncapacidadEnum de forma segura.
    
    Args:
        estado: String del estado
    
    Returns:
        EstadoIncapacidadEnum o None si no es válido
    """
    try:
        return EstadoIncapacidadEnum(estado)
    except ValueError:
        return None

"""Utilidades para cálculo de días hábiles y formateo de fechas."""
from datetime import date, datetime, timedelta
from typing import Union

# Festivos nacionales de Colombia 2025-2026
FESTIVOS_COLOMBIA = [
    # 2025
    '2025-01-01',  # Año Nuevo
    '2025-01-06',  # Reyes Magos
    '2025-03-24',  # San José
    '2025-04-10',  # Jueves Santo
    '2025-04-11',  # Viernes Santo
    '2025-05-01',  # Día del Trabajo
    '2025-05-12',  # Ascensión del Señor
    '2025-06-02',  # Corpus Christi
    '2025-06-09',  # Sagrado Corazón
    '2025-06-16',  # San Pedro y San Pablo
    '2025-06-23',  # San Pedro y San Pablo (traslado)
    '2025-06-30',  # San Pedro y San Pablo (observado)
    '2025-07-01',  # San Pedro y San Pablo (festivo trasladado)
    '2025-07-07',  # San Fermín
    '2025-07-20',  # Día de la Independencia
    '2025-07-24',  # Simón Bolívar (traslado)
    '2025-08-07',  # Batalla de Boyacá
    '2025-08-18',  # Asunción de la Virgen
    '2025-10-12',  # Día de la Raza (traslado)
    '2025-10-13',  # Día de la Raza
    '2025-11-01',  # Todos los Santos (traslado)
    '2025-11-03',  # Todos los Santos
    '2025-11-17',  # Independencia de Cartagena
    '2025-12-08',  # Inmaculada Concepción
    '2025-12-25',  # Navidad
    # 2026
    '2026-01-01',  # Año Nuevo
    '2026-01-12',  # Reyes Magos (traslado)
    '2026-03-23',  # San José
    '2026-04-02',  # Jueves Santo
    '2026-04-03',  # Viernes Santo
    '2026-05-01',  # Día del Trabajo
    '2026-05-18',  # Ascensión del Señor
    '2026-06-08',  # Corpus Christi
    '2026-06-15',  # Sagrado Corazón
    '2026-06-29',  # San Pedro y San Pablo
    '2026-07-20',  # Día de la Independencia
    '2026-08-07',  # Batalla de Boyacá
    '2026-08-17',  # Asunción de la Virgen (traslado)
    '2026-10-12',  # Día de la Raza
    '2026-11-02',  # Todos los Santos (traslado)
    '2026-11-16',  # Independencia de Cartagena (traslado)
    '2026-12-08',  # Inmaculada Concepción
    '2026-12-25',  # Navidad
]

# Convertir a set de objetos date para búsqueda rápida
_FESTIVOS_SET = {datetime.strptime(f, '%Y-%m-%d').date() for f in FESTIVOS_COLOMBIA}

# Nombres de meses en español
_MESES_ES = [
    'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
    'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
]

# Nombres de días en español
_DIAS_ES = [
    'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo'
]


def es_dia_habil(fecha: Union[date, datetime]) -> bool:
    """
    Determina si una fecha es día hábil.
    
    Un día hábil es aquel que:
    - No es sábado (5) ni domingo (6)
    - No está en la lista de festivos nacionales
    
    Args:
        fecha: Fecha a verificar (date o datetime)
    
    Returns:
        bool: True si es día hábil, False si es fin de semana o festivo
    
    Examples:
        >>> es_dia_habil(date(2025, 10, 20))  # Lunes
        True
        >>> es_dia_habil(date(2025, 10, 25))  # Sábado
        False
        >>> es_dia_habil(date(2025, 12, 25))  # Navidad
        False
    """
    if isinstance(fecha, datetime):
        fecha = fecha.date()
    
    # Verificar si es fin de semana (sábado=5, domingo=6)
    if fecha.weekday() >= 5:
        return False
    
    # Verificar si es festivo
    if fecha in _FESTIVOS_SET:
        return False
    
    return True


def sumar_dias_habiles(fecha_inicio: Union[date, datetime], dias: int = 3) -> date:
    """
    Suma N días hábiles a una fecha, saltando fines de semana y festivos.
    
    Args:
        fecha_inicio: Fecha de inicio
        dias: Número de días hábiles a sumar (default: 3)
    
    Returns:
        date: Fecha resultante después de sumar los días hábiles
    
    Examples:
        >>> sumar_dias_habiles(date(2025, 10, 20), 3)  # Lunes + 3 días
        datetime.date(2025, 10, 23)  # Jueves
        
        >>> sumar_dias_habiles(date(2025, 10, 23), 3)  # Jueves + 3 días
        datetime.date(2025, 10, 28)  # Martes (salta fin de semana)
    """
    if isinstance(fecha_inicio, datetime):
        fecha_inicio = fecha_inicio.date()
    
    fecha_actual = fecha_inicio
    dias_sumados = 0
    
    while dias_sumados < dias:
        fecha_actual += timedelta(days=1)
        if es_dia_habil(fecha_actual):
            dias_sumados += 1
    
    return fecha_actual


def dias_habiles_restantes(fecha_inicio: Union[date, datetime], 
                          fecha_vencimiento: Union[date, datetime]) -> int:
    """
    Calcula cuántos días hábiles faltan entre dos fechas.
    
    Args:
        fecha_inicio: Fecha de referencia (hoy)
        fecha_vencimiento: Fecha de vencimiento
    
    Returns:
        int: Número de días hábiles restantes
             - Positivo: días que faltan
             - Negativo: días de retraso
             - 0: vence hoy o ya venció
    
    Examples:
        >>> dias_habiles_restantes(date(2025, 10, 20), date(2025, 10, 23))
        3  # 3 días hábiles entre lunes y jueves
        
        >>> dias_habiles_restantes(date(2025, 10, 25), date(2025, 10, 23))
        -2  # Ya venció hace 2 días hábiles
    """
    if isinstance(fecha_inicio, datetime):
        fecha_inicio = fecha_inicio.date()
    if isinstance(fecha_vencimiento, datetime):
        fecha_vencimiento = fecha_vencimiento.date()
    
    # Si ya venció o vence hoy
    if fecha_inicio >= fecha_vencimiento:
        # Contar días hábiles de retraso (negativo)
        if fecha_inicio == fecha_vencimiento:
            return 0
        
        dias = 0
        fecha_actual = fecha_vencimiento
        while fecha_actual < fecha_inicio:
            fecha_actual += timedelta(days=1)
            if es_dia_habil(fecha_actual):
                dias -= 1
        return dias
    
    # Contar días hábiles restantes
    dias = 0
    fecha_actual = fecha_inicio
    while fecha_actual < fecha_vencimiento:
        fecha_actual += timedelta(days=1)
        if es_dia_habil(fecha_actual):
            dias += 1
    
    return dias


def formatar_fecha_legible(fecha: Union[date, datetime]) -> str:
    """
    Formatea una fecha en español de forma legible.
    
    Args:
        fecha: Fecha a formatear
    
    Returns:
        str: Fecha formateada (ej: "viernes 17 de octubre de 2025")
    
    Examples:
        >>> formatar_fecha_legible(date(2025, 10, 17))
        'viernes 17 de octubre de 2025'
        
        >>> formatar_fecha_legible(date(2025, 12, 25))
        'jueves 25 de diciembre de 2025'
    """
    if isinstance(fecha, datetime):
        fecha = fecha.date()
    
    dia_semana = _DIAS_ES[fecha.weekday()]
    dia = fecha.day
    mes = _MESES_ES[fecha.month - 1]
    anio = fecha.year
    
    return f"{dia_semana} {dia} de {mes} de {anio}"

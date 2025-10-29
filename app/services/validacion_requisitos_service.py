"""
Servicio de validación de requisitos por tipo de incapacidad (UC5).

Este módulo implementa la lógica de validación automática de documentos
requeridos según el tipo de incapacidad registrada.

Autor: Sistema
Fecha: 2025-10-28
Caso de Uso: UC5 - Verificar requisitos por tipo
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.models.incapacidad import Incapacidad, TIPOS_INCAPACIDAD
from app.models.documento import Documento
from app.models.enums import TipoDocumentoEnum

# Configurar logger
logger = logging.getLogger(__name__)


# ============================================================================
# EXCEPCIONES PERSONALIZADAS (UC5)
# ============================================================================

class TipoIncapacidadNoDefinido(ValueError):
    """
    Excepción E1: Tipo de incapacidad no está definido.
    
    Se eleva cuando se intenta validar una incapacidad que no tiene
    el campo 'tipo' definido, lo cual es requerido para aplicar
    las reglas de validación correspondientes.
    """
    def __init__(self, incapacidad_id: int):
        self.incapacidad_id = incapacidad_id
        self.codigo_error = "E1"
        mensaje = (
            f"[E1] La incapacidad ID {incapacidad_id} no tiene tipo definido. "
            "Para validar requisitos debe especificar un tipo válido: "
            f"{', '.join(TIPOS_INCAPACIDAD.keys())}."
        )
        super().__init__(mensaje)
        
        # Logging inmediato del error
        logger.error(
            f"E1 - Tipo no definido: incapacidad_id={incapacidad_id}. "
            "Validación bloqueada hasta definir tipo."
        )


class ReglasNoConfiguradas(Exception):
    """
    Excepción E2: No existen reglas configuradas para un tipo específico.
    
    Se eleva cuando se solicita validación para un tipo de incapacidad
    que no tiene reglas definidas en REQUISITOS_POR_TIPO. El sistema
    aplicará un fallback a validación básica y notificará al administrador.
    """
    def __init__(self, tipo: str):
        self.tipo = tipo
        self.codigo_error = "E2"
        mensaje = (
            f"[E2] No existen reglas de validación configuradas para el tipo '{tipo}'. "
            f"Tipos válidos: {', '.join(TIPOS_INCAPACIDAD.keys())}. "
            "Se aplicará validación básica (solo CERTIFICADO_INCAPACIDAD)."
        )
        super().__init__(mensaje)
        
        # Logging con nivel WARNING para administrador
        logger.warning(
            f"E2 - Reglas no configuradas: tipo='{tipo}'. "
            "ACCIÓN REQUERIDA: Configurar reglas en REQUISITOS_POR_TIPO. "
            "Aplicando fallback a validación básica."
        )


# ============================================================================
# VALIDADOR DE REQUISITOS - CLASE PRINCIPAL
# ============================================================================

class IncapacidadMock:
    """
    Clase mock para simular objetos Incapacidad en validaciones.
    Se usa para evaluar condiciones sin necesidad de una instancia completa.
    """
    def __init__(self):
        self.dias = 0
        self.tipo = ''

class ValidadorRequisitos:
    """
    Validador de requisitos de documentación por tipo de incapacidad.
    
    Implementa UC5: Verificar requisitos por tipo
    
    Responsabilidades:
        - Validar documentos obligatorios según tipo de incapacidad
        - Aplicar reglas condicionales (ej: epicrisis si días > 2)
        - Generar checklist de documentos presentes y faltantes
        - Determinar si documentación está completa o incompleta
    
    Uso:
        >>> validador = ValidadorRequisitos()
        >>> resultado = validador.validar(incapacidad)
        >>> if resultado['completo']:
        >>>     print("Documentación completa")
        >>> else:
        >>>     print(f"Faltan: {resultado['faltantes']}")
    """
    
    # Mapeo de tipos de incapacidad a sus valores en BD
    TIPO_ENFERMEDAD_GENERAL = 'Enfermedad General'
    TIPO_ACCIDENTE_LABORAL = 'Accidente Laboral'
    TIPO_ACCIDENTE_TRANSITO = 'Accidente de Tránsito'
    TIPO_LICENCIA_MATERNIDAD = 'Licencia de Maternidad'
    TIPO_LICENCIA_PATERNIDAD = 'Licencia de Paternidad'
    
    def __init__(self):
        """
        Inicializa el validador y carga las reglas de validación.
        
        Las reglas se definen en el diccionario REQUISITOS_POR_TIPO.
        """
        self._cargar_reglas()
        logger.info(
            f"ValidadorRequisitos inicializado con {len(self.REQUISITOS_POR_TIPO)} tipos"
        )
    
    def _cargar_reglas(self):
        """
        Define las reglas de validación para cada tipo de incapacidad.
        
        Estructura:
            - obligatorios: Lista de documentos siempre requeridos
            - condicionales: Lista de reglas que dependen de condiciones
                - condicion: Función lambda que evalúa la condición
                - documento: Tipo de documento requerido si condición es True
                - descripcion: Texto explicativo de la regla
        """
        self.REQUISITOS_POR_TIPO = {
            # ================================================================
            # ENFERMEDAD GENERAL
            # ================================================================
            self.TIPO_ENFERMEDAD_GENERAL: {
                'obligatorios': [
                    TipoDocumentoEnum.CERTIFICADO_INCAPACIDAD.value
                ],
                'condicionales': [
                    {
                        'condicion': lambda inc: inc.dias > 2,
                        'documento': TipoDocumentoEnum.EPICRISIS.value,
                        'descripcion': 'Epicrisis requerida para incapacidades mayores a 2 días'
                    }
                ],
                'descripcion': 'Enfermedad General'
            },
            
            # ================================================================
            # ACCIDENTE LABORAL
            # ================================================================
            self.TIPO_ACCIDENTE_LABORAL: {
                'obligatorios': [
                    TipoDocumentoEnum.CERTIFICADO_INCAPACIDAD.value,
                    TipoDocumentoEnum.EPICRISIS.value
                ],
                'condicionales': [],
                'descripcion': 'Accidente Laboral'
            },
            
            # ================================================================
            # ACCIDENTE DE TRÁNSITO
            # ================================================================
            self.TIPO_ACCIDENTE_TRANSITO: {
                'obligatorios': [
                    TipoDocumentoEnum.CERTIFICADO_INCAPACIDAD.value,
                    TipoDocumentoEnum.EPICRISIS.value,
                    TipoDocumentoEnum.FURIPS.value
                ],
                'condicionales': [],
                'descripcion': 'Accidente de Tránsito'
            },
            
            # ================================================================
            # LICENCIA DE MATERNIDAD
            # ================================================================
            self.TIPO_LICENCIA_MATERNIDAD: {
                'obligatorios': [
                    TipoDocumentoEnum.CERTIFICADO_INCAPACIDAD.value,
                    TipoDocumentoEnum.EPICRISIS.value,
                    TipoDocumentoEnum.CERTIFICADO_NACIDO_VIVO.value,
                    TipoDocumentoEnum.REGISTRO_CIVIL.value,
                    TipoDocumentoEnum.DOCUMENTO_IDENTIDAD.value
                ],
                'condicionales': [],
                'descripcion': 'Licencia de Maternidad'
            },
            
            # ================================================================
            # LICENCIA DE PATERNIDAD
            # ================================================================
            self.TIPO_LICENCIA_PATERNIDAD: {
                'obligatorios': [
                    TipoDocumentoEnum.CERTIFICADO_INCAPACIDAD.value,
                    TipoDocumentoEnum.EPICRISIS.value,
                    TipoDocumentoEnum.CERTIFICADO_NACIDO_VIVO.value,
                    TipoDocumentoEnum.REGISTRO_CIVIL.value,
                    TipoDocumentoEnum.DOCUMENTO_IDENTIDAD.value
                ],
                'condicionales': [],
                'descripcion': 'Licencia de Paternidad (incluye documento de identidad de la madre)'
            }
        }
    
    def validar(self, incapacidad: Incapacidad) -> Dict[str, Any]:
        """
        Valida automáticamente los requisitos documentales de una incapacidad.
        
        Implementa el flujo completo de UC5 (pasos 1-10).
        
        Args:
            incapacidad: Objeto Incapacidad a validar
        
        Returns:
            Dict con estructura:
            {
                'completo': bool,           # True si tiene todos los documentos
                'faltantes': List[Dict],    # Lista de documentos faltantes
                'presentes': List[Dict],    # Lista de documentos presentes
                'detalles': Dict            # Información adicional
            }
        
        Raises:
            TipoIncapacidadNoDefinido: Si incapacidad.tipo es None o vacío (E1)
            ReglasNoConfiguradas: Si no hay reglas para el tipo (E2)
        
        Example:
            >>> resultado = validador.validar(incapacidad)
            >>> print(resultado['completo'])
            False
            >>> print(resultado['faltantes'])
            [{'tipo': 'EPICRISIS', 'nombre': 'Epicrisis', 'motivo': '...'}]
        """
        # Paso 1: Identificar el tipo de incapacidad (E1 Check)
        if not incapacidad.tipo:
            # E1: Tipo no definido - elevar excepción custom
            logger.error(
                f"E1 - Validación bloqueada: incapacidad {incapacidad.id} "
                f"sin tipo definido. Usuario: {getattr(incapacidad, 'usuario_id', 'N/A')}"
            )
            raise TipoIncapacidadNoDefinido(incapacidad.id)
        
        tipo = incapacidad.tipo
        logger.info(
            f"Validando incapacidad {incapacidad.id} "
            f"(tipo: {tipo}, días: {incapacidad.dias})"
        )
        
        # Paso 2: Cargar reglas de validación para ese tipo
        reglas = self._obtener_reglas(tipo)
        
        # Obtener documentos cargados en la incapacidad
        documentos_cargados = incapacidad.documentos
        tipos_cargados = {doc.tipo_documento for doc in documentos_cargados}
        
        logger.debug(f"Documentos cargados: {tipos_cargados}")
        
        # Paso 3-8: Verificar documentos según reglas
        requisitos_totales = self._calcular_requisitos(incapacidad, reglas)
        
        logger.debug(f"Requisitos totales: {requisitos_totales}")
        
        # Paso 9: Generar checklist
        faltantes = []
        presentes = []
        
        for req_tipo in requisitos_totales:
            if req_tipo in tipos_cargados:
                # Documento presente
                doc = next(d for d in documentos_cargados if d.tipo_documento == req_tipo)
                presentes.append({
                    'tipo': req_tipo,
                    'nombre': self._nombre_documento(req_tipo),
                    'uuid': doc.nombre_unico,
                    'fecha_carga': doc.fecha_carga.strftime('%Y-%m-%d %H:%M'),
                    'tamaño_mb': doc.tamaño_mb
                })
            else:
                # Documento faltante
                motivo = self._motivo_requerido(req_tipo, reglas, incapacidad)
                faltantes.append({
                    'tipo': req_tipo,
                    'nombre': self._nombre_documento(req_tipo),
                    'obligatorio': req_tipo in reglas['obligatorios'],
                    'motivo': motivo
                })
        
        # Determinar si está completo
        completo = len(faltantes) == 0
        
        # Paso 10: Retornar resultado
        resultado = {
            'completo': completo,
            'faltantes': faltantes,
            'presentes': presentes,
            'detalles': {
                'tipo_incapacidad': tipo,
                'dias': incapacidad.dias,
                'total_requisitos': len(requisitos_totales),
                'total_presentes': len(presentes),
                'total_faltantes': len(faltantes),
                'fecha_validacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }
        
        logger.info(
            f"Validación completada: completo={completo}, "
            f"presentes={len(presentes)}, faltantes={len(faltantes)}"
        )
        
        return resultado
    
    def get_faltantes(self, incapacidad: Incapacidad) -> List[Dict[str, Any]]:
        """
        Retorna solo los documentos faltantes.
        
        Args:
            incapacidad: Objeto Incapacidad a validar
        
        Returns:
            Lista de diccionarios con documentos faltantes
        
        Example:
            >>> faltantes = validador.get_faltantes(incapacidad)
            >>> for doc in faltantes:
            >>>     print(f"Falta: {doc['nombre']}")
        """
        resultado = self.validar(incapacidad)
        return resultado['faltantes']
    
    def get_presentes(self, incapacidad: Incapacidad) -> List[Dict[str, Any]]:
        """
        Retorna solo los documentos presentes.
        
        Args:
            incapacidad: Objeto Incapacidad a validar
        
        Returns:
            Lista de diccionarios con documentos presentes
        
        Example:
            >>> presentes = validador.get_presentes(incapacidad)
            >>> for doc in presentes:
            >>>     print(f"Presente: {doc['nombre']}")
        """
        resultado = self.validar(incapacidad)
        return resultado['presentes']
    
    def es_completo(self, incapacidad: Incapacidad) -> bool:
        """
        Retorna True si la documentación está completa, False si falta algo.
        
        Args:
            incapacidad: Objeto Incapacidad a validar
        
        Returns:
            bool: True si completo, False si falta documentación
        
        Example:
            >>> if validador.es_completo(incapacidad):
            >>>     print("✓ Documentación completa")
            >>> else:
            >>>     print("✗ Falta documentación")
        """
        resultado = self.validar(incapacidad)
        return resultado['completo']
    
    # ========================================================================
    # MÉTODOS PRIVADOS (HELPERS)
    # ========================================================================
    
    def _obtener_reglas(self, tipo: str) -> Dict[str, Any]:
        """
        Obtiene las reglas de validación para un tipo de incapacidad.
        
        Args:
            tipo: Tipo de incapacidad
        
        Returns:
            Diccionario con reglas (obligatorios, condicionales)
        
        Raises:
            ReglasNoConfiguradas: Si no hay reglas para el tipo (E2)
            
        Note:
            En caso E2, se aplica fallback automático a validación básica
            y se notifica al administrador vía logging.
        """
        if tipo not in self.REQUISITOS_POR_TIPO:
            # E2: Elevar excepción y aplicar fallback
            excepcion_e2 = ReglasNoConfiguradas(tipo)
            
            # Notificar al administrador (logging ya hecho en __init__)
            logger.critical(
                f"ADMINISTRADOR: Configurar reglas para tipo '{tipo}' "
                f"en ValidadorRequisitos.REQUISITOS_POR_TIPO"
            )
            
            # Fallback a validación básica (solo CERTIFICADO)
            reglas_fallback = {
                'obligatorios': [TipoDocumentoEnum.CERTIFICADO_INCAPACIDAD.value],
                'condicionales': [],
                'descripcion': f'{tipo} (reglas no configuradas - usando fallback)',
                'es_fallback': True
            }
            
            logger.info(f"Aplicando fallback para tipo '{tipo}': {reglas_fallback}")
            return reglas_fallback
        
        return self.REQUISITOS_POR_TIPO[tipo]
    
    def _calcular_requisitos(
        self,
        incapacidad: Incapacidad,
        reglas: Dict[str, Any]
    ) -> List[str]:
        """
        Calcula la lista total de requisitos (obligatorios + condicionales aplicables).
        
        Args:
            incapacidad: Objeto Incapacidad
            reglas: Diccionario de reglas
        
        Returns:
            Lista de tipos de documentos requeridos
        """
        requisitos = list(reglas['obligatorios'])
        
        # Evaluar condicionales
        for regla_condicional in reglas['condicionales']:
            condicion = regla_condicional['condicion']
            documento = regla_condicional['documento']
            
            # Evaluar la condición (lambda)
            if condicion(incapacidad):
                requisitos.append(documento)
                logger.debug(
                    f"Condición cumplida: {regla_condicional['descripcion']}"
                )
        
        return requisitos
    
    def _nombre_documento(self, tipo_documento: str) -> str:
        """
        Convierte el tipo de documento a nombre legible.
        
        Args:
            tipo_documento: Tipo de documento (enum value)
        
        Returns:
            Nombre legible del documento
        """
        nombres = {
            TipoDocumentoEnum.CERTIFICADO_INCAPACIDAD.value: 'Certificado de Incapacidad',
            TipoDocumentoEnum.EPICRISIS.value: 'Epicrisis',
            TipoDocumentoEnum.FURIPS.value: 'FURIPS',
            TipoDocumentoEnum.CERTIFICADO_NACIDO_VIVO.value: 'Certificado de Nacido Vivo',
            TipoDocumentoEnum.REGISTRO_CIVIL.value: 'Registro Civil',
            TipoDocumentoEnum.DOCUMENTO_IDENTIDAD.value: 'Documento de Identidad',
        }
        return nombres.get(tipo_documento, tipo_documento)
    
    def _motivo_requerido(
        self,
        tipo_documento: str,
        reglas: Dict[str, Any],
        incapacidad: Incapacidad
    ) -> str:
        """
        Genera el motivo por el cual un documento es requerido.
        
        Args:
            tipo_documento: Tipo de documento
            reglas: Reglas de validación
            incapacidad: Objeto Incapacidad
        
        Returns:
            Texto explicativo del motivo
        """
        # Verificar si es obligatorio
        if tipo_documento in reglas['obligatorios']:
            return f"Obligatorio para {reglas['descripcion']}"
        
        # Verificar si es condicional
        for regla_cond in reglas['condicionales']:
            if regla_cond['documento'] == tipo_documento:
                return regla_cond['descripcion']
        
        return "Requerido"
    
    def obtener_requisitos_para_tipo(self, tipo: str, dias: Optional[int] = None) -> Dict[str, Any]:
        """
        Obtiene los requisitos para un tipo sin necesidad de incapacidad completa.
        
        Útil para mostrar en UI qué documentos serán necesarios según tipo.
        
        Args:
            tipo: Tipo de incapacidad
            dias: Días de incapacidad (opcional, para evaluar condicionales)
        
        Returns:
            Dict con obligatorios y condicionales aplicables
        
        Example:
            >>> reqs = validador.obtener_requisitos_para_tipo('Enfermedad General', dias=5)
            >>> print(reqs['obligatorios'])
            ['CERTIFICADO_INCAPACIDAD', 'EPICRISIS']
        """
        reglas = self._obtener_reglas(tipo)
        
        requisitos = {
            'obligatorios': reglas['obligatorios'],
            'condicionales_posibles': [],
            'condicionales_aplicables': []
        }
        
        # Listar todos los condicionales posibles
        for regla_cond in reglas['condicionales']:
            requisitos['condicionales_posibles'].append({
                'documento': regla_cond['documento'],
                'condicion': regla_cond['descripcion']
            })
        
        # Si se proporcionan días, evaluar condicionales
        if dias is not None:
            # Crear objeto mock para evaluar condiciones
            inc_mock = IncapacidadMock()
            inc_mock.dias = dias
            inc_mock.tipo = tipo
            
            for regla_cond in reglas['condicionales']:
                if regla_cond['condicion'](inc_mock):
                    requisitos['condicionales_aplicables'].append(
                        regla_cond['documento']
                    )
        
        return requisitos

    def obtener_requisitos_por_tipo_y_dias(self, tipo: str, dias: int) -> dict:
        """
        Obtiene los documentos requeridos para un tipo específico y cantidad de días.
        
        Args:
            tipo (str): Tipo de incapacidad
            dias (int): Cantidad de días de incapacidad
            
        Returns:
            dict: Diccionario con documentos obligatorios y condicionales
                {
                    'obligatorios': [lista de documentos],
                    'condicionales': [lista de documentos],
                    'total': número total
                }
        """
        if tipo not in self.REQUISITOS_POR_TIPO:
            logger.warning(f"Tipo de incapacidad no reconocido: {tipo}")
            return {
                'obligatorios': [],
                'condicionales': [],
                'total': 0
            }
        
        reglas = self.REQUISITOS_POR_TIPO[tipo]
        
        # Documentos base obligatorios
        obligatorios = reglas.get('obligatorios', []).copy()
        condicionales = []
        
        # Evaluar condiciones usando una incapacidad mock
        inc_mock = IncapacidadMock()
        inc_mock.dias = dias
        inc_mock.tipo = tipo
        
        for regla_cond in reglas.get('condicionales', []):
            documento = regla_cond['documento']
            
            try:
                if regla_cond['condicion'](inc_mock):
                    # La condición se cumple, el documento es obligatorio
                    if documento not in obligatorios:
                        obligatorios.append(documento)
                # Si la condición NO se cumple, el documento NO es requerido
                # (no se agrega ni a obligatorios ni a condicionales)
            except Exception as e:
                logger.error(f"Error evaluando condición para {documento}: {e}")
                # En caso de error, tratar como condicional (no obligatorio)
                if documento not in condicionales:
                    condicionales.append(documento)
        
        return {
            'obligatorios': obligatorios,
            'condicionales': condicionales,
            'total': len(obligatorios) + len(condicionales)
        }


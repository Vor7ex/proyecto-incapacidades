"""Tests para la máquina de estados de incapacidades."""
import pytest
from unittest.mock import MagicMock

from app.models.enums import EstadoIncapacidadEnum
from app.utils.maquina_estados import (
    es_transicion_valida,
    obtener_transiciones_posibles,
    validar_cambio_estado,
    TRANSICIONES_VALIDAS,
)


class TestEsTransicionValida:
    """Tests para la función es_transicion_valida."""
    
    def test_transicion_valida_pendiente_a_incompleta(self):
        """PENDIENTE_VALIDACION -> DOCUMENTACION_INCOMPLETA debe ser válida."""
        resultado = es_transicion_valida(
            EstadoIncapacidadEnum.PENDIENTE_VALIDACION.value,
            EstadoIncapacidadEnum.DOCUMENTACION_INCOMPLETA.value
        )
        assert resultado is True
    
    def test_transicion_valida_pendiente_a_completa(self):
        """PENDIENTE_VALIDACION -> DOCUMENTACION_COMPLETA debe ser válida."""
        resultado = es_transicion_valida(
            EstadoIncapacidadEnum.PENDIENTE_VALIDACION.value,
            EstadoIncapacidadEnum.DOCUMENTACION_COMPLETA.value
        )
        assert resultado is True
    
    def test_transicion_invalida_pagada_a_pendiente(self):
        """PAGADA -> PENDIENTE_VALIDACION debe ser inválida (estado final)."""
        resultado = es_transicion_valida(
            EstadoIncapacidadEnum.PAGADA.value,
            EstadoIncapacidadEnum.PENDIENTE_VALIDACION.value
        )
        assert resultado is False
    
    def test_transicion_invalida_rechazada_a_aprobada(self):
        """RECHAZADA -> APROBADA debe ser inválida (estado final)."""
        resultado = es_transicion_valida(
            EstadoIncapacidadEnum.RECHAZADA.value,
            EstadoIncapacidadEnum.APROBADA_PENDIENTE_TRANSCRIPCION.value
        )
        assert resultado is False
    
    def test_mismo_estado_siempre_valido(self):
        """Mismo estado debe ser siempre válido."""
        resultado = es_transicion_valida(
            EstadoIncapacidadEnum.PENDIENTE_VALIDACION.value,
            EstadoIncapacidadEnum.PENDIENTE_VALIDACION.value
        )
        assert resultado is True
    
    def test_acepta_enums_y_strings(self):
        """Debe aceptar tanto enums como strings."""
        # Con enums
        resultado1 = es_transicion_valida(
            EstadoIncapacidadEnum.PENDIENTE_VALIDACION,
            EstadoIncapacidadEnum.DOCUMENTACION_COMPLETA
        )
        assert resultado1 is True
        
        # Con strings
        resultado2 = es_transicion_valida(
            EstadoIncapacidadEnum.PENDIENTE_VALIDACION.value,
            EstadoIncapacidadEnum.DOCUMENTACION_COMPLETA.value
        )
        assert resultado2 is True
    
    def test_estado_invalido_retorna_false(self):
        """Estado inválido debe retornar False."""
        resultado = es_transicion_valida(
            "ESTADO_INVENTADO",
            EstadoIncapacidadEnum.PENDIENTE_VALIDACION.value
        )
        assert resultado is False


class TestObtenerTransicionesPosibles:
    """Tests para la función obtener_transiciones_posibles."""
    
    def test_transiciones_desde_pendiente_validacion(self):
        """Debe retornar transiciones correctas desde PENDIENTE_VALIDACION."""
        resultado = obtener_transiciones_posibles(
            EstadoIncapacidadEnum.PENDIENTE_VALIDACION.value
        )
        esperado = [
            EstadoIncapacidadEnum.DOCUMENTACION_INCOMPLETA,
            EstadoIncapacidadEnum.DOCUMENTACION_COMPLETA,
            EstadoIncapacidadEnum.RECHAZADA,
        ]
        assert resultado == esperado
    
    def test_transiciones_desde_documentacion_completa(self):
        """Debe retornar transiciones correctas desde DOCUMENTACION_COMPLETA."""
        resultado = obtener_transiciones_posibles(
            EstadoIncapacidadEnum.DOCUMENTACION_COMPLETA.value
        )
        esperado = [
            EstadoIncapacidadEnum.APROBADA_PENDIENTE_TRANSCRIPCION,
            EstadoIncapacidadEnum.RECHAZADA,
        ]
        assert resultado == esperado
    
    def test_transiciones_desde_estado_final_vacia(self):
        """Estados finales no deben tener transiciones."""
        resultado = obtener_transiciones_posibles(
            EstadoIncapacidadEnum.PAGADA.value
        )
        assert resultado == []
        
        resultado2 = obtener_transiciones_posibles(
            EstadoIncapacidadEnum.RECHAZADA.value
        )
        assert resultado2 == []
    
    def test_estado_invalido_retorna_lista_vacia(self):
        """Estado inválido debe retornar lista vacía."""
        resultado = obtener_transiciones_posibles("ESTADO_INVENTADO")
        assert resultado == []
    
    def test_acepta_enum_y_string(self):
        """Debe aceptar enum o string."""
        resultado1 = obtener_transiciones_posibles(
            EstadoIncapacidadEnum.PENDIENTE_VALIDACION
        )
        resultado2 = obtener_transiciones_posibles(
            EstadoIncapacidadEnum.PENDIENTE_VALIDACION.value
        )
        assert resultado1 == resultado2


class TestValidarCambioEstado:
    """Tests para la función validar_cambio_estado."""
    
    def test_cambio_valido_sin_precondiciones(self):
        """Cambio válido sin verificar precondiciones debe pasar."""
        # Mock de incapacidad
        incapacidad = MagicMock()
        incapacidad.estado = EstadoIncapacidadEnum.PENDIENTE_VALIDACION.value
        incapacidad.documentos = [MagicMock()]  # Al menos un documento
        
        valido, mensaje = validar_cambio_estado(
            EstadoIncapacidadEnum.DOCUMENTACION_INCOMPLETA.value,
            incapacidad,
            verificar_precondiciones=False
        )
        assert valido is True
        assert mensaje == ""
    
    def test_cambio_invalido_por_transicion(self):
        """Cambio inválido por transición incorrecta."""
        incapacidad = MagicMock()
        incapacidad.estado = EstadoIncapacidadEnum.PAGADA.value
        
        valido, mensaje = validar_cambio_estado(
            EstadoIncapacidadEnum.PENDIENTE_VALIDACION.value,
            incapacidad
        )
        assert valido is False
        assert "Transición no válida" in mensaje
    
    def test_documentacion_completa_requiere_documentos(self):
        """DOCUMENTACION_COMPLETA requiere que haya documentos."""
        incapacidad = MagicMock()
        incapacidad.estado = EstadoIncapacidadEnum.PENDIENTE_VALIDACION.value
        incapacidad.documentos = []  # Sin documentos
        incapacidad.todas_solicitudes_respondidas.return_value = True
        
        valido, mensaje = validar_cambio_estado(
            EstadoIncapacidadEnum.DOCUMENTACION_COMPLETA.value,
            incapacidad,
            verificar_precondiciones=True
        )
        assert valido is False
        assert "No hay documentos cargados" in mensaje
    
    def test_rechazada_requiere_motivo(self):
        """RECHAZADA requiere motivo_rechazo."""
        incapacidad = MagicMock()
        incapacidad.estado = EstadoIncapacidadEnum.PENDIENTE_VALIDACION.value
        incapacidad.motivo_rechazo = None  # Sin motivo
        
        valido, mensaje = validar_cambio_estado(
            EstadoIncapacidadEnum.RECHAZADA.value,
            incapacidad,
            verificar_precondiciones=True
        )
        assert valido is False
        assert "motivo de rechazo" in mensaje
    
    def test_estado_invalido_retorna_error(self):
        """Estado inválido debe retornar error."""
        incapacidad = MagicMock()
        incapacidad.estado = EstadoIncapacidadEnum.PENDIENTE_VALIDACION.value
        
        valido, mensaje = validar_cambio_estado(
            "ESTADO_INVENTADO",
            incapacidad
        )
        assert valido is False
        assert "no es válido" in mensaje
    
    def test_documentacion_completa_con_solicitudes_pendientes(self):
        """DOCUMENTACION_COMPLETA no debe pasar si hay solicitudes pendientes."""
        incapacidad = MagicMock()
        incapacidad.estado = EstadoIncapacidadEnum.DOCUMENTACION_INCOMPLETA.value
        incapacidad.documentos = [MagicMock()]
        incapacidad.todas_solicitudes_respondidas.return_value = False  # Hay pendientes
        
        valido, mensaje = validar_cambio_estado(
            EstadoIncapacidadEnum.DOCUMENTACION_COMPLETA.value,
            incapacidad,
            verificar_precondiciones=True
        )
        assert valido is False
        assert "solicitudes de documentos pendientes" in mensaje


class TestMatrizTransiciones:
    """Tests para verificar la integridad de la matriz de transiciones."""
    
    def test_todos_estados_en_matriz(self):
        """Todos los estados deben estar en la matriz."""
        for estado in EstadoIncapacidadEnum:
            assert estado in TRANSICIONES_VALIDAS, (
                f"Estado {estado} no está en TRANSICIONES_VALIDAS"
            )
    
    def test_estados_finales_sin_transiciones(self):
        """Estados finales no deben tener transiciones."""
        assert TRANSICIONES_VALIDAS[EstadoIncapacidadEnum.PAGADA] == []
        assert TRANSICIONES_VALIDAS[EstadoIncapacidadEnum.RECHAZADA] == []
    
    def test_pendiente_validacion_tiene_transiciones(self):
        """PENDIENTE_VALIDACION debe tener al menos 2 transiciones."""
        transiciones = TRANSICIONES_VALIDAS[EstadoIncapacidadEnum.PENDIENTE_VALIDACION]
        assert len(transiciones) >= 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

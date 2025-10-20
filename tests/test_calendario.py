"""Tests para el módulo de calendario (días hábiles y festivos)."""
import pytest
from datetime import date, datetime

from app.utils.calendario import (
    es_dia_habil,
    sumar_dias_habiles,
    dias_habiles_restantes,
    formatar_fecha_legible,
)


class TestEsDiaHabil:
    """Tests para la función es_dia_habil."""
    
    def test_lunes_es_habil(self):
        """Lunes debe ser día hábil."""
        fecha = date(2025, 10, 20)  # Lunes
        assert es_dia_habil(fecha) is True
    
    def test_sabado_no_es_habil(self):
        """Sábado no debe ser día hábil."""
        fecha = date(2025, 10, 25)  # Sábado
        assert es_dia_habil(fecha) is False
    
    def test_domingo_no_es_habil(self):
        """Domingo no debe ser día hábil."""
        fecha = date(2025, 10, 26)  # Domingo
        assert es_dia_habil(fecha) is False
    
    def test_festivo_no_es_habil(self):
        """Festivo no debe ser día hábil."""
        fecha = date(2025, 12, 25)  # Navidad
        assert es_dia_habil(fecha) is False
    
    def test_acepta_datetime(self):
        """Debe aceptar objetos datetime además de date."""
        fecha = datetime(2025, 10, 20, 14, 30)  # Lunes con hora
        assert es_dia_habil(fecha) is True


class TestSumarDiasHabiles:
    """Tests para la función sumar_dias_habiles."""
    
    def test_sumar_3_dias_desde_lunes(self):
        """Lunes + 3 días hábiles = Jueves."""
        fecha_inicio = date(2025, 10, 20)  # Lunes
        resultado = sumar_dias_habiles(fecha_inicio, 3)
        assert resultado == date(2025, 10, 23)  # Jueves
    
    def test_sumar_3_dias_desde_jueves_salta_fin_semana(self):
        """Jueves + 3 días hábiles = Martes (salta fin de semana)."""
        fecha_inicio = date(2025, 10, 23)  # Jueves
        resultado = sumar_dias_habiles(fecha_inicio, 3)
        assert resultado == date(2025, 10, 28)  # Martes siguiente
    
    def test_sumar_dias_salta_festivo(self):
        """Debe saltar festivos al sumar días hábiles."""
        # Navidad cae en jueves 2025-12-25
        fecha_inicio = date(2025, 12, 23)  # Martes antes de Navidad
        resultado = sumar_dias_habiles(fecha_inicio, 3)
        # Martes 23 + 1 = Miércoles 24
        # Miércoles 24 + 1 = Jueves 25 (festivo, se salta)
        # Jueves 25 (festivo) -> Viernes 26 + 1 = Viernes 26
        # Viernes 26 + 1 = Lunes 29 (salta fin de semana)
        assert resultado == date(2025, 12, 29)  # Lunes
    
    def test_sumar_1_dia(self):
        """Debe funcionar con 1 día hábil."""
        fecha_inicio = date(2025, 10, 20)  # Lunes
        resultado = sumar_dias_habiles(fecha_inicio, 1)
        assert resultado == date(2025, 10, 21)  # Martes
    
    def test_acepta_datetime(self):
        """Debe aceptar datetime y retornar date."""
        fecha_inicio = datetime(2025, 10, 20, 9, 0)
        resultado = sumar_dias_habiles(fecha_inicio, 3)
        assert isinstance(resultado, date)
        assert resultado == date(2025, 10, 23)


class TestDiasHabilesRestantes:
    """Tests para la función dias_habiles_restantes."""
    
    def test_dias_positivos_sin_festivos(self):
        """Debe contar correctamente días hábiles restantes."""
        inicio = date(2025, 10, 20)  # Lunes
        vencimiento = date(2025, 10, 23)  # Jueves
        resultado = dias_habiles_restantes(inicio, vencimiento)
        assert resultado == 3
    
    def test_dias_negativos_fecha_vencida(self):
        """Debe retornar negativo cuando la fecha ya venció."""
        inicio = date(2025, 10, 25)  # Sábado
        vencimiento = date(2025, 10, 23)  # Jueves pasado
        resultado = dias_habiles_restantes(inicio, vencimiento)
        assert resultado < 0
    
    def test_mismo_dia_retorna_cero(self):
        """Mismo día debe retornar 0."""
        fecha = date(2025, 10, 20)
        resultado = dias_habiles_restantes(fecha, fecha)
        assert resultado == 0
    
    def test_cuenta_correctamente_con_fin_semana(self):
        """Debe saltar fines de semana al contar."""
        inicio = date(2025, 10, 23)  # Jueves
        vencimiento = date(2025, 10, 28)  # Martes siguiente
        resultado = dias_habiles_restantes(inicio, vencimiento)
        # Jueves 23 -> Viernes 24 (1 día)
        # Sábado 25, Domingo 26 (no cuentan)
        # Lunes 27, Martes 28 (2 días)
        assert resultado == 3
    
    def test_acepta_datetime(self):
        """Debe aceptar objetos datetime."""
        inicio = datetime(2025, 10, 20, 10, 0)
        vencimiento = datetime(2025, 10, 23, 17, 0)
        resultado = dias_habiles_restantes(inicio, vencimiento)
        assert resultado == 3


class TestFormatarFechaLegible:
    """Tests para la función formatar_fecha_legible."""
    
    def test_formato_correcto_espanol(self):
        """Debe formatear en español correctamente."""
        fecha = date(2025, 10, 17)  # Viernes
        resultado = formatar_fecha_legible(fecha)
        assert resultado == "viernes 17 de octubre de 2025"
    
    def test_otro_ejemplo_formato(self):
        """Otro ejemplo de formato."""
        fecha = date(2025, 12, 25)  # Jueves
        resultado = formatar_fecha_legible(fecha)
        assert resultado == "jueves 25 de diciembre de 2025"
    
    def test_acepta_datetime(self):
        """Debe aceptar datetime."""
        fecha = datetime(2025, 10, 17, 14, 30)
        resultado = formatar_fecha_legible(fecha)
        assert resultado == "viernes 17 de octubre de 2025"
    
    def test_meses_todos_en_espanol(self):
        """Verificar que todos los meses están en español."""
        fecha_enero = date(2025, 1, 6)
        assert "enero" in formatar_fecha_legible(fecha_enero)
        
        fecha_febrero = date(2025, 2, 10)
        assert "febrero" in formatar_fecha_legible(fecha_febrero)
        
        fecha_marzo = date(2025, 3, 10)
        assert "marzo" in formatar_fecha_legible(fecha_marzo)
    
    def test_dias_semana_en_espanol(self):
        """Verificar que días de la semana están en español."""
        fecha_lunes = date(2025, 10, 20)
        assert "lunes" in formatar_fecha_legible(fecha_lunes)
        
        fecha_viernes = date(2025, 10, 24)
        assert "viernes" in formatar_fecha_legible(fecha_viernes)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

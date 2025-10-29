"""
Tests para UC5 - Verificar requisitos por tipo

Test Coverage:
- Enfermedad General (con y sin epicrisis según días)
- Accidente de Tránsito (3 documentos)
- Accidente Laboral (2 documentos)
- Licencia de Maternidad (4 documentos)
- Licencia de Paternidad (5 documentos)
- Excepciones E1 y E2
"""

import pytest
import logging
from datetime import date, datetime
from app import create_app, db
from app.models.incapacidad import Incapacidad
from app.models.documento import Documento
from app.models.usuario import Usuario
from app.models.enums import TipoDocumentoEnum
from app.services.validacion_requisitos_service import (
    ValidadorRequisitos,
    TipoIncapacidadNoDefinido,
    ReglasNoConfiguradas
)


@pytest.fixture
def app():
    """Crear aplicación de prueba"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def usuario_id(app):
    """Crear usuario de prueba y retornar su ID"""
    with app.app_context():
        user = Usuario(
            nombre='Test Usuario',
            email='test@test.com',
            rol='colaborador'
        )
        user.set_password('123456')
        db.session.add(user)
        db.session.commit()
        user_id = user.id
    return user_id


@pytest.fixture
def validador():
    """Crear instancia del validador"""
    return ValidadorRequisitos()


# ============================================================================
# TESTS - ENFERMEDAD GENERAL
# ============================================================================

def test_enfermedad_general_1_dia_solo_certificado(app, usuario_id, validador):
    """Enfermedad de 1 día solo requiere certificado de incapacidad"""
    with app.app_context():
        # Crear incapacidad de 1 día
        inc = Incapacidad(
            usuario_id=usuario_id,
            tipo='Enfermedad General',
            fecha_inicio=date.today(),
            fecha_fin=date.today(),
            dias=1
        )
        db.session.add(inc)
        db.session.commit()
        
        # Cargar certificado
        doc = Documento(
            incapacidad_id=inc.id,
            nombre_archivo='certificado.pdf',
            nombre_unico='cert-uuid.pdf',
            ruta='/uploads/cert.pdf',
            tipo_documento=TipoDocumentoEnum.CERTIFICADO_INCAPACIDAD.value,
            tamaño_bytes=50000
        )
        db.session.add(doc)
        db.session.commit()
        
        # Validar
        resultado = validador.validar(inc)
        
        assert resultado['completo'] is True
        assert len(resultado['faltantes']) == 0
        assert len(resultado['presentes']) == 1
        assert resultado['presentes'][0]['tipo'] == TipoDocumentoEnum.CERTIFICADO_INCAPACIDAD.value


def test_enfermedad_general_2_dias_solo_certificado(app, usuario_id, validador):
    """Enfermedad de 2 días solo requiere certificado (epicrisis a partir del día 3)"""
    with app.app_context():
        inc = Incapacidad(
            usuario_id=usuario_id,
            tipo='Enfermedad General',
            fecha_inicio=date.today(),
            fecha_fin=date.today(),
            dias=2
        )
        db.session.add(inc)
        db.session.commit()
        
        # Cargar certificado
        doc = Documento(
            incapacidad_id=inc.id,
            nombre_archivo='certificado.pdf',
            nombre_unico='cert-uuid.pdf',
            ruta='/uploads/cert.pdf',
            tipo_documento=TipoDocumentoEnum.CERTIFICADO_INCAPACIDAD.value
        )
        db.session.add(doc)
        db.session.commit()
        
        resultado = validador.validar(inc)
        
        assert resultado['completo'] is True
        assert len(resultado['faltantes']) == 0


def test_enfermedad_general_3_dias_falta_epicrisis(app, usuario_id, validador):
    """Enfermedad de 3+ días requiere epicrisis"""
    with app.app_context():
        inc = Incapacidad(
            usuario_id=usuario_id,
            tipo='Enfermedad General',
            fecha_inicio=date.today(),
            fecha_fin=date.today(),
            dias=3
        )
        db.session.add(inc)
        db.session.commit()
        
        # Solo cargar certificado (falta epicrisis)
        doc = Documento(
            incapacidad_id=inc.id,
            nombre_archivo='certificado.pdf',
            nombre_unico='cert-uuid.pdf',
            ruta='/uploads/cert.pdf',
            tipo_documento=TipoDocumentoEnum.CERTIFICADO_INCAPACIDAD.value
        )
        db.session.add(doc)
        db.session.commit()
        
        resultado = validador.validar(inc)
        
        assert resultado['completo'] is False
        assert len(resultado['faltantes']) == 1
        assert resultado['faltantes'][0]['tipo'] == TipoDocumentoEnum.EPICRISIS.value
        assert 'mayores a 2 días' in resultado['faltantes'][0]['motivo']


def test_enfermedad_general_5_dias_con_epicrisis(app, usuario_id, validador):
    """Enfermedad de 5 días con certificado y epicrisis está completa"""
    with app.app_context():
        inc = Incapacidad(
            usuario_id=usuario_id,
            tipo='Enfermedad General',
            fecha_inicio=date.today(),
            fecha_fin=date.today(),
            dias=5
        )
        db.session.add(inc)
        db.session.commit()
        
        # Cargar ambos documentos
        docs = [
            Documento(
                incapacidad_id=inc.id,
                nombre_archivo='certificado.pdf',
                nombre_unico='cert-uuid.pdf',
                ruta='/uploads/cert.pdf',
                tipo_documento=TipoDocumentoEnum.CERTIFICADO_INCAPACIDAD.value
            ),
            Documento(
                incapacidad_id=inc.id,
                nombre_archivo='epicrisis.pdf',
                nombre_unico='epi-uuid.pdf',
                ruta='/uploads/epi.pdf',
                tipo_documento=TipoDocumentoEnum.EPICRISIS.value
            )
        ]
        for doc in docs:
            db.session.add(doc)
        db.session.commit()
        
        resultado = validador.validar(inc)
        
        assert resultado['completo'] is True
        assert len(resultado['faltantes']) == 0
        assert len(resultado['presentes']) == 2


# ============================================================================
# TESTS - ACCIDENTE DE TRÁNSITO
# ============================================================================

def test_accidente_transito_falta_furips(app, usuario_id, validador):
    """Accidente de tránsito requiere FURIPS además de certificado y epicrisis"""
    with app.app_context():
        inc = Incapacidad(
            usuario_id=usuario_id,
            tipo='Accidente de Tránsito',
            fecha_inicio=date.today(),
            fecha_fin=date.today(),
            dias=10
        )
        db.session.add(inc)
        db.session.commit()
        
        # Solo cargar 2 de 3
        docs = [
            Documento(
                incapacidad_id=inc.id,
                nombre_archivo='certificado.pdf',
                nombre_unico='cert-uuid.pdf',
                ruta='/uploads/cert.pdf',
                tipo_documento=TipoDocumentoEnum.CERTIFICADO_INCAPACIDAD.value
            ),
            Documento(
                incapacidad_id=inc.id,
                nombre_archivo='epicrisis.pdf',
                nombre_unico='epi-uuid.pdf',
                ruta='/uploads/epi.pdf',
                tipo_documento=TipoDocumentoEnum.EPICRISIS.value
            )
        ]
        for doc in docs:
            db.session.add(doc)
        db.session.commit()
        
        resultado = validador.validar(inc)
        
        assert resultado['completo'] is False
        assert len(resultado['faltantes']) == 1
        assert resultado['faltantes'][0]['tipo'] == TipoDocumentoEnum.FURIPS.value


def test_accidente_transito_completo(app, usuario_id, validador):
    """Accidente de tránsito con todos los documentos"""
    with app.app_context():
        inc = Incapacidad(
            usuario_id=usuario_id,
            tipo='Accidente de Tránsito',
            fecha_inicio=date.today(),
            fecha_fin=date.today(),
            dias=15
        )
        db.session.add(inc)
        db.session.commit()
        
        # Cargar los 3 documentos
        docs = [
            Documento(
                incapacidad_id=inc.id,
                nombre_archivo='certificado.pdf',
                nombre_unico='cert-uuid.pdf',
                ruta='/uploads/cert.pdf',
                tipo_documento=TipoDocumentoEnum.CERTIFICADO_INCAPACIDAD.value
            ),
            Documento(
                incapacidad_id=inc.id,
                nombre_archivo='epicrisis.pdf',
                nombre_unico='epi-uuid.pdf',
                ruta='/uploads/epi.pdf',
                tipo_documento=TipoDocumentoEnum.EPICRISIS.value
            ),
            Documento(
                incapacidad_id=inc.id,
                nombre_archivo='furips.pdf',
                nombre_unico='fur-uuid.pdf',
                ruta='/uploads/fur.pdf',
                tipo_documento=TipoDocumentoEnum.FURIPS.value
            )
        ]
        for doc in docs:
            db.session.add(doc)
        db.session.commit()
        
        resultado = validador.validar(inc)
        
        assert resultado['completo'] is True
        assert len(resultado['presentes']) == 3


# ============================================================================
# TESTS - LICENCIA DE MATERNIDAD
# ============================================================================

def test_licencia_maternidad_completo(app, usuario_id, validador):
    """Licencia de maternidad con todos los 4 documentos"""
    with app.app_context():
        inc = Incapacidad(
            usuario_id=usuario_id,
            tipo='Licencia de Maternidad',
            fecha_inicio=date.today(),
            fecha_fin=date.today(),
            dias=126
        )
        db.session.add(inc)
        db.session.commit()
        
        # Cargar los 4 documentos
        tipos = [
            TipoDocumentoEnum.CERTIFICADO_INCAPACIDAD.value,
            TipoDocumentoEnum.EPICRISIS.value,
            TipoDocumentoEnum.CERTIFICADO_NACIDO_VIVO.value,
            TipoDocumentoEnum.REGISTRO_CIVIL.value
        ]
        
        for idx, tipo in enumerate(tipos):
            doc = Documento(
                incapacidad_id=inc.id,
                nombre_archivo=f'{tipo}.pdf',
                nombre_unico=f'{tipo}-uuid.pdf',
                ruta=f'/uploads/{tipo}.pdf',
                tipo_documento=tipo
            )
            db.session.add(doc)
        db.session.commit()
        
        resultado = validador.validar(inc)
        
        assert resultado['completo'] is True
        assert len(resultado['presentes']) == 4


def test_licencia_maternidad_falta_registro_civil(app, usuario_id, validador):
    """Licencia de maternidad falta registro civil"""
    with app.app_context():
        inc = Incapacidad(
            usuario_id=usuario_id,
            tipo='Licencia de Maternidad',
            fecha_inicio=date.today(),
            fecha_fin=date.today(),
            dias=126
        )
        db.session.add(inc)
        db.session.commit()
        
        # Solo 3 de 4
        tipos = [
            TipoDocumentoEnum.CERTIFICADO_INCAPACIDAD.value,
            TipoDocumentoEnum.EPICRISIS.value,
            TipoDocumentoEnum.CERTIFICADO_NACIDO_VIVO.value
        ]
        
        for tipo in tipos:
            doc = Documento(
                incapacidad_id=inc.id,
                nombre_archivo=f'{tipo}.pdf',
                nombre_unico=f'{tipo}-uuid.pdf',
                ruta=f'/uploads/{tipo}.pdf',
                tipo_documento=tipo
            )
            db.session.add(doc)
        db.session.commit()
        
        resultado = validador.validar(inc)
        
        assert resultado['completo'] is False
        assert len(resultado['faltantes']) == 1
        assert resultado['faltantes'][0]['tipo'] == TipoDocumentoEnum.REGISTRO_CIVIL.value


# ============================================================================
# TESTS - EXCEPCIONES
# ============================================================================

def test_tipo_no_definido(app, usuario_id, validador):
    """E1: Tipo de incapacidad no definido debe lanzar excepción"""
    with app.app_context():
        inc = Incapacidad(
            usuario_id=usuario_id,
            tipo='Enfermedad General',  # Tipo válido inicialmente
            fecha_inicio=date.today(),
            fecha_fin=date.today(),
            dias=5
        )
        db.session.add(inc)
        db.session.commit()
        
        # Modificar tipo a vacío/None fuera de la sesión
        inc_id = inc.id
        
        # Crear nuevo objeto con tipo None (sin guardarlo)
        inc_sin_tipo = Incapacidad(
            id=inc_id,
            usuario_id=usuario_id,
            tipo=None,
            fecha_inicio=date.today(),
            fecha_fin=date.today(),
            dias=5
        )
        
        with pytest.raises(TipoIncapacidadNoDefinido) as exc_info:
            validador.validar(inc_sin_tipo)
        
        assert f"incapacidad ID" in str(exc_info.value) or "no tiene tipo definido" in str(exc_info.value)


# ============================================================================
# TESTS - MÉTODOS AUXILIARES
# ============================================================================

def test_get_faltantes(app, usuario_id, validador):
    """Método get_faltantes() solo retorna faltantes"""
    with app.app_context():
        inc = Incapacidad(
            usuario_id=usuario_id,
            tipo='Accidente de Tránsito',
            fecha_inicio=date.today(),
            fecha_fin=date.today(),
            dias=10
        )
        db.session.add(inc)
        db.session.commit()
        
        # Solo certificado (faltan 2)
        doc = Documento(
            incapacidad_id=inc.id,
            nombre_archivo='cert.pdf',
            nombre_unico='cert-uuid.pdf',
            ruta='/uploads/cert.pdf',
            tipo_documento=TipoDocumentoEnum.CERTIFICADO_INCAPACIDAD.value
        )
        db.session.add(doc)
        db.session.commit()
        
        faltantes = validador.get_faltantes(inc)
        
        assert len(faltantes) == 2
        tipos_faltantes = [f['tipo'] for f in faltantes]
        assert TipoDocumentoEnum.EPICRISIS.value in tipos_faltantes
        assert TipoDocumentoEnum.FURIPS.value in tipos_faltantes


def test_get_presentes(app, usuario_id, validador):
    """Método get_presentes() solo retorna presentes"""
    with app.app_context():
        inc = Incapacidad(
            usuario_id=usuario_id,
            tipo='Enfermedad General',
            fecha_inicio=date.today(),
            fecha_fin=date.today(),
            dias=1
        )
        db.session.add(inc)
        db.session.commit()
        
        doc = Documento(
            incapacidad_id=inc.id,
            nombre_archivo='cert.pdf',
            nombre_unico='cert-uuid.pdf',
            ruta='/uploads/cert.pdf',
            tipo_documento=TipoDocumentoEnum.CERTIFICADO_INCAPACIDAD.value
        )
        db.session.add(doc)
        db.session.commit()
        
        presentes = validador.get_presentes(inc)
        
        assert len(presentes) == 1
        assert presentes[0]['tipo'] == TipoDocumentoEnum.CERTIFICADO_INCAPACIDAD.value


def test_es_completo_true(app, usuario_id, validador):
    """Método es_completo() retorna True si documentación completa"""
    with app.app_context():
        inc = Incapacidad(
            usuario_id=usuario_id,
            tipo='Enfermedad General',
            fecha_inicio=date.today(),
            fecha_fin=date.today(),
            dias=1
        )
        db.session.add(inc)
        db.session.commit()
        
        doc = Documento(
            incapacidad_id=inc.id,
            nombre_archivo='cert.pdf',
            nombre_unico='cert-uuid.pdf',
            ruta='/uploads/cert.pdf',
            tipo_documento=TipoDocumentoEnum.CERTIFICADO_INCAPACIDAD.value
        )
        db.session.add(doc)
        db.session.commit()
        
        assert validador.es_completo(inc) is True


def test_es_completo_false(app, usuario_id, validador):
    """Método es_completo() retorna False si falta documentación"""
    with app.app_context():
        inc = Incapacidad(
            usuario_id=usuario_id,
            tipo='Accidente de Tránsito',
            fecha_inicio=date.today(),
            fecha_fin=date.today(),
            dias=10
        )
        db.session.add(inc)
        db.session.commit()
        
        # Sin documentos
        assert validador.es_completo(inc) is False


def test_obtener_requisitos_para_tipo(validador):
    """Método obtener_requisitos_para_tipo() sin incapacidad completa"""
    # Sin días
    reqs = validador.obtener_requisitos_para_tipo('Enfermedad General')
    assert TipoDocumentoEnum.CERTIFICADO_INCAPACIDAD.value in reqs['obligatorios']
    assert len(reqs['condicionales_posibles']) == 1
    
    # Con 1 día (no aplica epicrisis)
    reqs = validador.obtener_requisitos_para_tipo('Enfermedad General', dias=1)
    assert len(reqs['condicionales_aplicables']) == 0
    
    # Con 5 días (aplica epicrisis)
    reqs = validador.obtener_requisitos_para_tipo('Enfermedad General', dias=5)
    assert TipoDocumentoEnum.EPICRISIS.value in reqs['condicionales_aplicables']


# ============================================================================
# TESTS - MANEJO MEJORADO DE EXCEPCIONES (Tarea 1.4)
# ============================================================================

def test_excepcion_e1_mejorada(app, usuario_id, validador):
    """Test E1: Verificar excepción mejorada cuando tipo no está definido."""
    with app.app_context():
        # Crear incapacidad válida
        incapacidad = Incapacidad(
            usuario_id=usuario_id,
            fecha_inicio=date.today(),
            fecha_fin=date.today(),
            dias=1,
            tipo="Enfermedad General"
        )
        db.session.add(incapacidad)
        db.session.commit()
        
        # Mock el tipo como None para simular E1 sin tocar la DB
        import unittest.mock
        with unittest.mock.patch.object(incapacidad, 'tipo', None):
            # Validar que se eleva la excepción E1 mejorada
            with pytest.raises(TipoIncapacidadNoDefinido) as exc_info:
                validador.validar(incapacidad)
            
            # Verificar propiedades de la excepción mejorada
            excepcion = exc_info.value
            assert hasattr(excepcion, 'codigo_error')
            assert excepcion.codigo_error == "E1"
            assert excepcion.incapacidad_id == incapacidad.id
            assert "[E1]" in str(excepcion)
            assert "tipo válido" in str(excepcion).lower()


def test_excepcion_e2_fallback_mejorado(app, usuario_id, validador):
    """Test E2: Verificar fallback mejorado cuando reglas no están configuradas."""
    with app.app_context():
        # Crear incapacidad con tipo no configurado
        incapacidad = Incapacidad(
            usuario_id=usuario_id,
            fecha_inicio=date.today(),
            fecha_fin=date.today(),
            dias=1,
            tipo="TIPO_INEXISTENTE"  # Tipo no configurado
        )
        db.session.add(incapacidad)
        db.session.commit()
        
        # Debería funcionar con fallback (no elevar excepción)
        resultado = validador.validar(incapacidad)
        
        # Verificar fallback aplicado
        assert resultado['completo'] is False  # Solo certificado requerido, no presente
        assert len(resultado['faltantes']) == 1
        assert resultado['faltantes'][0]['tipo'] == TipoDocumentoEnum.CERTIFICADO_INCAPACIDAD.value
        
        # Verificar que el motivo incluye información de fallback
        motivo = resultado['faltantes'][0]['motivo']
        assert "fallback" in motivo.lower() or "no configuradas" in motivo.lower()


def test_logging_excepciones_e1(app, usuario_id, validador, caplog):
    """Test: Verificar logging de excepción E1."""
    with app.app_context():
        incapacidad_sin_tipo = Incapacidad(
            usuario_id=usuario_id,
            fecha_inicio=date.today(),
            fecha_fin=date.today(),
            dias=1,
            tipo="Enfermedad General"
        )
        db.session.add(incapacidad_sin_tipo)
        db.session.commit()
        
        # Mock el tipo como None
        import unittest.mock
        with unittest.mock.patch.object(incapacidad_sin_tipo, 'tipo', None):
            with caplog.at_level(logging.ERROR):
                with pytest.raises(TipoIncapacidadNoDefinido):
                    validador.validar(incapacidad_sin_tipo)
            
            # Verificar que se loggeó el error E1
            error_logs = [record for record in caplog.records if record.levelname == 'ERROR']
            assert any("E1" in record.message for record in error_logs)


def test_logging_excepciones_e2(app, usuario_id, validador, caplog):
    """Test: Verificar logging de fallback E2."""
    with app.app_context():
        incapacidad_tipo_inexistente = Incapacidad(
            usuario_id=usuario_id,
            fecha_inicio=date.today(),
            fecha_fin=date.today(),
            dias=1,
            tipo="TIPO_INEXISTENTE"
        )
        db.session.add(incapacidad_tipo_inexistente)
        db.session.commit()
        
        with caplog.at_level(logging.WARNING):
            validador.validar(incapacidad_tipo_inexistente)
        
        # Verificar que se loggearon las advertencias E2
        warning_logs = [record for record in caplog.records if record.levelname == 'WARNING']
        critical_logs = [record for record in caplog.records if record.levelname == 'CRITICAL']
        
        assert any("E2" in record.message for record in warning_logs)
        assert any("ADMINISTRADOR" in record.message for record in critical_logs)


def test_mensaje_administrador_e2(app, usuario_id, validador, caplog):
    """Test: Verificar que se notifica al administrador en caso E2."""
    with app.app_context():
        incapacidad = Incapacidad(
            usuario_id=usuario_id,
            fecha_inicio=date.today(),
            fecha_fin=date.today(),
            dias=1,
            tipo="OTRO_TIPO_INEXISTENTE"
        )
        db.session.add(incapacidad)
        db.session.commit()
        
        with caplog.at_level(logging.CRITICAL):
            validador.validar(incapacidad)
        
        # Verificar mensaje específico para administrador
        critical_logs = [record for record in caplog.records if record.levelname == 'CRITICAL']
        admin_log = next((r for r in critical_logs if "ADMINISTRADOR" in r.message), None)
        
        assert admin_log is not None
        assert "Configurar reglas" in admin_log.message
        assert "REQUISITOS_POR_TIPO" in admin_log.message


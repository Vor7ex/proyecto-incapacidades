"""Tests para el servicio de solicitud de documentos."""
import pytest
from datetime import datetime, date, timedelta
from unittest.mock import MagicMock, patch

from app import create_app, db
from app.models.documento import Documento
from app.models.enums import (
    EstadoIncapacidadEnum,
    EstadoSolicitudDocumentoEnum,
    TipoDocumentoEnum,
)
from app.models.incapacidad import Incapacidad
from app.models.solicitud_documento import SolicitudDocumento
from app.models.usuario import Usuario
from app.services.solicitud_documentos_service import SolicitudDocumentosService


@pytest.fixture
def app():
    """Crear aplicación de prueba."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def datos_prueba(app):
    """Crear todos los datos de prueba en un solo fixture."""
    with app.app_context():
        # Crear usuarios
        auxiliar = Usuario(
            nombre='Auxiliar Test',
            email='auxiliar@test.com',
            rol='auxiliar'
        )
        auxiliar.set_password('123456')
        
        colaborador = Usuario(
            nombre='Colaborador Test',
            email='colaborador@test.com',
            rol='colaborador'
        )
        colaborador.set_password('123456')
        
        db.session.add(auxiliar)
        db.session.add(colaborador)
        db.session.commit()
        
        # Crear incapacidad
        incapacidad = Incapacidad(
            usuario_id=colaborador.id,
            codigo_radicacion='INC-20251019-TEST',
            tipo='Enfermedad General',
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=3),
            dias=3,
            estado=EstadoIncapacidadEnum.PENDIENTE_VALIDACION.value
        )
        db.session.add(incapacidad)
        db.session.commit()
        
        # Retornar IDs para recuperar en cada test
        return {
            'auxiliar_id': auxiliar.id,
            'colaborador_id': colaborador.id,
            'incapacidad_id': incapacidad.id
        }


class TestCrearSolicitudDocumentos:
    """Tests para crear_solicitud_documentos."""
    
    def test_crear_solicitud_valida(self, app, datos_prueba):
        """Debe crear solicitud correctamente con precondiciones válidas."""
        with app.app_context():
            # Recuperar objetos del contexto actual
            auxiliar = Usuario.query.get(datos_prueba['auxiliar_id'])
            incapacidad = Incapacidad.query.get(datos_prueba['incapacidad_id'])
            
            documentos = [TipoDocumentoEnum.EPICRISIS.value, TipoDocumentoEnum.FURIPS.value]
            observaciones = {
                TipoDocumentoEnum.EPICRISIS.value: "Documento ilegible",
                TipoDocumentoEnum.FURIPS.value: "Falta información"
            }
            
            exito, mensaje, solicitudes = SolicitudDocumentosService.crear_solicitud_documentos(
                incapacidad_id=incapacidad.id,
                documentos_a_solicitar=documentos,
                observaciones_por_tipo=observaciones,
                usuario_auxiliar=auxiliar
            )
            
            assert exito is True
            assert "exitosamente" in mensaje
            assert solicitudes is not None
            assert len(solicitudes) == 2
            
            # Verificar que se crearon en BD
            solicitudes_bd = SolicitudDocumento.query.filter_by(incapacidad_id=incapacidad.id).all()
            assert len(solicitudes_bd) == 2
            
            # Verificar estado de incapacidad
            incapacidad = Incapacidad.query.get(incapacidad.id)
            assert incapacidad.estado == EstadoIncapacidadEnum.DOCUMENTACION_INCOMPLETA.value
    
    def test_crear_solicitud_sin_permisos(self, app, datos_prueba):
        """Debe rechazar si el usuario no es auxiliar."""
        with app.app_context():
            colaborador = Usuario.query.get(datos_prueba['colaborador_id'])
            incapacidad = Incapacidad.query.get(datos_prueba['incapacidad_id'])
            
            exito, mensaje, solicitudes = SolicitudDocumentosService.crear_solicitud_documentos(
                incapacidad_id=incapacidad.id,
                documentos_a_solicitar=[TipoDocumentoEnum.EPICRISIS.value],
                observaciones_por_tipo={},
                usuario_auxiliar=colaborador
            )
            
            assert exito is False
            assert "Solo auxiliares" in mensaje
            assert solicitudes is None
    
    def test_crear_solicitud_incapacidad_no_existe(self, app, datos_prueba):
        """Debe rechazar si la incapacidad no existe."""
        with app.app_context():
            auxiliar = Usuario.query.get(datos_prueba['auxiliar_id'])
            
            exito, mensaje, solicitudes = SolicitudDocumentosService.crear_solicitud_documentos(
                incapacidad_id=99999,
                documentos_a_solicitar=[TipoDocumentoEnum.EPICRISIS.value],
                observaciones_por_tipo={},
                usuario_auxiliar=auxiliar
            )
            
            assert exito is False
            assert "no encontrada" in mensaje
            assert solicitudes is None
    
    def test_crear_solicitud_estado_invalido(self, app, datos_prueba):
        """Debe rechazar si incapacidad no está en PENDIENTE_VALIDACION."""
        with app.app_context():
            auxiliar = Usuario.query.get(datos_prueba['auxiliar_id'])
            incapacidad = Incapacidad.query.get(datos_prueba['incapacidad_id'])
            
            # Cambiar estado
            incapacidad.estado = EstadoIncapacidadEnum.APROBADA_PENDIENTE_TRANSCRIPCION.value
            db.session.commit()
            
            exito, mensaje, solicitudes = SolicitudDocumentosService.crear_solicitud_documentos(
                incapacidad_id=incapacidad.id,
                documentos_a_solicitar=[TipoDocumentoEnum.EPICRISIS.value],
                observaciones_por_tipo={},
                usuario_auxiliar=auxiliar
            )
            
            assert exito is False
            assert "PENDIENTE_VALIDACION" in mensaje
            assert solicitudes is None
    
    def test_crear_solicitud_sin_documentos(self, app, datos_prueba):
        """Debe rechazar si no se especifican documentos."""
        with app.app_context():
            auxiliar = Usuario.query.get(datos_prueba['auxiliar_id'])
            incapacidad = Incapacidad.query.get(datos_prueba['incapacidad_id'])
            
            exito, mensaje, solicitudes = SolicitudDocumentosService.crear_solicitud_documentos(
                incapacidad_id=incapacidad.id,
                documentos_a_solicitar=[],
                observaciones_por_tipo={},
                usuario_auxiliar=auxiliar
            )
            
            assert exito is False
            assert "al menos un documento" in mensaje
            assert solicitudes is None


class TestValidarRespuestaColaborador:
    """Tests para validar_respuesta_colaborador."""
    
    def test_validar_todos_documentos_entregados(self, app, datos_prueba):
        """Debe marcar solicitudes como entregadas cuando se entregan todos."""
        with app.app_context():
            auxiliar = Usuario.query.get(datos_prueba['auxiliar_id'])
            incapacidad = Incapacidad.query.get(datos_prueba['incapacidad_id'])
            
            # Crear solicitudes
            SolicitudDocumentosService.crear_solicitud_documentos(
                incapacidad_id=incapacidad.id,
                documentos_a_solicitar=[TipoDocumentoEnum.EPICRISIS.value],
                observaciones_por_tipo={},
                usuario_auxiliar=auxiliar
            )
            
            # Crear documentos entregados
            doc = Documento(
                incapacidad_id=incapacidad.id,
                nombre_archivo='epicrisis.pdf',
                nombre_unico='epic_unique.pdf',
                ruta='/uploads/epic.pdf',
                tipo_documento=TipoDocumentoEnum.EPICRISIS.value,
                tamaño_bytes=1024,
                mime_type='application/pdf'
            )
            db.session.add(doc)
            db.session.commit()
            
            # Validar respuesta
            completo, errores, pendientes = SolicitudDocumentosService.validar_respuesta_colaborador(
                incapacidad_id=incapacidad.id,
                documentos_entregados=[doc]
            )
            
            assert completo is True
            assert len(errores) == 0
            assert len(pendientes) == 0
            
            # Verificar estado
            incapacidad = Incapacidad.query.get(incapacidad.id)
            assert incapacidad.estado == EstadoIncapacidadEnum.PENDIENTE_VALIDACION.value
    
    def test_validar_documentos_parciales(self, app, datos_prueba):
        """Debe mantener solicitudes pendientes si faltan documentos."""
        with app.app_context():
            auxiliar = Usuario.query.get(datos_prueba['auxiliar_id'])
            incapacidad = Incapacidad.query.get(datos_prueba['incapacidad_id'])
            
            # Crear 2 solicitudes
            SolicitudDocumentosService.crear_solicitud_documentos(
                incapacidad_id=incapacidad.id,
                documentos_a_solicitar=[
                    TipoDocumentoEnum.EPICRISIS.value,
                    TipoDocumentoEnum.FURIPS.value
                ],
                observaciones_por_tipo={},
                usuario_auxiliar=auxiliar
            )
            
            # Entregar solo 1 documento
            doc = Documento(
                incapacidad_id=incapacidad.id,
                nombre_archivo='epicrisis.pdf',
                nombre_unico='epic_unique.pdf',
                ruta='/uploads/epic.pdf',
                tipo_documento=TipoDocumentoEnum.EPICRISIS.value,
                tamaño_bytes=1024,
                mime_type='application/pdf'
            )
            db.session.add(doc)
            db.session.commit()
            
            # Validar respuesta
            completo, errores, pendientes = SolicitudDocumentosService.validar_respuesta_colaborador(
                incapacidad_id=incapacidad.id,
                documentos_entregados=[doc]
            )
            
            assert completo is False
            assert len(errores) == 0
            assert len(pendientes) == 1
            assert pendientes[0].tipo_documento == TipoDocumentoEnum.FURIPS.value
    
    def test_validar_documento_tamano_invalido(self, app, datos_prueba):
        """Debe rechazar documentos que exceden 10MB."""
        with app.app_context():
            auxiliar = Usuario.query.get(datos_prueba['auxiliar_id'])
            incapacidad = Incapacidad.query.get(datos_prueba['incapacidad_id'])
            
            SolicitudDocumentosService.crear_solicitud_documentos(
                incapacidad_id=incapacidad.id,
                documentos_a_solicitar=[TipoDocumentoEnum.EPICRISIS.value],
                observaciones_por_tipo={},
                usuario_auxiliar=auxiliar
            )
            
            # Documento muy grande
            doc = Documento(
                incapacidad_id=incapacidad.id,
                nombre_archivo='epicrisis.pdf',
                nombre_unico='epic_unique.pdf',
                ruta='/uploads/epic.pdf',
                tipo_documento=TipoDocumentoEnum.EPICRISIS.value,
                tamaño_bytes=11 * 1024 * 1024,  # 11MB
                mime_type='application/pdf'
            )
            db.session.add(doc)
            db.session.commit()
            
            # Validar respuesta
            completo, errores, pendientes = SolicitudDocumentosService.validar_respuesta_colaborador(
                incapacidad_id=incapacidad.id,
                documentos_entregados=[doc]
            )
            
            assert completo is False
            assert len(errores) > 0
            assert "10MB" in errores[0]


class TestProcesarRecordatorios:
    """Tests para procesar_recordatorios."""
    
    def test_recordatorio_dia_vencimiento(self, app, datos_prueba):
        """Debe enviar primer recordatorio el día de vencimiento."""
        with app.app_context():
            incapacidad = Incapacidad.query.get(datos_prueba['incapacidad_id'])
            
            # Crear solicitud con vencimiento hoy
            solicitud = SolicitudDocumento(
                incapacidad_id=incapacidad.id,
                tipo_documento=TipoDocumentoEnum.EPICRISIS.value,
                estado=EstadoSolicitudDocumentoEnum.PENDIENTE.value,
                fecha_solicitud=datetime.utcnow() - timedelta(days=3),
                fecha_vencimiento=datetime.utcnow(),  # Vence hoy
                observaciones_auxiliar="Test",
                intentos_notificacion=0
            )
            db.session.add(solicitud)
            db.session.commit()
            
            # Procesar recordatorios
            stats = SolicitudDocumentosService.procesar_recordatorios()
            
            assert stats['recordatorios_dia2'] == 1
            
            # Verificar que se actualizó la solicitud
            solicitud = SolicitudDocumento.query.get(solicitud.id)
            assert solicitud.intentos_notificacion == 1
    
    def test_recordatorio_urgente_3_dias(self, app, datos_prueba):
        """Debe enviar segunda notificación después de 1-3 días."""
        with app.app_context():
            incapacidad = Incapacidad.query.get(datos_prueba['incapacidad_id'])
            
            # Crear solicitud vencida hace 2 días
            solicitud = SolicitudDocumento(
                incapacidad_id=incapacidad.id,
                tipo_documento=TipoDocumentoEnum.EPICRISIS.value,
                estado=EstadoSolicitudDocumentoEnum.PENDIENTE.value,
                fecha_solicitud=datetime.utcnow() - timedelta(days=5),
                fecha_vencimiento=datetime.utcnow() - timedelta(days=2),
                observaciones_auxiliar="Test",
                intentos_notificacion=1,
                numero_reintentos=0
            )
            db.session.add(solicitud)
            db.session.commit()
            
            # Procesar recordatorios
            stats = SolicitudDocumentosService.procesar_recordatorios()
            
            assert stats['recordatorios_urgentes'] == 1
            
            # Verificar actualización
            solicitud = SolicitudDocumento.query.get(solicitud.id)
            assert solicitud.numero_reintentos == 1
    
    def test_requiere_citacion_despues_6_dias(self, app, datos_prueba):
        """Debe marcar como requiere citación después de 6 días."""
        with app.app_context():
            incapacidad = Incapacidad.query.get(datos_prueba['incapacidad_id'])
            
            # Crear solicitud vencida hace 7 días
            solicitud = SolicitudDocumento(
                incapacidad_id=incapacidad.id,
                tipo_documento=TipoDocumentoEnum.EPICRISIS.value,
                estado=EstadoSolicitudDocumentoEnum.PENDIENTE.value,
                fecha_solicitud=datetime.utcnow() - timedelta(days=10),
                fecha_vencimiento=datetime.utcnow() - timedelta(days=7),
                observaciones_auxiliar="Test",
                intentos_notificacion=2,
                numero_reintentos=1
            )
            db.session.add(solicitud)
            db.session.commit()
            
            # Procesar recordatorios
            stats = SolicitudDocumentosService.procesar_recordatorios()
            
            assert stats['requieren_citacion'] == 1
            
            # Verificar estado
            solicitud = SolicitudDocumento.query.get(solicitud.id)
            assert solicitud.estado == EstadoSolicitudDocumentoEnum.REQUIERE_CITACION.value


class TestPermitirExtensionPlazo:
    """Tests para permitir_extension_plazo."""
    
    def test_extension_plazo_valida(self, app, datos_prueba):
        """Debe extender plazo correctamente."""
        with app.app_context():
            auxiliar = Usuario.query.get(datos_prueba['auxiliar_id'])
            incapacidad = Incapacidad.query.get(datos_prueba['incapacidad_id'])
            
            # Crear solicitud
            solicitud = SolicitudDocumento(
                incapacidad_id=incapacidad.id,
                tipo_documento=TipoDocumentoEnum.EPICRISIS.value,
                estado=EstadoSolicitudDocumentoEnum.PENDIENTE.value,
                fecha_solicitud=datetime.utcnow(),
                fecha_vencimiento=datetime.utcnow() + timedelta(days=1),
                observaciones_auxiliar="Test",
                extension_solicitada=False
            )
            db.session.add(solicitud)
            db.session.commit()
            
            fecha_venc_original = solicitud.fecha_vencimiento
            
            # Extender plazo
            exito, mensaje = SolicitudDocumentosService.permitir_extension_plazo(
                solicitud_documento_id=solicitud.id,
                motivo_extension="Problemas de salud del colaborador",
                usuario_auxiliar=auxiliar
            )
            
            assert exito is True
            assert "extendido" in mensaje
            
            # Verificar extensión
            solicitud = SolicitudDocumento.query.get(solicitud.id)
            assert solicitud.extension_solicitada is True
            assert solicitud.fecha_vencimiento > fecha_venc_original
            assert solicitud.motivo_extension == "Problemas de salud del colaborador"
    
    def test_extension_plazo_sin_permisos(self, app, datos_prueba):
        """Debe rechazar si el usuario no es auxiliar."""
        with app.app_context():
            colaborador = Usuario.query.get(datos_prueba['colaborador_id'])
            incapacidad = Incapacidad.query.get(datos_prueba['incapacidad_id'])
            
            solicitud = SolicitudDocumento(
                incapacidad_id=incapacidad.id,
                tipo_documento=TipoDocumentoEnum.EPICRISIS.value,
                estado=EstadoSolicitudDocumentoEnum.PENDIENTE.value,
                fecha_solicitud=datetime.utcnow(),
                fecha_vencimiento=datetime.utcnow() + timedelta(days=1),
                extension_solicitada=False
            )
            db.session.add(solicitud)
            db.session.commit()
            
            exito, mensaje = SolicitudDocumentosService.permitir_extension_plazo(
                solicitud_documento_id=solicitud.id,
                motivo_extension="Test",
                usuario_auxiliar=colaborador
            )
            
            assert exito is False
            assert "Solo auxiliares" in mensaje
    
    def test_extension_plazo_ya_extendida(self, app, datos_prueba):
        """Debe rechazar si ya tiene una extensión previa."""
        with app.app_context():
            auxiliar = Usuario.query.get(datos_prueba['auxiliar_id'])
            incapacidad = Incapacidad.query.get(datos_prueba['incapacidad_id'])
            
            solicitud = SolicitudDocumento(
                incapacidad_id=incapacidad.id,
                tipo_documento=TipoDocumentoEnum.EPICRISIS.value,
                estado=EstadoSolicitudDocumentoEnum.PENDIENTE.value,
                fecha_solicitud=datetime.utcnow(),
                fecha_vencimiento=datetime.utcnow() + timedelta(days=1),
                extension_solicitada=True  # Ya extendida
            )
            db.session.add(solicitud)
            db.session.commit()
            
            exito, mensaje = SolicitudDocumentosService.permitir_extension_plazo(
                solicitud_documento_id=solicitud.id,
                motivo_extension="Test",
                usuario_auxiliar=auxiliar
            )
            
            assert exito is False
            assert "extensión previa" in mensaje


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

"""Tests para notificaciones UC6 - Solicitud de Documentos."""
import unittest
from unittest.mock import patch, MagicMock, call
from datetime import datetime, timedelta

from app import create_app, db
from app.models.usuario import Usuario
from app.models.incapacidad import Incapacidad
from app.models.solicitud_documento import SolicitudDocumento
from app.models.enums import (
    EstadoIncapacidadEnum,
    EstadoSolicitudDocumentoEnum,
    TipoDocumentoEnum,
)
from app.utils.email_service import (
    notificar_solicitud_documentos,
    notificar_recordatorio_documentos,
    notificar_documentacion_completada,
)


class TestNotificacionesUC6(unittest.TestCase):
    """Tests para notificaciones de UC6."""

    def setUp(self):
        """Configuración inicial de cada test."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['MAIL_ENABLED'] = True  # Habilitar emails para tests
        self.app.config['SERVER_NAME'] = 'localhost:5000'  # Necesario para url_for en templates
        
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        
        db.create_all()
        self._crear_datos_prueba()

    def tearDown(self):
        """Limpieza después de cada test."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _crear_datos_prueba(self):
        """Crea datos de prueba para los tests."""
        # Generar emails únicos para evitar conflictos entre tests
        import uuid
        test_id = str(uuid.uuid4())[:8]
        
        # Usuario colaborador
        self.colaborador = Usuario(
            nombre='Juan Pérez',
            email=f'juan.perez.{test_id}@empresa.com',
            rol='colaborador'
        )
        self.colaborador.set_password('password123')
        
        # Usuario auxiliar
        self.auxiliar = Usuario(
            nombre='María López',
            email=f'maria.lopez.{test_id}@empresa.com',
            rol='auxiliar'
        )
        self.auxiliar.set_password('password123')
        
        db.session.add_all([self.colaborador, self.auxiliar])
        db.session.commit()
        
        # Incapacidad de prueba
        self.incapacidad = Incapacidad(
            usuario_id=self.colaborador.id,
            tipo='Enfermedad General',
            fecha_inicio=datetime.utcnow().date(),
            fecha_fin=datetime.utcnow().date() + timedelta(days=5),
            dias=5,
            estado=EstadoIncapacidadEnum.DOCUMENTACION_INCOMPLETA.value,
            codigo_radicacion=f'INC-2024-{test_id}'
        )
        db.session.add(self.incapacidad)
        db.session.commit()
        
        # Solicitudes de documentos
        fecha_vencimiento = datetime.utcnow() + timedelta(days=3)
        
        self.solicitud1 = SolicitudDocumento(
            incapacidad_id=self.incapacidad.id,
            tipo_documento=TipoDocumentoEnum.EPICRISIS.value,
            estado=EstadoSolicitudDocumentoEnum.PENDIENTE.value,
            fecha_vencimiento=fecha_vencimiento,
            observaciones_auxiliar='Falta epicrisis completa'
        )
        
        self.solicitud2 = SolicitudDocumento(
            incapacidad_id=self.incapacidad.id,
            tipo_documento=TipoDocumentoEnum.FURIPS.value,
            estado=EstadoSolicitudDocumentoEnum.PENDIENTE.value,
            fecha_vencimiento=fecha_vencimiento,
            observaciones_auxiliar='Requerimos FURIPS'
        )
        
        db.session.add_all([self.solicitud1, self.solicitud2])
        db.session.commit()

    @patch('app.utils.email_service.send_email')
    def test_notificar_solicitud_documentos_enviada(self, mock_send_email):
        """Test 1: Verifica que se envíe la notificación inicial de solicitud."""
        mock_send_email.return_value = True
        
        # Ejecutar
        solicitudes = [self.solicitud1, self.solicitud2]
        resultado = notificar_solicitud_documentos(
            incapacidad=self.incapacidad,
            solicitudes=solicitudes,
            usuario_auxiliar=self.auxiliar
        )
        
        # Verificar
        self.assertTrue(resultado, "Debe retornar True si el email se envió")
        mock_send_email.assert_called_once()
        
        # Verificar argumentos del email
        args, kwargs = mock_send_email.call_args
        self.assertIn('Documentos faltantes', kwargs['subject'])
        self.assertIn(self.incapacidad.codigo_radicacion, kwargs['subject'])
        self.assertIn(self.colaborador.email, kwargs['recipients'])
        self.assertIsNotNone(kwargs['html_body'])

    @patch('app.utils.email_service.send_email')
    def test_notificar_solicitud_incluye_lista_documentos(self, mock_send_email):
        """Test 2: Verifica que el email incluya la lista de documentos solicitados."""
        mock_send_email.return_value = True
        
        # Ejecutar
        solicitudes = [self.solicitud1, self.solicitud2]
        notificar_solicitud_documentos(
            incapacidad=self.incapacidad,
            solicitudes=solicitudes,
            usuario_auxiliar=self.auxiliar
        )
        
        # Obtener el HTML generado
        args, kwargs = mock_send_email.call_args
        html_body = kwargs['html_body']
        
        # Verificar que contiene información de documentos
        self.assertIn('Epicrisis', html_body)
        self.assertIn('Furips', html_body)
        self.assertIn(self.incapacidad.codigo_radicacion, html_body)
        self.assertIn(self.colaborador.nombre, html_body)

    @patch('app.utils.email_service.send_email')
    def test_notificar_recordatorio_tono_urgente(self, mock_send_email):
        """Test 3: Verifica que el primer recordatorio tenga tono urgente."""
        mock_send_email.return_value = True
        
        # Ejecutar recordatorio #1 (día antes)
        solicitudes_pendientes = [self.solicitud1, self.solicitud2]
        resultado = notificar_recordatorio_documentos(
            incapacidad=self.incapacidad,
            numero_recordatorio=1,
            solicitudes_pendientes=solicitudes_pendientes
        )
        
        # Verificar
        self.assertTrue(resultado)
        mock_send_email.assert_called_once()
        
        # Verificar asunto urgente
        args, kwargs = mock_send_email.call_args
        self.assertIn('RECORDATORIO', kwargs['subject'])
        self.assertIn(self.incapacidad.codigo_radicacion, kwargs['subject'])
        
        # Verificar contenido
        html_body = kwargs['html_body']
        self.assertIn('MAÑANA', html_body.upper())

    @patch('app.utils.email_service.send_email')
    def test_segunda_notificacion_muy_urgente(self, mock_send_email):
        """Test 4: Verifica que la segunda notificación sea MUY urgente."""
        mock_send_email.return_value = True
        
        # Ejecutar recordatorio #2 (vencido)
        solicitudes_pendientes = [self.solicitud1]
        resultado = notificar_recordatorio_documentos(
            incapacidad=self.incapacidad,
            numero_recordatorio=2,
            solicitudes_pendientes=solicitudes_pendientes
        )
        
        # Verificar
        self.assertTrue(resultado)
        mock_send_email.assert_called_once()
        
        # Verificar asunto MUY urgente
        args, kwargs = mock_send_email.call_args
        self.assertIn('URGENTE', kwargs['subject'])
        
        # Verificar contenido crítico
        html_body = kwargs['html_body']
        self.assertIn('VENCIDO', html_body.upper())
        self.assertIn('SEGUNDA', html_body.upper())

    @patch('app.utils.email_service.send_email')
    def test_notificar_documentacion_completada_auxiliar(self, mock_send_email):
        """Test 5: Verifica que se notifique al auxiliar cuando se completa la documentación."""
        mock_send_email.return_value = True
        
        # Ejecutar
        resultado = notificar_documentacion_completada(
            incapacidad=self.incapacidad,
            email_auxiliar=self.auxiliar.email
        )
        
        # Verificar
        self.assertTrue(resultado)
        mock_send_email.assert_called_once()
        
        # Verificar destinatario correcto (auxiliar, no colaborador)
        args, kwargs = mock_send_email.call_args
        self.assertIn(self.auxiliar.email, kwargs['recipients'])
        self.assertNotIn(self.colaborador.email, kwargs['recipients'])
        
        # Verificar asunto
        self.assertIn('completada', kwargs['subject'].lower())
        self.assertIn(self.incapacidad.codigo_radicacion, kwargs['subject'])
        
        # Verificar contenido
        html_body = kwargs['html_body']
        self.assertIn(self.colaborador.nombre, html_body)
        self.assertIn(self.incapacidad.codigo_radicacion, html_body)

    @patch('app.utils.email_service.send_email')
    def test_actualiza_ultima_notificacion_en_solicitud(self, mock_send_email):
        """Test 6: Verifica que se actualice ultima_notificacion en las solicitudes."""
        mock_send_email.return_value = True
        
        # Verificar estado inicial
        self.assertIsNone(self.solicitud1.ultima_notificacion)
        
        # Ejecutar
        solicitudes = [self.solicitud1, self.solicitud2]
        notificar_solicitud_documentos(
            incapacidad=self.incapacidad,
            solicitudes=solicitudes,
            usuario_auxiliar=self.auxiliar
        )
        
        # Hacer commit para persistir los cambios
        db.session.commit()
        
        # Verificar que se actualizó
        db.session.refresh(self.solicitud1)
        db.session.refresh(self.solicitud2)
        
        self.assertIsNotNone(self.solicitud1.ultima_notificacion)
        self.assertIsNotNone(self.solicitud2.ultima_notificacion)
        
        # Verificar que es una fecha reciente (últimos 5 segundos)
        ahora = datetime.utcnow()
        diferencia = ahora - self.solicitud1.ultima_notificacion
        self.assertLess(diferencia.total_seconds(), 5)

    @patch('app.utils.email_service.send_email')
    def test_mail_enabled_false_simula_envio(self, mock_send_email):
        """Test 7: Verifica que con MAIL_ENABLED=False se simule el envío."""
        # Configurar MAIL_ENABLED = False
        self.app.config['MAIL_ENABLED'] = False
        
        # Ejecutar
        solicitudes = [self.solicitud1]
        resultado = notificar_solicitud_documentos(
            incapacidad=self.incapacidad,
            solicitudes=solicitudes,
            usuario_auxiliar=self.auxiliar
        )
        
        # Verificar que retorna True (simulado)
        self.assertTrue(resultado)
        
        # Verificar que NO se llamó send_email
        mock_send_email.assert_not_called()

    @patch('app.utils.email_service.send_email')
    def test_error_en_envio_retorna_false(self, mock_send_email):
        """Test 8: Verifica que si falla el envío, se retorne False."""
        # Simular error en envío
        mock_send_email.return_value = False
        
        # Ejecutar
        solicitudes = [self.solicitud1]
        resultado = notificar_solicitud_documentos(
            incapacidad=self.incapacidad,
            solicitudes=solicitudes,
            usuario_auxiliar=self.auxiliar
        )
        
        # Verificar
        self.assertFalse(resultado, "Debe retornar False si el email falló")

    @patch('app.utils.email_service.send_email')
    @patch('app.utils.email_service.logger')
    def test_logging_correcto_en_notificaciones(self, mock_logger, mock_send_email):
        """Test 9: Verifica que se logueen correctamente las notificaciones."""
        mock_send_email.return_value = True
        
        # Ejecutar
        solicitudes = [self.solicitud1]
        notificar_solicitud_documentos(
            incapacidad=self.incapacidad,
            solicitudes=solicitudes,
            usuario_auxiliar=self.auxiliar
        )
        
        # Verificar que se logueó
        self.assertTrue(mock_logger.info.called)
        
        # Verificar que el log contiene información relevante
        log_calls = [str(call) for call in mock_logger.info.call_args_list]
        log_text = ' '.join(log_calls)
        
        self.assertIn('UC6', log_text)
        self.assertIn(str(self.incapacidad.id), log_text)


if __name__ == '__main__':
    unittest.main()

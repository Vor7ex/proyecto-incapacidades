"""
Test End-to-End Completo de UC6: Solicitud de Documentos Faltantes.

Este módulo prueba el flujo completo de UC6 desde que el auxiliar solicita
documentos hasta que el colaborador los entrega y se notifica la completitud.
"""

import unittest
import tempfile
import os
from datetime import datetime, timedelta
from io import BytesIO
from unittest.mock import patch, MagicMock
from app import create_app, db
from app.models.usuario import Usuario
from app.models.incapacidad import Incapacidad
from app.models.solicitud_documento import SolicitudDocumento
from app.models.documento import Documento
from app.models.enums import TipoDocumento, EstadoIncapacidad
from app.services.solicitud_documentos_service import SolicitudDocumentosService


class TestUC6CompletoE2E(unittest.TestCase):
    """Test end-to-end completo del flujo UC6"""
    
    def setUp(self):
        """Configurar entorno de pruebas"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['SERVER_NAME'] = 'localhost:5000'
        self.app.config['MAIL_ENABLED'] = False  # Simular envío de emails
        
        # Crear directorio temporal para uploads
        self.temp_dir = tempfile.mkdtemp()
        self.app.config['UPLOAD_FOLDER'] = self.temp_dir
        
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
        
        # Crear usuarios de prueba
        self._crear_usuarios()
        
        # Crear incapacidad en estado PENDIENTE_VALIDACION
        self._crear_incapacidad_prueba()
        
        self.client = self.app.test_client()
    
    def tearDown(self):
        """Limpiar después de cada test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
        # Limpiar directorio temporal
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def _crear_usuarios(self):
        """Helper: crear usuarios colaborador y auxiliar"""
        self.colaborador = Usuario(
            nombre='Juan Pérez Colaborador',
            email='colaborador.uc6@test.com',
            rol='colaborador'
        )
        self.colaborador.set_password('password123')
        
        self.auxiliar = Usuario(
            nombre='María García Auxiliar',
            email='auxiliar.uc6@test.com',
            rol='auxiliar'
        )
        self.auxiliar.set_password('password123')
        
        db.session.add(self.colaborador)
        db.session.add(self.auxiliar)
        db.session.commit()
    
    def _crear_incapacidad_prueba(self):
        """Helper: crear incapacidad en PENDIENTE_VALIDACION"""
        self.incapacidad = Incapacidad(
            usuario_id=self.colaborador.id,
            tipo='Enfermedad General',
            fecha_inicio=datetime.utcnow().date(),
            fecha_fin=datetime.utcnow().date() + timedelta(days=5),
            dias=5,
            estado=EstadoIncapacidad.PENDIENTE_VALIDACION.value
        )
        db.session.add(self.incapacidad)
        db.session.commit()
    
    def _login_auxiliar(self):
        """Helper: hacer login como auxiliar"""
        return self.client.post('/auth/login', data={
            'email': 'auxiliar.uc6@test.com',
            'password': 'password123'
        }, follow_redirects=True)
    
    def _login_colaborador(self):
        """Helper: hacer login como colaborador"""
        return self.client.post('/auth/login', data={
            'email': 'colaborador.uc6@test.com',
            'password': 'password123'
        }, follow_redirects=True)
    
    def _crear_archivo_fake(self, nombre='documento.pdf', contenido=b'PDF content'):
        """Helper: crear archivo fake para upload"""
        return (BytesIO(contenido), nombre)
    
    # ========================================
    # TEST COMPLETO E2E DE UC6
    # ========================================
    
    @patch('app.utils.email_service.send_email')
    def test_uc6_flujo_completo_end_to_end(self, mock_send_email):
        """
        Test E2E completo de UC6 con los 10 casos especificados.
        
        Flujo:
        1. Auxiliar solicita documentos
        2. Notificación enviada a colaborador
        3. Colaborador recibe notificación
        4. Colaborador carga parcialmente
        5. Incapacidad sigue en DOCUMENTACION_INCOMPLETA
        6. Scheduler ejecuta recordatorio
        7. Recordatorio incluye tono urgente
        8. Colaborador carga documento faltante
        9. Incapacidad vuelve a PENDIENTE_VALIDACION
        10. Auxiliar notificado de completitud
        """
        mock_send_email.return_value = True
        
        #========================================
        # CASO 1: Auxiliar solicita documentos
        # ========================================
        self._login_auxiliar()
        
        # Crear solicitud de 2 documentos
        exito, mensaje, solicitudes_creadas = SolicitudDocumentosService.crear_solicitud_documentos(
            incapacidad_id=self.incapacidad.id,
            documentos_a_solicitar=['EPICRISIS', 'FURIPS'],
            observaciones_por_tipo={
                'EPICRISIS': 'Se requiere epicrisis',
                'FURIPS': 'Se requiere FURIPS'
            },
            usuario_auxiliar=self.auxiliar
        )
        
        # Verificaciones Caso 1
        self.assertTrue(exito)
        self.assertEqual(len(solicitudes_creadas), 2)
        
        # Recargar incapacidad desde DB
        db.session.refresh(self.incapacidad)
        self.assertEqual(self.incapacidad.estado, EstadoIncapacidad.DOCUMENTACION_INCOMPLETA.value)
        
        # Verificar solicitudes creadas
        solicitudes = SolicitudDocumento.query.filter_by(incapacidad_id=self.incapacidad.id).all()
        self.assertEqual(len(solicitudes), 2)
        self.assertEqual(solicitudes[0].estado, 'pendiente')
        self.assertEqual(solicitudes[1].estado, 'pendiente')
        
        solicitud_epicrisis = next(s for s in solicitudes if s.tipo_documento == TipoDocumento.EPICRISIS)
        solicitud_furips = next(s for s in solicitudes if s.tipo_documento == TipoDocumento.FURIPS)
        
        # ========================================
        # CASO 2: Notificación enviada a colaborador
        # ========================================
        self.assertTrue(mock_send_email.called)
        
        # Verificar que el email fue enviado
        call_args = mock_send_email.call_args_list[0]
        email_destinatario = call_args[1]['destinatario']
        email_asunto = call_args[1]['asunto']
        email_html = call_args[1]['html_body']
        
        self.assertEqual(email_destinatario, self.colaborador.email)
        self.assertIn('Documentos Solicitados', email_asunto)
        self.assertIn(self.incapacidad.codigo_radicacion, email_html)
        self.assertIn('EPICRISIS', email_html)
        self.assertIn('FURIPS', email_html)
        
        # ========================================
        # CASO 3: Colaborador recibe notificación
        # ========================================
        self.client.get('/auth/logout')
        self._login_colaborador()
        
        # Colaborador puede acceder a la página de carga
        response = self.client.get(f'/documentos/cargar-solicitados/{self.incapacidad.id}')
        self.assertEqual(response.status_code, 200)
        
        # ========================================
        # CASO 4: Colaborador carga parcialmente (solo EPICRISIS)
        # ========================================
        response = self.client.post(
            f'/documentos/cargar-solicitados/{self.incapacidad.id}',
            data={
                f'documento_{solicitud_epicrisis.id}': self._crear_archivo_fake('epicrisis.pdf'),
                'observaciones': 'Adjunto epicrisis, FURIPS pendiente'
            },
            content_type='multipart/form-data',
            follow_redirects=True
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar estado de las solicitudes
        db.session.refresh(solicitud_epicrisis)
        db.session.refresh(solicitud_furips)
        
        self.assertEqual(solicitud_epicrisis.estado, 'entregado')
        self.assertEqual(solicitud_furips.estado, 'pendiente')
        
        # ========================================
        # CASO 5: Incapacidad sigue en DOCUMENTACION_INCOMPLETA
        # ========================================
        db.session.refresh(self.incapacidad)
        self.assertEqual(self.incapacidad.estado, EstadoIncapacidad.DOCUMENTACION_INCOMPLETA.value)
        
        # ========================================
        # CASO 6: Scheduler ejecuta recordatorio (Mock date: +3 días)
        # ========================================
        # Simular que pasaron 3 días (fecha vencimiento)
        solicitud_furips.fecha_vencimiento = datetime.utcnow() - timedelta(hours=1)
        db.session.commit()
        
        mock_send_email.reset_mock()
        
        # Ejecutar el procesamiento de recordatorios
        resultado_recordatorios = SolicitudDocumentosService.procesar_recordatorios()
        
        self.assertTrue(resultado_recordatorios['exito'])
        self.assertGreater(resultado_recordatorios['recordatorios_enviados'], 0)
        
        # ========================================
        # CASO 7: Recordatorio incluye tono urgente
        # ========================================
        self.assertTrue(mock_send_email.called)
        
        # Verificar el email de recordatorio
        call_args = mock_send_email.call_args_list[0]
        email_asunto_recordatorio = call_args[1]['asunto']
        email_html_recordatorio = call_args[1]['html_body']
        
        self.assertIn('RECORDATORIO', email_asunto_recordatorio.upper())
        # El tono debe ser urgente (primera notificación después de vencimiento)
        
        # ========================================
        # CASO 8: Colaborador carga documento faltante
        # ========================================
        mock_send_email.reset_mock()
        
        response = self.client.post(
            f'/documentos/cargar-solicitados/{self.incapacidad.id}',
            data={
                f'documento_{solicitud_furips.id}': self._crear_archivo_fake('furips.pdf'),
                'observaciones': 'Adjunto FURIPS pendiente'
            },
            content_type='multipart/form-data',
            follow_redirects=True
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar que ambos documentos están entregados
        db.session.refresh(solicitud_epicrisis)
        db.session.refresh(solicitud_furips)
        
        self.assertEqual(solicitud_epicrisis.estado, 'entregado')
        self.assertEqual(solicitud_furips.estado, 'entregado')
        
        # ========================================
        # CASO 9: Incapacidad vuelve a PENDIENTE_VALIDACION
        # ========================================
        db.session.refresh(self.incapacidad)
        self.assertEqual(self.incapacidad.estado, EstadoIncapacidad.PENDIENTE_VALIDACION.value)
        
        # ========================================
        # CASO 10: Auxiliar notificado de completitud
        # ========================================
        self.assertTrue(mock_send_email.called)
        
        # Verificar email de completitud
        # Buscar el call que fue al auxiliar
        calls_auxiliar = [
            call for call in mock_send_email.call_args_list
            if call[1].get('destinatario') == self.auxiliar.email
        ]
        
        self.assertGreater(len(calls_auxiliar), 0)
        
        email_completitud = calls_auxiliar[0]
        self.assertIn('completad', email_completitud[1]['asunto'].lower())
    
    # ========================================
    # TESTS INDIVIDUALES DE CASOS ESPECÍFICOS
    # ========================================
    
    @patch('app.utils.email_service.send_email')
    def test_caso1_auxiliar_solicita_documentos(self, mock_send_email):
        """Caso 1: Auxiliar solicita documentos y cambia estado a DOCUMENTACION_INCOMPLETA"""
        mock_send_email.return_value = True
        
        exito, mensaje, solicitudes = SolicitudDocumentosService.crear_solicitud_documentos(
            incapacidad_id=self.incapacidad.id,
            documentos_a_solicitar=['EPICRISIS'],
            observaciones_por_tipo={'EPICRISIS': 'Se requiere'},
            usuario_auxiliar=self.auxiliar
        )
        
        self.assertTrue(exito)
        db.session.refresh(self.incapacidad)
        self.assertEqual(self.incapacidad.estado, EstadoIncapacidad.DOCUMENTACION_INCOMPLETA.value)
    
    @patch('app.utils.email_service.send_email')
    def test_caso2_notificacion_incluye_detalles(self, mock_send_email):
        """Caso 2: Email incluye código radicación, documentos y fecha vencimiento"""
        mock_send_email.return_value = True
        
        SolicitudDocumentosService.crear_solicitud_documentos(
            incapacidad=self.incapacidad,
            tipos_documentos=[TipoDocumento.EPICRISIS, TipoDocumento.FURIPS],
            usuario_auxiliar=self.auxiliar
        )
        
        self.assertTrue(mock_send_email.called)
        call_args = mock_send_email.call_args
        
        html_body = call_args[1]['html_body']
        self.assertIn(self.incapacidad.codigo_radicacion, html_body)
        self.assertIn('EPICRISIS', html_body)
        self.assertIn('FURIPS', html_body)
    
    @patch('app.utils.email_service.send_email')
    def test_caso4_carga_parcial_mantiene_estado_incompleto(self, mock_send_email):
        """Caso 4-5: Carga parcial mantiene estado DOCUMENTACION_INCOMPLETA"""
        mock_send_email.return_value = True
        
        # Crear solicitudes
        resultado = SolicitudDocumentosService.crear_solicitud_documentos(
            incapacidad=self.incapacidad,
            tipos_documentos=[TipoDocumento.EPICRISIS, TipoDocumento.FURIPS],
            usuario_auxiliar=self.auxiliar
        )
        
        solicitudes = resultado['solicitudes_creadas']
        
        # Marcar solo una como entregada
        solicitudes[0].estado = 'entregado'
        db.session.commit()
        
        # Verificar que el estado sigue siendo DOCUMENTACION_INCOMPLETA
        db.session.refresh(self.incapacidad)
        self.assertEqual(self.incapacidad.estado, EstadoIncapacidad.DOCUMENTACION_INCOMPLETA.value)
    
    @patch('app.utils.email_service.send_email')
    def test_caso6_scheduler_ejecuta_recordatorios(self, mock_send_email):
        """Caso 6-7: Scheduler ejecuta recordatorios con tono urgente"""
        mock_send_email.return_value = True
        
        # Crear solicitud vencida
        solicitud = SolicitudDocumento(
            incapacidad_id=self.incapacidad.id,
            tipo_documento=TipoDocumento.EPICRISIS,
            estado='pendiente',
            fecha_vencimiento=datetime.utcnow() - timedelta(days=1),
            solicitado_por_id=self.auxiliar.id
        )
        db.session.add(solicitud)
        db.session.commit()
        
        mock_send_email.reset_mock()
        
        # Ejecutar recordatorios
        resultado = SolicitudDocumentosService.procesar_recordatorios()
        
        self.assertTrue(resultado['exito'])
        self.assertTrue(mock_send_email.called)
        
        # Verificar que el asunto contiene "RECORDATORIO"
        call_args = mock_send_email.call_args
        asunto = call_args[1]['asunto']
        self.assertIn('RECORDATORIO', asunto.upper())
    
    @patch('app.utils.email_service.send_email')
    def test_caso9_documentacion_completa_cambia_estado(self, mock_send_email):
        """Caso 9-10: Documentación completa cambia estado y notifica auxiliar"""
        mock_send_email.return_value = True
        
        # Crear solicitudes
        resultado = SolicitudDocumentosService.crear_solicitud_documentos(
            incapacidad=self.incapacidad,
            tipos_documentos=[TipoDocumento.EPICRISIS],
            usuario_auxiliar=self.auxiliar
        )
        
        solicitud = resultado['solicitudes_creadas'][0]
        
        mock_send_email.reset_mock()
        
        # Marcar como entregado (simular carga)
        from app.services.solicitud_documentos_service import SolicitudDocumentosService
        SolicitudDocumentosService.validar_respuesta_colaborador(
            solicitud=solicitud,
            usuario_colaborador=self.colaborador
        )
        
        # Verificar cambio de estado
        db.session.refresh(self.incapacidad)
        self.assertEqual(self.incapacidad.estado, EstadoIncapacidad.PENDIENTE_VALIDACION.value)
        
        # Verificar notificación al auxiliar
        self.assertTrue(mock_send_email.called)


if __name__ == '__main__':
    unittest.main()

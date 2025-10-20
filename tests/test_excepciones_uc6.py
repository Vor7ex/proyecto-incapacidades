"""
Test de Excepciones de UC6: Solicitud de Documentos Faltantes.

Este módulo prueba los flujos alternos y excepciones (E1-E4) del caso de uso UC6.
"""

import unittest
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import patch
from app import create_app, db
from app.models.usuario import Usuario
from app.models.incapacidad import Incapacidad
from app.models.solicitud_documento import SolicitudDocumento
from app.models.enums import TipoDocumento, EstadoIncapacidad
from app.services.solicitud_documentos_service import SolicitudDocumentosService


class TestExcepcionesUC6(unittest.TestCase):
    """Test de flujos alternos y excepciones de UC6"""
    
    def setUp(self):
        """Configurar entorno de pruebas"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['SERVER_NAME'] = 'localhost:5000'
        self.app.config['MAIL_ENABLED'] = False
        
        # Crear directorio temporal para uploads
        self.temp_dir = tempfile.mkdtemp()
        self.app.config['UPLOAD_FOLDER'] = self.temp_dir
        
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
        
        # Crear usuarios de prueba
        self._crear_usuarios()
        
        # Crear incapacidad base
        self._crear_incapacidad_prueba()
    
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
            nombre='Carlos Rodríguez',
            email='colaborador.exc@test.com',
            rol='colaborador'
        )
        self.colaborador.set_password('password123')
        
        self.auxiliar = Usuario(
            nombre='Ana Martínez',
            email='auxiliar.exc@test.com',
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
    
    # ========================================
    # E1: Colaborador no responde en 3 días
    # ========================================
    
    @patch('app.utils.email_service.send_email')
    def test_e1_colaborador_no_responde_tres_dias(self, mock_send_email):
        """
        E1: Colaborador no responde en 3 días hábiles.
        
        Flujo:
        1. Solicitud creada (día 0)
        2. +3 días sin respuesta → vencimiento
        3. Scheduler ejecuta y envía primer recordatorio
        4. +3 días más sin respuesta → 6 días total
        5. Scheduler envía segunda notificación (muy urgente)
        6. Solicitud marcada como 'requiere_citacion'
        """
        mock_send_email.return_value = True
        
        # Crear solicitud
        resultado = SolicitudDocumentosService.crear_solicitud_documentos(
            incapacidad=self.incapacidad,
            tipos_documentos=[TipoDocumento.EPICRISIS],
            usuario_auxiliar=self.auxiliar
        )
        
        solicitud = resultado['solicitudes_creadas'][0]
        
        # Simular día 3: vencimiento
        solicitud.fecha_vencimiento = datetime.utcnow() - timedelta(hours=1)
        solicitud.ultima_notificacion = datetime.utcnow() - timedelta(days=3)
        db.session.commit()
        
        mock_send_email.reset_mock()
        
        # Ejecutar recordatorios (día 3)
        resultado_r1 = SolicitudDocumentosService.procesar_recordatorios()
        
        self.assertTrue(resultado_r1['exito'])
        self.assertEqual(mock_send_email.call_count, 1)  # Primer recordatorio
        
        # Verificar que fue recordatorio de día 2-3
        call_args = mock_send_email.call_args
        asunto = call_args[1]['asunto']
        self.assertIn('RECORDATORIO', asunto.upper())
        
        # Simular día 6: segunda notificación
        solicitud.fecha_vencimiento = datetime.utcnow() - timedelta(days=3)
        solicitud.ultima_notificacion = datetime.utcnow() - timedelta(days=3)
        db.session.commit()
        
        mock_send_email.reset_mock()
        
        # Ejecutar recordatorios (día 6)
        resultado_r2 = SolicitudDocumentosService.procesar_recordatorios()
        
        self.assertTrue(resultado_r2['exito'])
        self.assertEqual(mock_send_email.call_count, 1)  # Segunda notificación
        
        # Verificar tono muy urgente
        call_args = mock_send_email.call_args
        asunto = call_args[1]['asunto']
        html = call_args[1]['html_body']
        self.assertIn('URGENTE', asunto.upper())
        
        # Verificar que se marcó como requiere citación
        db.session.refresh(solicitud)
        self.assertEqual(solicitud.estado, 'requiere_citacion')
    
    # ========================================
    # E2: Documentos incompletos nuevamente
    # ========================================
    
    @patch('app.utils.email_service.send_email')
    def test_e2_documentos_incompletos_nuevamente(self, mock_send_email):
        """
        E2: Colaborador carga documentos pero auxiliar nota deficiencias.
        
        Flujo:
        1. Colaborador carga documentos
        2. Auxiliar valida y encuentra problemas
        3. Auxiliar puede reiniciar UC6 con nueva solicitud
        4. Nuevo plazo de 3 días hábiles
        """
        mock_send_email.return_value = True
        
        # Primera solicitud
        resultado1 = SolicitudDocumentosService.crear_solicitud_documentos(
            incapacidad=self.incapacidad,
            tipos_documentos=[TipoDocumento.EPICRISIS],
            usuario_auxiliar=self.auxiliar,
            observaciones='Primera solicitud'
        )
        
        solicitud1 = resultado1['solicitudes_creadas'][0]
        
        # Colaborador "carga" documento (marcar como entregado)
        solicitud1.estado = 'entregado'
        solicitud1.fecha_entrega = datetime.utcnow()
        db.session.commit()
        
        # Auxiliar valida y encuentra problemas
        # Incapacidad volvió a PENDIENTE_VALIDACION
        db.session.refresh(self.incapacidad)
        
        # Auxiliar reinicia UC6 (nueva solicitud)
        mock_send_email.reset_mock()
        
        resultado2 = SolicitudDocumentosService.crear_solicitud_documentos(
            incapacidad=self.incapacidad,
            tipos_documentos=[TipoDocumento.EPICRISIS],
            usuario_auxiliar=self.auxiliar,
            observaciones='Documento anterior tenía problemas, por favor volver a adjuntar'
        )
        
        solicitud2 = resultado2['solicitudes_creadas'][0]
        
        # Verificar nueva solicitud
        self.assertTrue(resultado2['exito'])
        self.assertNotEqual(solicitud1.id, solicitud2.id)
        self.assertEqual(solicitud2.estado, 'pendiente')
        
        # Verificar nuevo plazo (3 días hábiles desde ahora)
        diferencia = solicitud2.fecha_vencimiento - datetime.utcnow()
        self.assertGreater(diferencia.days, 0)
        self.assertLessEqual(diferencia.days, 5)  # Máximo 5 días calendario para 3 días hábiles
        
        # Verificar notificación enviada
        self.assertTrue(mock_send_email.called)
        call_args = mock_send_email.call_args
        observaciones = call_args[1]['html_body']
        self.assertIn('problemas', observaciones.lower())
    
    # ========================================
    # E3: Segunda notificación sin respuesta
    # ========================================
    
    @patch('app.utils.email_service.send_email')
    def test_e3_segunda_notificacion_sin_respuesta(self, mock_send_email):
        """
        E3: Segunda notificación sin respuesta → Requiere citación.
        
        Flujo:
        1. Primera solicitud sin respuesta (día 0-3)
        2. Primer recordatorio (día 3)
        3. Sin respuesta hasta día 6
        4. Segunda notificación muy urgente
        5. Estado → "requiere_citacion"
        6. Coordinación debe ser notificada (fuera de scope actual)
        """
        mock_send_email.return_value = True
        
        # Crear solicitud
        resultado = SolicitudDocumentosService.crear_solicitud_documentos(
            incapacidad=self.incapacidad,
            tipos_documentos=[TipoDocumento.FURIPS],
            usuario_auxiliar=self.auxiliar
        )
        
        solicitud = resultado['solicitudes_creadas'][0]
        
        # Simular +6 días sin respuesta (muy vencido)
        solicitud.fecha_vencimiento = datetime.utcnow() - timedelta(days=3)
        solicitud.ultima_notificacion = datetime.utcnow() - timedelta(days=3)
        solicitud.numero_recordatorios = 1  # Ya se envió un recordatorio antes
        db.session.commit()
        
        mock_send_email.reset_mock()
        
        # Ejecutar procesamiento de recordatorios
        resultado_proc = SolicitudDocumentosService.procesar_recordatorios()
        
        self.assertTrue(resultado_proc['exito'])
        
        # Verificar que se envió segunda notificación
        self.assertTrue(mock_send_email.called)
        
        # Verificar estado cambió a requiere_citacion
        db.session.refresh(solicitud)
        self.assertEqual(solicitud.estado, 'requiere_citacion')
        
        # Verificar número de recordatorios incrementó
        self.assertEqual(solicitud.numero_recordatorios, 2)
    
    # ========================================
    # E4: Colaborador solicita extensión
    # ========================================
    
    @patch('app.utils.email_service.send_email')
    def test_e4_colaborador_solicita_extension(self, mock_send_email):
        """
        E4: Colaborador solicita extensión de plazo (funcionalidad básica).
        
        Flujo:
        1. Colaborador tiene solicitud pendiente
        2. Antes de vencimiento: solicita extensión (simulado con observaciones)
        3. Auxiliar aprueba: actualiza fecha_vencimiento +3 días
        4. Colaborador es notificado de nueva fecha
        
        Nota: Este test simula la extensión manualmente ya que la funcionalidad
        completa de solicitud de extensión está fuera del scope de UC6 básico.
        """
        mock_send_email.return_value = True
        
        # Crear solicitud
        resultado = SolicitudDocumentosService.crear_solicitud_documentos(
            incapacidad=self.incapacidad,
            tipos_documentos=[TipoDocumento.HISTORIA_CLINICA],
            usuario_auxiliar=self.auxiliar
        )
        
        solicitud = resultado['solicitudes_creadas'][0]
        fecha_vencimiento_original = solicitud.fecha_vencimiento
        
        # Simular solicitud de extensión (campo de observaciones)
        # En una implementación real, habría un endpoint específico
        solicitud.observaciones_colaborador = 'Solicito extensión de 3 días, estoy esperando el documento del hospital'
        db.session.commit()
        
        # Auxiliar aprueba extensión (manualmente en este test)
        nueva_fecha_vencimiento = fecha_vencimiento_original + timedelta(days=3)
        solicitud.fecha_vencimiento = nueva_fecha_vencimiento
        solicitud.observaciones_auxiliar = 'Extensión aprobada por 3 días adicionales'
        db.session.commit()
        
        # Verificar que la fecha se extendió
        db.session.refresh(solicitud)
        self.assertGreater(solicitud.fecha_vencimiento, fecha_vencimiento_original)
        
        # Simular notificación al colaborador (en implementación real sería automática)
        from app.utils.email_service import notificar_solicitud_documentos
        
        mock_send_email.reset_mock()
        
        # En una implementación real, habría una función específica para notificar extensión
        # Por ahora verificamos que se puede re-notificar
        resultado_notif = notificar_solicitud_documentos(
            incapacidad=self.incapacidad,
            solicitudes=[solicitud],
            usuario_auxiliar=self.auxiliar
        )
        
        self.assertTrue(resultado_notif)
        self.assertTrue(mock_send_email.called)
    
    # ========================================
    # TEST ADICIONAL: Múltiples solicitudes concurrentes
    # ========================================
    
    @patch('app.utils.email_service.send_email')
    def test_multiples_solicitudes_diferentes_estados(self, mock_send_email):
        """
        Test adicional: Múltiples solicitudes en diferentes estados.
        
        Verifica que el sistema maneja correctamente múltiples solicitudes
        con diferentes estados y plazos.
        """
        mock_send_email.return_value = True
        
        # Crear múltiples solicitudes
        resultado = SolicitudDocumentosService.crear_solicitud_documentos(
            incapacidad=self.incapacidad,
            tipos_documentos=[
                TipoDocumento.EPICRISIS,
                TipoDocumento.FURIPS,
                TipoDocumento.HISTORIA_CLINICA
            ],
            usuario_auxiliar=self.auxiliar
        )
        
        solicitudes = resultado['solicitudes_creadas']
        self.assertEqual(len(solicitudes), 3)
        
        # Simular diferentes estados:
        # 1. EPICRISIS: entregado
        solicitudes[0].estado = 'entregado'
        solicitudes[0].fecha_entrega = datetime.utcnow()
        
        # 2. FURIPS: vencido (requiere recordatorio)
        solicitudes[1].fecha_vencimiento = datetime.utcnow() - timedelta(days=1)
        solicitudes[1].ultima_notificacion = datetime.utcnow() - timedelta(days=3)
        
        # 3. HISTORIA_CLINICA: pendiente (aún dentro de plazo)
        solicitudes[2].fecha_vencimiento = datetime.utcnow() + timedelta(days=2)
        
        db.session.commit()
        
        mock_send_email.reset_mock()
        
        # Ejecutar recordatorios
        resultado_proc = SolicitudDocumentosService.procesar_recordatorios()
        
        self.assertTrue(resultado_proc['exito'])
        
        # Verificar que solo se envió recordatorio para FURIPS (la vencida)
        # EPICRISIS ya está entregada, HISTORIA_CLINICA aún tiene tiempo
        self.assertEqual(mock_send_email.call_count, 1)
        
        # Verificar estados finales
        db.session.refresh(solicitudes[0])
        db.session.refresh(solicitudes[1])
        db.session.refresh(solicitudes[2])
        
        self.assertEqual(solicitudes[0].estado, 'entregado')
        self.assertEqual(solicitudes[1].estado, 'pendiente')  # Aún pendiente, solo recordatorio
        self.assertEqual(solicitudes[2].estado, 'pendiente')


if __name__ == '__main__':
    unittest.main()

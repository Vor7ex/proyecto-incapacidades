"""
Tests para UC2 - Notificar a líder y Gestión Humana
Cubre flujo normal y excepciones E1-E4

Autor: Sistema de Gestión de Incapacidades
Fecha: 2024
"""
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, call
import re

from app import create_app, db
from app.models.usuario import Usuario
from app.models.incapacidad import Incapacidad
from app.models.notificacion import Notificacion
from app.models.enums import TipoNotificacionEnum, EstadoNotificacionEnum
from app.utils.email_service import (
    get_usuarios_gestion_humana,
    crear_notificacion_interna,
    marcar_notificacion_enviada,
    marcar_notificacion_entregada,
    send_email,
    notificar_nueva_incapacidad
)
from config import Config


class TestUC2Notificaciones(unittest.TestCase):
    """Tests para UC2 - Notificar a líder y Gestión Humana"""
    
    def setUp(self):
        """Configurar ambiente de prueba"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['MAIL_ENABLED'] = False  # Desactivar envío real
        self.app.config['WTF_CSRF_ENABLED'] = False
        
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Crear tablas
        db.create_all()
        
        # Crear usuarios de prueba
        self.colaborador = Usuario(
            nombre='Juan Pérez',
            email='juan.perez@test.com',
            email_notificaciones='juan.notif@test.com',
            rol='colaborador'
        )
        self.colaborador.set_password('123456')
        db.session.add(self.colaborador)
        
        self.auxiliar = Usuario(
            nombre='Ana García',
            email='ana.garcia@test.com',
            email_notificaciones='ana.notif@test.com',
            rol='auxiliar'
        )
        self.auxiliar.set_password('123456')
        db.session.add(self.auxiliar)
        
        db.session.commit()
    
    def tearDown(self):
        """Limpiar ambiente de prueba"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def crear_incapacidad_prueba(self):
        """Helper: Crea incapacidad de prueba"""
        incapacidad = Incapacidad(
            usuario_id=self.colaborador.id,
            tipo='Enfermedad General',
            fecha_inicio=datetime.utcnow().date(),
            fecha_fin=(datetime.utcnow() + timedelta(days=3)).date(),
            dias=3,
            codigo_radicacion='INC-20241107-0001',
            estado='PENDIENTE_VALIDACION'
        )
        db.session.add(incapacidad)
        db.session.commit()
        return incapacidad
    
    # =========================================================================
    # UC2: Funciones Auxiliares
    # =========================================================================
    
    def test_get_usuarios_gestion_humana_encontrados(self):
        """Test: Debe retornar usuarios con rol auxiliar/gestion_humana"""
        usuarios = get_usuarios_gestion_humana()
        
        self.assertEqual(len(usuarios), 1)
        self.assertEqual(usuarios[0].email, 'ana.garcia@test.com')
        self.assertEqual(usuarios[0].rol, 'auxiliar')
    
    def test_get_usuarios_gestion_humana_vacio(self):
        """Test: Debe retornar lista vacía si no hay usuarios RRHH"""
        # Eliminar auxiliar
        db.session.delete(self.auxiliar)
        db.session.commit()
        
        usuarios = get_usuarios_gestion_humana()
        
        self.assertEqual(len(usuarios), 0)
    
    def test_crear_notificacion_interna_exitosa(self):
        """UC2 (pasos 6-7): Debe crear notificación interna en BD"""
        notif = crear_notificacion_interna(
            tipo=TipoNotificacionEnum.REGISTRO_INCAPACIDAD,
            destinatario_id=self.colaborador.id,
            asunto='Test notificación',
            contenido='<p>Contenido HTML</p>'
        )
        
        self.assertIsNotNone(notif)
        self.assertEqual(notif.tipo, TipoNotificacionEnum.REGISTRO_INCAPACIDAD.value)
        self.assertEqual(notif.destinatario_id, self.colaborador.id)
        self.assertEqual(notif.asunto, 'Test notificación')
        self.assertEqual(notif.estado, EstadoNotificacionEnum.PENDIENTE.value)
    
    def test_marcar_notificacion_enviada(self):
        """UC2 (paso 9): Debe actualizar estado a ENVIADA"""
        notif = crear_notificacion_interna(
            tipo='TEST',
            destinatario_id=self.colaborador.id,
            asunto='Test',
            contenido='Test'
        )
        db.session.commit()
        
        resultado = marcar_notificacion_enviada(notif.id)
        
        self.assertTrue(resultado)
        notif_actualizada = Notificacion.query.get(notif.id)
        self.assertEqual(notif_actualizada.estado, EstadoNotificacionEnum.ENVIADA.value)
    
    def test_marcar_notificacion_entregada(self):
        """UC2 (paso 9): Debe actualizar estado a ENTREGADA"""
        notif = crear_notificacion_interna(
            tipo='TEST',
            destinatario_id=self.colaborador.id,
            asunto='Test',
            contenido='Test'
        )
        db.session.commit()
        
        resultado = marcar_notificacion_entregada(notif.id)
        
        self.assertTrue(resultado)
        notif_actualizada = Notificacion.query.get(notif.id)
        self.assertEqual(notif_actualizada.estado, EstadoNotificacionEnum.ENTREGADA.value)
    
    # =========================================================================
    # UC2-E2: Email Inválido
    # =========================================================================
    
    def test_e2_email_invalido_crea_solo_notificacion_interna(self):
        """UC2-E2: Si email es inválido, solo crea notificación interna"""
        with self.app.app_context():
            resultado = send_email(
                subject='Test',
                recipients=['email-invalido'],  # Sin @
                html_body='<p>Test</p>',
                crear_notificacion=True,
                tipo_notificacion='TEST',
                destinatario_id=self.colaborador.id
            )
            
            # Email no debe enviarse pero notificación sí debe crearse
            self.assertFalse(resultado['email_ok'])
            self.assertIsNotNone(resultado['notificacion_id'])
            
            # Verificar que la notificación existe en BD
            notif = Notificacion.query.get(resultado['notificacion_id'])
            self.assertIsNotNone(notif)
            self.assertEqual(notif.destinatario_id, self.colaborador.id)
    
    def test_e2_email_valido_crea_email_y_notificacion(self):
        """UC2-E2: Si email es válido, crea ambos"""
        with self.app.app_context():
            resultado = send_email(
                subject='Test',
                recipients=['usuario@dominio.com'],
                html_body='<p>Test</p>',
                crear_notificacion=True,
                tipo_notificacion='TEST',
                destinatario_id=self.colaborador.id
            )
            
            # Ambos deben crearse
            self.assertTrue(resultado['email_ok'])
            self.assertIsNotNone(resultado['notificacion_id'])
    
    # =========================================================================
    # UC2-E3: Sistema de Reintentos
    # =========================================================================
    
    @patch('app.utils.email_service.mail.send')
    @patch('app.utils.email_service.time.sleep')  # Mock sleep para acelerar tests
    def test_e3_reintentos_en_error(self, mock_sleep, mock_send):
        """UC2-E3: Debe reintentar 3 veces con delay de 5 segundos"""
        from flask_mail import Message
        
        # Simular error en todos los intentos
        mock_send.side_effect = Exception('SMTP Error')
        
        with self.app.app_context():
            msg = Message(
                subject='Test',
                recipients=['test@test.com'],
                html='<p>Test</p>'
            )
            
            from app.utils.email_service import send_async_email
            resultado = send_async_email(
                self.app,
                msg,
                reintentos=3
            )
            
            # Debe fallar después de 3 intentos
            self.assertFalse(resultado)
            self.assertEqual(mock_send.call_count, 3)
            self.assertEqual(mock_sleep.call_count, 2)  # 2 delays entre 3 intentos
    
    @patch('app.utils.email_service.mail.send')
    def test_e3_exito_en_segundo_intento(self, mock_send):
        """UC2-E3: Debe tener éxito en segundo intento"""
        from flask_mail import Message
        
        # Simular error en primer intento, éxito en segundo
        mock_send.side_effect = [Exception('Error temporal'), None]
        
        with self.app.app_context():
            msg = Message(
                subject='Test',
                recipients=['test@test.com'],
                html='<p>Test</p>'
            )
            
            from app.utils.email_service import send_async_email
            resultado = send_async_email(
                self.app,
                msg,
                reintentos=3
            )
            
            # Debe tener éxito
            self.assertTrue(resultado)
            self.assertEqual(mock_send.call_count, 2)
    
    # =========================================================================
    # UC2-E4: Sin Usuarios de Gestión Humana
    # =========================================================================
    
    @patch('app.utils.email_service.send_email')
    def test_e4_sin_usuarios_rrhh_notifica_admin(self, mock_send_email):
        """UC2-E4: Si no hay usuarios RRHH, debe notificar a administrador"""
        # Eliminar auxiliar
        db.session.delete(self.auxiliar)
        db.session.commit()
        
        # Mock retorno de send_email
        mock_send_email.return_value = {'email_ok': True, 'notificacion_id': None}
        
        incapacidad = self.crear_incapacidad_prueba()
        
        with self.app.app_context():
            resultado = notificar_nueva_incapacidad(incapacidad)
            
            # Debe haber llamado a send_email 3 veces:
            # 1. Email al admin (E4)
            # 2. Email al colaborador
            # 3. Email a GESTION_HUMANA_EMAIL (fallback)
            self.assertEqual(mock_send_email.call_count, 3)
            
            # Verificar que se llamó al admin
            llamadas = mock_send_email.call_args_list
            llamada_admin = llamadas[0]
            self.assertIn('URGENTE', llamada_admin[1]['subject'])
            self.assertEqual(llamada_admin[1]['recipients'], [Config.ADMIN_EMAIL])
    
    # =========================================================================
    # UC2: Flujo Normal Completo
    # =========================================================================
    
    @patch('app.utils.email_service.send_email')
    def test_flujo_normal_notificacion_completa(self, mock_send_email):
        """UC2: Debe enviar 2 emails y crear 2 notificaciones internas"""
        # Mock para que send_email cree notificaciones
        def side_effect_send_email(*args, **kwargs):
            if kwargs.get('crear_notificacion'):
                notif = crear_notificacion_interna(
                    tipo=kwargs['tipo_notificacion'],
                    destinatario_id=kwargs['destinatario_id'],
                    asunto=kwargs['subject'],
                    contenido=kwargs['html_body']
                )
                db.session.commit()
                return {'email_ok': True, 'notificacion_id': notif.id if notif else None}
            return {'email_ok': True, 'notificacion_id': None}
        
        mock_send_email.side_effect = side_effect_send_email
        
        incapacidad = self.crear_incapacidad_prueba()
        
        with self.app.app_context():
            resultado = notificar_nueva_incapacidad(incapacidad)
            
            # Debe haber enviado 2 emails
            self.assertTrue(resultado['email_ok'])
            self.assertEqual(resultado['notificaciones_internas'], 2)
            
            # Verificar notificaciones en BD
            notificaciones = Notificacion.query.all()
            self.assertEqual(len(notificaciones), 2)
            
            # Una para colaborador, una para RRHH
            destinatarios = [n.destinatario_id for n in notificaciones]
            self.assertIn(self.colaborador.id, destinatarios)
            self.assertIn(self.auxiliar.id, destinatarios)
    
    @patch('app.utils.email_service.send_email')
    def test_paso_8_logs_detallados(self, mock_send_email):
        """UC2 (paso 8): Debe registrar logs con toda la información"""
        mock_send_email.return_value = {'email_ok': True, 'notificacion_id': None}
        
        incapacidad = self.crear_incapacidad_prueba()
        
        with self.app.app_context():
            with self.assertLogs('app.utils.email_service', level='INFO') as logs:
                notificar_nueva_incapacidad(incapacidad)
                
                # Verificar que hay logs con información relevante
                log_output = '\n'.join(logs.output)
                self.assertIn('UC2', log_output)
                self.assertIn(incapacidad.codigo_radicacion, log_output)
                self.assertIn('paso 4', log_output)  # Email colaborador
                self.assertIn('paso 5', log_output)  # Email RRHH
    
    def test_notificacion_sin_usuario(self):
        """UC2: Debe fallar si incapacidad no tiene usuario"""
        # Crear incapacidad sin usuario (solo para test, violará constraint si se commitea)
        incapacidad = Incapacidad()
        incapacidad.tipo = 'Enfermedad General'
        incapacidad.fecha_inicio = datetime.utcnow().date()
        incapacidad.fecha_fin = (datetime.utcnow() + timedelta(days=3)).date()
        incapacidad.dias = 3
        incapacidad.codigo_radicacion = 'INC-TEST-0001'
        incapacidad.estado = 'PENDIENTE_VALIDACION'
        incapacidad.usuario_id = None
        incapacidad.usuario = None
        # NO hacer commit para evitar constraint error
        
        with self.app.app_context():
            resultado = notificar_nueva_incapacidad(incapacidad)
            
            self.assertFalse(resultado['email_ok'])
            self.assertEqual(resultado['notificaciones_internas'], 0)
    
    # =========================================================================
    # UC2: Integración con Notificaciones
    # =========================================================================
    
    def test_ciclo_completo_estado_notificacion(self):
        """UC2: Ciclo completo PENDIENTE → ENVIADA → ENTREGADA"""
        # Crear notificación
        notif = crear_notificacion_interna(
            tipo=TipoNotificacionEnum.REGISTRO_INCAPACIDAD,
            destinatario_id=self.colaborador.id,
            asunto='Test',
            contenido='Test'
        )
        db.session.commit()
        
        # Estado inicial
        self.assertEqual(notif.estado, EstadoNotificacionEnum.PENDIENTE.value)
        
        # Marcar como enviada
        marcar_notificacion_enviada(notif.id)
        notif = Notificacion.query.get(notif.id)
        self.assertEqual(notif.estado, EstadoNotificacionEnum.ENVIADA.value)
        
        # Marcar como entregada
        marcar_notificacion_entregada(notif.id)
        notif = Notificacion.query.get(notif.id)
        self.assertEqual(notif.estado, EstadoNotificacionEnum.ENTREGADA.value)
    
    def test_email_notificaciones_fallback_a_email_login(self):
        """UC2: Si email_notificaciones es None, debe usar email de login"""
        # Crear usuario sin email_notificaciones
        usuario_sin_email_notif = Usuario(
            nombre='Test User',
            email='test@test.com',
            email_notificaciones=None,
            rol='colaborador'
        )
        usuario_sin_email_notif.set_password('123456')
        db.session.add(usuario_sin_email_notif)
        db.session.commit()
        
        incapacidad = Incapacidad(
            usuario_id=usuario_sin_email_notif.id,
            tipo='Enfermedad General',
            fecha_inicio=datetime.utcnow().date(),
            fecha_fin=(datetime.utcnow() + timedelta(days=1)).date(),
            dias=1,
            codigo_radicacion='INC-TEST-0002',
            estado='PENDIENTE_VALIDACION'
        )
        db.session.add(incapacidad)
        db.session.commit()
        
        with self.app.app_context():
            with patch('app.utils.email_service.send_email') as mock_send:
                mock_send.return_value = {'email_ok': True, 'notificacion_id': None}
                
                notificar_nueva_incapacidad(incapacidad)
                
                # Verificar que se usó el email de login
                llamadas = mock_send.call_args_list
                emails_enviados = [call[1]['recipients'][0] for call in llamadas]
                self.assertIn('test@test.com', emails_enviados)
    
    def test_validacion_formato_email(self):
        """UC2-E2: Debe validar formato de email correctamente"""
        with self.app.app_context():
            # Emails inválidos
            emails_invalidos = [
                'sin-arroba',
                '@sinusuario.com',
                'usuario@',
                'usuario@.com',
                'usuario @dominio.com',
                ''
            ]
            
            for email_invalido in emails_invalidos:
                resultado = send_email(
                    subject='Test',
                    recipients=[email_invalido],
                    html_body='<p>Test</p>',
                    crear_notificacion=True,
                    tipo_notificacion='TEST',
                    destinatario_id=self.colaborador.id
                )
                
                # Email no debe enviarse
                self.assertFalse(resultado['email_ok'], 
                               f"Email inválido '{email_invalido}' no fue rechazado")
            
            # Emails válidos
            emails_validos = [
                'usuario@dominio.com',
                'usuario.apellido@dominio.com',
                'usuario+tag@dominio.co.uk',
                'usuario123@dominio-largo.com'
            ]
            
            for email_valido in emails_validos:
                resultado = send_email(
                    subject='Test',
                    recipients=[email_valido],
                    html_body='<p>Test</p>'
                )
                
                # Email debe programarse
                self.assertTrue(resultado['email_ok'],
                              f"Email válido '{email_valido}' fue rechazado")


if __name__ == '__main__':
    unittest.main()

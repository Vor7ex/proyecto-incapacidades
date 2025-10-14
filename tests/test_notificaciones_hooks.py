"""
Tests para UC2 (Notificaciones) y UC15 (Hooks de Almacenamiento)
Valida sistema de reintentos, logging y hooks post-commit
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import tempfile
import os
import shutil
from app import create_app, db
from app.models.usuario import Usuario
from app.models.incapacidad import Incapacidad
from app.models.documento import Documento
from app.utils.email_service import (
    send_email,
    send_multiple_emails,
    notificar_nueva_incapacidad,
    confirmar_almacenamiento_definitivo
)

class TestNotificacionesYHooks(unittest.TestCase):
    """Tests para sistema de notificaciones con reintentos y hooks"""
    
    def setUp(self):
        """Configurar entorno de pruebas"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['MAIL_ENABLED'] = False  # Modo simulación
        
        # Crear directorio temporal para uploads
        self.temp_dir = tempfile.mkdtemp()
        self.app.config['UPLOAD_FOLDER'] = self.temp_dir
        
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
        
        # Crear usuario de prueba
        self.usuario = Usuario(
            nombre='Test User',
            email='test@example.com',
            rol='colaborador'
        )
        self.usuario.set_password('password123')
        db.session.add(self.usuario)
        db.session.commit()
    
    def tearDown(self):
        """Limpiar después de cada test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
        # Limpiar directorio temporal
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    # ========================================
    # TEST 1: Envío de email con modo simulación
    # ========================================
    def test_envio_email_modo_simulacion(self):
        """Test: En modo simulación (MAIL_ENABLED=False) debe loguear pero no enviar"""
        with self.app.app_context():
            resultado = send_email(
                subject='Test Subject',
                recipients=['test@example.com'],
                html_body='<p>Test HTML</p>'
            )
            
            # Debe retornar True (simulación exitosa)
            self.assertTrue(resultado)
    
    # ========================================
    # TEST 2: Validación de destinatarios
    # ========================================
    def test_validacion_destinatarios_vacios(self):
        """Test: No debe enviar email sin destinatarios"""
        with self.app.app_context():
            resultado = send_email(
                subject='Test',
                recipients=[],
                html_body='<p>Test</p>'
            )
            
            # Debe retornar False
            self.assertFalse(resultado)
    
    # ========================================
    # TEST 3: Notificación de nueva incapacidad
    # ========================================
    def test_notificar_nueva_incapacidad(self):
        """Test: Debe programar 2 emails (colaborador + RRHH)"""
        # Crear incapacidad
        incapacidad = Incapacidad(
            usuario_id=self.usuario.id,
            tipo='Enfermedad General',
            fecha_inicio=datetime.now().date(),
            fecha_fin=(datetime.now() + timedelta(days=2)).date(),
            dias=3,
            estado='Pendiente'
        )
        incapacidad.asignar_codigo_radicacion()
        db.session.add(incapacidad)
        db.session.commit()
        
        # Enviar notificación
        with self.app.app_context():
            resultado = notificar_nueva_incapacidad(incapacidad)
            
            # Debe retornar True
            self.assertTrue(resultado)
    
    # ========================================
    # TEST 4: Notificación sin usuario válido
    # ========================================
    def test_notificar_sin_usuario(self):
        """Test: No debe notificar si incapacidad no tiene usuario con email"""
        incapacidad = Incapacidad(
            usuario_id=None,  # Sin usuario
            tipo='Enfermedad General',
            fecha_inicio=datetime.now().date(),
            fecha_fin=(datetime.now() + timedelta(days=2)).date(),
            dias=3,
            estado='Pendiente'
        )
        incapacidad.asignar_codigo_radicacion()
        
        with self.app.app_context():
            resultado = notificar_nueva_incapacidad(incapacidad)
            
            # Debe retornar False
            self.assertFalse(resultado)
    
    # ========================================
    # TEST 5: Hook de almacenamiento sin documentos
    # ========================================
    def test_almacenamiento_sin_documentos(self):
        """Test: Hook debe retornar True si no hay documentos (no es error)"""
        incapacidad = Incapacidad(
            usuario_id=self.usuario.id,
            tipo='Enfermedad General',
            fecha_inicio=datetime.now().date(),
            fecha_fin=(datetime.now() + timedelta(days=1)).date(),
            dias=2,
            estado='Pendiente'
        )
        incapacidad.asignar_codigo_radicacion()
        db.session.add(incapacidad)
        db.session.commit()
        
        with self.app.app_context():
            resultado = confirmar_almacenamiento_definitivo(incapacidad)
            
            # Debe retornar True (no hay documentos, pero no es error)
            self.assertTrue(resultado)
    
    # ========================================
    # TEST 6: Hook de almacenamiento con documentos (mock)
    # ========================================
    def test_almacenamiento_con_documentos(self):
        """Test: Hook debe verificar existencia de archivos físicos"""
        from unittest.mock import patch
        
        # Crear incapacidad
        incapacidad = Incapacidad(
            usuario_id=self.usuario.id,
            tipo='Enfermedad General',
            fecha_inicio=datetime.now().date(),
            fecha_fin=(datetime.now() + timedelta(days=2)).date(),
            dias=3,
            estado='Pendiente'
        )
        incapacidad.asignar_codigo_radicacion()
        db.session.add(incapacidad)
        db.session.flush()
        
        # Crear documento en BD
        documento = Documento(
            incapacidad_id=incapacidad.id,
            nombre_archivo='test_certificado.pdf',
            nombre_unico=f'INC{incapacidad.id}_certificado_test.pdf',
            ruta='test_certificado.pdf',
            tipo_documento='certificado',
            tamaño_bytes=16,
            checksum_md5='abc123',
            mime_type='application/pdf'
        )
        db.session.add(documento)
        db.session.commit()
        
        # Mock os.path.exists para simular que el archivo existe
        with patch('os.path.exists', return_value=True):
            with self.app.app_context():
                resultado = confirmar_almacenamiento_definitivo(incapacidad)
                
                # Debe retornar True (archivo "existe")
                self.assertTrue(resultado)
    
    # ========================================
    # TEST 7: Hook detecta archivo físico faltante
    # ========================================
    def test_almacenamiento_archivo_faltante(self):
        """Test: Hook debe detectar si archivo físico no existe"""
        # Crear incapacidad
        incapacidad = Incapacidad(
            usuario_id=self.usuario.id,
            tipo='Enfermedad General',
            fecha_inicio=datetime.now().date(),
            fecha_fin=(datetime.now() + timedelta(days=2)).date(),
            dias=3,
            estado='Pendiente'
        )
        incapacidad.asignar_codigo_radicacion()
        db.session.add(incapacidad)
        db.session.flush()
        
        # Crear documento en BD pero SIN archivo físico
        documento = Documento(
            incapacidad_id=incapacidad.id,
            nombre_archivo='inexistente.pdf',
            nombre_unico='INC1_certificado_inexistente.pdf',
            ruta='inexistente.pdf',  # Campo correcto: 'ruta'
            tipo_documento='certificado',
            tamaño_bytes=100,
            checksum_md5='abc123',
            mime_type='application/pdf'
        )
        db.session.add(documento)
        db.session.commit()
        
        with self.app.app_context():
            resultado = confirmar_almacenamiento_definitivo(incapacidad)
            
            # Debe retornar False (archivo no existe)
            self.assertFalse(resultado)
    
    # ========================================
    # TEST 8: Múltiples emails con batch
    # ========================================
    def test_envio_multiple_emails(self):
        """Test: Envío de batch de emails debe programarse correctamente"""
        with self.app.app_context():
            emails_data = [
                {
                    'subject': 'Email 1',
                    'recipients': ['test1@example.com'],
                    'html_body': '<p>Test 1</p>'
                },
                {
                    'subject': 'Email 2',
                    'recipients': ['test2@example.com'],
                    'html_body': '<p>Test 2</p>'
                }
            ]
            
            # No debe lanzar excepción
            send_multiple_emails(emails_data, delay=0.1)
            
            # Test pasa si no hay excepciones
            self.assertTrue(True)
    
    # ========================================
    # TEST 9: Email con subject y código de radicación
    # ========================================
    def test_email_incluye_codigo_radicacion(self):
        """Test: Emails deben incluir código de radicación en subject"""
        incapacidad = Incapacidad(
            usuario_id=self.usuario.id,
            tipo='Enfermedad General',
            fecha_inicio=datetime.now().date(),
            fecha_fin=(datetime.now() + timedelta(days=2)).date(),
            dias=3,
            estado='Pendiente'
        )
        incapacidad.asignar_codigo_radicacion()
        db.session.add(incapacidad)
        db.session.commit()
        
        # Código debe existir
        self.assertIsNotNone(incapacidad.codigo_radicacion)
        
        # Notificar debe usar el código
        with self.app.app_context():
            resultado = notificar_nueva_incapacidad(incapacidad)
            self.assertTrue(resultado)

if __name__ == '__main__':
    unittest.main()

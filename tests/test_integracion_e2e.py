"""
Test de Integración End-to-End: Registro completo de incapacidad
Verifica el flujo completo desde validaciones hasta código de radicación
"""
import unittest
import tempfile
import os
from datetime import datetime, timedelta
from io import BytesIO
from app import create_app, db
from app.models.usuario import Usuario
from app.models.incapacidad import Incapacidad
from app.models.documento import Documento

class TestRegistroIntegracionCompleta(unittest.TestCase):
    """Test de integración del flujo completo de registro"""
    
    def setUp(self):
        """Configurar entorno de pruebas"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        
        # Crear directorio temporal para uploads
        self.temp_dir = tempfile.mkdtemp()
        self.app.config['UPLOAD_FOLDER'] = self.temp_dir
        
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
        
        # Crear usuario colaborador
        self.colaborador = Usuario(
            nombre='Juan Pérez',
            email='juan@test.com',
            rol='colaborador'
        )
        self.colaborador.set_password('password123')
        db.session.add(self.colaborador)
        db.session.commit()
        
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
    
    def crear_archivo_fake(self, nombre='certificado.pdf', contenido=b'PDF content'):
        """Helper: crear archivo fake para upload"""
        return (BytesIO(contenido), nombre)
    
    def login(self):
        """Helper: hacer login como colaborador"""
        return self.client.post('/auth/login', data={
            'email': 'juan@test.com',
            'password': 'password123'
        }, follow_redirects=True)
    
    # ========================================
    # TEST 1: Flujo completo exitoso
    # ========================================
    def test_flujo_completo_enfermedad_general_corta(self):
        """Test E2E: Registro de Enfermedad General <= 2 días (solo certificado)"""
        self.login()
        
        # Datos de la incapacidad
        fecha_inicio = datetime.now().date()
        fecha_fin = fecha_inicio + timedelta(days=1)
        
        # Registrar incapacidad
        response = self.client.post('/incapacidades/registrar', data={
            'tipo': 'Enfermedad General',
            'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
            'fecha_fin': fecha_fin.strftime('%Y-%m-%d'),
            'certificado': self.crear_archivo_fake('certificado.pdf')
        }, follow_redirects=True, content_type='multipart/form-data')
        
        # Verificar respuesta exitosa
        self.assertEqual(response.status_code, 200)
        
        # Verificar que se creó la incapacidad
        incapacidad = Incapacidad.query.first()
        self.assertIsNotNone(incapacidad)
        
        # ✅ Verificar CÓDIGO DE RADICACIÓN
        self.assertIsNotNone(incapacidad.codigo_radicacion)
        self.assertRegex(incapacidad.codigo_radicacion, r'^INC-\d{8}-[A-F0-9]{4}$')
        
        # Verificar datos básicos
        self.assertEqual(incapacidad.tipo, 'Enfermedad General')
        self.assertEqual(incapacidad.fecha_inicio, fecha_inicio)
        self.assertEqual(incapacidad.fecha_fin, fecha_fin)
        self.assertEqual(incapacidad.dias, 2)
        self.assertEqual(incapacidad.estado, 'Pendiente')
        
        # Verificar documento
        documentos = Documento.query.filter_by(incapacidad_id=incapacidad.id).all()
        self.assertEqual(len(documentos), 1)
        self.assertEqual(documentos[0].tipo_documento, 'certificado')
        
        # ✅ Verificar METADATOS
        self.assertIsNotNone(documentos[0].nombre_unico)
        self.assertIsNotNone(documentos[0].tamaño_bytes)
        self.assertIsNotNone(documentos[0].checksum_md5)
        self.assertIsNotNone(documentos[0].mime_type)
    
    # ========================================
    # TEST 2: Enfermedad General > 2 días (requiere epicrisis)
    # ========================================
    def test_flujo_completo_enfermedad_general_larga(self):
        """Test E2E: Enfermedad General > 2 días (certificado + epicrisis)"""
        self.login()
        
        fecha_inicio = datetime.now().date()
        fecha_fin = fecha_inicio + timedelta(days=5)
        
        response = self.client.post('/incapacidades/registrar', data={
            'tipo': 'Enfermedad General',
            'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
            'fecha_fin': fecha_fin.strftime('%Y-%m-%d'),
            'certificado': self.crear_archivo_fake('certificado.pdf'),
            'epicrisis': self.crear_archivo_fake('epicrisis.pdf')
        }, follow_redirects=True, content_type='multipart/form-data')
        
        self.assertEqual(response.status_code, 200)
        
        incapacidad = Incapacidad.query.first()
        self.assertIsNotNone(incapacidad)
        self.assertEqual(incapacidad.dias, 6)
        
        # ✅ Código de radicación presente
        self.assertIsNotNone(incapacidad.codigo_radicacion)
        
        # Verificar 2 documentos
        documentos = Documento.query.filter_by(incapacidad_id=incapacidad.id).all()
        self.assertEqual(len(documentos), 2)
        
        tipos = {doc.tipo_documento for doc in documentos}
        self.assertEqual(tipos, {'certificado', 'epicrisis'})
    
    # ========================================
    # TEST 3: Rollback por falta de documentos
    # ========================================
    def test_rollback_sin_documentos(self):
        """Test E2E: Rollback cuando no se cargan documentos"""
        self.login()
        
        fecha_inicio = datetime.now().date()
        fecha_fin = fecha_inicio + timedelta(days=2)
        
        # Intentar registrar SIN documentos
        response = self.client.post('/incapacidades/registrar', data={
            'tipo': 'Enfermedad General',
            'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
            'fecha_fin': fecha_fin.strftime('%Y-%m-%d')
            # NO se envía ningún archivo
        }, follow_redirects=True, content_type='multipart/form-data')
        
        self.assertEqual(response.status_code, 200)
        
        # ✅ NO debe haberse creado la incapacidad (rollback)
        incapacidades = Incapacidad.query.all()
        self.assertEqual(len(incapacidades), 0)
        
        # ✅ NO debe haber documentos huérfanos
        documentos = Documento.query.all()
        self.assertEqual(len(documentos), 0)
    
    # ========================================
    # TEST 4: Licencia Maternidad (múltiples documentos)
    # ========================================
    def test_flujo_licencia_maternidad(self):
        """Test E2E: Licencia Maternidad con 3 documentos requeridos"""
        self.login()
        
        fecha_inicio = datetime.now().date()
        fecha_fin = fecha_inicio + timedelta(days=90)
        
        response = self.client.post('/incapacidades/registrar', data={
            'tipo': 'Licencia Maternidad',
            'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
            'fecha_fin': fecha_fin.strftime('%Y-%m-%d'),
            'certificado': self.crear_archivo_fake('certificado.pdf'),
            'certificado_nacido_vivo': self.crear_archivo_fake('nacido_vivo.pdf'),
            'registro_civil': self.crear_archivo_fake('registro_civil.pdf')
        }, follow_redirects=True, content_type='multipart/form-data')
        
        self.assertEqual(response.status_code, 200)
        
        incapacidad = Incapacidad.query.first()
        self.assertIsNotNone(incapacidad)
        
        # ✅ Código de radicación
        self.assertIsNotNone(incapacidad.codigo_radicacion)
        
        # Verificar 3 documentos
        documentos = Documento.query.filter_by(incapacidad_id=incapacidad.id).all()
        self.assertEqual(len(documentos), 3)
        
        tipos = {doc.tipo_documento for doc in documentos}
        self.assertEqual(tipos, {
            'certificado',
            'certificado_nacido_vivo',
            'registro_civil'
        })
        
        # Verificar metadatos en todos los documentos
        for doc in documentos:
            self.assertIsNotNone(doc.nombre_unico)
            self.assertIsNotNone(doc.checksum_md5)
            self.assertTrue(doc.tamaño_bytes > 0)
    
    # ========================================
    # TEST 5: Unicidad de códigos en múltiples registros
    # ========================================
    def test_unicidad_codigos_multiples_registros(self):
        """Test E2E: Verificar que múltiples registros tengan códigos únicos"""
        self.login()
        
        codigos = []
        
        # Registrar 5 incapacidades
        for i in range(5):
            fecha_inicio = datetime.now().date() + timedelta(days=i*10)
            fecha_fin = fecha_inicio + timedelta(days=2)
            
            response = self.client.post('/incapacidades/registrar', data={
                'tipo': 'Enfermedad General',
                'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
                'fecha_fin': fecha_fin.strftime('%Y-%m-%d'),
                'certificado': self.crear_archivo_fake(f'cert{i}.pdf')
            }, follow_redirects=True, content_type='multipart/form-data')
            
            self.assertEqual(response.status_code, 200)
        
        # Verificar 5 incapacidades creadas
        incapacidades = Incapacidad.query.all()
        self.assertEqual(len(incapacidades), 5)
        
        # Recopilar códigos
        for inc in incapacidades:
            self.assertIsNotNone(inc.codigo_radicacion)
            codigos.append(inc.codigo_radicacion)
        
        # ✅ Todos los códigos deben ser únicos
        self.assertEqual(len(codigos), len(set(codigos)))
    
    # ========================================
    # TEST 6: Validación de tipo de incapacidad
    # ========================================
    def test_validacion_tipo_invalido(self):
        """Test E2E: Rechazar tipo de incapacidad inválido"""
        self.login()
        
        fecha_inicio = datetime.now().date()
        fecha_fin = fecha_inicio + timedelta(days=2)
        
        response = self.client.post('/incapacidades/registrar', data={
            'tipo': 'Tipo Inválido',  # ❌ No permitido
            'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
            'fecha_fin': fecha_fin.strftime('%Y-%m-%d'),
            'certificado': self.crear_archivo_fake('cert.pdf')
        }, follow_redirects=True, content_type='multipart/form-data')
        
        self.assertEqual(response.status_code, 200)
        
        # ✅ NO debe crearse la incapacidad
        incapacidades = Incapacidad.query.all()
        self.assertEqual(len(incapacidades), 0)

if __name__ == '__main__':
    unittest.main()

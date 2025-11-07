"""
Tests para Excepciones de UC1 - Registrar Incapacidad

- E3: Validación de archivo >10MB
- E5: Guardado automático en sesión expirada (validación frontend)
- E6: Guardado local y recuperación tras pérdida de conexión (validación frontend)
"""

import unittest
import os
import io
from datetime import date, datetime
from app import create_app, db
from app.models.usuario import Usuario
from app.models.incapacidad import Incapacidad
from app.utils.validaciones import validar_archivo
from werkzeug.datastructures import FileStorage


class TestUC1Excepciones(unittest.TestCase):
    """Tests para excepciones UC1-E3, E5, E6"""
    
    def setUp(self):
        """Configurar aplicación de prueba"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['UPLOAD_FOLDER'] = 'test_uploads'
        
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
        
        # Crear carpeta de uploads
        os.makedirs(self.app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Crear usuario de prueba
        self.usuario = Usuario(
            nombre='Test User',
            email='test@test.com',
            rol='colaborador'
        )
        self.usuario.set_password('123456')
        db.session.add(self.usuario)
        db.session.commit()
    
    def tearDown(self):
        """Limpiar"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
        # Limpiar uploads
        if os.path.exists(self.app.config['UPLOAD_FOLDER']):
            for file in os.listdir(self.app.config['UPLOAD_FOLDER']):
                os.remove(os.path.join(self.app.config['UPLOAD_FOLDER'], file))
            os.rmdir(self.app.config['UPLOAD_FOLDER'])
    
    def crear_archivo_mock(self, tamaño_mb, nombre='test.pdf', tipo='application/pdf'):
        """Crear archivo mock de tamaño específico"""
        tamaño_bytes = int(tamaño_mb * 1024 * 1024)
        contenido = b'X' * tamaño_bytes
        
        return FileStorage(
            stream=io.BytesIO(contenido),
            filename=nombre,
            content_type=tipo
        )
    
    # =========================================================================
    # UC1-E3: VALIDACIÓN DE ARCHIVO >10MB
    # =========================================================================
    
    def test_e3_archivo_5mb_valido(self):
        """E3: Archivo de 5MB debe ser válido"""
        archivo = self.crear_archivo_mock(5.0, 'certificado.pdf')
        errores = validar_archivo(archivo)
        
        self.assertEqual(len(errores), 0, "5MB debe ser válido")
    
    def test_e3_archivo_10mb_valido(self):
        """E3: Archivo de exactamente 10MB debe ser válido (límite)"""
        archivo = self.crear_archivo_mock(10.0, 'certificado.pdf')
        errores = validar_archivo(archivo)
        
        self.assertEqual(len(errores), 0, "10MB debe ser válido (límite)")
    
    def test_e3_archivo_11mb_rechazado(self):
        """E3: Archivo >10MB debe ser rechazado con mensaje específico"""
        archivo = self.crear_archivo_mock(11.0, 'certificado.pdf')
        errores = validar_archivo(archivo)
        
        self.assertGreater(len(errores), 0, "Debe generar error")
        self.assertIn('UC1-E3', errores[0], "Debe mencionar UC1-E3")
        self.assertIn('10MB', errores[0], "Debe mencionar límite")
        self.assertIn('certificado.pdf', errores[0], "Debe mencionar nombre archivo")
    
    def test_e3_archivo_15mb_mensaje_detallado(self):
        """E3: Mensaje debe incluir tamaño actual y sugerencias"""
        archivo = self.crear_archivo_mock(15.3, 'epicrisis.pdf')
        errores = validar_archivo(archivo)
        
        self.assertGreater(len(errores), 0)
        mensaje = errores[0]
        
        # Verificar elementos del mensaje
        self.assertIn('UC1-E3', mensaje, "Debe mencionar excepción")
        self.assertIn('15', mensaje, "Debe mostrar tamaño")
        self.assertIn('MB', mensaje, "Debe incluir unidad")
        # Buscar sin distinción de mayúsculas
        self.assertIn('comprim', mensaje.lower(), "Debe sugerir comprimir")
    
    def test_e3_archivo_50mb_muy_grande(self):
        """E3: Archivos muy grandes también son rechazados"""
        archivo = self.crear_archivo_mock(50.0, 'documento.pdf')
        errores = validar_archivo(archivo)
        
        self.assertGreater(len(errores), 0)
        self.assertIn('UC1-E3', errores[0])
    
    def test_e3_imagen_jpg_12mb_rechazada(self):
        """E3: Imágenes grandes también son rechazadas"""
        imagen = self.crear_archivo_mock(12.0, 'certificado.jpg', 'image/jpeg')
        errores = validar_archivo(imagen)
        
        self.assertGreater(len(errores), 0)
        self.assertIn('UC1-E3', errores[0])
    
    def test_e3_imagen_png_8mb_valida(self):
        """E3: Imágenes <10MB son válidas"""
        imagen = self.crear_archivo_mock(8.0, 'epicrisis.png', 'image/png')
        errores = validar_archivo(imagen)
        
        self.assertEqual(len(errores), 0)
    
    def test_e3_caso_borde_9_99mb(self):
        """E3: 9.99MB debe ser válido (justo debajo del límite)"""
        archivo = self.crear_archivo_mock(9.99, 'documento.pdf')
        errores = validar_archivo(archivo)
        
        self.assertEqual(len(errores), 0, "9.99MB debe ser válido")
    
    def test_e3_caso_borde_10_01mb(self):
        """E3: 10.01MB debe ser rechazado (justo arriba del límite)"""
        archivo = self.crear_archivo_mock(10.01, 'documento.pdf')
        errores = validar_archivo(archivo)
        
        self.assertGreater(len(errores), 0, "10.01MB debe ser rechazado")
        self.assertIn('UC1-E3', errores[0])
    
    def test_e3_formato_invalido_no_sobrescribe_error(self):
        """E2+E3: Formato inválido se detecta antes que tamaño"""
        archivo_txt = self.crear_archivo_mock(15.0, 'documento.txt', 'text/plain')
        errores = validar_archivo(archivo_txt)
        
        self.assertGreater(len(errores), 0)
        # Debe detectar formato primero (E2), no tamaño (E3)
        self.assertIn('UC1-E2', errores[0])
    
    def test_e3_validacion_con_endpoint(self):
        """E3: Endpoint debe rechazar archivos grandes"""
        # Login
        self.client.post('/login', data={
            'email': 'test@test.com',
            'password': '123456'
        })
        
        # Intentar subir archivo grande
        archivo_grande = self.crear_archivo_mock(11.0, 'certificado.pdf')
        
        response = self.client.post('/incapacidades/registrar',
            data={
                'tipo': 'Enfermedad General',
                'fecha_inicio': date.today().strftime('%Y-%m-%d'),
                'fecha_fin': date.today().strftime('%Y-%m-%d'),
                'certificado': (archivo_grande.stream, 'certificado.pdf')
            },
            content_type='multipart/form-data',
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )
        
        # Debe retornar error (413 = Request Entity Too Large)
        self.assertIn(response.status_code, [400, 413, 500])
    
    # =========================================================================
    # UC1-E5: SESIÓN EXPIRADA (Validación conceptual)
    # =========================================================================
    
    def test_e5_concepto_borrador_implementado(self):
        """E5: Verificar que existe funcionalidad de borrador en template"""
        # Este test verifica que el concepto está implementado en JavaScript
        # La implementación real está en el template HTML con localStorage
        
        # Leer el template
        template_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'app', 'templates', 'incapacidades', 'crear.html'
        )
        
        with open(template_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Verificar que existen las funciones clave de E5
        self.assertIn('guardarBorradorLocal', contenido, "Debe existir función de guardado")
        self.assertIn('recuperarBorrador', contenido, "Debe existir función de recuperación")
        self.assertIn('UC1-E5', contenido, "Debe documentar la excepción E5")
        self.assertIn('localStorage', contenido, "Debe usar localStorage")
        self.assertIn('BORRADOR_KEY', contenido, "Debe definir clave de borrador")
    
    def test_e5_intervalo_guardado_automatico(self):
        """E5: Verificar que existe guardado automático periódico"""
        template_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'app', 'templates', 'incapacidades', 'crear.html'
        )
        
        with open(template_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Verificar intervalo de guardado automático
        self.assertIn('setInterval', contenido, "Debe tener guardado periódico")
        self.assertIn('guardarBorradorAutomatico', contenido, "Debe tener función automática")
        self.assertIn('30000', contenido, "Debe guardar cada 30 segundos")
    
    def test_e5_guardado_antes_descargar(self):
        """E5: Verificar que guarda antes de salir de la página"""
        template_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'app', 'templates', 'incapacidades', 'crear.html'
        )
        
        with open(template_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Verificar listener beforeunload
        self.assertIn('beforeunload', contenido, "Debe capturar salida de página")
        self.assertIn('formularioTieneDatos', contenido, "Debe verificar si hay datos")
    
    # =========================================================================
    # UC1-E6: PÉRDIDA DE CONEXIÓN (Validación conceptual)
    # =========================================================================
    
    def test_e6_concepto_offline_implementado(self):
        """E6: Verificar que existe funcionalidad offline"""
        template_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'app', 'templates', 'incapacidades', 'crear.html'
        )
        
        with open(template_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Verificar funciones de conexión
        self.assertIn('onConexionPerdida', contenido, "Debe manejar pérdida de conexión")
        self.assertIn('onConexionRestaurada', contenido, "Debe manejar reconexión")
        self.assertIn('UC1-E6', contenido, "Debe documentar excepción E6")
    
    def test_e6_listeners_online_offline(self):
        """E6: Verificar que escucha eventos de conexión"""
        template_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'app', 'templates', 'incapacidades', 'crear.html'
        )
        
        with open(template_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Verificar listeners de eventos online/offline
        self.assertIn("'online'", contenido, "Debe escuchar evento online")
        self.assertIn("'offline'", contenido, "Debe escuchar evento offline")
        self.assertIn('navigator.onLine', contenido, "Debe verificar estado de conexión")
    
    def test_e6_guardado_inmediato_offline(self):
        """E6: Verificar que guarda inmediatamente al perder conexión"""
        template_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'app', 'templates', 'incapacidades', 'crear.html'
        )
        
        with open(template_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # En onConexionPerdida debe llamar a guardarBorradorLocal
        lines = contenido.split('\n')
        found_function = False
        found_save = False
        
        for i, line in enumerate(lines):
            if 'function onConexionPerdida' in line:
                found_function = True
            if found_function and 'guardarBorradorLocal' in line:
                found_save = True
                break
        
        self.assertTrue(found_function, "Debe existir función onConexionPerdida")
        self.assertTrue(found_save, "Debe guardar borrador al perder conexión")
    
    def test_e6_alertas_visuales(self):
        """E6: Verificar que muestra alertas al usuario"""
        template_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'app', 'templates', 'incapacidades', 'crear.html'
        )
        
        with open(template_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Verificar alertas visuales
        self.assertIn('alert-conexion', contenido, "Debe tener alerta de conexión")
        self.assertIn('Sin conexión', contenido, "Debe avisar pérdida de conexión")
        self.assertIn('Conexión restaurada', contenido, "Debe avisar reconexión")
    
    # =========================================================================
    # TESTS INTEGRADOS
    # =========================================================================
    
    def test_integracion_e3_e5_e6(self):
        """Integración: E3, E5, E6 trabajan juntos"""
        template_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'app', 'templates', 'incapacidades', 'crear.html'
        )
        
        with open(template_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Todas las excepciones deben estar documentadas
        self.assertIn('UC1-E3', contenido)
        self.assertIn('UC1-E5', contenido)
        self.assertIn('UC1-E6', contenido)
        
        # Funcionalidades clave presentes
        funciones_requeridas = [
            'validarArchivo',
            'guardarBorradorLocal',
            'recuperarBorrador',
            'onConexionPerdida',
            'onConexionRestaurada'
        ]
        
        for funcion in funciones_requeridas:
            self.assertIn(funcion, contenido, f"Debe incluir función {funcion}")


if __name__ == '__main__':
    unittest.main()

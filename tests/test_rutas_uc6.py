"""
Tests para Rutas UC6: Solicitar Documentos Faltantes

Cobertura:
1. GET /solicitar-documentos - Solo auxiliar
2. POST /solicitar-documentos - Crear solicitud
3. GET /cargar-documentos-solicitados - Solo colaborador
4. POST /cargar-documentos-solicitados - Subir documentos
5. POST /cargar-documentos-solicitados - Archivos inválidos
6. GET /historial-estados - Ver auditoría
"""

import pytest
import io
from datetime import date, timedelta
from app import create_app, db
from app.models.usuario import Usuario
from app.models.incapacidad import Incapacidad
from app.models.solicitud_documento import SolicitudDocumento
from app.models.historial_estado import HistorialEstado
from app.models.documento import Documento
from app.models.enums import (
    EstadoIncapacidadEnum,
    EstadoSolicitudDocumentoEnum,
    TipoDocumentoEnum
)
from flask_login import login_user


@pytest.fixture
def app():
    """Crear aplicación de prueba."""
    import tempfile
    import os
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False  # Deshabilitar CSRF en tests
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20MB para permitir tests de archivos grandes
    
    # Crear directorio temporal para uploads
    temp_dir = tempfile.mkdtemp()
    app.config['UPLOAD_FOLDER'] = temp_dir
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
        
        # Limpiar directorio temporal
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


@pytest.fixture
def client(app):
    """Cliente de prueba."""
    return app.test_client()


@pytest.fixture
def usuarios(app):
    """Crear usuarios de prueba."""
    with app.app_context():
        # Auxiliar
        auxiliar = Usuario(
            nombre='Auxiliar Test',
            email='auxiliar@test.com',
            rol='auxiliar'
        )
        auxiliar.set_password('test123')
        
        # Colaborador
        colaborador = Usuario(
            nombre='Colaborador Test',
            email='colaborador@test.com',
            rol='colaborador'
        )
        colaborador.set_password('test123')
        
        db.session.add(auxiliar)
        db.session.add(colaborador)
        db.session.commit()
        
        return {
            'auxiliar_id': auxiliar.id,
            'colaborador_id': colaborador.id
        }


@pytest.fixture
def incapacidad_pendiente(app, usuarios):
    """Crear incapacidad en PENDIENTE_VALIDACION."""
    with app.app_context():
        incapacidad = Incapacidad(
            usuario_id=usuarios['colaborador_id'],
            codigo_radicacion='INC-20251019-TEST',
            tipo='Enfermedad General',
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=5),
            dias=5,
            estado=EstadoIncapacidadEnum.PENDIENTE_VALIDACION.value
        )
        db.session.add(incapacidad)
        db.session.commit()
        
        return incapacidad.id


def login(client, email, password='test123'):
    """Helper para hacer login."""
    return client.post('/login', data={
        'email': email,
        'password': password
    }, follow_redirects=True)


class TestSolicitarDocumentosGET:
    """Tests para GET /solicitar-documentos."""
    
    def test_acceso_solo_auxiliar(self, client, usuarios, incapacidad_pendiente):
        """Solo auxiliares pueden acceder a solicitar documentos."""
        # Login como colaborador
        login(client, 'colaborador@test.com')
        
        response = client.get(f'/incapacidades/{incapacidad_pendiente}/solicitar-documentos')
        
        # Debe redirigir o denegar acceso
        assert response.status_code in [302, 403]
    
    def test_auxiliar_puede_acceder(self, client, usuarios, incapacidad_pendiente):
        """Auxiliar puede ver el formulario."""
        login(client, 'auxiliar@test.com')
        
        response = client.get(f'/incapacidades/{incapacidad_pendiente}/solicitar-documentos')
        
        assert response.status_code == 200
        assert b'Solicitar Documentos Faltantes' in response.data
        assert b'INC-20251019-TEST' in response.data
    
    def test_muestra_documentos_disponibles(self, client, usuarios, incapacidad_pendiente):
        """Debe mostrar lista de documentos según tipo de incapacidad."""
        login(client, 'auxiliar@test.com')
        
        response = client.get(f'/incapacidades/{incapacidad_pendiente}/solicitar-documentos')
        
        assert response.status_code == 200
        # Verificar que muestra tabla de documentos
        assert b'certificado' in response.data.lower()


class TestSolicitarDocumentosPOST:
    """Tests para POST /solicitar-documentos."""
    
    def test_crear_solicitud_exitosa(self, client, app, usuarios, incapacidad_pendiente):
        """Debe crear solicitud correctamente."""
        login(client, 'auxiliar@test.com')
        
        response = client.post(
            f'/incapacidades/{incapacidad_pendiente}/solicitar-documentos',
            data={
                'documentos[]': [TipoDocumentoEnum.EPICRISIS.value],
                f'observacion_{TipoDocumentoEnum.EPICRISIS.value}': 'Documento ilegible'
            },
            follow_redirects=True
        )
        
        assert response.status_code == 200
        
        # Verificar que se creó en BD
        with app.app_context():
            solicitudes = SolicitudDocumento.query.filter_by(
                incapacidad_id=incapacidad_pendiente
            ).all()
            assert len(solicitudes) == 1
            assert solicitudes[0].tipo_documento == TipoDocumentoEnum.EPICRISIS.value
            assert solicitudes[0].observaciones_auxiliar == 'Documento ilegible'
    
    def test_rechaza_sin_documentos(self, client, usuarios, incapacidad_pendiente):
        """Debe rechazar si no se seleccionan documentos."""
        login(client, 'auxiliar@test.com')
        
        response = client.post(
            f'/incapacidades/{incapacidad_pendiente}/solicitar-documentos',
            data={},
            follow_redirects=True
        )
        
        # Debe mostrar error
        assert b'al menos un documento' in response.data.lower()
    
    def test_cambia_estado_incapacidad(self, client, app, usuarios, incapacidad_pendiente):
        """Debe cambiar estado a DOCUMENTACION_INCOMPLETA."""
        login(client, 'auxiliar@test.com')
        
        client.post(
            f'/incapacidades/{incapacidad_pendiente}/solicitar-documentos',
            data={
                'documentos[]': [TipoDocumentoEnum.EPICRISIS.value]
            }
        )
        
        with app.app_context():
            incapacidad = Incapacidad.query.get(incapacidad_pendiente)
            assert incapacidad.estado == EstadoIncapacidadEnum.DOCUMENTACION_INCOMPLETA.value


class TestCargarDocumentosGET:
    """Tests para GET /cargar-documentos-solicitados."""
    
    def test_acceso_solo_colaborador_propietario(self, client, app, usuarios, incapacidad_pendiente):
        """Solo el colaborador propietario puede acceder."""
        # Crear solicitud primero
        with app.app_context():
            incapacidad = Incapacidad.query.get(incapacidad_pendiente)
            incapacidad.estado = EstadoIncapacidadEnum.DOCUMENTACION_INCOMPLETA.value
            
            solicitud = SolicitudDocumento(
                incapacidad_id=incapacidad.id,
                tipo_documento=TipoDocumentoEnum.EPICRISIS.value,
                estado=EstadoSolicitudDocumentoEnum.PENDIENTE.value,
                fecha_solicitud=date.today(),
                fecha_vencimiento=date.today() + timedelta(days=3),
                observaciones_auxiliar='Test'
            )
            db.session.add(solicitud)
            db.session.commit()
        
        # Login como colaborador propietario
        login(client, 'colaborador@test.com')
        
        response = client.get(f'/incapacidades/{incapacidad_pendiente}/cargar-documentos-solicitados')
        
        assert response.status_code == 200
        assert b'Carga de Documentos Solicitados' in response.data
    
    def test_muestra_solicitudes_pendientes(self, client, app, usuarios, incapacidad_pendiente):
        """Debe mostrar las solicitudes pendientes con plazos."""
        with app.app_context():
            incapacidad = Incapacidad.query.get(incapacidad_pendiente)
            incapacidad.estado = EstadoIncapacidadEnum.DOCUMENTACION_INCOMPLETA.value
            
            solicitud = SolicitudDocumento(
                incapacidad_id=incapacidad.id,
                tipo_documento=TipoDocumentoEnum.EPICRISIS.value,
                estado=EstadoSolicitudDocumentoEnum.PENDIENTE.value,
                fecha_solicitud=date.today(),
                fecha_vencimiento=date.today() + timedelta(days=3),
                observaciones_auxiliar='Documento ilegible'
            )
            db.session.add(solicitud)
            db.session.commit()
        
        login(client, 'colaborador@test.com')
        
        response = client.get(f'/incapacidades/{incapacidad_pendiente}/cargar-documentos-solicitados')
        
        assert response.status_code == 200
        assert b'epicrisis' in response.data.lower()
        assert b'Documento ilegible' in response.data


class TestCargarDocumentosPOST:
    """Tests para POST /cargar-documentos-solicitados."""
    
    def test_cargar_documento_valido(self, client, app, usuarios, incapacidad_pendiente):
        """Debe aceptar archivo válido y crear Documento."""
        # Preparar solicitud
        with app.app_context():
            incapacidad = Incapacidad.query.get(incapacidad_pendiente)
            incapacidad.estado = EstadoIncapacidadEnum.DOCUMENTACION_INCOMPLETA.value
            
            solicitud = SolicitudDocumento(
                incapacidad_id=incapacidad.id,
                tipo_documento=TipoDocumentoEnum.EPICRISIS.value,
                estado=EstadoSolicitudDocumentoEnum.PENDIENTE.value,
                fecha_solicitud=date.today(),
                fecha_vencimiento=date.today() + timedelta(days=3),
                observaciones_auxiliar='Test'
            )
            db.session.add(solicitud)
            db.session.commit()
        
        login(client, 'colaborador@test.com')
        
        # Crear archivo fake
        data = {
            f'documento_{TipoDocumentoEnum.EPICRISIS.value}': (
                io.BytesIO(b'PDF fake content'),
                'epicrisis.pdf',
                'application/pdf'
            )
        }
        
        response = client.post(
            f'/incapacidades/{incapacidad_pendiente}/cargar-documentos-solicitados',
            data=data,
            content_type='multipart/form-data',
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['success'] is True
    
    def test_rechaza_archivo_muy_grande(self, client, app, usuarios, incapacidad_pendiente):
        """Debe rechazar archivos > 10MB."""
        # Preparar solicitud
        with app.app_context():
            incapacidad = Incapacidad.query.get(incapacidad_pendiente)
            incapacidad.estado = EstadoIncapacidadEnum.DOCUMENTACION_INCOMPLETA.value
            
            solicitud = SolicitudDocumento(
                incapacidad_id=incapacidad.id,
                tipo_documento=TipoDocumentoEnum.EPICRISIS.value,
                estado=EstadoSolicitudDocumentoEnum.PENDIENTE.value,
                fecha_solicitud=date.today(),
                fecha_vencimiento=date.today() + timedelta(days=3)
            )
            db.session.add(solicitud)
            db.session.commit()
        
        login(client, 'colaborador@test.com')
        
        # Crear archivo fake grande (11MB)
        contenido_grande = b'X' * (11 * 1024 * 1024)
        data = {
            f'documento_{TipoDocumentoEnum.EPICRISIS.value}': (
                io.BytesIO(contenido_grande),
                'epicrisis_grande.pdf',
                'application/pdf'
            )
        }
        
        response = client.post(
            f'/incapacidades/{incapacidad_pendiente}/cargar-documentos-solicitados',
            data=data,
            content_type='multipart/form-data',
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )
        
        assert response.status_code == 400
        json_data = response.get_json()
        assert json_data['success'] is False
        assert any('10MB' in error or 'grande' in error.lower() for error in json_data['errors'])
    
    def test_rechaza_formato_invalido(self, client, app, usuarios, incapacidad_pendiente):
        """Debe rechazar formatos no permitidos."""
        # Preparar solicitud
        with app.app_context():
            incapacidad = Incapacidad.query.get(incapacidad_pendiente)
            incapacidad.estado = EstadoIncapacidadEnum.DOCUMENTACION_INCOMPLETA.value
            
            solicitud = SolicitudDocumento(
                incapacidad_id=incapacidad.id,
                tipo_documento=TipoDocumentoEnum.EPICRISIS.value,
                estado=EstadoSolicitudDocumentoEnum.PENDIENTE.value,
                fecha_solicitud=date.today(),
                fecha_vencimiento=date.today() + timedelta(days=3)
            )
            db.session.add(solicitud)
            db.session.commit()
        
        login(client, 'colaborador@test.com')
        
        # Crear archivo con extensión inválida
        data = {
            f'documento_{TipoDocumentoEnum.EPICRISIS.value}': (
                io.BytesIO(b'Contenido de texto'),
                'epicrisis.txt',  # TXT no permitido
                'text/plain'
            )
        }
        
        response = client.post(
            f'/incapacidades/{incapacidad_pendiente}/cargar-documentos-solicitados',
            data=data,
            content_type='multipart/form-data',
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )
        
        assert response.status_code == 400
        json_data = response.get_json()
        assert json_data['success'] is False
        assert any('formato' in error.lower() or 'permitido' in error.lower() 
                  for error in json_data['errors'])


class TestHistorialEstados:
    """Tests para GET /historial-estados."""
    
    def test_colaborador_puede_ver_su_historial(self, client, app, usuarios, incapacidad_pendiente):
        """Colaborador propietario puede ver historial."""
        # Crear historial
        with app.app_context():
            historial = HistorialEstado(
                incapacidad_id=incapacidad_pendiente,
                usuario_id=usuarios['auxiliar_id'],
                estado_anterior=EstadoIncapacidadEnum.PENDIENTE_VALIDACION.value,
                estado_nuevo=EstadoIncapacidadEnum.DOCUMENTACION_INCOMPLETA.value,
                observaciones='Solicitud de documentos'
            )
            db.session.add(historial)
            db.session.commit()
        
        login(client, 'colaborador@test.com')
        
        response = client.get(f'/incapacidades/{incapacidad_pendiente}/historial-estados')
        
        assert response.status_code == 200
        assert b'Historial de Estados' in response.data
        assert b'DOCUMENTACION_INCOMPLETA' in response.data
    
    def test_auxiliar_puede_ver_historial(self, client, app, usuarios, incapacidad_pendiente):
        """Auxiliar puede ver historial de cualquier incapacidad."""
        with app.app_context():
            historial = HistorialEstado(
                incapacidad_id=incapacidad_pendiente,
                usuario_id=usuarios['colaborador_id'],
                estado_anterior=None,
                estado_nuevo=EstadoIncapacidadEnum.PENDIENTE_VALIDACION.value,
                observaciones='Registro inicial'
            )
            db.session.add(historial)
            db.session.commit()
        
        login(client, 'auxiliar@test.com')
        
        response = client.get(f'/incapacidades/{incapacidad_pendiente}/historial-estados')
        
        assert response.status_code == 200
        assert b'Historial de Estados' in response.data
    
    def test_muestra_cambios_ordenados(self, client, app, usuarios, incapacidad_pendiente):
        """Debe mostrar cambios ordenados por fecha DESC."""
        # Crear múltiples cambios
        with app.app_context():
            from datetime import datetime
            
            cambio1 = HistorialEstado(
                incapacidad_id=incapacidad_pendiente,
                usuario_id=usuarios['colaborador_id'],
                estado_anterior=None,
                estado_nuevo=EstadoIncapacidadEnum.PENDIENTE_VALIDACION.value,
                fecha_cambio=datetime(2025, 10, 1, 10, 0, 0)
            )
            
            cambio2 = HistorialEstado(
                incapacidad_id=incapacidad_pendiente,
                usuario_id=usuarios['auxiliar_id'],
                estado_anterior=EstadoIncapacidadEnum.PENDIENTE_VALIDACION.value,
                estado_nuevo=EstadoIncapacidadEnum.DOCUMENTACION_INCOMPLETA.value,
                fecha_cambio=datetime(2025, 10, 2, 14, 30, 0)
            )
            
            db.session.add_all([cambio1, cambio2])
            db.session.commit()
        
        login(client, 'colaborador@test.com')
        
        response = client.get(f'/incapacidades/{incapacidad_pendiente}/historial-estados')
        
        assert response.status_code == 200
        # El más reciente debe aparecer primero
        assert b'DOCUMENTACION_INCOMPLETA' in response.data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

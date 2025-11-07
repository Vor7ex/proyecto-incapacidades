"""
Tests para el sistema de notificaciones internas (frontend).

Tests de integración para verificar:
- API de notificaciones
- Contador de no leídas
- Marcar como leída
- Marcar todas como leídas
"""

import unittest
from datetime import datetime

from app import create_app
from app.models import db
from app.models.notificacion import Notificacion
from app.models.usuario import Usuario
from app.models.enums import EstadoNotificacionEnum, TipoNotificacionEnum


class TestNotificacionesFrontend(unittest.TestCase):
    def setUp(self):
        """Configuración inicial para cada test."""
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.app.config["SECRET_KEY"] = "test-secret-key"
        
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        
        db.create_all()
        
        # Crear usuario de prueba
        self.usuario = Usuario(
            nombre="Test User",
            email="test@test.com",
            rol="colaborador"
        )
        self.usuario.set_password("123456")
        db.session.add(self.usuario)
        db.session.commit()
        
        # Crear notificaciones de prueba
        for i in range(5):
            notif = Notificacion(
                tipo=TipoNotificacionEnum.REGISTRO_INCAPACIDAD.value,
                destinatario_id=self.usuario.id,
                asunto=f"Notificación de prueba {i+1}",
                contenido=f"Contenido de la notificación {i+1}",
                estado=EstadoNotificacionEnum.ENTREGADA.value
            )
            db.session.add(notif)
        
        db.session.commit()
    
    def tearDown(self):
        """Limpieza después de cada test."""
        db.session.remove()
        db.drop_all()
        self.ctx.pop()
    
    def login(self):
        """Helper para hacer login."""
        return self.client.post('/auth/login', data={
            'email': 'test@test.com',
            'password': '123456'
        }, follow_redirects=True)
    
    def test_api_mis_notificaciones_requiere_login(self):
        """Test: API requiere autenticación."""
        response = self.client.get('/notificaciones/api/mis-notificaciones')
        # Flask-Login redirige a login si no está autenticado
        self.assertEqual(response.status_code, 302)
    
    def test_api_mis_notificaciones_devuelve_datos(self):
        """Test: API devuelve las notificaciones del usuario."""
        self.login()
        
        response = self.client.get('/notificaciones/api/mis-notificaciones')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIn('notificaciones', data)
        self.assertIn('total', data)
        self.assertIn('no_leidas', data)
        self.assertEqual(data['total'], 5)
    
    def test_api_contador_no_leidas(self):
        """Test: API contador devuelve cantidad correcta."""
        self.login()
        
        response = self.client.get('/notificaciones/api/contador-no-leidas')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIn('no_leidas', data)
        # Todas están con estado ENTREGADA, no LEIDA
        self.assertEqual(data['no_leidas'], 5)
    
    def test_api_marcar_leida(self):
        """Test: Marcar notificación como leída funciona."""
        self.login()
        
        notif = Notificacion.query.first()
        notif_id = notif.id
        
        response = self.client.post(f'/notificaciones/api/marcar-leida/{notif_id}')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('fecha_lectura', data)
        
        # Verificar en BD
        notif = Notificacion.query.get(notif_id)
        self.assertEqual(notif.estado, EstadoNotificacionEnum.LEIDA.value)
        self.assertIsNotNone(notif.fecha_lectura)
    
    def test_api_marcar_todas_leidas(self):
        """Test: Marcar todas las notificaciones como leídas."""
        self.login()
        
        response = self.client.post('/notificaciones/api/marcar-todas-leidas')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['marcadas'], 5)
        
        # Verificar que el contador es 0
        response = self.client.get('/notificaciones/api/contador-no-leidas')
        data = response.get_json()
        self.assertEqual(data['no_leidas'], 0)
    
    def test_api_filtro_solo_no_leidas(self):
        """Test: Filtro de solo no leídas funciona."""
        self.login()
        
        # Marcar una como leída
        notif = Notificacion.query.first()
        notif.marcar_leida()
        db.session.commit()
        
        # Consultar solo no leídas
        response = self.client.get('/notificaciones/api/mis-notificaciones?solo_no_leidas=true')
        data = response.get_json()
        
        self.assertEqual(len(data['notificaciones']), 4)
        self.assertEqual(data['no_leidas'], 4)
    
    def test_api_paginacion(self):
        """Test: Paginación funciona correctamente."""
        self.login()
        
        # Página 1 con límite de 2
        response = self.client.get('/notificaciones/api/mis-notificaciones?limite=2&pagina=1')
        data = response.get_json()
        
        self.assertEqual(len(data['notificaciones']), 2)
        self.assertEqual(data['total'], 5)
        self.assertEqual(data['pagina'], 1)
        self.assertEqual(data['total_paginas'], 3)
    
    def test_vista_notificaciones_requiere_login(self):
        """Test: Vista principal requiere autenticación."""
        response = self.client.get('/notificaciones/')
        # Debe redirigir al login
        self.assertEqual(response.status_code, 302)
    
    def test_vista_notificaciones_accesible_autenticado(self):
        """Test: Vista principal accesible con login."""
        self.login()
        
        response = self.client.get('/notificaciones/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Mis Notificaciones', response.data)


if __name__ == "__main__":
    unittest.main()

# Guía Rápida: Emails Dobles

## ¿Qué es?

Cada usuario tiene **2 emails**:
- **Email de Login**: para iniciar sesión (ej: `empleado@test.com`)
- **Email de Notificaciones**: donde recibe correos del sistema (ej: `tumail@gmail.com`)

---

## Setup Rápido (5 minutos)

### 1. Configurar `.env`

```properties
COLABORADOR_EMAIL=tumail@gmail.com
```

### 2. Recrear BD con usuarios

```bash
python -c "from app import create_app; from app.models import db; app = create_app(); db.drop_all()" && python crear_usuario_final.py
```

### 3. Iniciar app

```bash
python run.py
```

### 4. Login y Prueba

- **Login**: `empleado@test.com` / `123456`
- **Notificaciones llegan a**: `tumail@gmail.com` (lo que pusiste en `.env`)

---

## Cambiar Email de Notificaciones

### Por Usuario (Individual)

```python
from app import create_app
from app.models import db, Usuario

app = create_app()
with app.app_context():
    usuario = Usuario.query.filter_by(email='empleado@test.com').first()
    usuario.email_notificaciones = 'nuevo@email.com'
    db.session.commit()
    print(f"✅ Actualizado a: {usuario.email_notificaciones}")
```

### Todos los Usuarios (Global)

```python
from app import create_app
from app.models import db, Usuario

app = create_app()
with app.app_context():
    for u in Usuario.query.all():
        u.email_notificaciones = 'central@empresa.com'
    db.session.commit()
    print(f"✅ Todos actualizados a: central@empresa.com")
```

---

## Verificar Configuración

```python
from app import create_app
from app.models import db, Usuario
from app.utils.email_service import get_email_notificaciones

app = create_app()
with app.app_context():
    for u in Usuario.query.all():
        email_notif = get_email_notificaciones(u)
        print(f"{u.nombre}")
        print(f"  Login: {u.email}")
        print(f"  Notificaciones: {email_notif}")
```

---

## Notas Importantes

1. ✅ **Retrocompatible**: Usuarios sin `email_notificaciones` usan `email` automáticamente
2. ✅ **Configurable por usuario**: Cada uno puede tener distinto email de notificaciones
3. ✅ **Centralizado en `.env`**: `COLABORADOR_EMAIL` define el default para nuevos usuarios
4. ✅ **Sin cambios de código**: Solo configura `.env` y listo

---

## Documentación Completa

Ver: `docs/CONFIGURACION_EMAILS_DOBLES.md`

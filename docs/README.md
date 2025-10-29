# 📚 Documentación del Sistema de Incapacidades

**Última actualización:** Octubre 2025  
**Versión consolidada:** Pre-Release

---

## 📂 Estructura de la Documentación

La documentación ha sido **consolidada en 4 archivos principales** para facilitar su lectura y mantenimiento:

### 1. 📘 GUIA_COMPLETA.md
**Documento principal del sistema**

Contenido:
- ✅ Inicio rápido (5 minutos)
- ✅ Arquitectura del sistema completa
- ✅ 16 Casos de uso implementados (UC1-UC16)
- ✅ Roles y permisos detallados
- ✅ Manual de usuario resumido
- ✅ Configuración básica
- ✅ Flujos completos de trabajo
- ✅ Sistema de notificaciones
- ✅ Comandos útiles
- ✅ Métricas del proyecto

**Para quién:** Desarrolladores, Product Owners, nuevos miembros del equipo

**Leer primero:** Este documento

---

### 2. ⚙️ CONFIGURACION_TECNICA.md
**Guía técnica de deployment y configuración**

Contenido:
- ⚙️ Requisitos del sistema
- ⚙️ Instalación detallada paso a paso
- ⚙️ Variables de entorno (.env completo)
- ⚙️ Configuración de base de datos
- ⚙️ Sistema de emails (Mailtrap, SendGrid, Gmail)
- ⚙️ Scheduler y tareas automáticas (UC6)
- ⚙️ Deployment en producción (Gunicorn, Nginx, Docker)
- ⚙️ Monitoreo y logs
- ⚙️ Seguridad (HTTPS, rate limiting, headers)
- ⚙️ Troubleshooting avanzado

**Para quién:** DevOps, Administradores de sistemas, Desarrolladores backend

**Cuándo leer:** Al configurar entorno de desarrollo/producción

---

### 3. 📖 MANUAL_USUARIO.md
**Guía para usuarios finales**

Contenido:
- 📖 Introducción al sistema
- 📖 Acceso y credenciales
- 📖 Guía paso a paso para Colaboradores:
  - Registrar incapacidad
  - Consultar estado
  - Cargar documentos solicitados
- 📖 Guía paso a paso para Auxiliares RRHH:
  - Validar documentación
  - Solicitar documentos (UC6)
  - Aprobar/Rechazar
- 📖 Preguntas frecuentes
- 📖 Glosario de términos
- 📖 Soporte técnico

**Para quién:** Colaboradores, Personal de Gestión Humana

**Cuándo leer:** Al usar el sistema por primera vez

---

### 4. 📄 CASOS_DE_USO.md
**Especificación detallada de casos de uso**

Contenido:
- 📄 16 casos de uso completos (UC1-UC16)
- 📄 Organizados en 5 módulos:
  - Módulo de Registro (UC1-UC3)
  - Módulo de Validación (UC4-UC7)
  - Módulo de Seguimiento (UC8-UC11)
  - Módulo de Conciliación (UC12-UC14)
  - Módulo de Gestión Documental (UC15-UC16)
- 📄 Cada UC incluye:
  - Propiedades (actores, propósito, precondiciones)
  - Flujo normal (pasos detallados)
  - Postcondiciones
  - Excepciones (E1-E6)
  - Frecuencia/Importancia/Urgencia

**Para quién:** Analistas, QA, Desarrolladores, Documentación de requisitos

**Cuándo leer:** Para entender requisitos funcionales específicos

---

## 🗂️ Archivos Eliminados (Consolidados)

Los siguientes archivos fueron **consolidados** en los 4 documentos principales:

### Eliminados:
- ❌ `BUG_FIX_ALERTAS.md` → Consolidado en CONFIGURACION_TECNICA.md (sección Troubleshooting)
- ❌ `CONTROL_EMAILS.md` → Consolidado en CONFIGURACION_TECNICA.md (sección Emails)
- ❌ `DECISION_ARQUITECTURA_ROLES.md` → Consolidado en GUIA_COMPLETA.md (sección Roles)
- ❌ `EMAILS_DOBLES_GUIA_RAPIDA.md` → Consolidado en CONFIGURACION_TECNICA.md
- ❌ `ESTADO_PROYECTO.md` → Consolidado en GUIA_COMPLETA.md (sección Estado)
- ❌ `INTEGRACIONES_UC2_UC15.md` → Consolidado en GUIA_COMPLETA.md (sección Arquitectura)
- ❌ `MEJORAS_UX_CLIENTE.md` → Consolidado en GUIA_COMPLETA.md (UC1)
- ❌ `RESUMEN_UC1_COMPLETO.md` → Consolidado en CASOS_DE_USO.md (UC1)
- ❌ `roles_permisos.md` → Consolidado en GUIA_COMPLETA.md (sección Roles)
- ❌ `SOLUCION_PROBLEMAS.md` → Consolidado en CONFIGURACION_TECNICA.md (Troubleshooting)
- ❌ `TAREA2_UC6_UTILIDADES.md` → Consolidado en CASOS_DE_USO.md (UC6)
- ❌ `TAREA3_UC6_SERVICIOS.md` → Consolidado en CASOS_DE_USO.md (UC6)
- ❌ `UC2_RESUMEN_FINAL.md` → Consolidado en CASOS_DE_USO.md (UC2)
- ❌ `UC6_BUGS_FIXED.md` → Consolidado en CONFIGURACION_TECNICA.md
- ❌ `UC6_IMPLEMENTACION.md` → Consolidado en CASOS_DE_USO.md (UC6)
- ❌ `UC6_SOLICITUD_DOCUMENTOS.md` → Consolidado en CASOS_DE_USO.md (UC6)

**Total eliminados:** 16 archivos → **Consolidados en 4 archivos**

---

## 🎯 Guía de Lectura Recomendada

### Para Nuevos Desarrolladores:
1. **GUIA_COMPLETA.md** (completo) - Entender el sistema
2. **CONFIGURACION_TECNICA.md** (Setup) - Configurar entorno
3. **CASOS_DE_USO.md** (según necesidad) - Profundizar en UC específico

### Para DevOps/SysAdmin:
1. **CONFIGURACION_TECNICA.md** (completo) - Deployment
2. **GUIA_COMPLETA.md** (Arquitectura) - Entender componentes

### Para Product Owner/Analistas:
1. **CASOS_DE_USO.md** (completo) - Requisitos funcionales
2. **GUIA_COMPLETA.md** (Estado del proyecto) - Progreso

### Para Usuarios Finales:
1. **MANUAL_USUARIO.md** (completo) - Cómo usar el sistema

### Para QA/Testing:
1. **CASOS_DE_USO.md** (Excepciones) - Casos de prueba
2. **GUIA_COMPLETA.md** (Flujos) - Escenarios E2E

---

## 🔄 Mantenimiento de la Documentación

### Cuándo Actualizar Cada Archivo:

**GUIA_COMPLETA.md:**
- Nuevo caso de uso implementado
- Cambio en arquitectura
- Nuevo rol o permiso
- Actualización de métricas de completitud

**CONFIGURACION_TECNICA.md:**
- Nueva variable de entorno
- Cambio en deployment
- Nueva dependencia
- Actualización de seguridad

**MANUAL_USUARIO.md:**
- Cambio en UI/UX
- Nuevo flujo de usuario
- Nueva FAQ

**CASOS_DE_USO.md:**
- Nuevo caso de uso
- Cambio en requisitos funcionales
- Nuevas excepciones

---


## 📞 Soporte

Si encuentras información faltante o desactualizada:
- Contacta al equipo de desarrollo
- Crea un issue en el repositorio
- Propone cambios vía pull request

---

**Fecha de consolidación:** Octubre 2025  
**Versión:** Pre-Release 1.0  
**Consolidado por:** Sistema automatizado de documentación

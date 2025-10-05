# Checklist de Pruebas Manuales

## Autenticacion
- [X] Login con usuario colaborador funciona
- [X] Login con usuario auxiliar funciona
- [X] Login con credenciales incorrectas muestra error
- [X] Logout funciona correctamente
- [ ] Rutas protegidas redirigen a login

## Colaborador - Registro (UC1 + UC2)
- [X] Formulario de registro se muestra correctamente
- [X] Seleccionar tipo de incapacidad funciona
- [ ] Fechas se validan correctamente
- [X] Calculo de dias es automatico y correcto
- [X] Upload de certificado funciona
- [X] Upload de epicrisis funciona
- [ ] Validacion de formatos de archivo funciona
- [ ] Mensaje de exito se muestra
- [X] Incapacidad aparece en lista

## Colaborador - Consulta (UC3 + UC4)
- [X] Lista de incapacidades se muestra
- [X] Estados se muestran con colores correctos
- [X] Click en "Ver Detalle" funciona
- [X] Detalle muestra toda la informacion
- [ ] Documentos se pueden descargar
- [X] Si hay rechazo, se muestra el motivo

## Auxiliar - Dashboard (UC5)
- [ ] Dashboard muestra estadisticas
- [X] Lista de pendientes se muestra
- [ ] Lista de en revision se muestra
- [ ] Botones de accion funcionan

## Auxiliar - Validacion (UC6 + UC10)
- [X] Vista de validacion se carga
- [ ] Validacion automatica funciona
- [X] Checklist manual funciona
- [ ] Documentos se pueden ver/descargar
- [X] Marcar como completa cambia estado
- [ ] Solicitar documentos funciona

## Auxiliar - Aprobacion (UC7)
- [X] Vista de aprobacion/rechazo se carga
- [X] Opcion aprobar funciona
- [X] Opcion rechazar requiere motivo
- [X] Confirmaciones funcionan
- [X] Estados se actualizan correctamente

## Sistema
- [ ] Notificaciones flash se muestran
- [ ] Navbar funciona correctamente
- [ ] Diseño es responsive
- [ ] No hay errores en consola del navegador
- [ ] No hay errores en logs del servidor
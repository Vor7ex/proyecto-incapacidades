// Funciones globales del sistema

// Formatear fecha para mostrar
function formatearFecha(fecha) {
  const opciones = { year: 'numeric', month: 'long', day: 'numeric' };
  return new Date(fecha).toLocaleDateString('es-ES', opciones);
}

// Confirmar acción
function confirmarAccion(mensaje) {
  return confirm(mensaje);
}

// Validar formato de archivo
function validarArchivo(input) {
  const archivo = input.files[0];
  if (!archivo) return false;

  const extensionesPermitidas = ['pdf', 'jpg', 'jpeg', 'png'];
  const extension = archivo.name.split('.').pop().toLowerCase();

  if (!extensionesPermitidas.includes(extension)) {
    alert('Formato de archivo no permitido. Use PDF, JPG o PNG');
    input.value = '';
    return false;
  }

  const tamanoMaxMB = 10;
  const tamanoMB = archivo.size / 1024 / 1024;

  if (tamanoMB > tamanoMaxMB) {
    alert(`El archivo no debe superar ${tamanoMaxMB} MB`);
    input.value = '';
    return false;
  }

  return true;
}

// Auto-cerrar alertas después de 5 segundos
document.addEventListener('DOMContentLoaded', function() {
  const alertas = document.querySelectorAll('.alert:not(.alert-warning):not(.alert-info)');
  alertas.forEach(alerta => {
    setTimeout(() => {
      const bsAlert = new bootstrap.Alert(alerta);
      bsAlert.close();
    }, 5000);
  });
});
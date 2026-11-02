const enlaces = document.querySelectorAll('.sidebar-menu a');
const secciones = document.querySelectorAll('.seccion-contenido');

enlaces.forEach(enlace => {
  enlace.addEventListener('click', function(evento) {
    evento.preventDefault();

    // Oculta todas las secciones
    secciones.forEach(sec => sec.classList.remove('activa'));

    // Obtiene la sección destino a través del href
    const targetId = evento.currentTarget.getAttribute('href');
    const seccionDestino = document.querySelector(targetId);

    if (seccionDestino) {
      seccionDestino.classList.add('activa');
    }
  });
});
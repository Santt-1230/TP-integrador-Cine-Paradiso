const enlaces = document.querySelectorAll('.sidebar-menu a');
const secciones = document.querySelectorAll('.seccion-contenido');

enlaces.forEach(enlace => {
  enlace.addEventListener('click', function(evento) {
    evento.preventDefault();

    secciones.forEach(sec => sec.classList.remove('activa'));

    const targetId = evento.currentTarget.getAttribute('href');
    const seccionDestino = document.querySelector(targetId);

    if (seccionDestino) {
      seccionDestino.classList.add('activa');
    }
  });
});

const links = document.querySelectorAll('.sidebar-menu a');

  links.forEach(link => {
      link.addEventListener('click', function() {
          document.querySelector('.sidebar-menu a.active')?.classList.remove('active');
            
          this.classList.add('active');
      });
  });
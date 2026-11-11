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


document.addEventListener('click', function (evento) {
    const desplegable = document.querySelector('.desplegable');
    if (desplegable && !desplegable.contains(evento.target)) {
        desplegable.removeAttribute('open');
    }
});

document.querySelectorAll('main .success').forEach(function(aviso){
  setTimeout(function() { aviso.remove(); }, 5000);
});
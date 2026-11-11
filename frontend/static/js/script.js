document.addEventListener('DOMContentLoaded', () => {
    const btnToggle = document.getElementById('btn-toggle-clave');
    const contenedor = document.getElementById('contenedor-cambiar-clave');
    const flecha = document.getElementById('flecha-clave');

    if (btnToggle && contenedor) {
        btnToggle.addEventListener('click', () => {
            const abierto = contenedor.classList.toggle('abierto');
            if (flecha) flecha.textContent = abierto ? '▲' : '▼';
        });
    }

    const form = document.getElementById('form-cambiar-clave');
    if (form) {
        form.addEventListener('submit', (e) => {
            const nueva = document.getElementById('nueva_clave').value;
            const confirmar = document.getElementById('confirmar_clave').value;
            const mensaje = document.getElementById('mensaje-clave');

            if (nueva !== confirmar) {
                e.preventDefault();
                mensaje.className = 'mensaje-alerta error';
                mensaje.style.display = 'block';
                mensaje.textContent = 'Las contraseñas nuevas no coinciden.';
            }
        });
    }
});

document.addEventListener('DOMContentLoaded', () => {
    // Desplegable de cambiar contraseña
    const btnToggle = document.getElementById('btn-toggle-clave');
    const contenedorClave = document.getElementById('contenedor-cambiar-clave');
    const flecha = document.getElementById('flecha-clave');

    if (btnToggle && contenedorClave) {
        btnToggle.addEventListener('click', () => {
            const estaOculto = contenedorClave.style.display === 'none';
            contenedorClave.style.display = estaOculto ? 'block' : 'none';
            if (flecha) flecha.textContent = estaOculto ? '▲' : '▼';
        });
    }

    // Aviso si las contraseñas nuevas no coinciden (no envía nada)
    const formClave = document.getElementById('form-cambiar-clave');
    if (formClave) {
        formClave.addEventListener('submit', (e) => {
            const nueva = document.getElementById('nueva_clave').value;
            const confirmar = document.getElementById('confirmar_clave').value;
            const mensaje = document.getElementById('mensaje-clave');

            if (nueva !== confirmar) {
                e.preventDefault();
                mensaje.className = 'mensaje-alerta error';
                mensaje.style.display = 'block';
                mensaje.textContent = 'Las contraseñas nuevas no coinciden.';
            }
        });
    }

    // Confirmación antes de darse de baja
    const formBaja = document.getElementById('form-baja-cuenta');
    if (formBaja) {
        formBaja.addEventListener('submit', (e) => {
            const ok = confirm('¿Estás seguro de que querés darte de baja del servicio? Esta acción no se puede deshacer.');
            if (!ok) e.preventDefault();
        });
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const boton = document.getElementById('btn-toggle-clave');
    const contenedor = document.getElementById('contenedor-cambiar-clave');
    const flecha = document.getElementById('flecha-clave');

    if (boton && contenedor) {
        boton.addEventListener('click', () => {
            const abierto = contenedor.style.display !== 'none';
            contenedor.style.display = abierto ? 'none' : 'block';
            if (flecha) flecha.textContent = abierto ? '▼' : '▲';
        });
    }

    const form = document.getElementById('form-cambiar-clave');
    if (form) {
        form.addEventListener('submit', (e) => {
            const nueva = document.getElementById('nueva_clave').value;
            const confirmar = document.getElementById('confirmar_clave').value;
            const mensaje = document.getElementById('mensaje-clave');

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
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

document.addEventListener('DOMContentLoaded', function () {
    // 1. Toggle Mostrar / Ocultar Formulario de Editar Datos
    const btnEditar = document.getElementById('btn-toggle-editar');
    const btnCancelar = document.getElementById('btn-cancelar-editar');
    const vistaDatos = document.getElementById('vista-datos-perfil');
    const formEditar = document.getElementById('form-editar-perfil');

    if (btnEditar && btnCancelar) {
        btnEditar.addEventListener('click', function () {
            vistaDatos.style.display = 'none';
            formEditar.style.display = 'block';
        });

        btnCancelar.addEventListener('click', function () {
            formEditar.style.display = 'none';
            vistaDatos.style.display = 'block';
        });
    }

    // 2. Toggle Contraer / Descontraer Cambiar Contraseña
    const btnClave = document.getElementById('btn-toggle-clave');
    const contenedorClave = document.getElementById('contenedor-cambiar-clave');
    const flechaClave = document.getElementById('flecha-clave');

    if (btnClave) {
        btnClave.addEventListener('click', function () {
            contenedorClave.classList.toggle('abierto');
            if (contenedorClave.classList.contains('abierto')) {
                flechaClave.textContent = '▲';
            } else {
                flechaClave.textContent = '▼';
            }
        });
    }
});

// 3. Función para Ver / Ocultar Contraseña con el Ojito
function toggleVisibilidadPassword(idInput, icono) {
    const input = document.getElementById(idInput);
    if (input.type === 'password') {
        input.type = 'text';
        icono.classList.remove('bi-eye');
        icono.classList.add('bi-eye-slash');
    } else {
        input.type = 'password';
        icono.classList.remove('bi-eye-slash');
        icono.classList.add('bi-eye');
    }
}

document.addEventListener('click', function (evento) {
    const desplegable = document.querySelector('.desplegable');
    if (desplegable && !desplegable.contains(evento.target)) {
        desplegable.removeAttribute('open');
    }
});

document.querySelectorAll('main .success').forEach(function(aviso){
  setTimeout(function() { aviso.remove(); }, 5000);
});
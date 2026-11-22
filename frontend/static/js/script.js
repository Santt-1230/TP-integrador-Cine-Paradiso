document.addEventListener('DOMContentLoaded', () => {
    // 1. Alternar edición de datos del perfil
    const btnEditar = document.getElementById('btn-toggle-editar');
    const btnCancelar = document.getElementById('btn-cancelar-editar');
    const vistaDatos = document.getElementById('vista-datos-perfil');
    const formEditar = document.getElementById('form-editar-perfil');

    if (btnEditar && btnCancelar && vistaDatos && formEditar) {
        btnEditar.addEventListener('click', () => {
            vistaDatos.style.display = 'none';
            formEditar.style.display = 'block';
        });

        btnCancelar.addEventListener('click', () => {
            formEditar.style.display = 'none';
            vistaDatos.style.display = 'block';
        });
    }

    // 2. Confirmación antes de darse de baja
    const formBaja = document.getElementById('form-baja-cuenta');
    if (formBaja) {
        formBaja.addEventListener('submit', (e) => {
            const ok = confirm('¿Estás seguro de que querés darte de baja del servicio? Esta acción no se puede deshacer.');
            if (!ok) e.preventDefault();
        });
    }

    // 3. Ocultar automáticamente avisos de éxito tras 5 segundos
    document.querySelectorAll('main .success').forEach((aviso) => {
        setTimeout(() => aviso.remove(), 5000);
    });
});

// Cerrar menú desplegable al hacer clic fuera
document.addEventListener('click', (evento) => {
    const desplegable = document.querySelector('.desplegable');
    if (desplegable && !desplegable.contains(evento.target)) {
        desplegable.removeAttribute('open');
    }
});
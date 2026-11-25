
document.querySelectorAll('form[data-accion]').forEach(form => {
    form.addEventListener('submit', e => {
        const { accion, numeroSala } = form.dataset;

        if (!confirm(`¿Seguro que querés ${accion} la sala ${numeroSala}?`)) {
            e.preventDefault();
        }
    });
});
document.addEventListener('DOMContentLoaded', function () {
    const formulario = document.querySelector('.formulario-sala');
    if (!formulario) {
        return;
    }

    const contenedor = document.getElementById('filas-container');
    const botonAgregar = document.getElementById('agregar-fila');
    const plantilla = document.getElementById('plantilla-fila');

    function actualizarBotones() {
        const filas = contenedor.querySelectorAll('.fila-formulario');
        filas.forEach(fila => {
            fila.querySelector('.eliminar-fila').disabled = filas.length === 1;
        });
    }

    botonAgregar.addEventListener('click', function () {
        const nuevaFila = plantilla.content.firstElementChild.cloneNode(true);
        contenedor.appendChild(nuevaFila);
        actualizarBotones();
        nuevaFila.querySelector('input[name="fila"]').focus();
    });

    contenedor.addEventListener('click', function (evento) {
        const boton = evento.target.closest('.eliminar-fila');
        if (!boton || boton.disabled) {
            return;
        }
        boton.closest('.fila-formulario').remove();
        actualizarBotones();
    });

    formulario.addEventListener('submit', function () {
        const boton = formulario.querySelector('button[type="submit"]');
        boton.disabled = true;
        boton.textContent = 'Guardando...';
    });

    actualizarBotones();
});
document.addEventListener('DOMContentLoaded', function () {
    const filtrosLocal = document.querySelectorAll('.filtro-local__select');

    filtrosLocal.forEach(filtro => {
        filtro.addEventListener('change', function () {
            this.form.submit();
        });
    });
});

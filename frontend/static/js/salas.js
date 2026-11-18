
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

    const numeroSala = document.getElementById('numero_sala');
    const contenedor = document.getElementById('filas-container');
    const botonAgregar = document.getElementById('agregar-fila');

    function validarNumeroSala() {
        const valor = numeroSala.value.trim();

        if (valor === '' || !Number.isInteger(Number(valor)) || Number(valor) <= 0) {
            alert('Ingresá un número de sala entero mayor a cero.');
            numeroSala.focus();
            return false;
        }

        return true;
    }

    function validarFilas() {
        const filas = contenedor.querySelectorAll('.fila-formulario');
        const letras = [];

        if (filas.length === 0) {
            alert('La sala debe tener al menos una fila.');
            return false;
        }

        for (const fila of filas) {
            const inputLetra = fila.querySelector('input[name="fila"]');
            const inputCantidad = fila.querySelector('input[name="cantidad"]');

            const letra = inputLetra.value.trim();
            const cantidad = inputCantidad.value.trim();

            if (!/^[A-Z]$/.test(letra)) {
                alert('Cada fila debe tener una letra mayúscula de la A a la Z.');
                inputLetra.focus();
                return false;
            }

            if (letras.includes(letra)) {
                alert(`La fila ${letra} está repetida.`);
                inputLetra.focus();
                return false;
            }

            if (cantidad === '' || !Number.isInteger(Number(cantidad)) || Number(cantidad) <= 0) {
                alert(`Ingresá una cantidad válida de butacas para la fila ${letra}.`);
                inputCantidad.focus();
                return false;
            }

            letras.push(letra);
        }

        for (let i = 1; i < letras.length; i++) {
            if (letras[i] <= letras[i - 1]) {
                alert('Las filas deben estar ordenadas alfabéticamente.');
                return false;
            }
        }

        return true;
    }

    function actualizarFilas() {
        const filas = contenedor.querySelectorAll('.fila-formulario');

        filas.forEach(function (fila, indice) {
            const inputLetra = fila.querySelector('input[name="fila"]');
            const inputCantidad = fila.querySelector('input[name="cantidad"]');
            const etiquetaLetra = fila.querySelector('label[for^="fila_"]');
            const etiquetaCantidad = fila.querySelector('label[for^="cantidad_"]');
            const botonEliminar = fila.querySelector('.eliminar-fila');

            inputLetra.id = 'fila_' + indice;
            inputCantidad.id = 'cantidad_' + indice;

            if (etiquetaLetra) {
                etiquetaLetra.htmlFor = inputLetra.id;
            }

            if (etiquetaCantidad) {
                etiquetaCantidad.htmlFor = inputCantidad.id;
            }

            botonEliminar.disabled = filas.length === 1;
        });

        botonAgregar.disabled = filas.length >= 26;
    }

    botonAgregar.addEventListener('click', function () {
        const cantidadFilas = contenedor.querySelectorAll('.fila-formulario').length;

        if (cantidadFilas >= 26) {
            return;
        }

        const nuevaFila = document.createElement('div');
        nuevaFila.className = 'fila-formulario';

        nuevaFila.innerHTML = `
            <div class="campo-fila">
                <label>Letra</label>
                <input
                    type="text"
                    name="fila"
                    maxlength="1"
                    pattern="[A-Z]"
                    required>
            </div>

            <div class="campo-cantidad">
                <label>Butacas</label>
                <input
                    type="number"
                    name="cantidad"
                    min="1"
                    step="1"
                    value="10"
                    required>
            </div>

            <button type="button" class="eliminar-fila">
                Eliminar
            </button>
        `;

        contenedor.appendChild(nuevaFila);
        actualizarFilas();

        nuevaFila.querySelector('input[name="fila"]').focus();
    });

    contenedor.addEventListener('click', function (evento) {
        if (evento.target.classList.contains('eliminar-fila')) {
            const filas = contenedor.querySelectorAll('.fila-formulario');

            if (filas.length > 1) {
                evento.target.closest('.fila-formulario').remove();
                actualizarFilas();
            }
        }
    });

    formulario.addEventListener('submit', function (evento) {
        if (!validarNumeroSala() || !validarFilas()) {
            evento.preventDefault();
            return;
        }

        const boton = formulario.querySelector('button[type="submit"]');
        boton.disabled = true;
        boton.textContent = 'Guardando...';
    });

    actualizarFilas();
});

document.addEventListener('DOMContentLoaded', function () {
    const filtrosLocal = document.querySelectorAll('.filtro-local__select');

    filtrosLocal.forEach(filtro => {
        filtro.addEventListener('change', function () {
            this.form.submit();
        });
    });
});

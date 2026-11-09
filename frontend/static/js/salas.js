
document.addEventListener('DOMContentLoaded', function(){
    const botonesBaja = document.querySelectorAll('.boton-tabla--baja');

    botonesBaja.forEach(boton => {
        boton.addEventListener('click', function(evento){
            const formulario = this.closest('form');
            const numeroSala = formulario.dataset.numeroSala;

            const confirmar = confirm(`¿Dar de baja la sala ${numeroSala}?`);
            
            if (!confirmar){
                evento.preventDefault();
            }
        });
    });
});


document.addEventListener('DOMContentLoaded', function() {
    const formulario = document.querySelector('.formulario-sala');

    if (!formulario) {
        return;
    }

    const campos = ['capacidad', 'numero_sala'];

    function validarCampo(campo) {
        const input = document.getElementById(campo);

        if (!input) {
            return true;
        }

        const error = document.getElementById(`error-${campo}`);
        const valor = input.value.trim();

        let mensaje = '';

        if (valor === '') {
            mensaje = 'Este campo es obligatorio.';
        } else if (!Number.isInteger(Number(valor)) || Number(valor) <= 0) {
            mensaje = 'Ingresá un número entero mayor a cero.';
        }

        error.textContent = mensaje;

        return mensaje === '';
    }

    campos.forEach(function(campo) {
        const input = document.getElementById(campo);
        const error = document.getElementById(`error-${campo}`);

        if (input && error) {
            error.textContent = '';
            input.addEventListener('input', function() {
                validarCampo(campo);
            });
        }
    });

    formulario.addEventListener('submit', function(evento) {
        let formularioValido = true;

        campos.forEach(function(campo) {
            if (!validarCampo(campo)) {
                formularioValido = false;
            }
        });

        if (!formularioValido) {
            evento.preventDefault();
        }
    });
});




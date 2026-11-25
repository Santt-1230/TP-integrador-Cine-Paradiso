document.addEventListener("DOMContentLoaded", function () {

    const modal = document.getElementById("modal-editar-usuario");

    const cerrarModal = document.getElementById("cerrar-modal-usuario");

    const cancelarEdicion = document.getElementById("cancelar-edicion-usuario");

    const formulario = document.getElementById("form-editar-usuario");

    const errorFormulario = document.getElementById("error-formulario-usuario");

    const guardarUsuario = document.getElementById("guardar-usuario");


    if (modal && modal.dataset.reabrir === "true") {

        modal.showModal();

        const nombre = document.getElementById("usuario-nombre");

        if (nombre) {
            nombre.focus();
        }

    }


    function cerrar() {

        if (modal && modal.open) {
            modal.close();
        }

    }

    if (cerrarModal) {
        cerrarModal.addEventListener("click", cerrar);
    }

    if (cancelarEdicion) {
        cancelarEdicion.addEventListener("click", cerrar);
    }

    if (modal) {

        modal.addEventListener("click", function (evento) {

            if (evento.target === modal) {
                cerrar();
            }

        });

    }


    if (formulario) {

        formulario.addEventListener("submit", function (evento) {

            const nombre = document.getElementById("usuario-nombre");

            const email = document.getElementById("usuario-email");

            const rol = document.getElementById("usuario-rol");


            errorFormulario.hidden = true;
            errorFormulario.textContent = "";


            if (!nombre.value.trim()) {

                evento.preventDefault();

                mostrarError("El nombre es obligatorio.");

                nombre.focus();

                return;

            }


            if (!email.value.trim() || !email.validity.valid) {

                evento.preventDefault();

                mostrarError("Ingresá un correo electrónico válido.");

                email.focus();

                return;

            }


            if (!["cliente", "administrador"].includes(rol.value)) {

                evento.preventDefault();

                mostrarError("Seleccioná un rol válido.");

                rol.focus();

                return;

            }


            if (guardarUsuario) {

                guardarUsuario.disabled = true;

                guardarUsuario.textContent = "Guardando...";

            }

        });

    }


    function mostrarError(mensaje) {

        errorFormulario.textContent = mensaje;

        errorFormulario.hidden = false;

    }

});
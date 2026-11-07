'use strict';

document.addEventListener('DOMContentLoaded', () => {

    // Puede haber más de un formulario:
    // uno en el header y otro en login.html.
    document.querySelectorAll('.form-login').forEach(formulario => {

        formulario.addEventListener('submit', async (evento) => {
            evento.preventDefault();

            const email = formulario.elements.email.value.trim();
            const contrasena = formulario.elements.contrasena.value;

            const boton = formulario.querySelector('button[type="submit"]');

            // Crear un espacio para mostrar errores.
            let feedback = formulario.querySelector('.mensaje-error');

            if (!feedback) {
                feedback = document.createElement('p');
                feedback.classList.add('mensaje-error');
                formulario.prepend(feedback);
            }

            feedback.textContent = '';

            boton.disabled = true;

            try {
                const respuesta = await fetch(
                'http://127.0.0.1:5000/api/auth/login',
                {
                    method: 'POST',
                    credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    email: email,
                    contrasena: contrasena
                })
            });

            // Leemos primero la respuesta como texto.
            const texto = await respuesta.text();

            let datos;

            try {
                datos = JSON.parse(texto);
            } catch (error) {
                console.error('El servidor no devolvió JSON:', {
                    status: respuesta.status,
                    url: respuesta.url,
                    contentType: respuesta.headers.get('content-type'),
                    respuesta: texto
                });

                    throw new Error(
                        `El servidor devolvió una respuesta inesperada (HTTP ${respuesta.status}). Revisá la consola.`
                    );
                }

                if (!respuesta.ok) {
                    throw new Error(
                        datos.mensaje || datos.error || 'No se pudo iniciar sesión.'
                    );
                }

                // Obtener el rol del usuario autenticado.
                const rol = datos.usuario.rol.toLowerCase();

                // Redireccionar según el rol.
                if (rol === 'admin' || rol === 'administrador') {
                    window.location.href = '/admin';
                } else {
                    window.location.href = '/';
                }

            } catch (error) {
                feedback.textContent = error.message;
            } finally {
                boton.disabled = false;
            }

        });

    });

});
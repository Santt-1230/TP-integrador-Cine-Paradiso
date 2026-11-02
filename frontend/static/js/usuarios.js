'use strict';


document.addEventListener('DOMContentLoaded', () => {
    configurarBusquedaUsuarios();
    configurarEdicionUsuarios();
});

function configurarBusquedaUsuarios() {
    const campo = document.getElementById('buscar-usuario');
    const tabla = document.getElementById('tabla-usuarios');
    if (!campo || !tabla) return;

    campo.addEventListener('input', () => {
        const termino = campo.value.trim().toLocaleLowerCase('es');
        tabla.querySelectorAll('tbody tr').forEach((fila) => {
            const coincide = fila.textContent.toLocaleLowerCase('es').includes(termino);
            fila.hidden = !coincide;
        });
    });
}

function obtenerTokenCSRF() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta?.content) return meta.content;

    const input = document.querySelector('input[name="csrf_token"]');
    if (input?.value) return input.value;

    return '';
}

async function leerRespuestaJson(respuesta) {
    const tipoContenido = respuesta.headers.get('content-type') || '';
    if (!tipoContenido.includes('application/json')) {
        throw new Error(
            'El servidor no devolvió JSON. Revisá la ruta, la sesión y los permisos de administrador.'
        );
    }
    return respuesta.json();
}

function configurarEdicionUsuarios() {
    const dialogo = document.getElementById('dialog-editar-usuario');
    const formulario = document.getElementById('form-editar-usuario');
    if (!dialogo || !formulario) return;

    const apiBase = formulario.dataset.apiBase || '/admin/usuarios';
    const idInput = document.getElementById('usuario-id');
    const nombreInput = document.getElementById('usuario-nombre');
    const emailInput = document.getElementById('usuario-email');
    const rolInput = document.getElementById('usuario-rol');
    const feedback = document.getElementById('usuario-feedback');
    const botonGuardar = formulario.querySelector('button[type="submit"]');

    if (!idInput || !nombreInput || !emailInput || !rolInput || !feedback || !botonGuardar) {
        console.error('El formulario de edición de usuarios no tiene todos los campos esperados.');
        return;
    }

    const mostrarMensaje = (mensaje, esError = false) => {
        feedback.textContent = mensaje;
        feedback.setAttribute('role', esError ? 'alert' : 'status');
    };

    document.querySelectorAll('[data-edit-user]').forEach((boton) => {
        boton.addEventListener('click', async () => {
            const id = boton.dataset.editUser;
            if (!id) {
                mostrarMensaje('No se encontró el identificador del usuario.', true);
                return;
            }

            idInput.value = id;
            nombreInput.value = boton.dataset.userName || '';
            emailInput.value = boton.dataset.userEmail || '';
            rolInput.value = boton.dataset.userRole || 'cliente';
            mostrarMensaje('Consultando los datos actualizados...');

            if (typeof dialogo.showModal === 'function') {
                dialogo.showModal();
            } else {
                mostrarMensaje('Este navegador no permite abrir el formulario de edición.', true);
                return;
            }

            try {
                const respuesta = await fetch(
                    `${apiBase}/${encodeURIComponent(id)}/editar`,
                    {
                        method: 'GET',
                        credentials: 'same-origin',
                        headers: { Accept: 'application/json' }
                    }
                );
                const datos = await leerRespuestaJson(respuesta);

                if (!respuesta.ok) {
                    throw new Error(datos.error || 'No se pudo obtener el usuario.');
                }

                const usuario = datos.usuario || datos;
                nombreInput.value = usuario.nombre ?? nombreInput.value;
                emailInput.value = usuario.email ?? emailInput.value;
                rolInput.value = usuario.rol ?? rolInput.value;
                mostrarMensaje('');
            } catch (error) {
                
                mostrarMensaje(error.message || 'No se pudieron cargar los datos.', true);
            }
        });
    });

    document.querySelectorAll('[data-close-dialog]').forEach((boton) => {
        boton.addEventListener('click', () => dialogo.close());
    });

    formulario.addEventListener('submit', async (evento) => {
        evento.preventDefault();

        const id = idInput.value.trim();
        const payload = {
            nombre: nombreInput.value.trim(),
            email: emailInput.value.trim(),
            rol: rolInput.value
        };

        if (!id) {
            mostrarMensaje('No se identificó qué usuario se quiere modificar.', true);
            return;
        }
        if (!payload.nombre || !payload.email || !payload.rol) {
            mostrarMensaje('Completá todos los campos.', true);
            return;
        }

        botonGuardar.disabled = true;
        mostrarMensaje('Guardando cambios...');

        const headers = {
            'Content-Type': 'application/json',
            Accept: 'application/json'
        };
        const csrfToken = obtenerTokenCSRF();
        if (csrfToken) headers['X-CSRFToken'] = csrfToken;

        try {
            const respuesta = await fetch(
                `${apiBase}/${encodeURIComponent(id)}/editar`,
                {
                    method: 'PATCH',
                    credentials: 'same-origin',
                    headers,
                    body: JSON.stringify(payload)
                }
            );
            const datos = await leerRespuestaJson(respuesta);

            if (!respuesta.ok) {
                throw new Error(datos.error || 'No se pudo actualizar el usuario.');
            }

            mostrarMensaje(datos.message || 'Usuario actualizado correctamente.');
            window.setTimeout(() => window.location.reload(), 700);
        } catch (error) {
            mostrarMensaje(error.message || 'Ocurrió un error al guardar.', true);
        } finally {
            botonGuardar.disabled = false;
        }
    });
}

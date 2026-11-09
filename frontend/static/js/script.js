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

  document.addEventListener('DOMContentLoaded', () => {
    const formBaja = document.getElementById('form-baja-cuenta');

    if (formBaja) {
        formBaja.addEventListener('submit', async (e) => {
            e.preventDefault();

            const confirmar = confirm('¿Estás seguro de que querés darte de baja del servicio? Esta acción no se puede deshacer.');
            if (!confirmar) return;

            const comentario = document.getElementById('comentario-baja').value;

            try {
                const response = await fetch('http://127.0.0.1:5000/api/usuarios/baja', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    credentials: 'include', 
                    body: JSON.stringify({ comentario: comentario })
                });

                const data = await response.json();

                if (response.ok) {
                    alert('Tu cuenta y servicio han sido dados de baja con éxito.');
                    // Redirige al inicio o al login
                    window.location.href = '/';
                } else {
                    alert(data.message || 'No se pudo procesar la solicitud de baja.');
                }
            } catch (error) {
                console.error('Error al solicitar la baja:', error);
                alert('Ocurrió un error de conexión.');
            }
        });
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const btnToggle = document.getElementById('btn-toggle-clave');
    const contenedorClave = document.getElementById('contenedor-cambiar-clave');
    const flecha = document.getElementById('flecha-clave');

    if (btnToggle && contenedorClave) {
        btnToggle.addEventListener('click', () => {
            const estaOculto = contenedorClave.style.display === 'none';
            
            // Alternar visibilidad
            contenedorClave.style.display = estaOculto ? 'block' : 'none';
            
            // Cambiar la dirección de la flecha
            if (flecha) {
                flecha.textContent = estaOculto ? '▲' : '▼';
            }
        });
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const formClave = document.getElementById('form-cambiar-clave');

    if (formClave) {
        formClave.addEventListener('submit', async (e) => {
            e.preventDefault();

            const claveActual = document.getElementById('clave_actual').value;
            const nuevaClave = document.getElementById('nueva_clave').value;
            const confirmarClave = document.getElementById('confirmar_clave').value;
            const mensajeDiv = document.getElementById('mensaje-clave');

            // 1. Validar que la nueva clave y su confirmación coincidan en el cliente
            if (nuevaClave !== confirmarClave) {
                mensajeDiv.style.display = 'block';
                mensajeDiv.className = 'mensaje-alerta error';
                mensajeDiv.textContent = 'Las contraseñas nuevas no coinciden.';
                return;
            }

            // 2. Enviar la petición al servidor backend
            try {
                const response = await fetch('http://127.0.0.1:5000/api/usuarios/cambiar-clave', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    credentials: 'include', // Incluye la sesión si usás cookies entre frontend y backend
                    body: JSON.stringify({
                        clave_actual: claveActual,
                        nueva_clave: nuevaClave
                    })
                });

                const data = await response.json();
                mensajeDiv.style.display = 'block';

                if (response.ok) {
                    mensajeDiv.className = 'mensaje-alerta exito';
                    mensajeDiv.textContent = '¡Contraseña actualizada con éxito!';
                    formClave.reset(); // Limpia los campos del formulario
                } else {
                    mensajeDiv.className = 'mensaje-alerta error';
                    mensajeDiv.textContent = data.message || 'Error al actualizar la contraseña.';
                }
            } catch (error) {
                console.error('Error al cambiar contraseña:', error);
                mensajeDiv.style.display = 'block';
                mensajeDiv.className = 'mensaje-alerta error';
                mensajeDiv.textContent = 'Ocurrió un error al conectar con el servidor.';
            }
        });
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('modal-qr');
    const imgQr = document.getElementById('img-modal-qr');
    const tituloModal = document.getElementById('titulo-modal-qr');
    const btnCerrar = document.querySelector('.cerrar-modal');

    // Escuchar clicks en botones de Ver QR
    document.querySelectorAll('.btn-ver-qr').forEach(btn => {
        btn.addEventListener('click', () => {
            const qrUrl = btn.getAttribute('data-qr-url');
            const compraId = btn.getAttribute('data-compra');
            
            imgQr.src = qrUrl;
            tituloModal.textContent = `Entrada Compra #${compraId}`;
            modal.style.display = 'flex';
        });
    });

    // Cerrar modal
    if (btnCerrar) {
        btnCerrar.addEventListener('click', () => modal.style.display = 'none');
    }
    
    window.addEventListener('click', (e) => {
        if (e.target === modal) modal.style.display = 'none';
    });
});
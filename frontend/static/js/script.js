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
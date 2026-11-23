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

(function () {
    function iniciarEstrellas() {
        const contenedor = document.getElementById("estrellas-interactivas");
        const inputNumero = document.getElementById("puntuacion-numero");
        const textoEstado = document.getElementById("texto-puntuacion");

        if (!contenedor || !inputNumero) return;

        const botones = contenedor.querySelectorAll(".btn-estrella");
        const etiquetas = {
            1: "1 / 5 — Muy malo",
            2: "2 / 5 — Malo",
            3: "3 / 5 — Regular",
            4: "4 / 5 — Muy bueno",
            5: "5 / 5 — Excelente"
        };

        function pintarEstrellas(cantidad, esPreview = false) {
            botones.forEach((btn) => {
                const valor = Number(btn.dataset.valor);
                const activa = valor <= cantidad;
                btn.classList.toggle("llena", activa && !esPreview);
                btn.classList.toggle("preview", activa && esPreview);
            });

            if (!esPreview && textoEstado) {
                textoEstado.textContent = etiquetas[cantidad] || "Elegí o escribí un puntaje";
            }
        }

        // Selección directa haciendo clic o pasando el mouse
        botones.forEach((btn) => {
            const valor = Number(btn.dataset.valor);

            btn.addEventListener("click", () => {
                inputNumero.value = valor;
                pintarEstrellas(valor);
            });

            btn.addEventListener("mouseenter", () => {
                pintarEstrellas(valor, true);
            });
        });

        contenedor.addEventListener("mouseleave", () => {
            const actual = parseInt(inputNumero.value, 10) || 0;
            pintarEstrellas(actual);
        });

        // Pintado automático al escribir o cambiar el número
        function actualizarDesdeInput() {
            const raw = inputNumero.value.trim();
            if (raw === "") {
                pintarEstrellas(0);
                return;
            }

            let valor = parseInt(raw, 10);
            if (Number.isNaN(valor)) {
                pintarEstrellas(0);
                return;
            }

            if (valor > 5) {
                valor = 5;
                inputNumero.value = 5;
            } else if (valor < 1) {
                valor = 1;
                inputNumero.value = 1;
            }

            pintarEstrellas(valor);
        }

        inputNumero.addEventListener("input", actualizarDesdeInput);
        inputNumero.addEventListener("change", actualizarDesdeInput);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", iniciarEstrellas);
    } else {
        iniciarEstrellas();
    }
})();
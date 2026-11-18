document.addEventListener("DOMContentLoaded", () => {
    const errorTemporal = document.querySelector("[data-error-temporal]");
    if (errorTemporal) {
        const url = new URL(window.location.href);
        url.searchParams.delete("checkout_expirado");
        window.history.replaceState({}, "", url);
        window.setTimeout(() => errorTemporal.remove(), 5000);
    }

    const formularioButacas = document.querySelector(".seleccion-butacas");
    if (formularioButacas) {
        const casillas = [...formularioButacas.querySelectorAll('input[name="butacas"]:not(:disabled)')];
        const aviso = document.querySelector("#aviso-seleccion-butacas");
        const contador = document.querySelector("#contador");
        const mostrarAviso = (mensaje) => {
            if (!aviso) return;
            aviso.textContent = mensaje;
            aviso.hidden = !mensaje;
        };

        casillas.forEach((casilla) => {
            casilla.addEventListener("change", () => {
                const elegidas = casillas.filter((item) => item.checked).length;
                if (contador) contador.textContent = elegidas;
                if (elegidas > 6) {
                    casilla.checked = false;
                    if (contador) contador.textContent = elegidas - 1;
                    mostrarAviso("Podés elegir hasta seis butacas.");
                    return;
                }
                mostrarAviso("");
            });
        });

        formularioButacas.addEventListener("submit", (event) => {
            const elegidas = casillas.filter((casilla) => casilla.checked).length;
            if (elegidas < 1 || elegidas > 6) {
                event.preventDefault();
                mostrarAviso("Elegí entre una y seis butacas para continuar.");
            }
        });
    }

    const formularioCheckout = document.querySelector(".checkout-form");
    if (!formularioCheckout) return;

    const totalContenedor = formularioCheckout.querySelector(".checkout-actions");
    const totalSalida = formularioCheckout.querySelector(".checkout-total-dinamico");
    const baseTotal = Number(totalContenedor?.dataset.baseTotal || 0);
    const formatoMoneda = new Intl.NumberFormat("es-AR", {
        style: "currency",
        currency: "ARS",
        maximumFractionDigits: 2,
    });

    const actualizarTotal = () => {
        let total = baseTotal;
        formularioCheckout.querySelectorAll('.servicio-checkout input[type="checkbox"]').forEach((casilla) => {
            if (!casilla.checked) return;
            const cantidadInput = formularioCheckout.querySelector(`[name="cantidad_${casilla.value}"]`);
            const cantidad = Math.max(1, Number(cantidadInput?.value || 1));
            total += Number(casilla.dataset.precio || 0) * cantidad;
        });
        if (totalSalida) totalSalida.textContent = formatoMoneda.format(total);
    };

    formularioCheckout.addEventListener("change", actualizarTotal);
    formularioCheckout.addEventListener("input", (event) => {
        if (event.target.matches('input[type="number"]')) actualizarTotal();
    });
    actualizarTotal();

    const paginaCheckout = document.querySelector(".checkout-pagina[data-checkout-duracion-segundos]");
    if (paginaCheckout) {
        const duracionSegundos = Number(paginaCheckout.dataset.checkoutDuracionSegundos);
        const expiraEnMs = Date.now() + duracionSegundos * 1000;
        const enlaceVolver = paginaCheckout.querySelector(":scope > a");

        const actualizarContador = () => {
            const segundos = Math.max(0, Math.ceil((expiraEnMs - Date.now()) / 1000));
            if (segundos === 0) {
                const destino = new URL(enlaceVolver.href, window.location.href);
                destino.searchParams.set("checkout_expirado", "1");
                window.location.replace(destino.toString());
                return;
            }
            window.setTimeout(actualizarContador, 1000);
        };

        actualizarContador();
    }
});
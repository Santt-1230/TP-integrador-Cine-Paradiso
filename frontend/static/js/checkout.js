
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

    let compraEnviandose = false;
    formularioCheckout.addEventListener("submit", (event) => {
        if (compraEnviandose) {
            event.preventDefault();
            return;
        }

        compraEnviandose = true;
        const botonCompra = formularioCheckout.querySelector('button[type="submit"]');
        if (botonCompra) {
            botonCompra.disabled = true;
            botonCompra.textContent = "Procesando compra…";
        }
    });

    const totalContenedor = formularioCheckout.querySelector(".checkout-actions");
    const totalSalida = formularioCheckout.querySelector(".checkout-total-dinamico");
    const subtotalEntradasSalida = document.querySelector(".checkout-subtotal-entradas");
    const descuentoSalida = formularioCheckout.querySelector(".checkout-descuento-dinamico");
    const lineaDescuento = formularioCheckout.querySelector(".checkout-descuento-linea");
    const selectorPromocion = formularioCheckout.querySelector('[name="id_promocion"]');
    const baseTotalCentavos = Math.round(Number(totalContenedor?.dataset.baseTotal || 0) * 100);
    const precioEntradaCentavos = Math.round(Number(totalContenedor?.dataset.precioEntrada || 0) * 100);
    const cantidadEntradas = formularioCheckout.querySelectorAll('input[name="butacas"]').length;
    const formatoMoneda = new Intl.NumberFormat("es-AR", {
        style: "currency",
        currency: "ARS",
        maximumFractionDigits: 2,
    });

    const actualizarTotal = () => {
        let subtotalServiciosCentavos = 0;
        let descuentoCentavos = 0;
        formularioCheckout.querySelectorAll('.servicio-checkout input[type="checkbox"]').forEach((casilla) => {
            if (!casilla.checked) return;
            const cantidadInput = formularioCheckout.querySelector(`[name="cantidad_${casilla.value}"]`);
            const cantidad = Math.max(1, Number(cantidadInput?.value || 1));
            subtotalServiciosCentavos += Math.round(Number(casilla.dataset.precio || 0) * 100) * cantidad;
        });
        const subtotalCompraCentavos = baseTotalCentavos + subtotalServiciosCentavos;
        const promocion = selectorPromocion?.selectedOptions[0];
        const tipoPromocion = promocion?.dataset.tipo;
        if (tipoPromocion === "nxm") {
            const cantidadComprar = Number(promocion.dataset.comprar || 0);
            const cantidadPagar = Number(promocion.dataset.pagar || 0);
            if (cantidadComprar > 0 && cantidadPagar >= 0 && cantidadPagar <= cantidadComprar) {
                const gruposCompletos = Math.floor(cantidadEntradas / cantidadComprar);
                const entradasBonificadas = gruposCompletos * (cantidadComprar - cantidadPagar);
                descuentoCentavos = precioEntradaCentavos * entradasBonificadas;
            }
        } else if (tipoPromocion === "porcentaje") {
            const porcentaje = Number(promocion.dataset.porcentaje || 0);
            descuentoCentavos = Math.round(subtotalCompraCentavos * porcentaje / 100);
        } else if (tipoPromocion === "monto_fijo") {
            const montoCentavos = Math.round(Number(promocion.dataset.montoDescuento || 0) * 100);
            descuentoCentavos = Math.min(subtotalCompraCentavos, montoCentavos);
        }
        descuentoCentavos = Math.min(subtotalCompraCentavos, descuentoCentavos);
        const totalCentavos = subtotalCompraCentavos - descuentoCentavos;
        if (totalSalida) totalSalida.textContent = formatoMoneda.format(totalCentavos / 100);
        if (subtotalEntradasSalida) {
            const descuentoSoloEntradas = tipoPromocion === "nxm" ? descuentoCentavos : 0;
            subtotalEntradasSalida.textContent = formatoMoneda.format((baseTotalCentavos - descuentoSoloEntradas) / 100);
        }
        if (descuentoSalida) descuentoSalida.textContent = formatoMoneda.format(descuentoCentavos / 100);
        if (lineaDescuento) lineaDescuento.hidden = descuentoCentavos <= 0;
    };

    formularioCheckout.addEventListener("change", actualizarTotal);
    selectorPromocion?.addEventListener("change", actualizarTotal);
    selectorPromocion?.addEventListener("input", actualizarTotal);
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
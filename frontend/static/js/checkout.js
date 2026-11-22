const MAX_BUTACAS = 6;
const MIN_BUTACAS = 1;
const DURACION_MENSAJE_MS = 5000;

const formatoMoneda = new Intl.NumberFormat("es-AR", {
    style: "currency",
    currency: "ARS",
    maximumFractionDigits: 2,
});

const aCentavos = (valor) => Math.round(Number(valor || 0) * 100);
const formatearCentavos = (centavos) => formatoMoneda.format(centavos / 100);

function iniciarErrorTemporal() {
    const error = document.querySelector("[data-error-temporal]");
    if (!error) return;

    const url = new URL(window.location.href);
    url.searchParams.delete("checkout_expirado");
    window.history.replaceState({}, "", url);

    window.setTimeout(() => error.remove(), DURACION_MENSAJE_MS);
}

function iniciarSeleccionButacas() {
    const formulario = document.querySelector(".seleccion-butacas");
    if (!formulario) return;

    const casillas = [...formulario.querySelectorAll('input[name="butacas"]:not(:disabled)')];
    const aviso = document.querySelector("#aviso-seleccion-butacas");
    const contador = document.querySelector("#contador");

    const contarElegidas = () => casillas.filter((casilla) => casilla.checked).length;

    const mostrarAviso = (mensaje) => {
        if (!aviso) return;
        aviso.textContent = mensaje;
        aviso.hidden = !mensaje;
    };

    const actualizarContador = () => {
        if (contador) contador.textContent = contarElegidas();
    };

    casillas.forEach((casilla) => {
        casilla.addEventListener("change", () => {
            if (contarElegidas() > MAX_BUTACAS) {
                casilla.checked = false;
                actualizarContador();
                mostrarAviso("Podés elegir hasta seis butacas.");
                return;
            }

            actualizarContador();
            mostrarAviso("");
        });
    });

    formulario.addEventListener("submit", (event) => {
        const elegidas = contarElegidas();
        if (elegidas < MIN_BUTACAS || elegidas > MAX_BUTACAS) {
            event.preventDefault();
            mostrarAviso("Elegí entre una y seis butacas para continuar.");
        }
    });
}

function evitarDobleEnvio(formulario) {
    let enviando = false;

    formulario.addEventListener("submit", (event) => {
        if (enviando) {
            event.preventDefault();
            return;
        }
        enviando = true;

        const boton = formulario.querySelector('button[type="submit"]');
        if (!boton) return;

        const esPasoServicios = formulario.querySelector("[data-continue-to-services]");
        boton.disabled = true;
        boton.textContent = esPasoServicios ? "Cargando servicios…" : "Procesando compra…";
    });
}

function calcularSubtotalServicios(formulario) {
    const casillas = formulario.querySelectorAll('.servicio-checkout input[type="checkbox"]');
    let subtotal = 0;

    casillas.forEach((casilla) => {
        if (!casilla.checked) return;

        const inputCantidad = formulario.querySelector(`[name="cantidad_${casilla.value}"]`);
        const cantidad = Math.max(1, Number(inputCantidad?.value || 1));
        subtotal += aCentavos(casilla.dataset.precio) * cantidad;
    });

    return subtotal;
}

function calcularDescuento({ promocion, subtotalCompra, precioEntrada, cantidadEntradas }) {
    const tipo = promocion?.dataset.tipo;
    let descuento = 0;

    if (tipo === "nxm") {
        const comprar = Number(promocion.dataset.comprar || 0);
        const pagar = Number(promocion.dataset.pagar || 0);
        const configuracionValida = comprar > 0 && pagar >= 0 && pagar <= comprar;

        if (configuracionValida) {
            const gruposCompletos = Math.floor(cantidadEntradas / comprar);
            const entradasBonificadas = gruposCompletos * (comprar - pagar);
            descuento = precioEntrada * entradasBonificadas;
        }
    } else if (tipo === "porcentaje") {
        const porcentaje = Number(promocion.dataset.porcentaje || 0);
        descuento = Math.round((subtotalCompra * porcentaje) / 100);
    } else if (tipo === "monto_fijo") {
        descuento = aCentavos(promocion.dataset.montoDescuento);
    }

    return Math.min(subtotalCompra, descuento);
}

function iniciarCalculoTotal(formulario) {
    const acciones = formulario.querySelector(".checkout-actions");
    const salidaTotal = formulario.querySelector(".checkout-total-dinamico");
    const salidaSubtotalEntradas = document.querySelector(".checkout-subtotal-entradas");
    const salidaDescuento = formulario.querySelector(".checkout-descuento-dinamico");
    const lineaDescuento = formulario.querySelector(".checkout-descuento-linea");
    const selectorPromocion =
        formulario.querySelector(".promocion-preview") ||
        formulario.querySelector('select[name="id_promocion"]');

    const baseEntradas = aCentavos(acciones?.dataset.baseTotal);
    const precioEntrada = aCentavos(acciones?.dataset.precioEntrada);
    const cantidadEntradas = formulario.querySelectorAll('input[name="butacas"]').length;

    const actualizarTotal = () => {
        const subtotalCompra = baseEntradas + calcularSubtotalServicios(formulario);
        const promocion = selectorPromocion?.selectedOptions[0];

        const descuento = calcularDescuento({
            promocion,
            subtotalCompra,
            precioEntrada,
            cantidadEntradas,
        });

        if (salidaTotal) {
            salidaTotal.textContent = formatearCentavos(subtotalCompra - descuento);
        }

        if (salidaSubtotalEntradas) {
            const descuentoEnEntradas = promocion?.dataset.tipo === "nxm" ? descuento : 0;
            salidaSubtotalEntradas.textContent = formatearCentavos(baseEntradas - descuentoEnEntradas);
        }

        if (salidaDescuento) salidaDescuento.textContent = formatearCentavos(descuento);
        if (lineaDescuento) lineaDescuento.hidden = descuento <= 0;
    };

    formulario.addEventListener("change", actualizarTotal);
    formulario.addEventListener("input", (event) => {
        if (event.target.matches('input[type="number"]')) actualizarTotal();
    });
    selectorPromocion?.addEventListener("change", actualizarTotal);
    selectorPromocion?.addEventListener("input", actualizarTotal);

    actualizarTotal();
}

function iniciarContadorExpiracion() {
    const pagina = document.querySelector(".checkout-pagina[data-checkout-duracion-segundos]");
    if (!pagina) return;

    const duracionMs = Number(pagina.dataset.checkoutDuracionSegundos) * 1000;
    const expiraEn = Date.now() + duracionMs;
    const enlaceVolver = pagina.querySelector(":scope > a");

    const verificarExpiracion = () => {
        const segundosRestantes = Math.max(0, Math.ceil((expiraEn - Date.now()) / 1000));

        if (segundosRestantes === 0) {
            const destino = new URL(enlaceVolver.href, window.location.href);
            destino.searchParams.set("checkout_expirado", "1");
            window.location.replace(destino.toString());
            return;
        }

        window.setTimeout(verificarExpiracion, 1000);
    };

    verificarExpiracion();
}

document.addEventListener("DOMContentLoaded", () => {
    iniciarErrorTemporal();
    iniciarSeleccionButacas();

    const formularioCheckout = document.querySelector(".checkout-form");
    if (!formularioCheckout) return;

    evitarDobleEnvio(formularioCheckout);
    iniciarCalculoTotal(formularioCheckout);
    iniciarContadorExpiracion();
});
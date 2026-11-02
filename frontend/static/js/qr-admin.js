(() => {
    "use strict";

    document.addEventListener("DOMContentLoaded", () => {

        const contenedor = document.getElementById("qr-admin");

        if (!contenedor) return;

        const urlValidacion = contenedor.dataset.validarUrl;

        const lectorElemento = document.getElementById("qr-reader");
        const botonIniciar = document.getElementById("qr-iniciar");
        const botonDetener = document.getElementById("qr-detener");
        const formularioManual = document.getElementById("qr-form-manual");
        const campoCodigo = document.getElementById("qr-codigo");

        const estadoCamara = document.getElementById("qr-estado");
        const resultado = document.getElementById("qr-resultado");
        const resultadoEstado = document.getElementById("qr-resultado-estado");
        const resultadoMensaje = document.getElementById("qr-resultado-mensaje");
        const resultadoDetalles = document.getElementById("qr-resultado-detalles");

        const elementosNecesarios = [
            lectorElemento,
            botonIniciar,
            botonDetener,
            formularioManual,
            campoCodigo,
            estadoCamara,
            resultado,
            resultadoEstado,
            resultadoMensaje,
            resultadoDetalles
        ];

        if (elementosNecesarios.some((elemento) => elemento === null)) {
            console.error("La página de QR no contiene todos los elementos HTML necesarios.");
            return;
        }

        let lector = null;
        let camaraActiva = false;
        let validacionEnCurso = false;
        let codigoProcesado = false;



        function mostrarEstadoCamara(mensaje, tipo = "") {

            estadoCamara.textContent = mensaje;

            if (tipo) {
                estadoCamara.dataset.tipo = tipo;
            } else {
                delete estadoCamara.dataset.tipo;
            }
        }



        function mostrarResultado(tipo, etiqueta, mensaje, datos = null) {

            resultado.hidden = false;
            resultado.dataset.resultado = tipo;

            resultadoEstado.textContent = etiqueta;
            resultadoMensaje.textContent = mensaje;

            resultadoDetalles.replaceChildren();

            const camposPermitidos = [
                ["pelicula", "Película"],
                ["nombre_pelicula", "Película"],
                ["funcion", "Función"],
                ["fecha_hora", "Fecha y hora"],
                ["fecha", "Fecha"],
                ["hora", "Hora"],
                ["sala", "Sala"],
                ["butaca", "Butaca"],
                ["numero_factura", "Factura"],
                ["id_entrada", "N.º de entrada"]
            ];

            if (datos && typeof datos === "object") {

                camposPermitidos.forEach(([clave, etiquetaCampo]) => {

                    const valor = datos[clave];

                    if (valor === undefined || valor === null || valor === "") {
                        return;
                    }

                    const fila = document.createElement("div");
                    const titulo = document.createElement("dt");
                    const contenido = document.createElement("dd");

                    titulo.textContent = etiquetaCampo;
                    contenido.textContent = String(valor);

                    fila.append(titulo, contenido);

                    resultadoDetalles.append(fila);
                });
            }

            resultadoDetalles.hidden =
                resultadoDetalles.childElementCount === 0;

            resultado.scrollIntoView({
                behavior: "smooth",
                block: "nearest"
            });
        }


        async function detenerCamara() {

            if (!lector || !camaraActiva) {

                botonDetener.disabled = true;
                botonIniciar.disabled = false;

                return;
            }

            try {

                await lector.stop();

            } catch (error) {

                console.warn("No se pudo detener el lector QR:", error);

            } finally {

                camaraActiva = false;

                botonDetener.disabled = true;
                botonIniciar.disabled = false;
            }
        }

        function interpretarRespuesta(datos) {

            const mensaje =
                datos.mensaje ||
                datos.message ||
                datos.error ||
                "El servidor no indicó explícitamente el resultado.";

            const valido =
                datos.valido ??
                datos.es_valido ??
                datos.valid ??
                datos.success;

            const detalles =
                datos.entrada ||
                datos.detalles ||
                datos;

            if (valido === true) {

                mostrarResultado(
                    "valido",
                    "Entrada válida",
                    mensaje,
                    detalles
                );

            } else if (valido === false || datos.error) {

                mostrarResultado(
                    "invalido",
                    "Entrada no válida",
                    mensaje,
                    detalles
                );

            } else {

                mostrarResultado(
                    "pendiente",
                    "Respuesta del servidor",
                    mensaje,
                    detalles
                );
            }
        }

        async function validarCodigo(codigo) {

            const codigoLimpio = String(codigo || "").trim();

            if (!codigoLimpio) {

                mostrarResultado(
                    "invalido",
                    "Código vacío",
                    "Ingresá o escaneá un código QR."
                );

                return;
            }

            if (validacionEnCurso) return;

            if (!urlValidacion) {

                mostrarResultado(
                    "invalido",
                    "Falta configurar la ruta",
                    "No se configuró la URL del endpoint de validación."
                );

                return;
            }

            validacionEnCurso = true;

            botonIniciar.disabled = true;

            const botonManual =
                formularioManual.querySelector('button[type="submit"]');

            if (botonManual) {
                botonManual.disabled = true;
            }

            mostrarEstadoCamara(
                "Enviando el código al servidor para validarlo..."
            );

            const encabezados = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            };

            // Token CSRF, si utilizan Flask-WTF.
            const metaCsrf = document.querySelector(
                'meta[name="csrf-token"]'
            );

            if (metaCsrf && metaCsrf.content) {

                encabezados["X-CSRFToken"] = metaCsrf.content;
            }

            try {

                const respuesta = await fetch(urlValidacion, {

                    method: "POST",

                    credentials: "same-origin",

                    headers: encabezados,

                    // Flask recibe el código mediante request.get_json().
                    body: JSON.stringify({
                        qr: codigoLimpio
                    })
                });

                const tipoContenido =
                    respuesta.headers.get("content-type") || "";

                let datos;

                if (tipoContenido.includes("application/json")) {

                    datos = await respuesta.json();

                } else {

                    const texto = await respuesta.text();

                    datos = {
                        message: texto || "El servidor devolvió una respuesta sin contenido JSON."
                    };
                }

                if (!respuesta.ok) {

                    const mensajeError =
                        datos.error ||
                        datos.message ||
                        `Error HTTP ${respuesta.status}`;

                    mostrarResultado(
                        "invalido",
                        "No se pudo validar",
                        mensajeError,
                        datos.entrada || null
                    );

                    mostrarEstadoCamara(
                        mensajeError,
                        "error"
                    );

                    return;
                }

                interpretarRespuesta(datos);

                mostrarEstadoCamara(
                    "El servidor respondió la solicitud.",
                    "exito"
                );

            } catch (error) {

                console.error("Error al validar el QR:", error);

                mostrarResultado(
                    "invalido",
                    "Error de conexión",
                    "No se pudo contactar al servidor. Revisá tu conexión e intentá nuevamente."
                );

                mostrarEstadoCamara(
                    "No se pudo contactar al servidor.",
                    "error"
                );

            } finally {

                validacionEnCurso = false;

                if (botonManual) {
                    botonManual.disabled = false;
                }

                if (!camaraActiva) {
                    botonIniciar.disabled = false;
                }
            }
        }


        async function iniciarCamara() {

            if (!window.Html5Qrcode) {

                mostrarEstadoCamara(
                    "No se pudo cargar la biblioteca para leer QR. Revisá la conexión y la etiqueta script.",
                    "error"
                );

                return;
            }

            if (camaraActiva) return;

            try {

                botonIniciar.disabled = true;

                mostrarEstadoCamara(
                    "Solicitando permiso para utilizar la cámara..."
                );

                lector = new window.Html5Qrcode("qr-reader");

                await lector.start(

                    { facingMode: "environment" },

                    {
                        fps: 10,
                        qrbox: {
                            width: 230,
                            height: 230
                        },
                        aspectRatio: 1
                    },

                    async (textoDecodificado) => {

                        if (validacionEnCurso || codigoProcesado) {
                            return;
                        }

                        codigoProcesado = true;

                        mostrarEstadoCamara(
                            "QR detectado. Deteniendo la cámara y validando..."
                        );

                        await detenerCamara();

                        await validarCodigo(textoDecodificado);
                    },

                    () => {
                    }
                );

                camaraActiva = true;

                codigoProcesado = false;

                botonIniciar.disabled = true;
                botonDetener.disabled = false;

                mostrarEstadoCamara(
                    "Cámara activa. Enfocá el código QR dentro del recuadro.",
                    "exito"
                );

            } catch (error) {

                console.error(
                    "No se pudo iniciar la cámara:",
                    error
                );

                camaraActiva = false;

                botonIniciar.disabled = false;
                botonDetener.disabled = true;

                mostrarEstadoCamara(
                    "No se pudo iniciar la cámara. Revisá los permisos y que el sitio use HTTPS o localhost.",
                    "error"
                );
            }
        }


        botonIniciar.addEventListener("click", iniciarCamara);


        botonDetener.addEventListener("click", async () => {

            await detenerCamara();

            mostrarEstadoCamara("Cámara detenida.");
        });


        formularioManual.addEventListener("submit", async (evento) => {

            evento.preventDefault();

            codigoProcesado = true;

            await detenerCamara();

            await validarCodigo(campoCodigo.value);
        });


        campoCodigo.addEventListener("input", () => {

            codigoProcesado = false;
        });


        window.addEventListener("pagehide", () => {

            if (lector && camaraActiva) {

                lector.stop().catch((error) => {

                    console.warn(
                        "No se pudo cerrar la cámara:",
                        error
                    );
                });
            }
        });

    });

})();
(() => {
    "use strict";

    document.addEventListener("DOMContentLoaded", () => {

        // Contenedor principal.
        const contenedor = document.getElementById("qr-admin");

        if (!contenedor) return;

        // URLs del backend.
        const urlValidarEntrada = contenedor.dataset.validarEntradaUrl;
        const urlValidarProducto = contenedor.dataset.validarProductoUrl;

        // Pantallas.
        const pantallaTipos = document.getElementById("qr-pantalla-tipos");
        const pantallaCategorias = document.getElementById("qr-pantalla-categorias");
        const pantallaLector = document.getElementById("qr-pantalla-lector");

        // Selección.
        const botonesTipo = contenedor.querySelectorAll("[data-tipo]");
        const botonesCategoria = contenedor.querySelectorAll("[data-categoria]");
        const botonVolverTipos = document.getElementById("qr-volver-tipos");
        const botonVolverSeleccion = document.getElementById("qr-volver-seleccion");

        // Cámara.
        const lectorElemento = document.getElementById("qr-reader");
        const botonIniciar = document.getElementById("qr-iniciar");
        const botonDetener = document.getElementById("qr-detener");

        // Formulario.
        const formularioManual = document.getElementById("qr-form-manual");
        const campoCodigo = document.getElementById("qr-codigo");
        const campoCategoria = document.getElementById("qr-categoria");
        const botonValidarManual = document.getElementById("qr-validar-manual");

        // Iframe que recibe la respuesta del backend.
        const iframeRespuesta = document.getElementById("qr-respuesta");

        // Contexto del escáner.
        const estadoCamara = document.getElementById("qr-estado");
        const contextoTipo = document.getElementById("qr-contexto-tipo");
        const contextoTitulo = document.getElementById("qr-contexto-titulo");
        const contextoDescripcion = document.getElementById("qr-contexto-descripcion");

        // Resultado.
        const resultado = document.getElementById("qr-resultado");
        const resultadoTitulo = document.getElementById("qr-resultado-titulo");
        const resultadoEstado = document.getElementById("qr-resultado-estado");
        const resultadoMensaje = document.getElementById("qr-resultado-mensaje");
        const resultadoDetalles = document.getElementById("qr-resultado-detalles");

        // Comprobar elementos HTML necesarios.
        const elementosNecesarios = [
            pantallaTipos,
            pantallaCategorias,
            pantallaLector,
            botonVolverTipos,
            botonVolverSeleccion,
            lectorElemento,
            botonIniciar,
            botonDetener,
            formularioManual,
            campoCodigo,
            campoCategoria,
            botonValidarManual,
            iframeRespuesta,
            estadoCamara,
            contextoTipo,
            contextoTitulo,
            contextoDescripcion,
            resultado,
            resultadoTitulo,
            resultadoEstado,
            resultadoMensaje,
            resultadoDetalles
        ];

        if (elementosNecesarios.some(elemento => !elemento)) {
            console.error(
                "La página de validación QR no contiene todos los elementos HTML necesarios."
            );
            return;
        }

        if (!urlValidarEntrada || !urlValidarProducto) {
            console.error("No se configuraron las URLs de validación QR.");
            return;
        }

        // Comprobar que el iframe tenga un nombre.
        if (!iframeRespuesta.name) {
            iframeRespuesta.name = "qr-respuesta";
        }

        // Asegurar que el formulario envíe la respuesta al iframe.
        formularioManual.target = iframeRespuesta.name;
        formularioManual.method = "POST";

        // Variables del escáner.
        let lector = null;

        let camaraActiva = false;
        let iniciandoCamara = false;
        let validacionEnCurso = false;
        let codigoProcesado = false;
        let envioEnCurso = false;

        let tipoSeleccionado = null;
        let categoriaSeleccionada = null;

        let temporizadorRespuesta = null;

        // --------------------------------------------------
        // ESTADOS Y PANTALLAS
        // --------------------------------------------------

        function mostrarEstadoCamara(mensaje, tipo = "") {

            estadoCamara.textContent = mensaje;

            if (tipo) {
                estadoCamara.dataset.tipo = tipo;
            } else {
                delete estadoCamara.dataset.tipo;
            }
        }


        function mostrarPantalla(pantalla) {

            pantallaTipos.hidden = true;
            pantallaCategorias.hidden = true;
            pantallaLector.hidden = true;

            pantalla.hidden = false;
        }


        function limpiarResultado() {

            resultado.hidden = true;

            resultado.removeAttribute("data-resultado");

            resultadoMensaje.textContent = "";
            resultadoEstado.textContent = "";

            resultadoDetalles.replaceChildren();
            resultadoDetalles.hidden = true;
        }


        function limpiarSeleccion() {

            tipoSeleccionado = null;
            categoriaSeleccionada = null;

            codigoProcesado = false;

            campoCodigo.value = "";
            campoCategoria.value = "";

            limpiarResultado();
        }


        // --------------------------------------------------
        // SELECCIÓN DE TIPO Y CATEGORÍA
        // --------------------------------------------------

        function seleccionarTipo(tipo) {

            tipoSeleccionado = tipo;
            categoriaSeleccionada = null;

            if (tipo === "entrada") {

                abrirEscaner();

            } else if (tipo === "producto") {

                mostrarPantalla(pantallaCategorias);

            }
        }


        function seleccionarCategoria(categoria) {

            categoriaSeleccionada = categoria;

            abrirEscaner();
        }


        function abrirEscaner() {

            limpiarResultado();

            campoCodigo.value = "";
            campoCategoria.value = "";

            codigoProcesado = false;

            if (tipoSeleccionado === "entrada") {

                contextoTipo.textContent = "ENTRADAS";

                contextoTitulo.textContent = "Validación de entradas";

                contextoDescripcion.textContent =
                    "Escaneá el QR de la entrada para comprobar el acceso.";

            } else {

                const nombresCategorias = {
                    bebida: "Bebidas",
                    comida: "Comidas",
                    estacionamiento: "Estacionamiento",
                    vip: "VIP"
                };

                contextoTipo.textContent = "PRODUCTOS";

                contextoTitulo.textContent = "Validación de productos";

                contextoDescripcion.textContent =
                    `Categoría seleccionada: ${nombresCategorias[categoriaSeleccionada]}.`;
            }

            mostrarEstadoCamara("La cámara está apagada.");

            mostrarPantalla(pantallaLector);
        }


        async function volverSeleccion() {

            await detenerCamara();

            limpiarResultado();

            campoCodigo.value = "";
            campoCategoria.value = "";

            codigoProcesado = false;

            if (tipoSeleccionado === "producto") {

                categoriaSeleccionada = null;

                mostrarPantalla(pantallaCategorias);

            } else {

                limpiarSeleccion();

                mostrarPantalla(pantallaTipos);
            }
        }


        // --------------------------------------------------
        // MOSTRAR RESULTADO
        // --------------------------------------------------

        function mostrarResultado(valido, mensaje, datos = null) {

            resultado.hidden = false;

            resultado.dataset.resultado =
                valido ? "valido" : "invalido";

            resultadoTitulo.textContent =
                valido ? "Validación aceptada" : "Validación rechazada";

            resultadoEstado.textContent =
                valido ? "VÁLIDO" : "NO VÁLIDO";

            resultadoMensaje.textContent = mensaje;

            resultadoDetalles.replaceChildren();

            const camposPermitidos = [

                ["pelicula", "Película"],
                ["fecha", "Fecha"],
                ["hora", "Hora"],
                ["sala", "Sala"],
                ["butaca", "Butaca"],
                ["id_entrada", "N.º de entrada"],

                // Datos de productos.
                ["producto", "Producto"],
                ["categoria", "Categoría"],
                ["cantidad", "Cantidad"],
                ["precio_unitario", "Precio unitario"],
                ["subtotal", "Subtotal"],

                ["id_compra", "N.º de compra"],
                ["id_compra_producto", "Detalle de compra"],
                ["numero_factura", "Factura"],
                ["fecha_uso", "Fecha de uso"],
                ["estado_entrada", "Estado de entrada"],
                ["estado_compra", "Estado de compra"]

            ];

            if (datos && typeof datos === "object") {

                camposPermitidos.forEach(([clave, etiqueta]) => {

                    const valor = datos[clave];

                    if (
                        valor === undefined ||
                        valor === null ||
                        valor === ""
                    ) {
                        return;
                    }

                    const fila = document.createElement("div");

                    const titulo = document.createElement("dt");
                    const contenido = document.createElement("dd");

                    titulo.textContent = etiqueta;
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


        // --------------------------------------------------
        // DETENER CÁMARA
        // --------------------------------------------------

        async function detenerCamara() {

            if (!lector) {

                camaraActiva = false;
                iniciandoCamara = false;

                botonDetener.disabled = true;
                botonIniciar.disabled = false;

                return;
            }

            const lectorActual = lector;

            try {

                if (camaraActiva) {
                    await lectorActual.stop();
                }

            } catch (error) {

                console.warn("No se pudo detener la cámara:", error);

            } finally {

                camaraActiva = false;
                iniciandoCamara = false;

                try {
                    await lectorActual.clear();
                } catch (error) {
                    console.warn("No se pudo limpiar el lector:", error);
                }

                lector = null;

                botonDetener.disabled = true;
                botonIniciar.disabled = false;
            }
        }


        // --------------------------------------------------
        // PREPARAR TOKEN Y ENVIAR FORMULARIO
        // --------------------------------------------------

        function prepararTokenCSRF() {

            const metaCsrf = document.querySelector(
                'meta[name="csrf-token"]'
            );

            // Si no hay meta CSRF, no se agrega ningún campo.
            if (!metaCsrf || !metaCsrf.content) {
                return;
            }

            let campoCsrf = formularioManual.querySelector(
                'input[name="csrf_token"]'
            );

            if (!campoCsrf) {

                campoCsrf = document.createElement("input");

                campoCsrf.type = "hidden";
                campoCsrf.name = "csrf_token";

                formularioManual.appendChild(campoCsrf);
            }

            campoCsrf.value = metaCsrf.content;
        }


        async function enviarFormulario() {

            if (validacionEnCurso) return;

            const codigoLimpio = campoCodigo.value.trim();

            if (!codigoLimpio) {

                mostrarResultado(
                    false,
                    "Ingresá o escaneá un código QR."
                );

                return;
            }

            // Determinar la ruta según el tipo seleccionado.
            if (tipoSeleccionado === "entrada") {

                formularioManual.action = urlValidarEntrada;

                campoCategoria.value = "";

            } else if (tipoSeleccionado === "producto") {

                if (!categoriaSeleccionada) {

                    mostrarResultado(
                        false,
                        "Primero seleccioná una categoría de producto."
                    );

                    return;
                }

                formularioManual.action = urlValidarProducto;

                campoCategoria.value = categoriaSeleccionada;

            } else {

                mostrarResultado(
                    false,
                    "Primero seleccioná qué querés validar."
                );

                return;
            }

            // Preparar los datos del formulario.
            campoCodigo.value = codigoLimpio;

            prepararTokenCSRF();

            // Bloquear nuevos envíos.
            validacionEnCurso = true;
            codigoProcesado = true;

            botonIniciar.disabled = true;
            botonValidarManual.disabled = true;

            mostrarEstadoCamara(
                "Enviando el código al servidor para validarlo..."
            );

            // Detener la cámara antes de enviar.
            await detenerCamara();

            // detenerCamara habilita los botones al finalizar,
            // por eso volvemos a bloquearlos durante el envío.
            botonIniciar.disabled = true;
            botonValidarManual.disabled = true;

            try {

                // Indicamos que esperamos una respuesta del iframe.
                envioEnCurso = true;

                // Evitar esperar indefinidamente si no hay respuesta.
                temporizadorRespuesta = setTimeout(() => {

                    if (!envioEnCurso) return;

                    envioEnCurso = false;
                    validacionEnCurso = false;
                    codigoProcesado = false;

                    mostrarResultado(
                        false,
                        "El servidor no respondió. Revisá la conexión e intentá nuevamente."
                    );

                    mostrarEstadoCamara(
                        "Tiempo de espera agotado.",
                        "error"
                    );

                    botonValidarManual.disabled = false;
                    botonIniciar.disabled = false;

                }, 20000);


                formularioManual.submit();

            } catch (error) {

                console.error(
                    "Error al enviar el formulario:",
                    error
                );

                envioEnCurso = false;
                validacionEnCurso = false;
                codigoProcesado = false;

                clearTimeout(temporizadorRespuesta);

                mostrarResultado(
                    false,
                    "No se pudo enviar el código al servidor."
                );

                mostrarEstadoCamara(
                    "Error al enviar el formulario.",
                    "error"
                );

                botonValidarManual.disabled = false;
                botonIniciar.disabled = false;
            }
        }


        // --------------------------------------------------
        // RECIBIR RESPUESTA DEL BACKEND EN EL IFRAME
        // --------------------------------------------------

        iframeRespuesta.addEventListener("load", () => {

            // Ignorar las cargas que no corresponden a un envío.
            if (!envioEnCurso) return;

            envioEnCurso = false;

            clearTimeout(temporizadorRespuesta);

            try {

                const documento = iframeRespuesta.contentDocument;

                if (!documento) {
                    throw new Error("No se pudo acceder al documento del iframe.");
                }

                // Obtener el contenido enviado por Flask.
                const textoRespuesta = (
                    documento.body?.textContent ||
                    documento.documentElement?.textContent ||
                    ""
                ).trim();

                if (!textoRespuesta) {
                    throw new Error("El servidor devolvió una respuesta vacía.");
                }

                // Interpretar el JSON enviado por Flask.
                const datos = JSON.parse(textoRespuesta);

                if (
                    !datos ||
                    typeof datos !== "object" ||
                    Array.isArray(datos)
                ) {
                    throw new Error("El servidor devolvió un JSON inválido.");
                }

                const valido = datos.valido === true;

                const mensaje =
                    datos.mensaje ||
                    datos.message ||
                    datos.error ||
                    "No se pudo validar el código.";

                const detalles =
                    datos.entrada ||
                    datos.detalles ||
                    null;

                // Mostrar el resultado.
                mostrarResultado(
                    valido,
                    mensaje,
                    detalles
                );

                if (valido) {

                    mostrarEstadoCamara(
                        "QR validado correctamente.",
                        "exito"
                    );

                } else {

                    mostrarEstadoCamara(
                        mensaje,
                        "error"
                    );

                }

            } catch (error) {

                console.error(
                    "Error al interpretar la respuesta del servidor:",
                    error
                );

                mostrarResultado(
                    false,
                    "No se pudo interpretar la respuesta del servidor. Comprobá que la sesión siga activa y que Flask devuelva JSON."
                );

                mostrarEstadoCamara(
                    "Error al procesar la respuesta.",
                    "error"
                );

            } finally {

                validacionEnCurso = false;
                codigoProcesado = false;

                botonValidarManual.disabled = false;

                if (!camaraActiva && !iniciandoCamara) {
                    botonIniciar.disabled = false;
                }
            }
        });


        // --------------------------------------------------
        // INICIAR CÁMARA
        // --------------------------------------------------

        async function iniciarCamara() {

            if (!window.Html5Qrcode) {

                mostrarEstadoCamara(
                    "No se pudo cargar la biblioteca para leer QR. Revisá la conexión.",
                    "error"
                );

                return;
            }

            if (camaraActiva || iniciandoCamara || validacionEnCurso) {
                return;
            }

            try {

                limpiarResultado();

                codigoProcesado = false;
                iniciandoCamara = true;

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

                        if (
                            validacionEnCurso ||
                            codigoProcesado
                        ) {
                            return;
                        }

                        codigoProcesado = true;

                        campoCodigo.value = textoDecodificado;

                        mostrarEstadoCamara(
                            "QR detectado. Deteniendo la cámara y enviando el código..."
                        );

                        // El envío del formulario se encargará
                        // de detener la cámara y enviar el token.
                        formularioManual.requestSubmit();

                    },

                    () => {
                        // Se ignoran los errores de lectura de cada fotograma.
                    }
                );

                camaraActiva = true;
                iniciandoCamara = false;

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

                await detenerCamara();

                mostrarEstadoCamara(
                    "No se pudo iniciar la cámara. Revisá los permisos y que el sitio utilice HTTPS o localhost.",
                    "error"
                );

            }
        }


        // --------------------------------------------------
        // EVENTOS DE SELECCIÓN
        // --------------------------------------------------

        botonesTipo.forEach((boton) => {

            boton.addEventListener("click", () => {

                seleccionarTipo(boton.dataset.tipo);

            });

        });


        botonesCategoria.forEach((boton) => {

            boton.addEventListener("click", () => {

                seleccionarCategoria(boton.dataset.categoria);

            });

        });


        botonVolverTipos.addEventListener("click", () => {

            limpiarSeleccion();

            mostrarPantalla(pantallaTipos);

        });


        botonVolverSeleccion.addEventListener("click", async () => {

            await volverSeleccion();

        });


        // --------------------------------------------------
        // EVENTOS DE CÁMARA
        // --------------------------------------------------

        botonIniciar.addEventListener("click", iniciarCamara);

        botonDetener.addEventListener("click", async () => {

            await detenerCamara();

            codigoProcesado = false;

            mostrarEstadoCamara("Cámara detenida.");

        });


        // --------------------------------------------------
        // ENVÍO DEL FORMULARIO
        // --------------------------------------------------

        formularioManual.addEventListener("submit", (evento) => {

            // Evita que el navegador reemplace la página principal.
            evento.preventDefault();

            enviarFormulario();

        });


        campoCodigo.addEventListener("input", () => {

            codigoProcesado = false;

        });


        // --------------------------------------------------
        // CERRAR CÁMARA AL ABANDONAR LA PÁGINA
        // --------------------------------------------------

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


        mostrarPantalla(pantallaTipos);

    });

})();
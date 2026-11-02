'use strict';

document.addEventListener('DOMContentLoaded', () => {
    const formulario = document.getElementById('form-validar-qr');
    const inputCodigo = document.getElementById('codigo-qr');
    if (!formulario || !inputCodigo) return;

    const urlValidacion = formulario.dataset.validarUrl || '/admin/api/qr/validar';
    const clavePayload = formulario.dataset.payloadKey || 'codigo_qr';

    const botonValidar = document.getElementById('boton-validar-qr');
    const feedbackCamara = document.getElementById('camera-feedback');
    const placeholderCamara = document.getElementById('scanner-placeholder');
    const estadoCamara = document.getElementById('scanner-status');
    const botonIniciar = document.getElementById('iniciar-camara');
    const botonDetener = document.getElementById('detener-camara');

    const panelResultado = document.getElementById('resultado-validacion');
    const iconoResultado = document.getElementById('resultado-icono');
    const etiquetaResultado = document.getElementById('resultado-etiqueta');
    const tituloResultado = document.getElementById('resultado-titulo');
    const mensajeResultado = document.getElementById('resultado-mensaje');
    const detallesResultado = document.getElementById('resultado-detalles');

    let lector = null;
    let camaraActiva = false;
    let validando = false;

    function mostrarFeedbackCamara(mensaje) {
        if (feedbackCamara) feedbackCamara.textContent = mensaje;
    }

    function mostrarResultado({ valido, titulo, mensaje, detalles = {} }) {
        if (!panelResultado) return;

        panelResultado.hidden = false;
        if (iconoResultado) {
            iconoResultado.textContent = valido ? '✓' : '!';
            iconoResultado.classList.toggle('result-icon--invalid', !valido);
        }
        if (etiquetaResultado) {
            etiquetaResultado.textContent = valido ? 'Entrada válida' : 'Entrada no válida';
        }
        if (tituloResultado) {
            tituloResultado.textContent = titulo || (valido ? 'Entrada validada' : 'Validación rechazada');
        }
        if (mensajeResultado) mensajeResultado.textContent = mensaje || '';

        if (detallesResultado) {
            detallesResultado.replaceChildren();
            Object.entries(detalles || {}).forEach(([clave, valor]) => {
                if (valor === null || valor === undefined || typeof valor === 'object') return;

                const contenedor = document.createElement('div');
                const termino = document.createElement('dt');
                const descripcion = document.createElement('dd');
                termino.textContent = clave.replaceAll('_', ' ');
                descripcion.textContent = String(valor);
                contenedor.append(termino, descripcion);
                detallesResultado.append(contenedor);
            });
        }

        panelResultado.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    async function detenerCamara() {
        if (lector && camaraActiva) {
            try {
                await lector.stop();
                lector.clear();
            } catch (error) {
                console.warn('No se pudo detener la cámara:', error);
            }
        }

        camaraActiva = false;
        if (placeholderCamara) placeholderCamara.hidden = false;
        if (botonIniciar) botonIniciar.disabled = false;
        if (botonDetener) botonDetener.disabled = true;
        if (estadoCamara) {
            estadoCamara.textContent = 'Cámara detenida';
            estadoCamara.classList.remove('is-active');
        }
    }

    async function leerRespuestaJson(respuesta) {
        const tipoContenido = respuesta.headers.get('content-type') || '';
        if (!tipoContenido.includes('application/json')) {
            throw new Error(
                'El servidor no devolvió JSON. Revisá la URL del endpoint y la autenticación.'
            );
        }
        return respuesta.json();
    }

    async function validarCodigo(codigo) {
        const codigoLimpio = String(codigo || '').trim();
        if (!codigoLimpio || validando) return;

        validando = true;
        if (botonValidar) {
            botonValidar.disabled = true;
            botonValidar.textContent = 'Validando...';
        }
        if (panelResultado) panelResultado.hidden = true;

        try {
            const respuesta = await fetch(urlValidacion, {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json',
                    Accept: 'application/json'
                },
                body: JSON.stringify({ [clavePayload]: codigoLimpio })
            });

            const datos = await leerRespuestaJson(respuesta);
            const indicadorValidez = datos.valido ?? datos.valida ?? datos.valid;

            const valido = respuesta.ok && indicadorValidez === true;
            const detalles = datos.entrada || datos.detalles || {};

            mostrarResultado({
                valido,
                titulo: datos.titulo || (valido ? 'Entrada validada' : 'Validación rechazada'),
                mensaje: datos.mensaje || datos.message || datos.error ||
                    (valido ? 'La entrada fue aceptada.' : 'El backend no confirmó que la entrada sea válida.'),
                detalles
            });
        } catch (error) {
            mostrarResultado({
                valido: false,
                titulo: 'No se pudo completar la validación',
                mensaje: error.message || 'Ocurrió un error de comunicación con el servidor.'
            });
        } finally {
            validando = false;
            if (botonValidar) {
                botonValidar.disabled = false;
                botonValidar.textContent = 'Validar entrada';
            }
        }
    }

    formulario.addEventListener('submit', (evento) => {
        evento.preventDefault();
        validarCodigo(inputCodigo.value);
    });

    if (botonIniciar) {
        botonIniciar.addEventListener('click', async () => {
            if (typeof Html5Qrcode === 'undefined') {
                mostrarFeedbackCamara(
                    'No se pudo cargar el lector QR. Revisá la conexión o utilizá la validación manual.'
                );
                return;
            }
            if (!navigator.mediaDevices?.getUserMedia) {
                mostrarFeedbackCamara(
                    'Este navegador no permite acceder a la cámara. Utilizá la validación manual.'
                );
                return;
            }

            try {
                lector = new Html5Qrcode('qr-reader');
                await lector.start(
                    { facingMode: 'environment' },
                    { fps: 10, qrbox: { width: 230, height: 230 } },
                    async (textoDecodificado) => {
                        if (validando) return;
                        inputCodigo.value = textoDecodificado;
                        await detenerCamara();
                        await validarCodigo(textoDecodificado);
                    },
                    () => {
                    }
                );

                camaraActiva = true;
                if (placeholderCamara) placeholderCamara.hidden = true;
                botonIniciar.disabled = true;
                if (botonDetener) botonDetener.disabled = false;
                if (estadoCamara) {
                    estadoCamara.textContent = 'Cámara activa';
                    estadoCamara.classList.add('is-active');
                }
                mostrarFeedbackCamara('Apuntá la cámara al código QR de la entrada.');
            } catch (error) {
                console.error('No se pudo iniciar el lector QR:', error);
                mostrarFeedbackCamara(
                    'No se pudo iniciar la cámara. Verificá los permisos y que estés usando HTTPS o localhost.'
                );
                await detenerCamara();
            }
        });
    }

    if (botonDetener) {
        botonDetener.addEventListener('click', detenerCamara);
    }

    window.addEventListener('beforeunload', () => {
        if (lector && camaraActiva) {
            lector.stop().catch(() => {});
        }
    });
});

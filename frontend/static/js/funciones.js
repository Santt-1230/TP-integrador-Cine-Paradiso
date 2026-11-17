(() => {
    const form = document.getElementById('form-funcion');
    if (!form) return;

    const pelicula = document.getElementById('id_pelicula');
    const local = document.getElementById('id_local');
    const sala = document.getElementById('id_sala');
    const fecha = document.getElementById('fecha-funcion');
    const hora = document.getElementById('hora-funcion');
    const duracion = document.getElementById('duracion-pelicula');
    const capacidad = document.getElementById('capacidad-sala');
    const fechaHora = document.getElementById('fecha_hora_inicio');
    const precio = document.getElementById('precio_entrada');
    const actualizarBoton = document.getElementById('actualizar-funciones');
    const guardarBoton = form.querySelector('button[type="submit"]:not(#actualizar-funciones)');
    const resumen = document.getElementById('resumen-funcion');
    const lista = document.getElementById('lista-funciones-dia');
    const mensajeFunciones = document.getElementById('mensaje-funciones-dia');
    let consultaVigente = form.dataset.funcionesConsultadas === 'true';

    function fechaCompleta() {
        if (!/^\d{4}-\d{2}-\d{2}$/.test(fecha.value) || !fecha.validity.valid) return false;
        const [anio, mes, dia] = fecha.value.split('-').map(Number);
        const comprobacion = new Date(Date.UTC(anio, mes - 1, dia));
        return comprobacion.getUTCFullYear() === anio
            && comprobacion.getUTCMonth() === mes - 1
            && comprobacion.getUTCDate() === dia;
    }

    function volverACargarFormulario() {
        actualizar();
        const destino = new URL(local.dataset.formUrl, window.location.origin);
        const parametros = new URLSearchParams(new FormData(form));
        parametros.set('id_pelicula', pelicula.value);
        if (local.value) {
            parametros.set('id_local', local.value);
            parametros.set('local_id', local.value);
        }
        if (fecha.value) parametros.set('fecha', fecha.value);
        if (hora.value) parametros.set('hora', hora.value);
        if (fechaHora.value) parametros.set('fecha_hora_inicio', fechaHora.value);
        if (precio.value) parametros.set('precio_entrada', precio.value);
        window.location.assign(`${destino.pathname}?${parametros.toString()}`);
    }

    function actualizarFunciones() {
        const existentes = [...(lista?.querySelectorAll('li') || [])];
        const filtrosCompletos = Boolean(fecha.value && local.value && sala.value);
        if (lista) lista.hidden = !consultaVigente || !filtrosCompletos || existentes.length === 0;
        if (mensajeFunciones) {
            mensajeFunciones.hidden = consultaVigente && filtrosCompletos && existentes.length > 0;
            mensajeFunciones.textContent = !filtrosCompletos
                ? 'Elegí cine, sala y fecha; actualiza las funciones para ver las del mismo dia.'
                : consultaVigente
                    ? 'No hay funciones para el cine, sala y fecha seleccionados.'
                    : 'Actualiza las funciones para ver las del mismo dia.';
        }
    }

    function actualizar() {
        const opcionPelicula = pelicula.selectedOptions[0];
        const opcionSala = sala.selectedOptions[0];
        duracion.textContent = opcionPelicula?.dataset.duracion
            ? `Duración: ${opcionPelicula.dataset.duracion} minutos`
            : '';
        capacidad.textContent = opcionSala?.dataset.capacidad
            ? `Capacidad: ${opcionSala.dataset.capacidad} butacas`
            : '';
        fechaHora.value = fecha.value && hora.value ? `${fecha.value}T${hora.value}` : '';
        actualizarFunciones();

        const valores = [
            opcionPelicula?.textContent,
            local.selectedOptions[0]?.textContent,
            opcionSala?.textContent,
            fecha.value,
            hora.value,
        ].filter(Boolean);
        resumen.textContent = valores.length
            ? valores.join(' · ')
            : 'Completá los pasos para ver el resumen.';
        actualizarDisponibilidad();
    }

    function actualizarDisponibilidad() {
        local.disabled = !pelicula.value;
        sala.disabled = !local.value;
        const habilitarFechaHora = Boolean(sala.value);
        fecha.disabled = !habilitarFechaHora;
        hora.disabled = !habilitarFechaHora;
        precio.disabled = !habilitarFechaHora;
        actualizarBoton.disabled = !local.value || !sala.value || !fechaCompleta();
        guardarBoton.disabled = !pelicula.value || !local.value || !sala.value
            || !fechaCompleta() || !hora.value || !precio.value;
    }

    [pelicula, fecha, hora, precio].forEach((control) => {
        control.addEventListener('change', actualizar);
    });
    pelicula.addEventListener('change', () => {
        consultaVigente = false;
        if (!pelicula.value) {
            local.value = '';
            sala.replaceChildren(new Option('Elegí una sala', ''));
            fecha.value = '';
            hora.value = '';
            precio.value = '';
        }
        actualizar();
    });
    local.addEventListener('change', () => {
        consultaVigente = false;
        sala.value = '';
        actualizar();
        volverACargarFormulario();
    });
    sala.addEventListener('change', () => {
        consultaVigente = false;
        actualizar();
        volverACargarFormulario();
    });
    fecha.addEventListener('input', () => {
        consultaVigente = false;
        actualizar();
    });
    fecha.addEventListener('change', () => {
        consultaVigente = false;
        actualizar();
    });
    actualizar();
})();
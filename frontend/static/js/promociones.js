const selectorTipo = document.getElementById('tipo');

const camposNxm = document.getElementById('campos-nxm');
const camposPorcentaje = document.getElementById('campos-porcentaje');
const camposMontoFijo = document.getElementById('campos-monto-fijo');

function actualizarCampos() {
    const tipo = selectorTipo.value;

    camposNxm.style.display = tipo === 'nxm' ? 'block' : 'none';
    camposPorcentaje.style.display = tipo === 'porcentaje' ? 'block' : 'none';
    camposMontoFijo.style.display = tipo === 'monto_fijo' ? 'block' : 'none';
}

selectorTipo.addEventListener('change', actualizarCampos);

actualizarCampos();
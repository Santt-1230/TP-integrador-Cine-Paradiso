'use strict';

document.addEventListener('DOMContentLoaded', () => {
    animarBarrasOcupacion();
    dimensionarBarrasComparativas();
    configurarFiltroPeriodo();
});

function limitarPorcentaje(valor) {
    if (!Number.isFinite(valor)) return 0;
    return Math.min(100, Math.max(0, valor));
}
function animarBarrasOcupacion() {
    const rellenos = document.querySelectorAll(
        '.tabla-barras--ocupacion .fila-barra__relleno'
    );

    rellenos.forEach((relleno) => {

        const anchoOriginal = Number.parseFloat(relleno.style.width);
        const anchoFinal = limitarPorcentaje(
            Number.isFinite(anchoOriginal) ? anchoOriginal : 0
        );

        const pista = relleno.closest('.fila-barra__pista');

        if (pista) {
            pista.setAttribute('aria-valuenow', String(anchoFinal));
        }
    });
}


function dimensionarBarrasComparativas() {
    document.querySelectorAll('.lista-barras').forEach((lista) => {
        const filas = Array.from(lista.querySelectorAll('.fila-barra--simple'));
        if (filas.length === 0) return;

        const elementos = filas.map((fila) => {
            const valorTexto = fila.querySelector('.fila-barra__valor')?.textContent || '0';
            const cantidad = Number.parseFloat(valorTexto.replace(',', '.'));
            return {
                fila,
                cantidad: Number.isFinite(cantidad) ? Math.max(0, cantidad) : 0
            };
        });

        const maximo = Math.max(...elementos.map((elemento) => elemento.cantidad), 0);

        elementos.forEach(({ fila, cantidad }) => {
            const relleno = fila.querySelector('.fila-barra__relleno');
            const pista = fila.querySelector('.fila-barra__pista');
            if (!relleno) return;

            const porcentaje = maximo > 0 ? (cantidad / maximo) * 100 : 0;
            relleno.style.width = '0%';
            window.requestAnimationFrame(() => {
                relleno.style.width = `${limitarPorcentaje(porcentaje)}%`;
            });

            if (pista) {
                pista.setAttribute('aria-valuenow', String(Math.round(porcentaje)));
            }
        });
    });
}

function configurarFiltroPeriodo() {
    const formulario = document.querySelector('.estadisticas-admin__filtro');
    if (!formulario) return;

    const selector = formulario.querySelector('select[name="periodo"]');
    const boton = formulario.querySelector('button[type="submit"]');
    const periodosPermitidos = new Set(['7', '30', '90', '365']);

    formulario.addEventListener('submit', (evento) => {
        if (selector && !periodosPermitidos.has(selector.value)) {
            evento.preventDefault();
            selector.focus();
            return;
        }

        if (boton) {
            boton.disabled = true;
            boton.textContent = 'Aplicando...';
        }
    });
}
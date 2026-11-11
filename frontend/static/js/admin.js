'use strict';


document.addEventListener('DOMContentLoaded', () => {
    marcarOpcionActual();
    configurarConfirmaciones();
});

function normalizarRuta(ruta) {
    if (!ruta) return '/';
    if (ruta.length > 1 && ruta.endsWith('/')) {
        return ruta.slice(0, -1);
    }
    return ruta;
}

function marcarOpcionActual() {
    const rutaActual = normalizarRuta(window.location.pathname);
    const enlaces = Array.from(document.querySelectorAll('.admin-sidebar nav a[href]'));

    let enlaceActivo = null;
    let longitudMayor = -1;

    enlaces.forEach((enlace) => {
        enlace.classList.remove('activo', 'is-active');
        enlace.removeAttribute('aria-current');

        let rutaEnlace;
        try {
            rutaEnlace = normalizarRuta(new URL(enlace.href, window.location.origin).pathname);
        } catch {
            return;
        }

        const coincide = rutaActual === rutaEnlace ||
            (rutaEnlace !== '/admin' && rutaActual.startsWith(`${rutaEnlace}/`));

        if (coincide && rutaEnlace.length > longitudMayor) {
            enlaceActivo = enlace;
            longitudMayor = rutaEnlace.length;
        }
    });

    if (enlaceActivo) {
        enlaceActivo.classList.add('activo', 'is-active');
        enlaceActivo.setAttribute('aria-current', 'page');
    }
}

function configurarConfirmaciones() {
    document.querySelectorAll('form[data-confirm]').forEach((formulario) => {
        formulario.addEventListener('submit', (evento) => {
            const mensaje = formulario.dataset.confirm || '¿Querés continuar?';
            if (!window.confirm(mensaje)) {
                evento.preventDefault();
            }
        });
    });
}


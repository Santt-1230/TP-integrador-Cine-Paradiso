'use strict';
function confirmarBaja(evento, enlace){
    evento.preventDefault();
    if(!confirm('Estás seguro de que querés dar de baja esta sala?')){
        return false;
    }
    const formulario = document.createElement('form');
    formulario.method = 'POST';
    formulario.action = enlace.href;
    document.body.appendChild(formulario);
    formulario.submit();
    return false;
}


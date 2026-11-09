
(function () {
    "use strict";

    const api = window.UsuariosAPI;


    const ROLES = {
        cliente: "Cliente",
        administrador: "Administrador"
    };

    const REGEX_EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const TIEMPO_MENSAJE_EXITO_MS = 5000;


    const porId = (id) => document.getElementById(id);

    const el = {
        buscar: porId("buscar-usuarios"),
        btnActualizar: porId("btn-actualizar-usuarios"),
        mensaje: porId("mensaje-usuarios"),
        contador: porId("cantidad-usuarios"),
        tabla: porId("tabla-usuarios"),
        modal: porId("modal-editar-usuario"),
        form: porId("form-editar-usuario"),
        id: porId("usuario-id"),
        nombre: porId("usuario-nombre"),
        email: porId("usuario-email"),
        rol: porId("usuario-rol"),
        error: porId("error-formulario-usuario"),
        btnCerrar: porId("cerrar-modal-usuario"),
        btnCancelar: porId("cancelar-edicion-usuario"),
        btnGuardar: porId("guardar-usuario")
    };

    if (!el.tabla || !el.modal || !el.form) {
        return;
    }

    let usuarios = [];
    let cargando = false;
    let guardando = false;
    let temporizadorMensaje = null;


    function crear(etiqueta, clase, texto) {
        const nodo = document.createElement(etiqueta);

        if (clase) {
            nodo.className = clase;
        }

        if (texto !== undefined) {
            nodo.textContent = texto;
        }

        return nodo;
    }
    function normalizar(texto) {
        return String(texto ?? "")
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .toLowerCase()
            .trim();
    }


    function mostrarMensaje(texto, tipo = "info") {
        clearTimeout(temporizadorMensaje);

        el.mensaje.textContent = texto;
        el.mensaje.dataset.tipo = tipo;
        el.mensaje.hidden = false;

        if (tipo === "exito") {
            temporizadorMensaje = setTimeout(ocultarMensaje, TIEMPO_MENSAJE_EXITO_MS);
        }
    }

    function ocultarMensaje() {
        clearTimeout(temporizadorMensaje);

        el.mensaje.hidden = true;
        el.mensaje.textContent = "";
        delete el.mensaje.dataset.tipo;
    }

    function mostrarErrorFormulario(texto) {
        el.error.textContent = texto;
        el.error.hidden = false;
    }

    function ocultarErrorFormulario() {
        el.error.textContent = "";
        el.error.hidden = true;
    }

    function filaEstado(texto, clase) {
        const fila = document.createElement("tr");
        const celda = crear("td", clase, texto);

        celda.colSpan = 4;
        fila.appendChild(celda);

        return fila;
    }

    function filaUsuario(usuario) {
        const fila = document.createElement("tr");
        fila.dataset.id = usuario.id_usuario;

        // Usuario
        fila.appendChild(crear("td", "", usuario.nombre));

        // Correo electrónico
        fila.appendChild(crear("td", "", usuario.email));

        // Rol
        const rol = String(usuario.rol ?? "").toLowerCase();
        const modificador = ROLES[rol] ? ` usuarios-admin__rol--${rol}` : "";
        const celdaRol = document.createElement("td");

        celdaRol.appendChild(
            crear("span", `usuarios-admin__rol${modificador}`, ROLES[rol] || usuario.rol || "-")
        );
        fila.appendChild(celdaRol);

        // Acciones
        const celdaAcciones = document.createElement("td");
        const acciones = crear("div", "acciones-tabla");
        const botonEditar = crear("button", "boton-tabla boton-tabla--editar", "Editar");

        botonEditar.type = "button";
        botonEditar.dataset.accion = "editar";
        botonEditar.dataset.id = usuario.id_usuario;
        botonEditar.setAttribute("aria-label", `Editar a ${usuario.nombre}`);

        acciones.appendChild(botonEditar);
        celdaAcciones.appendChild(acciones);
        fila.appendChild(celdaAcciones);

        return fila;
    }

    function actualizarContador(visibles) {
        const total = usuarios.length;
        const etiqueta = (n) => `${n} ${n === 1 ? "usuario" : "usuarios"}`;

        el.contador.textContent =
            visibles === total ? etiqueta(total) : `${visibles} de ${etiqueta(total)}`;
    }

    function renderizar() {
        const consulta = normalizar(el.buscar.value);

        const visibles = consulta
            ? usuarios.filter((u) =>
                normalizar(`${u.nombre} ${u.email} ${u.rol}`).includes(consulta)
            )
            : usuarios;

        el.tabla.replaceChildren();

        if (visibles.length === 0) {
            const texto = usuarios.length
                ? "No hay usuarios que coincidan con la búsqueda."
                : "Todavía no hay usuarios registrados.";

            el.tabla.appendChild(filaEstado(texto, "usuarios-admin__vacio"));
        } else {
            const fragmento = document.createDocumentFragment();
            visibles.forEach((usuario) => fragmento.appendChild(filaUsuario(usuario)));
            el.tabla.appendChild(fragmento);
        }

        actualizarContador(visibles.length);
    }


    async function cargarUsuarios() {
        if (cargando) {
            return;
        }

        cargando = true;
        el.btnActualizar.disabled = true;
        el.btnActualizar.textContent = "Actualizando...";

        ocultarMensaje();
        el.tabla.replaceChildren(
            filaEstado("Cargando usuarios...", "usuarios-admin__cargando")
        );

        try {
            const datos = await api.listar();
            usuarios = Array.isArray(datos) ? datos : [];
            renderizar();
        } catch (error) {
            if (usuarios.length > 0) {
                renderizar();
            } else {
                el.tabla.replaceChildren(
                    filaEstado("No se pudo cargar la lista de usuarios.", "usuarios-admin__vacio")
                );
                actualizarContador(0);
            }

            mostrarMensaje(error.message, "error");
        } finally {
            cargando = false;
            el.btnActualizar.disabled = false;
            el.btnActualizar.textContent = "Actualizar lista";
        }
    }


    function cargarFormulario(usuario) {
        el.id.value = usuario.id_usuario;
        el.nombre.value = usuario.nombre ?? "";
        el.email.value = usuario.email ?? "";
        el.rol.value = String(usuario.rol ?? "").toLowerCase();

        ocultarErrorFormulario();
    }

    async function abrirEdicion(id, boton) {
        ocultarMensaje();
        boton.disabled = true;

        try {
            const usuario = await api.obtener(id);

            cargarFormulario(usuario);
            el.modal.showModal();
            el.nombre.focus();
        } catch (error) {
            mostrarMensaje(error.message, "error");
        } finally {
            boton.disabled = false;
        }
    }

    function cerrarModal() {
        if (guardando) {
            return;
        }

        el.modal.close();
    }

    function establecerGuardando(valor) {
        guardando = valor;

        el.btnGuardar.disabled = valor;
        el.btnCancelar.disabled = valor;
        el.btnCerrar.disabled = valor;
        el.btnGuardar.textContent = valor ? "Guardando..." : "Guardar cambios";
    }

    function validar(datos) {
        if (!datos.nombre) {
            return { campo: el.nombre, mensaje: "Ingresa el nombre del usuario." };
        }

        if (!datos.email) {
            return { campo: el.email, mensaje: "Ingresa el correo electrónico." };
        }

        if (!REGEX_EMAIL.test(datos.email)) {
            return { campo: el.email, mensaje: "El correo electrónico no es válido." };
        }

        if (!ROLES[datos.rol]) {
            return { campo: el.rol, mensaje: "Selecciona un rol." };
        }

        return null;
    }

    async function guardarUsuario(evento) {
        evento.preventDefault();

        if (guardando) {
            return;
        }

        ocultarErrorFormulario();

        const id = Number(el.id.value);
        const datos = {
            nombre: el.nombre.value.trim(),
            email: el.email.value.trim(),
            rol: el.rol.value
        };

        const problema = validar(datos);

        if (problema) {
            mostrarErrorFormulario(problema.mensaje);
            problema.campo.focus();
            return;
        }

        establecerGuardando(true);

        try {
            await api.actualizar(id, datos);

            const indice = usuarios.findIndex((u) => Number(u.id_usuario) === id);

            if (indice !== -1) {
                usuarios[indice] = { ...usuarios[indice], ...datos };
            }

            el.modal.close();
            renderizar();
            mostrarMensaje("Cambios guardados.", "exito");
        } catch (error) {
            mostrarErrorFormulario(error.message);
        } finally {
            establecerGuardando(false);
        }
    }

    el.buscar.addEventListener("input", renderizar);
    el.btnActualizar.addEventListener("click", cargarUsuarios);

    el.tabla.addEventListener("click", (evento) => {
        const boton = evento.target.closest("[data-accion='editar']");

        if (boton) {
            abrirEdicion(Number(boton.dataset.id), boton);
        }
    });

    el.form.addEventListener("submit", guardarUsuario);
    el.btnCerrar.addEventListener("click", cerrarModal);
    el.btnCancelar.addEventListener("click", cerrarModal);

    el.modal.addEventListener("cancel", (evento) => {
        if (guardando) {
            evento.preventDefault();
        }
    });

    el.modal.addEventListener("close", () => {
        el.form.reset();
        ocultarErrorFormulario();
    });

    let presionoEnFondo = false;

    el.modal.addEventListener("pointerdown", (evento) => {
        presionoEnFondo = evento.target === el.modal;
    });

    el.modal.addEventListener("click", (evento) => {
        if (presionoEnFondo && evento.target === el.modal) {
            cerrarModal();
        }

        presionoEnFondo = false;
    });


    if (!api) {
        el.tabla.replaceChildren(
            filaEstado("No se pudo cargar la lista de usuarios.", "usuarios-admin__vacio")
        );
        mostrarMensaje(
            "Falta cargar usuarios_api.js antes de admin_usuarios.js.",
            "error"
        );
        return;
    }

    cargarUsuarios();
})();
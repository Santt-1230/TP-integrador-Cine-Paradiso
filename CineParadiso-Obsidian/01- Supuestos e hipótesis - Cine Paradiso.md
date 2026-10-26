

**Índice rápido:** [[#Resumen de avance]] · [[#Supuestos]] · [[#Decisiones resueltas]] · [[#Hipótesis]] · [[#Pendientes de decidir]]


## Resumen de avance

### Supuestos por área

| Área | Cantidad 
| --- | --- |
| Usuarios y acceso | 7 |
| Locales, salas y butacas | 3 |
| Películas y cartelera | 4 |
| Funciones | 4 |
| Compra | 6 |
| Servicios y promociones | 4 |
| Cancelación | 3 |
| QR e ingreso | 3 |
| Transversales | 6 |
| **Total** | **40** |

### Hipótesis y pendientes

| Indicador | Cantidad |
| --- | --- |
| Hipótesis sin verificar | 5 |
| Hipótesis verificadas | 0 |
| Pendientes de decidir | 10 |

---

## Supuestos

### Usuarios y acceso

| ID | Supuesto | Impacta en |
| --- | --- | --- |
| S-01 | Hay tres roles: cliente, administrador y publico. Front(cliente, administrador), Back(cliente, administrador y publico) | Tabla usuario, seguridad |
| S-02 | El cliente se registra solo, y el registro público nunca puede crear administradores. | `/api/auth/registro` |
| S-03 | El administrador viene cargado en el script inicial de datos. | Script SQL |
| S-04 | El email es único por usuario. | Tabla usuario, registro |
| S-05 | La autenticación es por token (a confirmar) y las contraseñas se guardan solo como hash. | Login, todos los endpoints |
| S-06 | Los permisos se comprueban siempre en el backend; ocultar un botón en el front no protege nada. | Decorador de roles |
| S-07 | Para comprar hay que iniciar sesión; la cartelera y las funciones se pueden ver sin cuenta. | Endpoints públicos |

### Locales, salas y butacas

| ID | Supuesto | Impacta en |
| --- | --- | --- |
| S-08 | Hay 3 locales, cargados desde el script inicial. | Tabla local |
| S-09 | Cada sala tiene una capacidad y butacas identificadas por fila(letras) y número, generadas al crear la sala. | Tablas sala y butaca, `POST /api/salas` |
| S-10 | Dar de baja una sala es una baja lógica si tiene funciones históricas. Cambiar estado a inactivo | Tabla sala, `PATCH /api/salas/<id>` |

### Películas y cartelera

| ID | Supuesto | Impacta en |
| --- | --- | --- |
| S-11 | Las películas se importan de OMDb o TMDB y se guardan en la base propia (título, sinopsis, póster, duración, clasificación, género), para no depender de la API en cada consulta. | Tabla pelicula, búsqueda externa |
| S-12 | Cada película tiene un período de cartelera (desde y hasta) activas minimo 1 semana, y el público solo ve las vigentes. Luego el admin decide si se aumenta o no el tiempo | `GET /api/peliculas`, backoffice |
| S-13 | Dar de baja una película es una baja lógica, para conservar el historial. bool activo | Tabla pelicula |
| S-14 | La página principal muestra la cartelera, los productos y las promociones. | Mockup de inicio, `/api/cartelera`, `/api/productos`, `/api/promociones` 

### Funciones

| ID | Supuesto | Impacta en |
| --- | --- | --- |
| S-15 | Una función es una película en una sala con un único DATETIME de inicio, y tiene sus propias butacas disponibles. | Tabla funcion |
| S-16 | Una sala no puede tener dos funciones que se superpongan en el horario. dif de tiempo 30mins despues de finalizada minimo | `POST /api/funciones` | 
| S-17 | Cada función tiene un precio de entrada único para todas sus butacas. | Tabla funcion, cálculo del total |
| S-18 | Cancelar una función se hace cambiando su estado a cancelada, sin borrarla. | `PATCH /api/funciones/<id>` |

### Compra

| ID | Supuesto | Impacta en |
| --- | --- | --- |
| S-19 | Una compra es de una sola función y puede incluir varias butacas con maximo 6. | Tablas compra y entrada, mockup |
| S-20 | Las butacas tienen reserva temporal durante 10 minutos mientras se confirma la compra, si se demora 10 mins o mas se cancela la compra y debe empezarse de nuevo | `POST /api/compras` |
| S-21 | Una butaca no se vende dos veces en la misma función, y el backend vuelve a verificarlo al confirmar. | Restricción en entrada, error 409 |
| S-22 | El total lo calcula el backend (entradas más servicios), nunca el front. | `POST /api/compras` |
| S-23 | No hay pasarela de pago real: el checkout se simula y genera la factura. | Checkout | Propuesto |
| S-24 | La factura se genera en PDF y se envía por mail junto con un QR para las entradas, uno para las compras y uno para estacionamientos. | Mail, `GET /api/compras/<id>/factura` |

### Servicios y promociones

| ID | Supuesto | Impacta en |
| --- | --- | --- |
| S-25 | Los servicios (comida, bebidas, estacionamiento, acceso VIP) valen para todas las salas y se compran junto con las entradas (formato promoción) o aparte de las entradas(estacionamiento y acceso VIP unicamente con las entradas). | Tablas servicio y compra_servicio |
| S-26 | Dar de baja un servicio lo marca como inactivo, sin borrar las compras que ya lo incluyen. | `PATCH /api/servicios/<id>` |
| S-27 | El precio del servicio se guarda en la compra al momento de comprar, para que un cambio de precio no altere compras viejas. | Tabla compra_servicio |
| S-28 | Los productos y las promociones se muestran en la página principal, solo los productos se pueden comprar por separado | Tablas y endpoints de productos y promociones |

### Cancelación

| ID | Supuesto | Impacta en |
| --- | --- | --- |
| S-29 | La cancelación se permite hasta 2 horas antes de la función. | `PATCH /api/compras/<id>` |
| S-30 | Al cancelar, las butacas vuelven a quedar libres y la compra queda con estado cancelada, conservando el historial. | Tablas compra y entrada | 
| S-31 | Solo el propietario de la compra puede reembolsarla 1 hora antes maximo, desde su cuenta o desde el botón del mail. Puede editar la compra. | Seguridad, mail |

### QR e ingreso

| ID | Supuesto | Impacta en |
| --- | --- | --- |
| S-32 | Se genera un QR por venta, con un token para cada entrada y su función. | `GET /api/entradas/<id>/qr` |
| S-33 | Al escanear se valida que corresponda a esa función y fecha y que no esté usado ni cancelado; si es válido, se marca como utilizado. | `POST /api/funciones/<id>/validaciones-qr` |
| S-34 | Solo el administrador o el personal autorizado puede validar QR. | Seguridad |

### Transversales

| ID | Supuesto | Impacta en |
| --- | --- | --- |
| S-35 | Toda la fecha y hora se guarda en un único campo DATETIME, en hora local de Argentina. | Todas las tablas |
| S-36 | El front se comunica con el back solo con requests desde Python, siempre en JSON. | Arquitectura |
| S-38 | Los mails (confirmación, factura y QR) se envían por SMTP. | Servicio de mail |
| S-39 | El sitio es responsive, con bootstrap | Templates |
| S-40 | Las estadísticas se calculan con consultas SQL sobre la base en el momento de pedirlas. | Dashboards |
| S-42 | Si se hacen las reseñas, solo pueden escribirlas los clientes cuya entrada fue validada en esa película. | Reseñas (deseable) |

---

## Hipótesis

| ID | Hipótesis | Se verifica con |
| --- | --- | --- |
| H-01 | Un flujo de 6 pasos (local, película, función, verifica si esta iniciada la sesion(en caso contrario pide iniciar sesion), butacas, confirmación) permite comprar sin ayuda. | Prueba con alguien ajeno al equipo |
| H-02 | Mostrar las butacas libres y ocupadas en el momento de elegir reduce los conflictos por doble venta. | Cantidad de errores 409 en la compra |
| H-03 | Enviar el QR por mail evita filas en la entrada, porque la validación toma segundos. | Tiempo de validación por ingreso |
| H-04 | Los dashboards de ocupación por función ayudan al administrador a decidir qué películas mantener en cartelera. | Revisión con el tutor |
| H-05 | Permitir cancelar 2 hora antes libera butacas que se pueden volver a vender. | Cancelaciones seguidas de nuevas ventas |

---

## Pendientes de decidir

> [!warning] Con el tutor
> Hasta que se resuelvan no son supuestos. Al resolver una, se completa la decisión y se actualiza el supuesto relacionado en la hoja Supuestos.

| ID | Pregunta | Estado |
| --- | --- | --- |
| P-01 | ¿Sesiones o tokens para autenticar? Esto define cómo funciona el logout. Como funciona la sesion |
| P-02 | Como funcionan las estadisticas, con SQL o python? para ventas y para graficos |
| P-03 | Condiciones para las promociones. Cantidad y tipo |
| P-04 | Un QR por entrada o por venta ? y un QR para compras y otro QR para estacionamiento y cantidad |
| P-05 | Que consideraciones hay que tener en base al tamaño/alcance del cine |
| P-06 | Consulta sobre estacionamiento y el espacio del mismo. Discutir |
| P-07 | En caso de que se elija la misma butaca al mismo tiempo por dos usuarios al mismo tiempo, que pasa? |
| P-08 | ¿Limite de cantidad de admins? |
| P-09 | ¿Se ingresa edad mediante form o con dni y con este se averigua edad con renaper? |
| P-10 | ¿Cuanto tiempo dura la sesion abierta? |

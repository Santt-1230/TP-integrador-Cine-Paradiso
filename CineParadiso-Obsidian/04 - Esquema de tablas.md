# Diccionario de tablas - Cine Paradiso

**Índice:** [[#usuario]] · [[#locales]] · [[#salas]] · [[#butacas]] · [[#estacionamiento]] · [[#peliculas]] · [[#generos]] · [[#pelicula_genero]] · [[#promociones]] · [[#funciones]] · [[#compras]] · [[#entradas]] · [[#productos]] · [[#compra_producto]] · [[#qr]] · [[#resenas]]

---

## usuario

Todas las personas que usan el sistema (clientes y administradores). También registra quién validó un QR.

**usuario** guarda a todas las personas que usan el sistema, tanto clientes como administradores. Tiene nombre, email, contraseña (solo el hash) y el rol, que define qué puede hacer cada uno. También sirve para registrar quién validó un QR en la entrada.

|Campo|Tipo|Clave|Conectado a|Valores / restricciones|
|---|---|---|---|---|
|id_usuario|INT|PK||Autoincremental|
|nombre|VARCHAR(150)|||Obligatorio|
|email|VARCHAR(200)|||Obligatorio, único|
|contrasena_hash|VARCHAR(255)|||Obligatorio, solo el hash|
|rol|ENUM|||`cliente` o `administrador`. Por defecto `cliente`|
|activo|BOOLEAN|||Por defecto verdadero|
|fecha_registro|DATETIME|||Por defecto la fecha actual|
## Infraestructura física
### locales

**locales** son los 3 centros de entretenimiento de Cine Paradiso. Es el punto de partida de toda la estructura física.

|Campo|Tipo|Clave|Conectado a|Valores / restricciones|
|---|---|---|---|---|
|id_local|INT|PK||Autoincremental|
|nombre|VARCHAR(50)|||Obligatorio, único|
|direccion|VARCHAR(200)|||Opcional|
|activo|BOOLEAN|||Por defecto verdadero|

## salas

**salas** son las salas de cada local. Cada una tiene su número, su capacidad y un estado (activa o inactiva). Dar de baja una sala no la borra, solo la marca como inactiva, para no perder las funciones históricas.

| Campo       | Tipo | Clave | Conectado a      | Valores / restricciones                          |
| ----------- | ---- | ----- | ---------------- | ------------------------------------------------ |
| id_sala     | INT  | PK    |                  | Autoincremental                                  |
| id_local    | INT  | FK    | locales.id_local | Obligatorio                                      |
| numero_sala | INT  |       |                  | Obligatorio. No se repite dentro del mismo local |
| capacidad   | INT  |       |                  | Obligatorio, mayor a 0                           |
| estado      | ENUM |       |                  | `activa` o `inactiva`. Por defecto `activa`      |

## butacas

**butacas** son los asientos de cada sala, identificados por fila (letra) y número, por ejemplo “C7”. Se generan cuando se crea la sala.

|Campo|Tipo|Clave|Conectado a|Valores / restricciones|
|---|---|---|---|---|
|id_butaca|INT|PK||Autoincremental|
|id_sala|INT|FK|salas.id_sala|Obligatorio|
|fila|CHAR(1)|||Obligatorio, una letra (A, B, C...)|
|numero|INT|||Obligatorio. La combinación sala + fila + número no se repite|

## estacionamiento

**estacionamiento** representa la playa de estacionamiento de cada local, con su capacidad. Es la tabla más provisoria, porque las reglas del estacionamiento todavía están pendientes (P-06).
Los 3 centros de entretenimiento de Cine Paradiso.
Salas de cada local. La baja es lógica (se marca inactiva).
Asientos de cada sala, identificados por fila (letra) y número.

|Campo|Tipo|Clave|Conectado a|Valores / restricciones|
|---|---|---|---|---|
|id_estacionamiento|INT|PK||Autoincremental|
|id_local|INT|FK|locales.id_local|Obligatorio, único (uno por local)|
|capacidad|INT|||Obligatorio, 0 o más|
|activo|BOOLEAN|||Por defecto verdadero|
## Películas y cartelera
## peliculas


**peliculas** es el catálogo propio, cargado desde OMDb o TMDB: título, sinopsis, póster, duración y clasificación. Guarda también el período de cartelera (desde y hasta) y un indicador de si está activa. Así no dependés de la API externa en cada consulta.


| Campo           | Tipo         | Clave | Conectado a | Valores / restricciones                         |
| --------------- | ------------ | ----- | ----------- | ----------------------------------------------- |
| id_pelicula     | INT          | PK    |             | Autoincremental                                 |
| id_externo      | VARCHAR(30)  |       |             | Opcional, único. ID en OMDb o TMDB              |
| nombre          | VARCHAR(255) |       |             | Obligatorio                                     |
| sinopsis        | TEXT         |       |             | Opcional                                        |
| poster_url      | VARCHAR(500) |       |             | Opcional                                        |
| duracion_min    | INT          |       |             | Obligatorio, mayor a 0                          |
| clasificacion   | VARCHAR(20)  |       |             | Opcional                                        |
| cartelera_desde | DATE         |       |             | Opcional                                        |
| cartelera_hasta | DATE         |       |             | Opcional. Igual o posterior a `cartelera_desde` |
| activo          | BOOLEAN      |       |             | Por defecto verdadero                           |

## generos

**generos** es la lista de géneros (acción, drama, etc.).
Catálogo propio, cargado desde OMDb o TMDB, con su período de cartelera.

|Campo|Tipo|Clave|Conectado a|Valores / restricciones|
|---|---|---|---|---|
|id_genero|INT|PK||Autoincremental|
|nombre|VARCHAR(50)|||Obligatorio, único|

## pelicula_genero

**pelicula_genero** conecta películas con géneros. Hace falta porque una película puede tener varios géneros y un género tiene muchas películas. Sirve para el dashboard de ventas por género.

|Campo|Tipo|Clave|Conectado a|Valores / restricciones|
|---|---|---|---|---|
|id_pelicula|INT|PK compuesta + FK|peliculas.id_pelicula|Obligatorio|
|id_genero|INT|PK compuesta + FK|generos.id_genero|Obligatorio. La pareja no se puede repetir|
## promociones

**promociones** son las promociones que se muestran en la página principal. Son solo informativas, y sus condiciones todavía están por definir (P-03).

|Campo|Tipo|Clave|Conectado a|Valores / restricciones|
|---|---|---|---|---|
|id_promocion|INT|PK||Autoincremental|
|titulo|VARCHAR(150)|||Obligatorio|
|descripcion|TEXT|||Opcional|
|imagen_url|VARCHAR(500)|||Opcional|
|vigente_desde|DATE|||Opcional|
|vigente_hasta|DATE|||Opcional|
|activo|BOOLEAN|||Por defecto verdadero|

## funciones

**funciones** es la tabla central del negocio: una película, en una sala, a una fecha y hora determinadas, con su precio de entrada y su estado (programada, cancelada o finalizada). Guarda también la hora de fin, que se usa para controlar que dos funciones no se pisen en la misma sala. Cancelar una función cambia el estado, no la borra.

|Campo|Tipo|Clave|Conectado a|Valores / restricciones|
|---|---|---|---|---|
|id_funcion|INT|PK||Autoincremental|
|id_pelicula|INT|FK|peliculas.id_pelicula|Obligatorio|
|id_sala|INT|FK|salas.id_sala|Obligatorio|
|fecha_hora_inicio|DATETIME|||Obligatorio. No puede haber dos funciones con el mismo inicio en la misma sala|
|fecha_hora_fin|DATETIME|||Obligatorio, posterior al inicio|
|precio_entrada|DECIMAL(10,2)|||Obligatorio, 0 o más|
|estado|ENUM|||`programada`, `cancelada` o `finalizada`. Por defecto `programada`|


## Compras

**compras** representa el acto de comprar: quién compró, para qué función, cuánto pagó y en qué estado está (pendiente, confirmada, cancelada o expirada). Guarda cuándo vence la reserva de 10 minutos, el número de factura y, si se canceló, cuándo, por qué y cuánto se reembolsó.

|Campo|Tipo|Clave|Conectado a|Valores / restricciones|
|---|---|---|---|---|
|id_compra|INT|PK||Autoincremental|
|id_usuario|INT|FK|usuario.id_usuario|Obligatorio|
|id_funcion|INT|FK|funciones.id_funcion|Obligatorio|
|estado|ENUM|||`pendiente`, `confirmada`, `cancelada` o `expirada`. Por defecto `pendiente`|
|fecha_creacion|DATETIME|||Por defecto la fecha actual|
|expira_en|DATETIME|||Obligatorio. Creación más 10 minutos|
|fecha_confirmacion|DATETIME|||Opcional, se llena al confirmar|
|total|DECIMAL(10,2)|||Por defecto 0. Lo calcula el backend|
|numero_factura|VARCHAR(30)|||Opcional, único|
|fecha_cancelacion|DATETIME|||Opcional, se llena al cancelar|
|motivo_cancelacion|ENUM|||`cliente` o `funcion_cancelada`. Opcional|
|monto_reembolsado|DECIMAL(10,2)|||Opcional|

## entradas


**entradas** son las butacas concretas de cada compra. Una compra puede tener varias entradas (hasta 6), una por butaca. Cada una guarda su precio y su estado. Esta tabla es la que impide vender una butaca dos veces en la misma función, y al cancelar la libera sin perder el historial.

|Campo|Tipo|Clave|Conectado a|Valores / restricciones|
|---|---|---|---|---|
|id_entrada|INT|PK||Autoincremental|
|id_compra|INT|FK|compras.id_compra|Obligatorio|
|id_funcion|INT|FK|funciones.id_funcion|Obligatorio|
|id_butaca|INT|FK|butacas.id_butaca|Obligatorio|
|precio_unitario|DECIMAL(10,2)|||Obligatorio|
|estado|ENUM|||`reservada`, `confirmada`, `utilizada` o `cancelada`. Por defecto `reservada`|
|butaca_ocupada|INT|||Se calcula sola: copia `id_butaca`, salvo que esté `cancelada` (queda vacía). Con función + butaca ocupada evita la doble venta|
## productos

**productos** es el catálogo de comida, bebidas, acceso VIP y estacionamiento, con su precio y si está activo. Dar de baja un producto lo marca como inactivo, sin tocar las compras viejas.

|Campo|Tipo|Clave|Conectado a|Valores / restricciones|
|---|---|---|---|---|
|id_producto|INT|PK||Autoincremental|
|nombre|VARCHAR(100)|||Obligatorio|
|tipo|ENUM|||`comida`, `bebida`, `estacionamiento`, `vip` u `otro`|
|descripcion|VARCHAR(255)|||Opcional|
|precio|DECIMAL(10,2)|||Obligatorio, 0 o más|
|activo|BOOLEAN|||Por defecto verdadero|

## compra_producto

**compra_producto** conecta cada compra con los productos que incluyó, con la cantidad. Guarda el precio del momento de la compra, así que un cambio de precio posterior no altera las compras anteriores.

|Campo|Tipo|Clave|Conectado a|Valores / restricciones|
|---|---|---|---|---|
|id_compra_producto|INT|PK||Autoincremental|
|id_compra|INT|FK|compras.id_compra|Obligatorio|
|id_producto|INT|FK|productos.id_producto|Obligatorio. No se repite dentro de la misma compra|
|cantidad|INT|||Obligatorio, mayor a 0. Por defecto 1|
|precio_unitario|DECIMAL(10,2)|||Obligatorio. Precio congelado al comprar|

## Ingreso a la sala

**qr** guarda los códigos QR que se mandan por mail. Cada uno tiene un token único (lo que lee el escáner) y un código manual de respaldo por si el escaneo falla. Registra si está válido, usado o cancelado, cuándo se usó y qué administrador lo validó. Puede ser un QR de entrada, de productos o de estacionamiento, y también sirve si al final decidís hacer uno por venta en vez de uno por entrada.

|Campo|Tipo|Clave|Conectado a|Valores / restricciones|
|---|---|---|---|---|
|id_qr|INT|PK||Autoincremental|
|id_compra|INT|FK|compras.id_compra|Obligatorio|
|id_entrada|INT|FK|entradas.id_entrada|Opcional. Vacío si el QR es por venta|
|tipo|ENUM|||`entrada`, `productos` o `estacionamiento`|
|token|CHAR(64)|||Obligatorio, único. Lo que lleva el QR|
|codigo_manual|VARCHAR(12)|||Obligatorio, único. Respaldo si falla el escaneo|
|estado|ENUM|||`valido`, `utilizado` o `cancelado`. Por defecto `valido`|
|fecha_uso|DATETIME|||Opcional, se llena al escanear|
|id_validador|INT|FK|usuario.id_usuario|Opcional. Quién lo escaneó|
## Reseñas

**resenas** (deseable) permite que un cliente puntúe y comente una película. Está atada a una entrada específica, y solo una por entrada, así que solo pueden reseñar quienes efectivamente fueron a la función.

|Campo|Tipo|Clave|Conectado a|Valores / restricciones|
|---|---|---|---|---|
|id_resena|INT|PK||Autoincremental|
|id_usuario|INT|FK|usuario.id_usuario|Obligatorio|
|id_pelicula|INT|FK|peliculas.id_pelicula|Obligatorio|
|id_entrada|INT|FK|entradas.id_entrada|Obligatorio, único (una reseña por entrada)|
|puntaje|TINYINT|||Obligatorio, entre 1 y 5|
|comentario|TEXT|||Opcional|
|fecha|DATETIME|||Por defecto la fecha actual|

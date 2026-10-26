**PROYECTO INTEGRADOR / HITO 1**

Cine Paradiso

**Alcance del producto y backlog**

> **PROPÓSITO**
>
> Definir qué valor entregará la primera versión de Cine Paradiso y ordenar el trabajo necesario para construirla.

Una propuesta inicial para revisar en equipo y acordar con el tutor.


| **PRODUCTO**                     | **USUARIOS**               | **ENTREGA**             |
| -------------------------------- | -------------------------- | ----------------------- |
| Sistema web de venta de entradas | Clientes y administradores | Hito 1 · 26 de octubre |

**BASE DEL PROYECTO**

Aplicación web responsive con frontend y backend en Flask, base de datos MySQL y código versionado en GitHub. La comunicación entre frontend y backend se realizará desde Python mediante requests, según los requisitos de la materia.

# 01 Alcance del producto

Cine Paradiso ofrecerá una experiencia web para consultar películas y funciones, elegir butacas y comprar entradas. El equipo administrador podrá mantener la programación y controlar el acceso a las salas. El alcance prioriza un recorrido de compra completo y una operación básica del cine.

## Objetivo

Permitir que un cliente complete una compra de forma clara y segura —desde la cartelera hasta la confirmación con QR— y dar al administrador herramientas para configurar películas, salas, funciones y servicios.

## Usuarios y valor

* **Cliente.** Encuentra una película y una función, consulta las butacas, compra entradas y conserva el comprobante de ingreso.
* **Administrador.** Organiza la cartelera y las funciones, gestiona salas y servicios, valida entradas y consulta indicadores de operación.

## Incluido en la primera versión

* **Acceso y perfiles.** Registro e inicio de sesión para clientes; acceso administrativo protegido por rol.
* **Cartelera y funciones.** Consulta de películas vigentes, información principal, locales, horarios y precios.
* **Butacas y compra.** Visualización de asientos libres y ocupados; compra de entradas y servicios con verificación de disponibilidad en el backend.
* **Confirmación e ingreso.** Checkout simulado, comprobante y QR vinculados a la compra; validación del QR y registro de uso.
* **Autogestión del cliente.** Consulta del historial y cancelación según un plazo que deberá acordarse.
* **Backoffice.** Gestión de películas, locales, salas, funciones y servicios; consulta de ocupación, ventas y cancelaciones.
* **Base técnica.** Frontend y backend Flask, MySQL, endpoints JSON protegidos, SQL explícito y sitio responsive.
* **Mejoras.** Reseñas de películas, reportes PDF y dockerización, que se incorporarán una vez completado el flujo principal.

## Fuera de alcance inicial

No se contempla procesar pagos reales, desarrollar una aplicación móvil nativa ni vender productos promocionales por separado.

# 02 Backlog de producto

Historias de usuario priorizadas para construir y validar el producto. Las prioridades orientan el orden de trabajo; el equipo puede ajustarlas en el tablero Kanban. “Alta” reúne el flujo principal y los controles básicos; “Media” completa la operación; “Baja” agrupa mejoras posteriores.


| **ID**     | **Prioridad** | **Épica**    | **Historia de usuario**                                                                          | **Criterio de aceptación**                                                                                         |
| ---------- | ------------- | ------------- | ------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------- |
| **PBI-01** | **Alta**      | Acceso        | Como administrador, quiero iniciar sesión para ingresar al backoffice.                          | Solo una cuenta con rol administrador accede a las funciones administrativas.                                       |
| **PBI-02** | **Alta**      | Acceso        | Como cliente, quiero registrarme e iniciar sesión para realizar compras.                        | El email es único; el registro público no permite crear cuentas administradoras.                                  |
| **PBI-03** | **Alta**      | Cartelera     | Como visitante, quiero consultar la cartelera para conocer las películas disponibles.           | Se muestran título, sinopsis, póster, duración, clasificación y funciones vigentes.                             |
| **PBI-04** | **Alta**      | Funciones     | Como cliente, quiero filtrar o consultar funciones por película y local para elegir un horario. | Cada función informa local, sala, fecha y hora de inicio, y precio.                                                |
| **PBI-05** | **Alta**      | Butacas       | Como cliente, quiero ver las butacas libres y ocupadas antes de comprar.                         | El plano distingue claramente disponibilidad y butacas ya vendidas para esa función.                               |
| **PBI-06** | **Alta**      | Compra        | Como cliente, quiero seleccionar butacas y comprar entradas para una función.                   | El backend vuelve a comprobar disponibilidad al confirmar; una misma butaca no se vende dos veces para la función. |
| **PBI-07** | **Alta**      | Compra        | Como cliente, quiero agregar servicios a mi compra para adquirir opciones adicionales.           | Puedo seleccionar servicios activos y el precio queda registrado en la compra.                                      |
| **PBI-08** | **Alta**      | Confirmación | Como cliente, quiero finalizar un checkout simulado y recibir la confirmación de mi compra.     | El total lo calcula el backend; se genera un comprobante con los datos de la compra.                                |
| **PBI-09** | **Alta**      | QR e ingreso  | Como cliente, quiero recibir un QR para presentar mi entrada al ingresar.                        | El QR identifica la compra o entrada y la función correspondiente.                                                 |
| **PBI-10** | **Alta**      | QR e ingreso  | Como administrador, quiero validar el QR para controlar el ingreso a la sala.                    | Se verifica función y fecha; un QR cancelado o usado se rechaza y uno válido queda marcado como utilizado.        |
| **PBI-11** | **Alta**      | Backoffice    | Como administrador, quiero cargar y modificar películas para mantener actualizada la cartelera. | Puedo guardar información principal y período de exhibición; la baja conserva el historial.                      |
| **PBI-12** | **Alta**      | Backoffice    | Como administrador, quiero configurar locales, salas y butacas para representar los cines.       | Cada sala pertenece a un local y contiene capacidad y butacas identificadas.                                        |
| **PBI-13** | **Alta**      | Backoffice    | Como administrador, quiero programar funciones para publicar horarios de películas.             | La función vincula película, sala y fecha/hora; no se superpone con otra función en la misma sala.               |
| **PBI-14** | **Media**     | Historial     | Como cliente, quiero consultar mis compras anteriores para revisar mis entradas.                 | El perfil muestra compras y estados, asociadas al cliente autenticado.                                              |
| **PBI-15** | **Media**     | Cancelaciones | Como cliente, quiero cancelar una compra dentro del plazo permitido para liberar mis butacas.    | La solicitud se acepta solo si cumple el plazo acordado; las butacas quedan disponibles nuevamente.                 |
| **PBI-16** | **Media**     | Backoffice    | Como administrador, quiero administrar servicios para ofrecer opciones adicionales.              | Puedo crear, modificar y desactivar servicios sin alterar compras históricas.                                      |
| **PBI-17** | **Media**     | Estadísticas | Como administrador, quiero consultar ocupación y ventas para evaluar la operación.             | El panel presenta ocupación por función y película, ventas y cancelaciones.                                      |
| **PBI-18** | **Media**     | Experiencia   | Como cliente, quiero recibir la factura y el QR por email para conservar la confirmación.       | El correo contiene el comprobante y el QR asociados a la compra.                                                    |
| **PBI-19** | **Media**     | Experiencia   | Como usuario, quiero usar la web desde celular o tablet para completar las tareas principales.   | La cartelera, selección de butacas y backoffice se adaptan a pantallas pequeñas.                                  |
| **PBI-20** | **Baja**      | Mejoras       | Como administrador, quiero importar datos de películas para agilizar la carga.                  | Puedo buscar en OMDb o TMDB y guardar los datos seleccionados en la base propia.                                    |
| **PBI-21** | **Baja**      | Mejoras       | Como cliente que asistió, quiero calificar una película para compartir mi opinión.            | La opción se habilita solo cuando el QR de la función fue validado.                                               |
| **PBI-22** | **Baja**      | Mejoras       | Como administrador, quiero exportar un reporte de ventas para compartir resultados.              | Se genera un PDF con ventas por función y películas más vistas.                                                  |

**Definición de terminado**

Una historia se considera terminada cuando cumple sus criterios de aceptación, respeta los permisos del rol, maneja errores sin interrumpir la aplicación y queda integrada al repositorio con un commit asociado a la tarea.

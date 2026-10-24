# Cine Paradiso — mapa entre mockups, Frontend y API

## Mapa de notas

- [[01- Supuestos e hipótesis - Cine Paradiso]] — Planteo de ideas, hipotesis y supuestos
- [[02 - Flujo de compra de entradas]] — recorrido completo, desde elegir una película hasta validar el QR.
- [[03- CineParadiso-Endpoints-por-Modulo-Obsidian]] — Endpoints del frontend y del backend
- [[04 - Esquema de tablas]] — Esquema de tablas con sus caracteristicas
## Regla de arquitectura de la materia

```mermaid
flowchart TD
    A[Usuario toca un botón] --> B[Navegador solicita una ruta al Frontend Flask]
    B --> C[La ruta Python del Frontend usa requests]
    C --> D[Backend Flask / API REST]
    D --> E[MySQL]
    E --> D
    D --> C
    C --> F[Frontend recibe JSON y renderiza HTML]
    F --> G[El navegador muestra la nueva página]
```

## Archivos incluidos

La imagen original compartida por el grupo está en `assets/Mockups-Cine-Paradiso.png`.

![[assets/Mockups-Cine-Paradiso.png]]

## Convenciones que usamos en el ejemplo

- Las rutas `/...` son páginas/formularios del **Frontend Flask**.
- Las rutas `/api/...` son endpoints del **Backend Flask**.


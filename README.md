# Cine Paradiso

Sistema de gestión de un cine desarrollado como proyecto integrador.

## Tecnologías utilizadas

- **Frontend:** Flask, Jinja, HTML, CSS y JavaScript.
- **Backend:** Flask (API REST).
- **Base de datos:** MySQL 8.
- **Contenedores:** Docker y Docker Compose.

## Estructura del proyecto

```text
TP-integrador-Cine-Paradiso/
├── CineParadiso-Obsidian/
│   ├── assets/
│   ├── repositories/
│   ├── routes/
│   ├── validators/
│   └── Documentación del proyecto (.md)
│
├── backend/
│   ├── repositories/
│   ├── routes/
│   ├── services/
│   ├── validators/
│   ├── .env.example
│   ├── .flaskenv
│   ├── app.py
│   ├── constants.py
│   ├── db.py
│   ├── requirements.txt
│   ├── tmdb.py
│   ├── utils.py
│   └── Dockerfile
│
├── frontend/
│   ├── routes/
│   ├── static/
│   ├── templates/
│   ├── .env.example
│   ├── .flaskenv
│   ├── api.py
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── sql/
│   └── init_db.sql
│
├── docker-compose.yml
├── .gitignore
└── README.md
```

## Requisitos

Para ejecutar el proyecto mediante Docker se necesita:

- Git.
- Docker.
- Docker Compose.

No es necesario instalar Python, Flask ni MySQL localmente. Docker instala las dependencias de cada servicio utilizando sus respectivos archivos `requirements.txt`.

## Instalación y configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/Santt-1230/TP-integrador-Cine-Paradiso.git
cd TP-integrador-Cine-Paradiso
```

### 2. Configurar las variables de entorno

Crear los archivos `.env` a partir de los ejemplos incluidos en cada carpeta:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

Completar ambos archivos con los valores correspondientes.

Cada integrante debe configurar sus propias credenciales y claves.

**Importante:** los archivos `.env` contienen información sensible y no deben subirse al repositorio.

### 3. Levantar el proyecto

Desde la carpeta raíz del proyecto, ejecutar:

```bash
docker compose --env-file backend/.env up --build -d
```

Docker construye las imágenes, instala las dependencias y levanta los siguientes servicios:

- MySQL.
- Backend.
- Frontend.

La primera ejecución puede demorar más debido a la descarga de imágenes, instalación de dependencias e inicialización de la base de datos.

### 4. Acceder a la aplicación

Una vez levantados los servicios, acceder desde el navegador:

| Servicio | Dirección |
|---|---|
| Frontend | http://localhost:5001 |
| Backend | http://localhost:5000 |

### 5. Comprobar el estado de los servicios

Para verificar que los contenedores estén funcionando:

```bash
docker compose --env-file backend/.env ps
```

Para consultar los registros de ejecución:

```bash
docker compose --env-file backend/.env logs
```

Para consultar los registros de un servicio específico:

```bash
docker compose --env-file backend/.env logs backend
```

Se puede reemplazar `backend` por `frontend` o `db`.

## Detener el proyecto

Para detener los contenedores:

```bash
docker compose --env-file backend/.env down
```

Este comando detiene y elimina los contenedores, pero conserva los datos de MySQL almacenados en el volumen de Docker.

**Importante:** no utilizar `docker compose down -v` salvo que se quiera eliminar también el volumen y perder los datos almacenados en la base de datos.

## Base de datos

La base de datos MySQL se inicializa automáticamente utilizando el archivo `sql/init_db.sql`.

Este archivo contiene la estructura inicial de la base de datos.

La inicialización automática se ejecuta únicamente cuando MySQL crea un volumen nuevo. Si el volumen ya existe, Docker no vuelve a ejecutar el script automáticamente.

Cada integrante tendrá su propia base de datos local. Los registros no se sincronizan automáticamente entre computadoras.

## Puertos utilizados

| Servicio | Puerto |
|---|---|
| Frontend | 5001 |
| Backend | 5000 |
| MySQL | 3307 (host) / 3306 (contenedor) |


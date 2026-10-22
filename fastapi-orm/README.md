# Clase 7 - ORM con FastAPI y PostgreSQL

## Tema

En esta clase conectamos una API de FastAPI con PostgreSQL usando un ORM.

## ¿Qué es un ORM?

ORM significa **Object Relational Mapping**. Permite trabajar con una base de datos usando clases y objetos de Python.

- Una clase representa una tabla.
- Un atributo representa una columna.
- Un objeto representa un registro.
- SQLAlchemy es el ORM utilizado en este proyecto.

## Estructura del proyecto

```text
main.py              Inicio de FastAPI
database.py          Conexión y sesiones de PostgreSQL
models/              Modelos ORM que representan tablas
schemas/             Validación de datos con Pydantic
crud/                Operaciones de base de datos
api/                 Rutas o endpoints
requirements.txt     Dependencias
.env.example         Ejemplo de variables de entorno
```

## Función de cada carpeta

- `models/`: contiene las clases de SQLAlchemy.
- `schemas/`: valida los datos recibidos y enviados por la API.
- `crud/`: contiene las operaciones de crear, consultar, actualizar y eliminar.
- `api/`: contiene las rutas que puede consumir el usuario.
- `database.py`: configura la conexión y las sesiones de la base de datos.

## Configuración

Crear el archivo local de variables de entorno:

```bash
cp .env.example .env
```

Completar `.env` con los datos reales de PostgreSQL. Este archivo no debe subirse a Git.

Instalar dependencias y ejecutar la API:

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

La documentación está disponible en:

```text
http://127.0.0.1:8000/docs
```

Para probar una operación:

1. Seleccione la operación que desea ejecutar.
2. Haga clic en **Try it out**.
3. Escriba los datos solicitados.
4. Haga clic en **Execute**.
5. Revise el código y el cuerpo de la respuesta.

## Peticiones de la API

### GET `/`

Esta es la ruta inicial de la aplicación. Sirve para comprobar que el servidor está funcionando.

Respuesta:

```json
{
  "message": "Hola mundo"
}
```

### POST `/estudiantes`

Agrega un nuevo estudiante al dataset. El cuerpo de la petición debe incluir todos los campos definidos en el modelo `Estudiante`.

Ejemplo de solicitud:

```json
{
  "id": 101,
  "nombre": "Ana Gómez",
  "edad": 20,
  "programa": "Ingeniería de Sistemas"
}
```

Internamente, el estudiante se convierte en una lista (el identificador es el primer elemento) y se agrega al dataset:

```text
[101, "Ana Gómez", 20, "Ingeniería de Sistemas"]
```

El `id` debe ser único. Si ya existe un estudiante con ese `id`, la API responde `{"error": "Ya existe un estudiante con ese id"}`.

Respuesta esperada:

```json
{
  "message": "Estudiante agregado correctamente",
  "estudiante": [101, "Ana Gómez", 20, "Ingeniería de Sistemas"],
  "dataset": [
    [101, "Ana Gómez", 20, "Ingeniería de Sistemas"]
  ]
}
```

Cada vez que se ejecuta el POST, el dataset completo también se imprime en la consola del servidor.

### GET `/estudiantes/{id}`

Consulta un único estudiante a partir de su identificador (`id`). A diferencia de PUT, PATCH y DELETE, este parámetro no es la posición en la lista sino el `id` guardado en el estudiante.

Ejemplo:

```text
GET /estudiantes/101
```

Respuesta para un `id` existente:

```json
{
  "estudiante": [101, "Ana Gómez", 20, "Ingeniería de Sistemas"]
}
```

Respuesta para un `id` que no existe:

```json
{
  "error": "Estudiante no encontrado"
}
```

### PUT `/estudiantes/{indice}`

Reemplaza completamente un estudiante existente. El parámetro `indice` indica la posición del estudiante dentro del dataset. El primer estudiante tiene índice `0`, el segundo índice `1`, y así sucesivamente.

Ejemplo para reemplazar el primer estudiante:

```text
PUT /estudiantes/0
```

Cuerpo de la solicitud:

```json
{
  "id": 101,
  "nombre": "Ana Rodríguez",
  "edad": 21,
  "programa": "Ingeniería de Software"
}
```

El PUT exige todos los campos (incluido el `id`) y reemplaza completamente la lista que se encuentra en la posición indicada. Si el `id` enviado pertenece a otro estudiante, la API responde con un error.

### PATCH `/estudiantes/{indice}`

Actualiza parcialmente un estudiante. A diferencia de PUT, solo es necesario enviar los campos que se desean modificar.

Ejemplo para cambiar únicamente el programa del primer estudiante:

```text
PATCH /estudiantes/0
```

Cuerpo de la solicitud:

| Método | Ruta | Función |
|---|---|---|
| GET | `/estudiantes` | Listar estudiantes |
| GET | `/estudiantes/{id}` | Consultar un estudiante |
| POST | `/estudiantes` | Crear un estudiante |
| PUT | `/estudiantes/{id}` | Reemplazar un estudiante |
| PATCH | `/estudiantes/{id}` | Actualizar parcialmente |
| DELETE | `/estudiantes/{id}` | Eliminar un estudiante |
| GET | `/health/db` | Verificar la conexión |

## Tarea: implementar mediciones

La base de datos ya contiene la tabla `public.mediciones`. No se debe crear otra tabla ni cambiar su estructura.

Los campos no enviados conservan su valor original. El `id` no se modifica con PATCH. Este comportamiento se logra con el modelo `EstudianteActualizacion` y `exclude_unset=True`.

| Columna | Tipo | Obligatoria | Descripción |
|---|---|---|---|
| `id` | integer | Sí | Identificador principal |
| `estudiante_id` | integer | Sí | Estudiante relacionado |
| `variable` | varchar(50) | Sí | Nombre de la medición |
| `valor` | numeric | Sí | Valor registrado |
| `unidad` | varchar(20) | Sí | Unidad del valor |
| `fecha_hora` | timestamp with time zone | Sí | Fecha y hora de la medición |

`estudiante_id` es una llave foránea que apunta a `estudiantes.id`. Para crear una medición se debe utilizar un estudiante existente.

### Orden de implementación

1. **Pydantic:** crear los schemas de entrada, actualización y respuesta.
2. **ORM:** crear en `models/` la clase que represente `mediciones` y su relación con `estudiantes`.
3. **CRUD:** crear en `crud/` las funciones para listar, consultar, crear, actualizar y eliminar.
4. **API:** crear en `api/` los endpoints que utilicen las funciones CRUD.
5. **Pruebas:** probar todas las operaciones desde Swagger en `/docs`.

La API debe permitir listar, consultar, crear, actualizar y eliminar mediciones.

### Endpoints de mediciones

| Método | Ruta | Función |
|---|---|---|
| GET | `/mediciones` | Listar mediciones |
| GET | `/mediciones/{id}` | Consultar una medición |
| POST | `/mediciones` | Crear una medición |
| PUT | `/mediciones/{id}` | Reemplazar una medición |
| PATCH | `/mediciones/{id}` | Actualizar parcialmente |
| DELETE | `/mediciones/{id}` | Eliminar una medición |

Ejemplo de cuerpo para `POST /mediciones`:

```json
{
  "estudiante_id": 1,
  "variable": "temperatura",
  "valor": 36.6,
  "unidad": "C",
  "fecha_hora": "2026-09-30T20:00:00-05:00"
}
```

Después de cada POST, PUT, PATCH o DELETE, el contenido actualizado del dataset se imprime en la consola del servidor.

## Resumen de operaciones

| Método | Ruta | Función |
|---|---|---|
| GET | `/` | Verificar que el servidor funciona |
| POST | `/estudiantes` | Agregar un estudiante |
| GET | `/estudiantes/{id}` | Consultar un estudiante por su id |
| PUT | `/estudiantes/{indice}` | Reemplazar todos los datos |
| PATCH | `/estudiantes/{indice}` | Actualizar algunos datos |
| DELETE | `/estudiantes/{indice}` | Eliminar un estudiante |

## Actividad propuesta

Amplíe la API para consultar un estudiante por su identificador.

1. Agregue el campo `id` al modelo `Estudiante`.
2. Modifique la estructura del dataset para guardar el identificador de cada estudiante.
3. Cree una operación `GET /estudiantes/{id}` que busque y retorne únicamente el estudiante solicitado.
4. Pruebe la operación desde Swagger UI con estudiantes existentes y con un ID que no exista.
5. Documente el nuevo endpoint en el README.
6. Publique los cambios en su repositorio de la clase.

Archivos agregados: `schemas/medicion.py`, `models/medicion.py`, `crud/medicion.py` y `api/mediciones.py`. El router se registra en `main.py`.

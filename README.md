# Aplicaciones y Servicios Web — Seguimiento del curso

Repositorio con todo el trabajo del curso. La rama `main` reúne el contenido de **todas las demás ramas**, y cada rama sigue disponible con su historial de commits.

## Mapa de ramas y carpetas

| Rama | Actividad | Dónde está en `main` | Qué contiene |
|---|---|---|---|
| `clase-3` | Laboratorio 01: análisis del funcionamiento de una aplicación web | [`evidencias/`](evidencias/) | Capturas del DOM, la pestaña Network, una request y la interacción en el navegador |
| `clase-4` | Práctica de datos: CSV a JSON | [`clase-03-datos/`](clase-03-datos/) | Lee `estudiantes.csv`, lo transforma y genera `estudiantes_resumen.json` |
| `clase-5` | Clase 5: primer servicio con FastAPI | [`fastapi-orm/`](fastapi-orm/) (versión inicial en la rama) | Primer GET con FastAPI, Uvicorn y Swagger UI |
| `clase-6` | Clase 6: FastAPI | [`fastapi-orm/`](fastapi-orm/) (versión intermedia en la rama) | Se agrega `GET /estudiantes/{id}` |
| `clase-7` | Clase 7: ORM con FastAPI y PostgreSQL | [`fastapi-orm/`](fastapi-orm/) | CRUD de estudiantes y mediciones con SQLAlchemy |
| `taller1` | Taller 1: integración de datos entre aplicaciones | [`taller_1/`](taller_1/) | Cliente integrador que normaliza dos proveedores, valida y envía a una API por HTTP |
| `clase-7_8` | Clase 7/8: autenticación y autorización con JWT | [`fastapi-jwt/`](fastapi-jwt/) | API FastAPI con registro, login, tokens JWT y permisos por rol (`reader` / `editor`) |
| `clase2` | Rama principal anterior | raíz del repo | Acumulaba las clases 3 a 7; ahora todo está integrado en `main` |

Las ramas `clase-5`, `clase-6` y `clase-7` son versiones sucesivas del mismo proyecto FastAPI. En `main` queda su estado final, `fastapi-orm/`.

## Cómo ejecutar cada proyecto

Cada carpeta es independiente: se ejecuta desde dentro de ella.

**`clase-03-datos/`** (CSV a JSON, solo biblioteca estándar)

```bash
cd clase-03-datos
python transformar_estudiantes.py
```

**`taller_1/`** (cliente integrador; las pruebas no usan la API real)

```bash
cd taller_1
pip install -r requirements.txt
python integrador.py
pytest
```

Resultado de la ejecución real documentado en [`taller_1/ANALISIS.md`](taller_1/ANALISIS.md): 400 registros procesados, 391 normalizados, 380 enviados y 380 aceptados por la API.

**`fastapi-orm/`** (requiere PostgreSQL; ver su README)

```bash
cd fastapi-orm
pip install -r requirements.txt
uvicorn main:app --reload
```

**`fastapi-jwt/`** (usa SQLite, no requiere instalar una base de datos)

```bash
cd fastapi-jwt
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn backend.main:app --reload
```

Documentación interactiva en <http://127.0.0.1:8000/docs>. Se registra un usuario, se inicia sesión con **Authorize** y se prueban los endpoints protegidos.

## Cómo está organizado el historial

- Cada actividad se desarrolló en su propia rama y se integró en `main` mediante un merge, de modo que el historial de cada rama es visible.
- Los commits de integración (`Integra taller1...`, `Integra clase-7_8...`) indican de dónde viene cada bloque.
- Los archivos `.env` y las bases de datos locales no se suben al repositorio; solo `.env.example`.

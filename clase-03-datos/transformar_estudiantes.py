"""Transforma un dataset CSV de estudiantes a un archivo JSON de resumen.

Flujo:
    estudiantes.csv -> estructuras de Python -> transformacion -> estudiantes_resumen.json
"""

import csv
import json
from pathlib import Path

print("Hola, Aplicaciones y Servicios Web")

# Rutas base construidas con pathlib para que el script funcione
# sin importar desde que carpeta se ejecute.
BASE_DIR = Path(__file__).resolve().parent
RUTA_CSV = BASE_DIR / "datos" / "estudiantes.csv"
RUTA_JSON = BASE_DIR / "salida" / "estudiantes_resumen.json"


# Paso 2 — Leer el CSV
def leer_estudiantes(ruta: Path) -> list[dict]:
    """Lee un CSV con csv.DictReader y devuelve una lista de diccionarios."""
    with open(ruta, encoding="utf-8") as archivo:
        lector = csv.DictReader(archivo)
        return list(lector)


# Paso 3 y 4 — Funcion de transformacion de un estudiante
def transformar_estudiante(fila: dict) -> dict:
    """Convierte una fila cruda del CSV al formato del panel academico.

    - codigo            -> id
    - nombre + apellido  -> nombre_completo
    - semestre (texto)   -> semestre (entero)
    - promedio (texto)   -> promedio (decimal)
    - activo true/false  -> estado Activo/Inactivo
    - correo             -> se descarta
    """
    return {
        "id": fila["codigo"],
        "nombre_completo": f"{fila['nombre']} {fila['apellido']}",
        "programa": fila["programa"],
        "semestre": int(fila["semestre"]),
        "promedio": float(fila["promedio"]),
        "estado": "Activo" if fila["activo"].strip().lower() == "true" else "Inactivo",
    }


# Paso 5 — Transformar todos los registros
def transformar_estudiantes(filas: list[dict]) -> list[dict]:
    """Aplica la transformacion a cada fila y devuelve la lista resultante."""
    return [transformar_estudiante(fila) for fila in filas]


# Paso 6 — Serializar y guardar el JSON
def serializar_estudiantes(ruta: Path, estudiantes: list[dict]) -> None:
    """Serializa una lista de diccionarios Python a un archivo JSON UTF-8."""
    ruta.parent.mkdir(exist_ok=True)

    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(estudiantes, archivo, indent=2, ensure_ascii=False)


# Paso 7 — Deserializar el JSON generado
def deserializar_estudiantes(ruta: Path) -> list[dict]:
    """Deserializa un archivo JSON a una lista de diccionarios Python."""
    with open(ruta, encoding="utf-8") as archivo:
        return json.load(archivo)


def main() -> None:
    filas = leer_estudiantes(RUTA_CSV)
    print(f"Registros leidos del CSV: {len(filas)}")

    estudiantes_transformados = transformar_estudiantes(filas)
    print("\nPrimer estudiante transformado:")
    print(estudiantes_transformados[0])

    serializar_estudiantes(RUTA_JSON, estudiantes_transformados)
    print(f"\nArchivo JSON generado: {RUTA_JSON}")

    estudiantes_recuperados = deserializar_estudiantes(RUTA_JSON)
    print("\nDatos recuperados desde el JSON:")
    print(estudiantes_recuperados[0])
    print(f"Total recuperado: {len(estudiantes_recuperados)}")


if __name__ == "__main__":
    main()

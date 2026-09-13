"""Lectura de los datasets crudos de cada proveedor.

Responsabilidad unica: convertir los archivos fuente (JSON / CSV) en
listas de diccionarios de Python, sin aplicar ninguna transformacion
de negocio. Los errores de acceso o de formato se controlan aqui para
que el resto del programa nunca reciba una excepcion no esperada.
"""

import csv
import json
from pathlib import Path


class ErrorLectura(Exception):
    """Se lanza cuando un archivo fuente no puede leerse o interpretarse."""


def leer_proveedor_a(ruta: Path) -> list[dict]:
    """Lee el dataset JSON del proveedor A y devuelve su lista de registros."""
    try:
        with open(ruta, encoding="utf-8") as archivo:
            contenido = json.load(archivo)
    except FileNotFoundError as exc:
        raise ErrorLectura(f"No se encontro el archivo: {ruta}") from exc
    except json.JSONDecodeError as exc:
        raise ErrorLectura(f"El archivo {ruta} no contiene JSON valido: {exc}") from exc

    registros = contenido.get("records", [])
    if not isinstance(registros, list):
        raise ErrorLectura(f"El archivo {ruta} no tiene la forma esperada (records: list)")
    return registros


def leer_proveedor_b(ruta: Path) -> list[dict]:
    """Lee el dataset CSV (delimitado por ';') del proveedor B.

    Las filas defectuosas (numero de columnas distinto al esperado) se
    omiten de la lectura y se reportan por consola, en vez de detener
    todo el procesamiento.
    """
    registros: list[dict] = []
    try:
        with open(ruta, encoding="utf-8", newline="") as archivo:
            lector = csv.DictReader(archivo, delimiter=";")
            columnas_esperadas = set(lector.fieldnames or [])
            for numero_fila, fila in enumerate(lector, start=2):
                if None in fila or any(valor is None for valor in fila.values()):
                    print(
                        f"[proveedor_b] Fila CSV defectuosa (linea {numero_fila}), "
                        f"columnas distintas a {sorted(columnas_esperadas)}: {fila}"
                    )
                    continue
                registros.append(fila)
    except FileNotFoundError as exc:
        raise ErrorLectura(f"No se encontro el archivo: {ruta}") from exc

    return registros

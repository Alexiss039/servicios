"""Cliente HTTP para la API institucional descrita en CONTRATO_API.md.

Responsabilidad unica: enviar y consultar mediciones, interpretando
codigo HTTP + cuerpo de respuesta, con la politica de reintentos del
enunciado (1 intento inicial + hasta 2 reintentos ante 5xx / timeout /
perdida de conexion; sin reintentos ante 4xx).
"""

import requests

MAX_INTENTOS = 3
TIMEOUT_SEGUNDOS = 10

CAMPOS_CONTRATO = (
    "ciudad",
    "pais",
    "latitud",
    "longitud",
    "temperatura_c",
    "humedad",
    "viento_kmh",
    "fecha_hora",
    "origen",
)


def construir_body(medicion: dict) -> dict:
    """Extrae del registro normalizado solo los campos del contrato
    institucional (el identificador de trazabilidad no se envia)."""
    return {campo: medicion[campo] for campo in CAMPOS_CONTRATO}


def _leer_cuerpo_json(respuesta: requests.Response):
    try:
        return respuesta.json()
    except ValueError:
        return None


def enviar_medicion(url_base: str, equipo: str, medicion: dict) -> dict:
    """Envia una medicion mediante POST /api/v1/mediciones.

    Devuelve un diccionario con el resultado de la comunicacion,
    nunca lanza una excepcion ante errores de red o respuestas
    inesperadas del servidor.
    """
    url = f"{url_base.rstrip('/')}/api/v1/mediciones"
    headers = {"Content-Type": "application/json", "X-Equipo": equipo}
    body = construir_body(medicion)

    ultimo_error = None
    ultimo_status = None
    for intento in range(1, MAX_INTENTOS + 1):
        try:
            respuesta = requests.post(url, json=body, headers=headers, timeout=TIMEOUT_SEGUNDOS)
        except requests.exceptions.Timeout:
            ultimo_error = "timeout"
            continue
        except requests.exceptions.ConnectionError:
            ultimo_error = "perdida de conexion"
            continue
        except requests.exceptions.RequestException as exc:
            ultimo_error = f"error de red: {exc}"
            continue

        ultimo_status = respuesta.status_code
        if ultimo_status >= 500:
            ultimo_error = f"HTTP {ultimo_status}"
            continue

        return {
            "exito_comunicacion": True,
            "codigo_http": ultimo_status,
            "cuerpo": _leer_cuerpo_json(respuesta),
            "intentos": intento,
        }

    return {
        "exito_comunicacion": False,
        "codigo_http": ultimo_status,
        "cuerpo": None,
        "intentos": MAX_INTENTOS,
        "error": ultimo_error,
    }


def consultar_mediciones(url_base: str, equipo: str) -> dict:
    """Consulta GET /api/v1/mediciones?equipo=<equipo>."""
    url = f"{url_base.rstrip('/')}/api/v1/mediciones"
    try:
        respuesta = requests.get(url, params={"equipo": equipo}, timeout=TIMEOUT_SEGUNDOS)
    except requests.exceptions.RequestException as exc:
        return {"exito_comunicacion": False, "codigo_http": None, "cuerpo": None, "error": str(exc)}

    return {
        "exito_comunicacion": True,
        "codigo_http": respuesta.status_code,
        "cuerpo": _leer_cuerpo_json(respuesta),
    }

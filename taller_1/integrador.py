"""Cliente integrador — Taller 1: Integracion de datos entre aplicaciones.

Flujo:
    proveedor_a.json + proveedor_b.csv
        -> normalizacion al contrato institucional
        -> validacion local
        -> envio HTTP de las mediciones validas
        -> consulta GET de lo almacenado
        -> evidencias: salida/normalizadas.json y salida/reporte.json

Ejecucion:
    python integrador.py
"""

from pathlib import Path

from cliente_api import consultar_mediciones, enviar_medicion
from lectura import ErrorLectura, leer_proveedor_a, leer_proveedor_b
from normalizacion import ErrorNormalizacion, normalizar_registro_a, normalizar_registro_b
from reporte import construir_normalizadas, construir_reporte, guardar_json
from validacion import validar_registro

# --- Configuracion del equipo (definir aqui los valores asignados) ---
URL_BASE = "https://appsweb.quantaiot.co"
EQUIPO = "CAMBIAR_IDENTIFICADOR_DE_EQUIPO"
# -----------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
RUTA_PROVEEDOR_A = BASE_DIR / "datos" / "proveedor_a.json"
RUTA_PROVEEDOR_B = BASE_DIR / "datos" / "proveedor_b.csv"
RUTA_NORMALIZADAS = BASE_DIR / "salida" / "normalizadas.json"
RUTA_REPORTE = BASE_DIR / "salida" / "reporte.json"


def normalizar_todos(registros_a: list[dict], registros_b: list[dict]) -> tuple[list[dict], list[dict]]:
    """Normaliza ambos datasets. Devuelve (normalizados, errores_normalizacion)."""
    normalizados = []
    errores = []

    for indice, registro in enumerate(registros_a, start=1):
        try:
            normalizados.append(normalizar_registro_a(registro, indice))
        except ErrorNormalizacion as exc:
            errores.append(
                {
                    "id_trazabilidad": f"proveedor_a#{registro.get('provider_record_id', indice)}",
                    "origen": "proveedor_a",
                    "motivo": str(exc),
                }
            )

    for indice, registro in enumerate(registros_b, start=1):
        try:
            normalizados.append(normalizar_registro_b(registro, indice))
        except ErrorNormalizacion as exc:
            errores.append(
                {
                    "id_trazabilidad": f"proveedor_b#{registro.get('record_code', indice)}",
                    "origen": "proveedor_b",
                    "motivo": str(exc),
                }
            )

    return normalizados, errores


def validar_todos(normalizados: list[dict]) -> list[dict]:
    """Aplica la validacion local y devuelve, por cada medicion, su
    estado (valido_localmente / rechazado_localmente) y motivo."""
    resultado = []
    for medicion in normalizados:
        es_valido, motivo = validar_registro(medicion)
        resultado.append(
            {
                "medicion": medicion,
                "estado_local": "valido_localmente" if es_valido else "rechazado_localmente",
                "motivo_rechazo": motivo,
            }
        )
    return resultado


def enviar_validos(registros_validados: list[dict]) -> list[dict]:
    """Envia a la API solo las mediciones validas localmente."""
    resultados = []
    for item in registros_validados:
        if item["estado_local"] != "valido_localmente":
            continue

        medicion = item["medicion"]
        respuesta = enviar_medicion(URL_BASE, EQUIPO, medicion)

        if not respuesta["exito_comunicacion"]:
            resultado = "error_comunicacion"
            motivo = respuesta.get("error")
        elif respuesta["codigo_http"] == 201:
            resultado = "aceptado_api"
            motivo = None
        else:
            resultado = "rechazado_api"
            cuerpo = respuesta.get("cuerpo")
            motivo = cuerpo if cuerpo is not None else f"HTTP {respuesta['codigo_http']}"

        resultados.append(
            {
                "id_trazabilidad": medicion["id_trazabilidad"],
                "origen": medicion["origen"],
                "resultado": resultado,
                "motivo": motivo,
                "codigo_http": respuesta.get("codigo_http"),
                "intentos": respuesta.get("intentos"),
            }
        )
    return resultados


def main() -> None:
    try:
        registros_a = leer_proveedor_a(RUTA_PROVEEDOR_A)
    except ErrorLectura as exc:
        print(f"No fue posible leer el proveedor A: {exc}")
        registros_a = []

    try:
        registros_b = leer_proveedor_b(RUTA_PROVEEDOR_B)
    except ErrorLectura as exc:
        print(f"No fue posible leer el proveedor B: {exc}")
        registros_b = []

    procesados = len(registros_a) + len(registros_b)
    print(f"Registros procesados (proveedor A + proveedor B): {procesados}")

    normalizados, errores_normalizacion = normalizar_todos(registros_a, registros_b)
    print(f"Registros normalizados: {len(normalizados)}")
    print(f"Errores de normalizacion: {len(errores_normalizacion)}")

    registros_validados = validar_todos(normalizados)
    guardar_json(RUTA_NORMALIZADAS, construir_normalizadas(registros_validados))
    print(f"Evidencia de normalizacion guardada en: {RUTA_NORMALIZADAS}")

    validos = sum(1 for r in registros_validados if r["estado_local"] == "valido_localmente")
    print(f"Validos localmente: {validos} | Rechazados localmente: {len(registros_validados) - validos}")

    resultados_envio = enviar_validos(registros_validados)
    aceptados = sum(1 for r in resultados_envio if r["resultado"] == "aceptado_api")
    rechazados = sum(1 for r in resultados_envio if r["resultado"] == "rechazado_api")
    fallidos = sum(1 for r in resultados_envio if r["resultado"] == "error_comunicacion")
    print(f"Enviados a la API: {len(resultados_envio)}")
    print(f"  Aceptados: {aceptados} | Rechazados por la API: {rechazados} | Errores de comunicacion: {fallidos}")

    resultado_consulta = consultar_mediciones(URL_BASE, EQUIPO)
    print(f"Consulta final (GET): {resultado_consulta}")

    reporte = construir_reporte(
        procesados, errores_normalizacion, registros_validados, resultados_envio, resultado_consulta
    )
    guardar_json(RUTA_REPORTE, reporte)
    print(f"Reporte final guardado en: {RUTA_REPORTE}")


if __name__ == "__main__":
    main()

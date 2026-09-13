"""Generacion de las evidencias del proceso de integracion:
salida/normalizadas.json y salida/reporte.json.
"""

import json
from pathlib import Path


def guardar_json(ruta: Path, datos) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=2, ensure_ascii=False)


def construir_normalizadas(registros_normalizados: list[dict]) -> list[dict]:
    """registros_normalizados: lista de dicts con 'medicion', 'estado_local'
    y 'motivo_rechazo'. Incluye tanto validos como rechazados_localmente,
    tal como exige el paso 6 del enunciado."""
    return [
        {
            "id_trazabilidad": item["medicion"]["id_trazabilidad"],
            "estado_local": item["estado_local"],
            "motivo_rechazo": item["motivo_rechazo"],
            "medicion": item["medicion"],
        }
        for item in registros_normalizados
    ]


def construir_reporte(
    procesados: int,
    errores_normalizacion: list[dict],
    registros_normalizados: list[dict],
    resultados_envio: list[dict],
    resultado_consulta: dict,
) -> dict:
    normalizados = len(registros_normalizados)
    validos_localmente = sum(1 for r in registros_normalizados if r["estado_local"] == "valido_localmente")
    rechazados_localmente = normalizados - validos_localmente

    aceptados_api = sum(1 for r in resultados_envio if r["resultado"] == "aceptado_api")
    rechazados_api = sum(1 for r in resultados_envio if r["resultado"] == "rechazado_api")
    errores_comunicacion = sum(1 for r in resultados_envio if r["resultado"] == "error_comunicacion")

    detalle = []
    for error in errores_normalizacion:
        detalle.append(
            {
                "id_trazabilidad": error["id_trazabilidad"],
                "origen": error["origen"],
                "resultado": "error_normalizacion",
                "motivo": error["motivo"],
                "codigo_http": None,
                "intentos": None,
            }
        )
    for item in registros_normalizados:
        if item["estado_local"] == "rechazado_localmente":
            detalle.append(
                {
                    "id_trazabilidad": item["medicion"]["id_trazabilidad"],
                    "origen": item["medicion"]["origen"],
                    "resultado": "rechazado_localmente",
                    "motivo": item["motivo_rechazo"],
                    "codigo_http": None,
                    "intentos": None,
                }
            )
    for envio in resultados_envio:
        detalle.append(
            {
                "id_trazabilidad": envio["id_trazabilidad"],
                "origen": envio["origen"],
                "resultado": envio["resultado"],
                "motivo": envio.get("motivo"),
                "codigo_http": envio.get("codigo_http"),
                "intentos": envio.get("intentos"),
            }
        )

    return {
        "resumen": {
            "procesados": procesados,
            "normalizados": normalizados,
            "errores_normalizacion": len(errores_normalizacion),
            "validos_localmente": validos_localmente,
            "rechazados_localmente": rechazados_localmente,
            "enviados": len(resultados_envio),
            "aceptados_api": aceptados_api,
            "rechazados_api": rechazados_api,
            "errores_comunicacion": errores_comunicacion,
        },
        "detalle": detalle,
        "consulta_api": resultado_consulta,
    }

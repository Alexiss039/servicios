"""Transformacion de los registros crudos de cada proveedor al contrato
institucional (ver CONTRATO_API.md).

Un registro que no puede convertirse al tipo o representacion exigida
por el contrato produce un ErrorNormalizacion: ese registro no avanza
a validacion ni se incluye en salida/normalizadas.json (paso 3).
"""

from datetime import datetime, timedelta, timezone

ORIGEN_PROVEEDOR_A = "proveedor_a"
ORIGEN_PROVEEDOR_B = "proveedor_b"

# El dataset del proveedor B no trae zona horaria; sus mediciones son de
# estaciones colombianas, igual que las del proveedor A (que sí traen
# offset -05:00), así que se asume la misma zona horaria para poder
# expresar la fecha en ISO 8601 de forma comparable entre proveedores.
ZONA_HORARIA_PROVEEDOR_B = timezone(timedelta(hours=-5))


class ErrorNormalizacion(Exception):
    """Un dato del registro no puede convertirse al contrato institucional."""


def _a_float(valor, nombre_campo: str) -> float:
    if valor is None:
        raise ErrorNormalizacion(f"Campo '{nombre_campo}' ausente")
    try:
        return float(valor)
    except (TypeError, ValueError) as exc:
        raise ErrorNormalizacion(f"Campo '{nombre_campo}' no es numerico: {valor!r}") from exc


def fahrenheit_a_celsius(temperatura_f: float) -> float:
    return (temperatura_f - 32) * 5 / 9


def metros_por_segundo_a_kmh(velocidad_ms: float) -> float:
    return velocidad_ms * 3.6


def _id_trazabilidad(origen: str, codigo: str | None, indice: int) -> str:
    if codigo:
        return f"{origen}#{codigo}"
    return f"{origen}#{indice:04d}"


def normalizar_registro_a(registro: dict, indice: int) -> dict:
    """Normaliza un registro del proveedor A (JSON, unidades F / m/s)."""
    codigo = registro.get("provider_record_id")
    id_trazabilidad = _id_trazabilidad(ORIGEN_PROVEEDOR_A, codigo, indice)

    estacion = registro.get("station") or {}
    ubicacion = registro.get("location") or {}
    mediciones = registro.get("measurements") or {}

    ciudad = estacion.get("city_name")
    if not isinstance(ciudad, str):
        raise ErrorNormalizacion("Campo 'station.city_name' ausente o invalido")
    pais = estacion.get("country_code")
    if not isinstance(pais, str):
        raise ErrorNormalizacion("Campo 'station.country_code' ausente o invalido")

    latitud = _a_float(ubicacion.get("lat"), "location.lat")
    longitud = _a_float(ubicacion.get("lon"), "location.lon")

    temperatura_f = _a_float(mediciones.get("temperature_f"), "measurements.temperature_f")
    humedad = _a_float(mediciones.get("relative_humidity"), "measurements.relative_humidity")
    viento_ms = _a_float(mediciones.get("wind_speed_ms"), "measurements.wind_speed_ms")

    observado_en = registro.get("observed_at")
    if not observado_en:
        raise ErrorNormalizacion("Campo 'observed_at' ausente")
    try:
        fecha = datetime.fromisoformat(observado_en)
    except ValueError as exc:
        raise ErrorNormalizacion(f"Campo 'observed_at' con formato invalido: {observado_en!r}") from exc

    return {
        "id_trazabilidad": id_trazabilidad,
        "origen": ORIGEN_PROVEEDOR_A,
        "ciudad": ciudad,
        "pais": pais,
        "latitud": latitud,
        "longitud": longitud,
        "temperatura_c": round(fahrenheit_a_celsius(temperatura_f), 2),
        "humedad": humedad,
        "viento_kmh": round(metros_por_segundo_a_kmh(viento_ms), 2),
        "fecha_hora": fecha.isoformat(),
    }


def normalizar_registro_b(registro: dict, indice: int) -> dict:
    """Normaliza un registro del proveedor B (CSV, unidades C / km/h)."""
    codigo = registro.get("record_code")
    id_trazabilidad = _id_trazabilidad(ORIGEN_PROVEEDOR_B, codigo, indice)

    ciudad = registro.get("municipality")
    if not isinstance(ciudad, str):
        raise ErrorNormalizacion("Campo 'municipality' ausente")
    pais = registro.get("country")
    if not isinstance(pais, str):
        raise ErrorNormalizacion("Campo 'country' ausente")

    latitud = _a_float(registro.get("latitude_deg"), "latitude_deg")
    longitud = _a_float(registro.get("longitude_deg"), "longitude_deg")
    temperatura_c = _a_float(registro.get("temp_celsius"), "temp_celsius")
    humedad = _a_float(registro.get("humidity_pct"), "humidity_pct")
    viento_kmh = _a_float(registro.get("wind_kmh"), "wind_kmh")

    marca_tiempo = registro.get("measurement_time")
    if not marca_tiempo:
        raise ErrorNormalizacion("Campo 'measurement_time' ausente")
    try:
        fecha_naive = datetime.strptime(marca_tiempo, "%d/%m/%Y %H:%M")
    except ValueError as exc:
        raise ErrorNormalizacion(f"Campo 'measurement_time' con formato invalido: {marca_tiempo!r}") from exc
    fecha = fecha_naive.replace(tzinfo=ZONA_HORARIA_PROVEEDOR_B)

    return {
        "id_trazabilidad": id_trazabilidad,
        "origen": ORIGEN_PROVEEDOR_B,
        "ciudad": ciudad,
        "pais": pais,
        "latitud": latitud,
        "longitud": longitud,
        "temperatura_c": round(temperatura_c, 2),
        "humedad": humedad,
        "viento_kmh": round(viento_kmh, 2),
        "fecha_hora": fecha.isoformat(),
    }

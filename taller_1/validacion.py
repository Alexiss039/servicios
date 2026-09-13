"""Validacion local de un registro ya normalizado, segun las reglas de
negocio publicadas en CONTRATO_API.md.

Un registro puede haberse normalizado correctamente (tipos y formato
correctos) y aun asi violar una regla del contrato: en ese caso se
clasifica como rechazado_localmente y no se envia a la API, pero
permanece en salida/normalizadas.json (paso 4).
"""

ORIGENES_VALIDOS = {"proveedor_a", "proveedor_b"}


def validar_registro(medicion: dict) -> tuple[bool, str | None]:
    """Devuelve (True, None) si la medicion cumple el contrato, o
    (False, motivo) con la primera regla incumplida."""
    if not medicion.get("ciudad"):
        return False, "ciudad vacia"
    if not medicion.get("pais"):
        return False, "pais vacio"
    if not (-90 <= medicion["latitud"] <= 90):
        return False, f"latitud fuera de rango: {medicion['latitud']}"
    if not (-180 <= medicion["longitud"] <= 180):
        return False, f"longitud fuera de rango: {medicion['longitud']}"
    if not (0 <= medicion["humedad"] <= 100):
        return False, f"humedad fuera de rango: {medicion['humedad']}"
    if medicion["viento_kmh"] < 0:
        return False, f"viento_kmh negativo: {medicion['viento_kmh']}"
    if medicion["origen"] not in ORIGENES_VALIDOS:
        return False, f"origen no permitido: {medicion['origen']}"
    return True, None

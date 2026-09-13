import pytest

from normalizacion import (
    ErrorNormalizacion,
    fahrenheit_a_celsius,
    metros_por_segundo_a_kmh,
    normalizar_registro_a,
    normalizar_registro_b,
)

REGISTRO_A_VALIDO = {
    "provider_record_id": "A-0001",
    "station": {"code": "STA-02", "city_name": "Medellin", "country_code": "CO"},
    "location": {"lat": 6.242282, "lon": -75.595933},
    "measurements": {"temperature_f": 66.1, "relative_humidity": 81.3, "wind_speed_ms": 8.47},
    "observed_at": "2026-09-01T00:00:00-05:00",
    "source": "weather_provider_a",
}

REGISTRO_B_VALIDO = {
    "record_code": "B-0001",
    "municipality": "Medellin",
    "country": "CO",
    "latitude_deg": "6.261520",
    "longitude_deg": "-75.575842",
    "temp_celsius": "21.55",
    "humidity_pct": "50.7",
    "wind_kmh": "21.85",
    "measurement_time": "01/09/2026 06:00",
    "origin_code": "PB",
}


def test_transformacion_correcta_proveedor_a():
    """Una transformacion correcta: proveedor A -> contrato institucional."""
    medicion = normalizar_registro_a(REGISTRO_A_VALIDO, 1)

    assert medicion["id_trazabilidad"] == "proveedor_a#A-0001"
    assert medicion["origen"] == "proveedor_a"
    assert medicion["ciudad"] == "Medellin"
    assert medicion["fecha_hora"] == "2026-09-01T00:00:00-05:00"


def test_conversion_unidades_temperatura_y_viento():
    """Conversion de unidades: F -> C y m/s -> km/h."""
    assert fahrenheit_a_celsius(32) == pytest.approx(0.0)
    assert fahrenheit_a_celsius(212) == pytest.approx(100.0)
    assert metros_por_segundo_a_kmh(10) == pytest.approx(36.0)

    medicion = normalizar_registro_a(REGISTRO_A_VALIDO, 1)
    assert medicion["temperatura_c"] == pytest.approx(fahrenheit_a_celsius(66.1), abs=0.01)
    assert medicion["viento_kmh"] == pytest.approx(metros_por_segundo_a_kmh(8.47), abs=0.01)


def test_normalizacion_proveedor_b_sin_conversion_de_unidades():
    medicion = normalizar_registro_b(REGISTRO_B_VALIDO, 1)

    assert medicion["origen"] == "proveedor_b"
    assert medicion["temperatura_c"] == pytest.approx(21.55)
    assert medicion["viento_kmh"] == pytest.approx(21.85)
    assert medicion["fecha_hora"] == "2026-09-01T06:00:00-05:00"


def test_error_de_normalizacion_por_dato_no_convertible():
    """Un dato que no puede convertirse al contrato es un error de normalizacion."""
    registro_con_error = dict(REGISTRO_A_VALIDO)
    registro_con_error["measurements"] = dict(REGISTRO_A_VALIDO["measurements"])
    registro_con_error["measurements"]["temperature_f"] = "N/A"

    with pytest.raises(ErrorNormalizacion):
        normalizar_registro_a(registro_con_error, 1)


def test_error_de_normalizacion_por_fecha_faltante():
    """Caso limite: el proveedor A puede no traer 'observed_at' (ver registro A-0040)."""
    registro_sin_fecha = dict(REGISTRO_A_VALIDO)
    del registro_sin_fecha["observed_at"]

    with pytest.raises(ErrorNormalizacion):
        normalizar_registro_a(registro_sin_fecha, 1)


def test_error_de_normalizacion_por_fecha_no_parseable_proveedor_b():
    registro_fecha_invalida = dict(REGISTRO_B_VALIDO)
    registro_fecha_invalida["measurement_time"] = "31/13/2026 28:75"

    with pytest.raises(ErrorNormalizacion):
        normalizar_registro_b(registro_fecha_invalida, 1)

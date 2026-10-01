from validacion import validar_registro

MEDICION_VALIDA = {
    "id_trazabilidad": "proveedor_a#A-0001",
    "origen": "proveedor_a",
    "ciudad": "Medellin",
    "pais": "CO",
    "latitud": 6.24,
    "longitud": -75.59,
    "temperatura_c": 18.9,
    "humedad": 81.3,
    "viento_kmh": 30.5,
    "fecha_hora": "2026-09-01T00:00:00-05:00",
}


def test_registro_valido():
    """Un registro que cumple todas las reglas del contrato es valido."""
    es_valido, motivo = validar_registro(MEDICION_VALIDA)

    assert es_valido is True
    assert motivo is None


def test_registro_invalido_por_humedad_fuera_de_rango():
    """Un registro correctamente normalizado puede ser invalido por reglas de negocio."""
    medicion = dict(MEDICION_VALIDA, humedad=117.5)

    es_valido, motivo = validar_registro(medicion)

    assert es_valido is False
    assert "humedad" in motivo


def test_registro_invalido_por_viento_negativo():
    medicion = dict(MEDICION_VALIDA, viento_kmh=-2.4)

    es_valido, motivo = validar_registro(medicion)

    assert es_valido is False
    assert "viento_kmh" in motivo


def test_registro_invalido_por_ciudad_vacia():
    """Caso limite: ciudad vacia (dato normalizable, pero incumple 'no vacio')."""
    medicion = dict(MEDICION_VALIDA, ciudad="")

    es_valido, motivo = validar_registro(medicion)

    assert es_valido is False
    assert motivo == "ciudad vacia"


def test_registro_invalido_por_latitud_fuera_de_rango():
    """Caso limite: coordenada corrupta como la del registro B-0006 (-94.22)."""
    medicion = dict(MEDICION_VALIDA, latitud=-94.22)

    es_valido, motivo = validar_registro(medicion)

    assert es_valido is False
    assert "latitud" in motivo


def test_registro_valido_en_el_limite_exacto_del_rango():
    """Caso limite elegido por el equipo: latitud=90 y humedad=100 son válidas (bordes inclusivos)."""
    medicion = dict(MEDICION_VALIDA, latitud=90, humedad=100)

    es_valido, motivo = validar_registro(medicion)

    assert es_valido is True
    assert motivo is None

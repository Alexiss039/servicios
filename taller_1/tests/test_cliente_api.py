from unittest.mock import MagicMock, patch

import requests

from cliente_api import construir_body, enviar_medicion

MEDICION = {
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


def test_construir_body_no_incluye_el_identificador_de_trazabilidad():
    body = construir_body(MEDICION)

    assert "id_trazabilidad" not in body
    assert body["ciudad"] == "Medellin"
    assert body["origen"] == "proveedor_a"


@patch("cliente_api.requests.post")
def test_envio_aceptado_en_el_primer_intento(mock_post):
    respuesta = MagicMock(status_code=201)
    respuesta.json.return_value = {"id": "srv-1"}
    mock_post.return_value = respuesta

    resultado = enviar_medicion("https://api.test", "equipo-1", MEDICION)

    assert resultado["exito_comunicacion"] is True
    assert resultado["codigo_http"] == 201
    assert resultado["intentos"] == 1
    assert mock_post.call_count == 1


@patch("cliente_api.requests.post")
def test_error_5xx_no_agota_reintentos_si_luego_hay_exito(mock_post):
    respuesta_error = MagicMock(status_code=503)
    respuesta_ok = MagicMock(status_code=201)
    respuesta_ok.json.return_value = {"id": "srv-2"}
    mock_post.side_effect = [respuesta_error, respuesta_ok]

    resultado = enviar_medicion("https://api.test", "equipo-1", MEDICION)

    assert resultado["exito_comunicacion"] is True
    assert resultado["intentos"] == 2


@patch("cliente_api.requests.post")
def test_respuesta_4xx_no_se_reintenta(mock_post):
    respuesta = MagicMock(status_code=422)
    respuesta.json.return_value = {"error": "dato invalido"}
    mock_post.return_value = respuesta

    resultado = enviar_medicion("https://api.test", "equipo-1", MEDICION)

    assert resultado["codigo_http"] == 422
    assert mock_post.call_count == 1


@patch("cliente_api.requests.post")
def test_agota_los_tres_intentos_ante_timeouts_y_reporta_error_comunicacion(mock_post):
    mock_post.side_effect = requests.exceptions.Timeout()

    resultado = enviar_medicion("https://api.test", "equipo-1", MEDICION)

    assert resultado["exito_comunicacion"] is False
    assert resultado["intentos"] == 3
    assert mock_post.call_count == 3

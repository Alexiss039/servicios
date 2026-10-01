# Análisis — Taller 1: Integración de datos entre aplicaciones

## 1. Diferencias entre los contratos de los proveedores

| Aspecto | Proveedor A (JSON) | Proveedor B (CSV) | Contrato institucional |
|---|---|---|---|
| Estructura | Anidada (`station`, `location`, `measurements`) | Plana, delimitada por `;` | Plana |
| Identificador | `provider_record_id` (ej. `A-0001`) | `record_code` (ej. `B-0001`) | No forma parte del body (solo trazabilidad interna) |
| Ciudad / país | `station.city_name` / `station.country_code` | `municipality` / `country` | `ciudad` / `pais` |
| Coordenadas | `location.lat` / `location.lon` | `latitude_deg` / `longitude_deg` | `latitud` / `longitud` |
| Temperatura | `measurements.temperature_f`, en **°F** | `temp_celsius`, ya en **°C** | `temperatura_c` (°C) |
| Humedad | `measurements.relative_humidity` (%) | `humidity_pct` (%) | `humedad` (%), sin conversión en ninguno de los dos |
| Viento | `measurements.wind_speed_ms`, en **m/s** | `wind_kmh`, ya en **km/h** | `viento_kmh` (km/h) |
| Fecha | `observed_at`, ISO 8601 con offset `-05:00` | `measurement_time`, formato `DD/MM/YYYY HH:MM`, **sin zona horaria** | `fecha_hora` en ISO 8601 |
| Origen | Campo `source` (no institucional) | Campo `origin_code` = `PB` (no institucional) | `origen` con valor fijo `proveedor_a` / `proveedor_b` |

Ambos proveedores, además, pueden traer registros incompletos o corruptos (ver sección 3).

## 2. Transformaciones necesarias

- **Aplanar** la estructura anidada del proveedor A a los 9 campos planos del contrato.
- **Convertir unidades** solo en el proveedor A: `°F → °C` con `(f-32)*5/9`, y `m/s → km/h` con `*3.6`. El proveedor B ya llega en las unidades del contrato.
- **Reformatear fechas**: el proveedor A ya viene en ISO 8601 (se valida con `datetime.fromisoformat`); el proveedor B se parsea con `strptime("%d/%m/%Y %H:%M")`. Como el proveedor B no trae zona horaria y ambos datasets corresponden a estaciones colombianas, se decidió asumir el mismo offset `-05:00` que usa el proveedor A, para que las fechas normalizadas sean comparables entre sí.
- **Fijar el campo `origen`** a `proveedor_a` / `proveedor_b` (valores institucionales), descartando los campos originales `source` / `origin_code`, que no pertenecen al contrato.
- **Descartar el identificador de trazabilidad del body enviado a la API**: se conserva solo como metadato interno (`id_trazabilidad`) para el reporte y las evidencias, tal como exige el numeral 5 del enunciado.

## 3. Errores encontrados antes de enviar información

**Errores de normalización** (el dato no puede convertirse al tipo/formato del contrato — 9 casos, ver `salida/reporte.json`):

- Fecha ausente (`A-0040` sin `observed_at`) o con formato inválido (`A-0174`: `"09-XX-2026 25:61"`, `B-0171`: `"31/13/2026 28:75"`).
- Valores no numéricos donde se esperaba un número: temperatura `"N/A"` (`A-0082`), `"error"` o vacía (`B-0114`, `B-0146`).
- Campos obligatorios ausentes: `temperature_f` (`A-0173`), `country_code` (`A-0150`), `measurement_time` (`B-0076`).

**Rechazos por validación local** (el dato normaliza correctamente pero incumple una regla del contrato — 11 casos):

- Coordenadas fuera de rango: latitud `95.245` (`A-0031`), `-94.22` (`B-0006`); longitud `-190.75` (`A-0175`), `188.45` (`B-0190`).
- Humedad fuera de `0–100`: `108.4` (`A-0015`), `117.5` (`B-0004`).
- Viento negativo: `-8.64` (`A-0088`), `-7.4` (`B-0115`).
- Campos de texto obligatorios vacíos: ciudad (`A-0136`, `B-0128`), país (`B-0135`).

## 4. Diferencias entre validación local y validación del servidor

La validación local solo puede verificar las reglas documentadas en `CONTRATO_API.md` (rangos numéricos, campos no vacíos, valores permitidos de `origen`). El servidor, en cambio, aplica **su propia validación independiente**, que puede incluir reglas no documentadas (duplicados, coherencia entre campos, límites adicionales, etc.). Por eso el enunciado aclara que "una medición validada localmente puede ser rechazada por el servidor": en esta ejecución los 380 registros válidos localmente fueron también aceptados por la API (código `201`), pero el cliente igual está preparado para interpretar `400`, `409` y `422` como rechazo del servidor sin detener el proceso, precisamente porque ambas validaciones no son intercambiables.

## 5. Decisión de implementación más importante

La decisión más importante fue **separar con claridad los tres estados de un registro problemático** (error de normalización, rechazo local, rechazo del servidor / error de comunicación) y mantener la trazabilidad de cada uno con un identificador propio (`origen#codigo`) a lo largo de todo el pipeline. Esto permite que ningún registro se pierda silenciosamente (restricción explícita del enunciado) y que el reporte final (`salida/reporte.json`) pueda reconstruir el resultado exacto de cada uno de los 400 registros procesados, sin importar en qué etapa quedó fuera del flujo.

## 6. Evidencia de una ejecución real

Ejecución con `EQUIPO=EQUIPO-14-APPSWEB` contra `https://appsweb.quantaiot.co`:

```
Registros procesados (proveedor A + proveedor B): 400
Registros normalizados: 391
Errores de normalizacion: 9
Validos localmente: 380 | Rechazados localmente: 11
Enviados a la API: 380
  Aceptados: 380 | Rechazados por la API: 0 | Errores de comunicacion: 0
Consulta final (GET): codigo_http=200, {"equipo": "EQUIPO-14-APPSWEB", "total": 380, "mediciones": [...]}
```

Resumen tomado de `salida/reporte.json`:

| Métrica | Valor |
|---|---:|
| Procesados | 400 |
| Normalizados | 391 |
| Errores de normalización | 9 |
| Válidos localmente | 380 |
| Rechazados localmente | 11 |
| Enviados a la API | 380 |
| Aceptados por la API | 380 |
| Rechazados por la API | 0 |
| Errores de comunicación | 0 |

Caso de error de normalización (`salida/reporte.json`, detalle):

```json
{
  "id_trazabilidad": "proveedor_a#A-0082",
  "origen": "proveedor_a",
  "resultado": "error_normalizacion",
  "motivo": "Campo 'measurements.temperature_f' no es numerico: 'N/A'"
}
```

Caso de rechazo local (dato normalizable pero fuera de las reglas del contrato):

```json
{
  "id_trazabilidad": "proveedor_b#B-0006",
  "origen": "proveedor_b",
  "resultado": "rechazado_localmente",
  "motivo": "latitud fuera de rango: -94.22"
}
```

Resultado de la consulta final mediante `GET /api/v1/mediciones?equipo=EQUIPO-14-APPSWEB`: `codigo_http = 200`, `total = 380`, coincidiendo exactamente con el número de mediciones aceptadas en esta ejecución.

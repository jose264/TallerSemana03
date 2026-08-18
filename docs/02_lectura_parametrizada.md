# Componente 2 — Lectura parametrizada de CSV, Excel y JSON

Implementación de referencia: [`scripts/lectura.py`](../scripts/lectura.py).

## Hallazgo: extensión de archivo no confiable

`estudiantes_master.xlsx` declara extensión `.xlsx`, pero su contenido
real es texto CSV plano (comprobado inspeccionando los primeros bytes del
archivo: un `.xlsx` real es un contenedor ZIP y empieza con la firma
binaria `PK`; este archivo empieza directamente con
`id_estudiante,nombre_completo,...` en texto). Un `pd.read_excel()` sin
más falla o, peor, no falla pero interpreta mal el contenido.

Por esto, `leer_catalogo_maestro()` **no confía en la extensión**: intenta
`pd.read_excel` primero y, si lanza una excepción de formato
(`ValueError`/`OSError` — el error que produce openpyxl al no encontrar
la firma ZIP esperada), reintenta como CSV con los mismos parámetros de
codificación y tipos. El resultado registra en `df.attrs["origen_lectura"]`
si terminó leyéndose como Excel o como CSV, para que quede evidencia en
el reporte de control de qué archivos requirieron la ruta alternativa.
Al ejecutar el script contra los datos del taller, el resultado es
`csv_disfrazado_de_excel`, confirmando el hallazgo.

Esta validación es deliberadamente defensiva: en un flujo real, un nuevo
archivo del catálogo maestro podría llegar como `.xlsx` verdadero (con
múltiples hojas) sin avisar, y el pipeline debe seguir funcionando sin
intervención manual.

## Parámetros de lectura y su justificación

### Codificación

Los tres archivos contienen tildes y eñes (nombres de estudiantes,
nombres de materias). Se fuerza `encoding="utf-8"` explícitamente en
lugar de dejar que pandas use el encoding por defecto del sistema
operativo (`cp1252` en Windows), que corrompería esos caracteres de
forma silenciosa — un tipo de error que no lanza excepción y por eso es
peligroso si no se fija explícitamente.

### Separador

Se confirmó por inspección directa que los tres archivos usan `,` como
separador de columnas. Se fija `sep=","` explícitamente en vez de dejarlo
por defecto, para que el pipeline no dependa de que pandas siga
adivinando correctamente si en el futuro se recibe un archivo con `;`
(común en exportaciones regionales de Excel).

### Tipos de columna

Todos los identificadores (`id_entrega`, `id_estudiante`) se leen como
`string`, nunca como numérico, porque tienen prefijos alfabéticos
(`E001`, `PRJ-1001`) y porque un ID nunca debe participar en operaciones
aritméticas. Dejar que pandas infiera el tipo es riesgoso: si en algún
archivo los IDs fueran puramente numéricos, pandas los leería como
`int64` y un futuro merge con otra fuente que sí trae ceros a la
izquierda (`"007"`) fallaría silenciosamente.

`puntaje_obtenido` se tipa como `float64`, no `int`, porque debe tolerar
valores nulos: las entregas con `estado_entrega == "Pendiente"` no tienen
calificación. Forzar `int` en una columna con `NaN` no es posible en
pandas sin una conversión adicional, así que `float64` es el tipo mínimo
que soporta el dato real sin perder información.

### Tratamiento de fechas

`fecha_nacimiento` y `fecha_subida` vienen en formato ISO 8601
(`YYYY-MM-DD`), por lo que `pd.read_csv(..., parse_dates=[...])` las
interpreta sin ambigüedad y sin necesidad de un `format` explícito. Se
parsean en el momento de la lectura (no después) para que cualquier
fecha malformada falle temprano, en la etapa de lectura, en vez de
propagarse silenciosamente como texto hasta una etapa posterior del
pipeline donde el error sería más difícil de rastrear.

### Normalización de estructuras anidadas (JSON)

Ninguno de los tres archivos provistos es JSON — los tres son
tabulares (dos CSV y uno disfrazado de Excel). Sin embargo, el reto exige
que el diseño contemple esta fuente porque un futuro campus o sistema de
entregas podría exponer su información como JSON anidado (por ejemplo,
una lista de estudiantes con una sublista de entregas embebida).

Para ese caso, `normalizar_json_anidado()` documenta el mecanismo de
`pd.json_normalize(registros, record_path=..., meta=...)`:
`record_path` indica qué lista anidada aplanar a filas (p. ej.
`"entregas"`) y `meta` qué columnas del nivel superior deben repetirse en
cada fila resultante (p. ej. `["id_estudiante"]`). Diseñar esta función
ahora, aunque no se ejerza con los datos actuales del taller, evita que
la incorporación de una fuente JSON futura requiera reescribir el
pipeline de lectura.

## Evidencia de ejecución

Ejecutando `python scripts/lectura.py` contra los archivos reales del
taller:

```
entregas_campus_matriz.csv -> (150, 7)
entregas_campus_extension.csv -> (150, 7)
estudiantes_master.xlsx -> shape (60, 7) | leído como: csv_disfrazado_de_excel
```

Los conteos de nulos en `puntaje_obtenido` (6 en matriz, 3 en extensión)
coinciden exactamente con el número de filas en estado `"Pendiente"` en
cada archivo, confirmando que el tipo `float64` y la ausencia de un
`fillna` prematuro preservan la distinción entre "nulo esperado" (entrega
pendiente) y un eventual nulo crítico, distinción que el reporte final de
indicadores de calidad debe auditar.

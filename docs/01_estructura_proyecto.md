# Componente 1 — Estructura del proyecto y justificación de la arquitectura

## Estructura de carpetas

```
TallerSemana03/
├── datos/
│   ├── originales/       # Fuentes tal como se recibieron (capa inmutable)
│   └── procesados/       # Dataset(s) consolidado(s), listos para análisis
├── notebooks/            # Flujo exploratorio y narrativo del análisis
├── scripts/               # Funciones reutilizables del pipeline (lectura, combinación, validación)
├── reportes/              # Indicadores de calidad del proceso (Componente 4 y cierre)
├── visualizaciones/       # Gráficos generados a partir de datos procesados
└── docs/                  # Documentación metodológica del flujo
```

## Justificación de la arquitectura

**Separación de datos originales y procesados.** `datos/originales/` se trata
como una capa de solo lectura: ningún script ni notebook debe sobrescribir
estos archivos. Esto permite que, si se detecta un error en el pipeline,
el análisis se pueda re-ejecutar desde cero sin depender de una copia de
respaldo externa. `datos/procesados/` contiene únicamente artefactos
generados por código (nunca editados a mano), de modo que su contenido
es siempre reproducible a partir de `datos/originales/` más el código en
`scripts/`.

**Separación entre lógica reutilizable (`scripts/`) y narrativa exploratoria
(`notebooks/`).** Las funciones de lectura, combinación y validación viven
en `scripts/` como módulos importables. Los notebooks las consumen en vez
de reimplementarlas, evitando que la misma lógica de limpieza exista
duplicada (y potencialmente inconsistente) en varias celdas. Esto también
hace posible ejecutar el pipeline completo fuera de un notebook (por
ejemplo, en un cron o pipeline de CI) sin depender de Jupyter.

**`reportes/` como salida obligatoria y separada de `visualizaciones/`.**
El reto exige indicadores de calidad cuantitativos (archivos procesados,
registros leídos/descartados, claves sin correspondencia, nulos críticos,
dimensiones de salida). Estos indicadores son texto/tablas, no gráficos,
por lo que se separan de `visualizaciones/` para que un revisor pueda
auditar la calidad del proceso sin tener que abrir imágenes.

**`docs/` como memoria del criterio técnico.** Cada decisión no evidente
en el código (por qué un merge y no un concat, por qué un umbral de nulos
es aceptable) se documenta aquí. El código responde *qué* se hizo; `docs/`
responde *por qué*, para que otro analista pueda auditar el razonamiento
sin depender de instrucciones informales o de preguntarle al autor
original.

**Trazabilidad de principio a fin.** La secuencia de carpetas
(`originales` → `scripts` → `procesados` → `reportes`/`visualizaciones`)
refleja el orden real del flujo de datos. Un analista nuevo puede inferir
el pipeline completo solo por la estructura de directorios, sin leer
código previamente.

## Estado de la estructura en este repositorio

Las siete carpetas anteriores existen y están versionadas (con `.gitkeep`
en las que aún no tienen archivos generados). Los tres archivos fuente
provistos por la cátedra están ubicados en `datos/originales/`:

| Archivo | Formato real | Registros |
|---|---|---|
| `estudiantes_master.xlsx` | CSV plano con extensión `.xlsx` (ver hallazgo en [02_lectura_parametrizada.md](02_lectura_parametrizada.md)) | 60 |
| `entregas_campus_matriz.csv` | CSV | 150 |
| `entregas_campus_extension.csv` | CSV | 150 |

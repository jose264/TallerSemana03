# Taller Práctico 3 — Diseño de un flujo analítico reproducible

Python para Ciencia de Datos  
Maestría en Ciencia de Datos y Machine Learning (mención IA) — UIDE

## Integrantes

- Kevin Apolo
- Sthefanny Chamorro
- Jose Luis Criollo

## Descripción

Consolidación de las entregas académicas de dos campus y su cruce con el catálogo maestro de estudiantes, mediante un flujo reproducible y auditable.

## Estructura del proyecto

| Carpeta | Contenido |
|---------|-----------|
| `datos/originales/` | Fuentes tal como se recibieron. Capa inmutable. |
| `datos/procesados/` | Dataset consolidado listo para análisis. |
| `notebooks/` | Cuaderno con el flujo completo. |
| `scripts/` | Funciones reutilizables del pipeline. |
| `reportes/` | Indicadores de calidad del proceso. |
| `visualizaciones/` | Gráficos generados. |
| `docs/` | Documento metodológico. |

## Requisitos

Python 3.11 o superior

## Ejecución

**Local (VS Code):**

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Google Colab:** subir el notebook de `notebooks/` junto con los archivos
de `datos/originales/`. No requiere instalación previa.

## Fuentes de datos

| Archivo | Registros |
|---------|-----------|
| entregas_campus_matriz.csv | 150 |
| entregas_campus_extension.csv | 150 |
| estudiantes_master.xlsx | 60 |
"""Funciones reutilizables de lectura parametrizada (Componente 2).

Centraliza los parámetros de codificación, separadores, tipos de columna,
tratamiento de fechas y normalización de estructuras anidadas para que
cualquier notebook o script del proyecto lea los datos de la misma forma.
"""

from pathlib import Path

import pandas as pd

# Tipos de columna comunes a los sistemas de entregas de ambos campus.
# Los identificadores se fuerzan a texto para no perder ceros a la izquierda
# ni ser interpretados como números.
DTYPES_ENTREGAS = {
    "id_entrega": "string",
    "id_estudiante": "string",
    "materia": "string",
    "tipo_proyecto": "string",
    "puntaje_obtenido": "float64",  # admite NaN para entregas "Pendiente"
    "estado_entrega": "string",
}

DTYPES_MAESTRO = {
    "id_estudiante": "string",
    "nombre_completo": "string",
    "carrera": "string",
    "campus_origen": "string",
    "tipo_beca": "string",
    "estado_academico": "string",
}


def leer_entregas_csv(ruta):
    """Lee un archivo de entregas (campus matriz o extensión).

    Parámetros aplicados y su justificación:
    - encoding="utf-8": las fuentes contienen tildes y eñes (nombres,
      materias); usar el encoding por defecto de Python (cp1252 en Windows)
      corrompería esos caracteres.
    - sep=",": separador confirmado inspeccionando los archivos crudos.
    - dtype=DTYPES_ENTREGAS: evita que pandas infiera tipos incorrectos
      para los IDs y deja "puntaje_obtenido" como float para tolerar nulos.
    - parse_dates=["fecha_subida"]: la columna viene en formato ISO
      (YYYY-MM-DD), por lo que no requiere un `format` explícito.
    """
    ruta = Path(ruta)
    return pd.read_csv(
        ruta,
        encoding="utf-8",
        sep=",",
        dtype=DTYPES_ENTREGAS,
        parse_dates=["fecha_subida"],
    )


def leer_catalogo_maestro(ruta):
    """Lee el catálogo maestro de estudiantes.

    Hallazgo del taller: `estudiantes_master.xlsx` tiene extensión .xlsx
    pero su contenido real es CSV plano (no tiene la firma binaria ZIP/PK
    de un Excel real). Confiar en la extensión rompería la lectura, así
    que primero se intenta como Excel y, si falla, se reintenta como CSV
    con los mismos parámetros de codificación/tipos/fechas.
    """
    ruta = Path(ruta)
    try:
        df = pd.read_excel(ruta, sheet_name=0, dtype=DTYPES_MAESTRO)
        origen_lectura = "excel"
    except (ValueError, KeyError, OSError):
        df = pd.read_csv(
            ruta,
            encoding="utf-8",
            sep=",",
            dtype=DTYPES_MAESTRO,
        )
        origen_lectura = "csv_disfrazado_de_excel"

    if "fecha_nacimiento" in df.columns:
        df["fecha_nacimiento"] = pd.to_datetime(df["fecha_nacimiento"])

    df.attrs["origen_lectura"] = origen_lectura
    return df


def normalizar_json_anidado(registros, record_path=None, meta=None):
    """Aplana estructuras JSON anidadas a formato tabular.

    El taller exige contemplar fuentes en JSON aunque los tres archivos
    provistos sean CSV (uno de ellos disfrazado de Excel). Esta función
    documenta el mecanismo que se usaría si el sistema de entregas de un
    futuro campus entregara los datos en JSON, p. ej. una lista de
    estudiantes con una sublista anidada de entregas:

        [{"id_estudiante": "E001", "entregas": [{...}, {...}]}]

    record_path indica la lista anidada a expandir (p. ej. "entregas") y
    meta las columnas del nivel superior que deben repetirse en cada fila
    (p. ej. ["id_estudiante"]).
    """
    return pd.json_normalize(registros, record_path=record_path, meta=meta)


if __name__ == "__main__":
    base = Path(__file__).resolve().parent.parent / "datos" / "originales"

    matriz = leer_entregas_csv(base / "entregas_campus_matriz.csv")
    extension = leer_entregas_csv(base / "entregas_campus_extension.csv")
    maestro = leer_catalogo_maestro(base / "estudiantes_master.xlsx")

    print("entregas_campus_matriz.csv ->", matriz.shape, dict(matriz.dtypes.astype(str)))
    print("entregas_campus_extension.csv ->", extension.shape)
    print(
        "estudiantes_master.xlsx -> shape",
        maestro.shape,
        "| leído como:",
        maestro.attrs["origen_lectura"],
    )

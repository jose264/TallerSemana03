"""
funciones.py - Funciones reutilizables del flujo analitico
Taller Practico 3 - Python para Ciencia de Datos - UIDE

Modulo con las operaciones de lectura, validacion, integracion y control
de calidad utilizadas por el cuaderno principal.
"""

from pathlib import Path

import pandas as pd

# Extensiones que corresponden a cada formato real detectado por contenido.
extensiones_por_formato = {
    "excel": {"xlsx", "xlsm", "xls"},
    "csv": {"csv", "txt", "tsv"},
}


# ==============================================================================
# LECTURA  (Componente 2)
# ==============================================================================

def detectar_formato(ruta):
    """Identifica el formato real de un archivo leyendo su contenido.

    La extension puede no corresponder al contenido: se inspeccionan los
    primeros bytes en lugar de confiar en el nombre del archivo.

    Devuelve: 'excel' o 'csv'.
    """
    ruta = Path(ruta)
    with open(ruta, "rb") as archivo:
        firma = archivo.read(4)

    # Los .xlsx son archivos ZIP: comienzan con PK\x03\x04
    if firma[:2] == b"PK":
        return "excel"

    # Los .xls antiguos usan el formato compuesto de Microsoft
    if firma == b"\xd0\xcf\x11\xe0":
        return "excel"

    return "csv"


def coincide_extension(ruta, formato):
    """Indica si la extension declarada corresponde al formato real."""
    return Path(ruta).suffix.lstrip(".").lower() in extensiones_por_formato[formato]


def leer_archivo(ruta, **parametros):
    """Lee un archivo aplicando el motor que corresponde a su formato real.

    Acepta los parametros propios de cada lector de Pandas
    (sep, encoding, dtype, parse_dates, etc.); los que no aplican al
    motor elegido se descartan.

    Devuelve: (DataFrame, formato_real)
    """
    ruta = Path(ruta)
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontro el archivo: {ruta}")

    formato = detectar_formato(ruta)

    if formato == "excel":
        validos = {"sheet_name", "dtype", "parse_dates", "usecols",
                   "na_values", "header", "skiprows"}
        df = pd.read_excel(ruta, **{k: v for k, v in parametros.items()
                                    if k in validos})

    else:
        validos = {"sep", "encoding", "dtype", "parse_dates", "usecols",
                   "na_values", "decimal", "header", "skiprows"}
        df = pd.read_csv(ruta, **{k: v for k, v in parametros.items()
                                  if k in validos})

    return df, formato


# ==============================================================================
# VALIDACION  (Componente 4 - controles)
# ==============================================================================

def validar_columnas(df, columnas_esperadas, nombre_fuente):
    """Verifica que el DataFrame contenga las columnas requeridas."""
    faltantes = set(columnas_esperadas) - set(df.columns)
    if faltantes:
        raise ValueError(
            f"[{nombre_fuente}] Faltan columnas obligatorias: {sorted(faltantes)}"
        )
    return True


def validar_clave_unica(df, clave, nombre_fuente):
    """Verifica que la clave no tenga valores repetidos."""
    repetidos = int(df[clave].duplicated().sum())
    if repetidos:
        raise ValueError(
            f"[{nombre_fuente}] La clave '{clave}' tiene {repetidos} "
            f"valores duplicados."
        )
    return True


def controlar_duplicados(df, clave, nombre_fuente):
    """Elimina filas identicas y reporta duplicados por clave."""
    exactos = int(df.duplicated().sum())
    df_limpio = df.drop_duplicates().reset_index(drop=True)
    por_clave = int(df_limpio[clave].duplicated().sum())

    return df_limpio, {
        "fuente": nombre_fuente,
        "duplicados_exactos": exactos,
        "duplicados_por_clave": por_clave,
    }


# ==============================================================================
# INTEGRACION  (Componente 3)
# ==============================================================================

def consolidar_campus(lista_df, columna_origen=None, etiquetas=None):
    """Apila DataFrames de estructura identica reiniciando el indice.

    Trabaja sobre copias para no alterar los DataFrames de entrada.
    ignore_index=True evita que los indices originales se repitan.
    """
    marcados = []
    for indice, df in enumerate(lista_df):
        copia = df.copy()
        if columna_origen and etiquetas:
            copia[columna_origen] = etiquetas[indice]
        marcados.append(copia)

    return pd.concat(marcados, ignore_index=True)


def cruzar_maestro(df_hechos, df_maestro, clave, cardinalidad="many_to_one"):
    """Cruza la tabla de hechos con el catalogo maestro.

    how='left' conserva todos los hechos aunque la clave no exista
    en el maestro. validate bloquea el cruce si la cardinalidad no se cumple.
    """
    filas_antes = len(df_hechos)

    df_cruzado = pd.merge(
        df_hechos,
        df_maestro,
        on=clave,
        how="left",
        validate=cardinalidad,
        indicator="_origen",
    )

    if len(df_cruzado) != filas_antes:
        raise ValueError(
            f"El cruce altero el numero de filas: {filas_antes} -> {len(df_cruzado)}"
        )

    return df_cruzado


# ==============================================================================
# CONTROL DE CALIDAD  (Indicadores - cierre obligatorio)
# ==============================================================================

def generar_reporte_calidad(indicadores):
    """Convierte el diccionario de indicadores en un DataFrame ordenado."""
    return pd.DataFrame(
        [{"indicador": k, "valor": v} for k, v in indicadores.items()]
    )

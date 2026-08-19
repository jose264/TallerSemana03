"""
funciones.py - Funciones reutilizables del flujo analitico
Taller Practico 3 - Python para Ciencia de Datos - UIDE

Modulo con las operaciones de validacion, integracion y control de
calidad utilizadas por el cuaderno principal. La lectura parametrizada
reside en scripts/lectura.py.
"""


import pandas as pd


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

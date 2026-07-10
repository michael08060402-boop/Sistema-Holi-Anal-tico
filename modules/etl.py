"""
================================================================
MÓDULO ETL - Extract, Transform & Load
================================================================
Proyecto: Sistema de Predicción de Demanda - Supermercados Holi
Descripción: Limpieza y transformación del dataset de ventas 2025
================================================================
"""

import pandas as pd
import numpy as np
import re


# ================================================================
# FUNCIÓN 1: VALIDAR ESTRUCTURA DEL DATASET
# ================================================================
def validar_columnas(df):
    """
    Verifica que el dataset tenga las columnas necesarias.
    Retorna: (es_valido, columnas_faltantes)
    """
    columnas_requeridas = [
        "ID_VENTA", "FECHA", "SUCURSAL", "PRODUCTO",
        "CATEGORIA", "CANTIDAD", "PRECIO_UNITARIO",
        "TOTAL_VENTA", "STOCK_ACTUAL", "METODO_PAGO"
    ]
    faltantes = [col for col in columnas_requeridas if col not in df.columns]
    return (len(faltantes) == 0, faltantes)


# ================================================================
# FUNCIÓN 2: DIAGNÓSTICO DEL DATASET SUCIO
# ================================================================
def diagnosticar_dataset(df):
    """
    Analiza el dataset y retorna un diccionario con los problemas detectados.
    """
    diagnostico = {
        "total_registros": len(df),
        "duplicados": int(df.duplicated().sum()),
        "nulos_por_columna": df.isnull().sum().to_dict(),
        "total_nulos": int(df.isnull().sum().sum()),
        "columnas": list(df.columns),
    }

    # Detectar errores específicos
    if "CANTIDAD" in df.columns:
        diagnostico["cantidad_cero_o_negativa"] = int((df["CANTIDAD"] <= 0).sum())

    if "STOCK_ACTUAL" in df.columns:
        diagnostico["stock_negativo"] = int((df["STOCK_ACTUAL"] < 0).sum())

    # Detectar errores tipográficos en categorías
    if "CATEGORIA" in df.columns:
        diagnostico["categorias_unicas_sucias"] = df["CATEGORIA"].nunique()

    if "SUCURSAL" in df.columns:
        diagnostico["sucursales_unicas_sucias"] = df["SUCURSAL"].nunique()

    if "METODO_PAGO" in df.columns:
        diagnostico["metodos_pago_unicos_sucios"] = df["METODO_PAGO"].nunique()

    return diagnostico


# ================================================================
# FUNCIÓN 3: NORMALIZAR TEXTO (quitar espacios, mayúsculas, etc.)
# ================================================================
def normalizar_texto(texto):
    """Estandariza un texto: quita espacios extra y aplica Title Case."""
    if pd.isna(texto):
        return texto
    texto = str(texto).strip()
    texto = re.sub(r"\s+", " ", texto)  # múltiples espacios → uno solo
    return texto.title()


# ================================================================
# FUNCIÓN 4: CORREGIR CATEGORÍAS CON ERRORES TIPOGRÁFICOS
# ================================================================
def corregir_categorias(valor):
    """Mapea variantes mal escritas a la categoría correcta."""
    if pd.isna(valor):
        return valor

    valor_limpio = str(valor).strip().lower()

    mapeo = {
        "snacks": "Snacks", "snack": "Snacks",
        "lacteos": "Lácteos", "lácteos": "Lácteos", "lacteo": "Lácteos",
        "bebidas": "Bebidas", "bebida": "Bebidas",
        "limpieza": "Limpieza", "limpiesa": "Limpieza",
        "cuidado personal": "Cuidado Personal", "cuid. personal": "Cuidado Personal",
        "enlatados": "Enlatados", "enlatado": "Enlatados",
        "abarrotes": "Abarrotes", "abarrote": "Abarrotes", "avarrotes": "Abarrotes",
    }

    return mapeo.get(valor_limpio, valor.title())


# ================================================================
# FUNCIÓN 5: CORREGIR SUCURSALES CON ERRORES TIPOGRÁFICOS
# ================================================================
def corregir_sucursales(valor):
    """Mapea variantes mal escritas a la sucursal correcta."""
    if pd.isna(valor):
        return valor

    valor_limpio = str(valor).strip().lower().replace("  ", " ")

    mapeo = {
        "holi surquillo": "Holi Surquillo",
        "holi barranco": "Holi Barranco", "holy barranco": "Holi Barranco",
        "holi miraflores": "Holi Miraflores",
        "holi surco": "Holi Surco", "holy surco": "Holi Surco",
        "holi san isidro": "Holi San Isidro",
    }

    return mapeo.get(valor_limpio, valor.title())


# ================================================================
# FUNCIÓN 6: CORREGIR MÉTODOS DE PAGO
# ================================================================
def corregir_metodo_pago(valor):
    """Estandariza los métodos de pago."""
    if pd.isna(valor):
        return valor

    valor_limpio = str(valor).strip().lower()

    mapeo = {
        "efectivo": "Efectivo", "efectibo": "Efectivo",
        "tarjeta": "Tarjeta", "tarjet": "Tarjeta",
        "yape": "Yape", "yapr": "Yape",
    }

    return mapeo.get(valor_limpio, valor.title())


# ================================================================
# FUNCIÓN 7: ETL COMPLETO (ORQUESTA TODO EL PROCESO)
# ================================================================
def aplicar_etl(df_original):
    """
    Aplica el proceso ETL completo al dataset.
    Retorna: (df_limpio, log_de_cambios)
    """
    df = df_original.copy()
    log = {}

    # ─────────────────────────────────────────────
    # 1. ELIMINAR DUPLICADOS
    # ─────────────────────────────────────────────
    duplicados_antes = df.duplicated().sum()
    df = df.drop_duplicates()
    log["duplicados_eliminados"] = int(duplicados_antes)

    # ─────────────────────────────────────────────
    # 2. NORMALIZAR FECHAS (varios formatos → uno solo)
    # ─────────────────────────────────────────────
    df["FECHA"] = pd.to_datetime(df["FECHA"], errors="coerce", dayfirst=True)
    fechas_invalidas = df["FECHA"].isnull().sum()
    df = df.dropna(subset=["FECHA"])
    log["fechas_invalidas_eliminadas"] = int(fechas_invalidas)

    # ─────────────────────────────────────────────
    # 3. CORREGIR ERRORES TIPOGRÁFICOS
    # ─────────────────────────────────────────────
    categorias_antes = df["CATEGORIA"].nunique()
    df["CATEGORIA"] = df["CATEGORIA"].apply(corregir_categorias)
    log["categorias_normalizadas"] = int(categorias_antes - df["CATEGORIA"].nunique())

    sucursales_antes = df["SUCURSAL"].nunique()
    df["SUCURSAL"] = df["SUCURSAL"].apply(corregir_sucursales)
    log["sucursales_normalizadas"] = int(sucursales_antes - df["SUCURSAL"].nunique())

    metodos_antes = df["METODO_PAGO"].nunique()
    df["METODO_PAGO"] = df["METODO_PAGO"].apply(corregir_metodo_pago)
    log["metodos_pago_normalizados"] = int(metodos_antes - df["METODO_PAGO"].nunique())

    # ─────────────────────────────────────────────
    # 4. NORMALIZAR PRODUCTOS (espacios, mayúsculas)
    # ─────────────────────────────────────────────
    df["PRODUCTO"] = df["PRODUCTO"].apply(normalizar_texto)

    # ─────────────────────────────────────────────
    # 5. CONVERTIR COLUMNAS NUMÉRICAS
    # ─────────────────────────────────────────────
    for col in ["CANTIDAD", "PRECIO_UNITARIO", "TOTAL_VENTA", "STOCK_ACTUAL"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # ─────────────────────────────────────────────
    # 6. TRATAR VALORES NULOS
    # ─────────────────────────────────────────────
    nulos_precio = df["PRECIO_UNITARIO"].isnull().sum()
    df["PRECIO_UNITARIO"] = df.groupby("PRODUCTO")["PRECIO_UNITARIO"].transform(
        lambda x: x.fillna(x.median())
    )
    log["nulos_precio_imputados"] = int(nulos_precio)

    nulos_stock = df["STOCK_ACTUAL"].isnull().sum()
    df["STOCK_ACTUAL"] = df["STOCK_ACTUAL"].fillna(df["STOCK_ACTUAL"].median())
    log["nulos_stock_imputados"] = int(nulos_stock)

    nulos_pago = df["METODO_PAGO"].isnull().sum()
    df["METODO_PAGO"] = df["METODO_PAGO"].fillna("Efectivo")
    log["nulos_metodo_pago_imputados"] = int(nulos_pago)

    # ─────────────────────────────────────────────
    # 7. VALIDAR Y CORREGIR VALORES ATÍPICOS
    # ─────────────────────────────────────────────
    cantidad_invalida = (df["CANTIDAD"] <= 0).sum()
    df = df[df["CANTIDAD"] > 0]
    log["cantidades_invalidas_eliminadas"] = int(cantidad_invalida)

    stock_negativo = (df["STOCK_ACTUAL"] < 0).sum()
    df.loc[df["STOCK_ACTUAL"] < 0, "STOCK_ACTUAL"] = 0
    log["stock_negativo_corregido"] = int(stock_negativo)

    # ─────────────────────────────────────────────
    # 8. RECALCULAR TOTAL_VENTA (asegurar consistencia)
    # ─────────────────────────────────────────────
    df["TOTAL_VENTA"] = (df["CANTIDAD"] * df["PRECIO_UNITARIO"]).round(2)

    # ─────────────────────────────────────────────
    # 9. ORDENAR POR FECHA
    # ─────────────────────────────────────────────
    df = df.sort_values("FECHA").reset_index(drop=True)

    # ─────────────────────────────────────────────
    # 10. RESUMEN FINAL
    # ─────────────────────────────────────────────
    log["registros_iniciales"] = len(df_original)
    log["registros_finales"] = len(df)
    log["registros_eliminados"] = len(df_original) - len(df)

    return df, log

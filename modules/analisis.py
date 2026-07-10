"""
================================================================
MÓDULO ANÁLISIS - Análisis comercial avanzado
================================================================
Proyecto: Sistema de Predicción de Demanda - Supermercados Holi
Descripción: KPIs, clasificación ABC, rotación y análisis temporal
================================================================
"""

import pandas as pd
import numpy as np


# ================================================================
# FUNCIÓN 1: KPIs PRINCIPALES DEL NEGOCIO
# ================================================================
def calcular_kpis(df):
    """
    Calcula los indicadores clave del negocio.
    Retorna un diccionario con los KPIs principales.
    """
    kpis = {
        "ventas_totales": float(df["TOTAL_VENTA"].sum()),
        "productos_unicos": int(df["PRODUCTO"].nunique()),
        "transacciones": int(len(df)),
        "ticket_promedio": float(df["TOTAL_VENTA"].mean()),
        "unidades_vendidas": int(df["CANTIDAD"].sum()),
        "sucursales_activas": int(df["SUCURSAL"].nunique()),
        "categorias": int(df["CATEGORIA"].nunique()),
        "fecha_inicio": df["FECHA"].min(),
        "fecha_fin": df["FECHA"].max(),
        "dias_operacion": int((df["FECHA"].max() - df["FECHA"].min()).days),
    }
    return kpis


# ================================================================
# FUNCIÓN 2: CLASIFICACIÓN ABC DE PRODUCTOS
# ================================================================
def analisis_abc(df):
    """
    Clasifica los productos en categorías A, B y C según su aporte
    a las ventas totales (Principio de Pareto 80/20).

    - Categoría A: 80% de las ventas (productos estrella)
    - Categoría B: 15% de las ventas (productos importantes)
    - Categoría C: 5% de las ventas (productos de baja rotación)
    """
    productos = (
        df.groupby("PRODUCTO")["TOTAL_VENTA"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    # Calcular porcentaje acumulado
    total = productos["TOTAL_VENTA"].sum()
    productos["% Acumulado"] = (productos["TOTAL_VENTA"].cumsum() / total) * 100
    productos["% Individual"] = (productos["TOTAL_VENTA"] / total) * 100

    # Asignar clasificación
    productos["Clasificación"] = productos["% Acumulado"].apply(
        lambda x: "A" if x <= 80 else ("B" if x <= 95 else "C")
    )

    # Redondear para presentación
    productos["TOTAL_VENTA"] = productos["TOTAL_VENTA"].round(2)
    productos["% Acumulado"] = productos["% Acumulado"].round(2)
    productos["% Individual"] = productos["% Individual"].round(2)

    return productos


# ================================================================
# FUNCIÓN 3: RESUMEN ABC POR CATEGORÍA
# ================================================================
def resumen_abc(df_abc):
    """
    Genera un resumen consolidado de la clasificación ABC.
    """
    resumen = (
        df_abc.groupby("Clasificación")
        .agg(
            Productos=("PRODUCTO", "count"),
            Ventas_Totales=("TOTAL_VENTA", "sum"),
            Porcentaje=("% Individual", "sum"),
        )
        .round(2)
        .reset_index()
    )
    return resumen


# ================================================================
# FUNCIÓN 4: ROTACIÓN DE PRODUCTOS
# ================================================================
def analisis_rotacion(df):
    """
    Calcula la rotación diaria de cada producto.
    Permite identificar productos de alta y baja rotación.
    """
    dias_totales = max((df["FECHA"].max() - df["FECHA"].min()).days, 1)

    rotacion = (
        df.groupby("PRODUCTO")
        .agg(
            Transacciones=("FECHA", "count"),
            Unidades_Vendidas=("CANTIDAD", "sum"),
            Ventas_Totales=("TOTAL_VENTA", "sum"),
            Stock_Promedio=("STOCK_ACTUAL", "mean"),
        )
        .reset_index()
    )

    rotacion["Rotación_Diaria"] = (rotacion["Unidades_Vendidas"] / dias_totales).round(2)
    rotacion["Ventas_Totales"] = rotacion["Ventas_Totales"].round(2)
    rotacion["Stock_Promedio"] = rotacion["Stock_Promedio"].round(1)

    return rotacion.sort_values("Rotación_Diaria", ascending=False).reset_index(drop=True)


# ================================================================
# FUNCIÓN 5: TOP PRODUCTOS POR VENTAS
# ================================================================
def top_productos(df, n=10):
    """Retorna los N productos con mayores ventas."""
    return (
        df.groupby("PRODUCTO")["TOTAL_VENTA"]
        .sum()
        .sort_values(ascending=False)
        .head(n)
        .round(2)
        .reset_index()
    )


# ================================================================
# FUNCIÓN 6: VENTAS POR SUCURSAL
# ================================================================
def ventas_por_sucursal(df):
    """Calcula el aporte de cada sucursal a las ventas totales."""
    ventas = (
        df.groupby("SUCURSAL")
        .agg(
            Ventas_Totales=("TOTAL_VENTA", "sum"),
            Transacciones=("FECHA", "count"),
            Ticket_Promedio=("TOTAL_VENTA", "mean"),
        )
        .round(2)
        .reset_index()
        .sort_values("Ventas_Totales", ascending=False)
    )
    return ventas


# ================================================================
# FUNCIÓN 7: VENTAS POR CATEGORÍA
# ================================================================
def ventas_por_categoria(df):
    """Calcula el aporte de cada categoría a las ventas."""
    ventas = (
        df.groupby("CATEGORIA")
        .agg(
            Ventas_Totales=("TOTAL_VENTA", "sum"),
            Unidades=("CANTIDAD", "sum"),
            Productos=("PRODUCTO", "nunique"),
        )
        .round(2)
        .reset_index()
        .sort_values("Ventas_Totales", ascending=False)
    )
    return ventas


# ================================================================
# FUNCIÓN 8: ANÁLISIS TEMPORAL (mensual, semanal, diario)
# ================================================================
def analisis_temporal(df, frecuencia="mensual"):
    """
    Agrupa las ventas por período temporal.
    frecuencia: 'diaria', 'semanal', 'mensual'
    """
    df_temp = df.copy()

    if frecuencia == "diaria":
        df_temp["Periodo"] = df_temp["FECHA"].dt.date
    elif frecuencia == "semanal":
        df_temp["Periodo"] = df_temp["FECHA"].dt.to_period("W").astype(str)
    else:  # mensual por defecto
        df_temp["Periodo"] = df_temp["FECHA"].dt.to_period("M").astype(str)

    resultado = (
        df_temp.groupby("Periodo")
        .agg(
            Ventas=("TOTAL_VENTA", "sum"),
            Transacciones=("FECHA", "count"),
            Unidades=("CANTIDAD", "sum"),
        )
        .round(2)
        .reset_index()
    )

    return resultado


# ================================================================
# FUNCIÓN 9: VENTAS POR MÉTODO DE PAGO
# ================================================================
def ventas_por_metodo_pago(df):
    """Analiza la distribución de ventas por método de pago."""
    metodo = (
        df.groupby("METODO_PAGO")
        .agg(
            Transacciones=("FECHA", "count"),
            Ventas_Totales=("TOTAL_VENTA", "sum"),
        )
        .round(2)
        .reset_index()
        .sort_values("Ventas_Totales", ascending=False)
    )

    # Agregar porcentaje
    total = metodo["Ventas_Totales"].sum()
    metodo["Porcentaje"] = (metodo["Ventas_Totales"] / total * 100).round(2)

    return metodo


# ================================================================
# FUNCIÓN 10: MATRIZ SUCURSAL x CATEGORÍA
# ================================================================
def matriz_sucursal_categoria(df):
    """Genera una matriz cruzada de ventas por sucursal y categoría."""
    matriz = pd.pivot_table(
        df,
        values="TOTAL_VENTA",
        index="SUCURSAL",
        columns="CATEGORIA",
        aggfunc="sum",
        fill_value=0,
    ).round(2)

    return matriz

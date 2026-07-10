"""
================================================================
MÓDULO DATABASE - Conexión a Neon PostgreSQL
================================================================
Proyecto: Sistema de Predicción de Demanda - Supermercados Holi
Descripción: Carga de datos desde la BD en la nube (Neon)
================================================================
"""

import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()


def get_engine():
    DATABASE_URL = os.getenv("DATABASE_URL")
    return create_engine(DATABASE_URL)


def cargar_datos():
    """
    Carga el dataset completo desde Neon uniendo todas las tablas
    del esquema estrella. Retorna un DataFrame con la misma
    estructura que el ETL, para que los módulos de análisis
    y predicción funcionen sin cambios.
    """
    engine = get_engine()

    query = """
        SELECT
            fv.id_venta          AS "ID_VENTA",
            df.id_fecha          AS "FECHA",
            ds.nombre            AS "SUCURSAL",
            dp.nombre            AS "PRODUCTO",
            dc.nombre            AS "CATEGORIA",
            fv.cantidad          AS "CANTIDAD",
            fv.precio_unit       AS "PRECIO_UNITARIO",
            fv.total_venta       AS "TOTAL_VENTA",
            fv.stock_actual      AS "STOCK_ACTUAL",
            dmp.nombre           AS "METODO_PAGO"
        FROM fact_ventas fv
        JOIN dim_fecha       df  ON fv.fecha       = df.id_fecha
        JOIN dim_sucursal    ds  ON fv.id_sucursal = ds.id_sucursal
        JOIN dim_producto    dp  ON fv.id_producto = dp.id_producto
        JOIN dim_categoria   dc  ON dp.id_categoria = dc.id_categoria
        JOIN dim_metodo_pago dmp ON fv.id_metodo   = dmp.id_metodo
        ORDER BY df.id_fecha
    """

    df = pd.read_sql(query, engine)
    df["FECHA"] = pd.to_datetime(df["FECHA"])
    return df


def cargar_kpis_sql():
    """
    KPIs calculados directamente en SQL (más eficiente para grandes volúmenes).
    """
    engine = get_engine()

    query = """
        SELECT
            SUM(fv.total_venta)              AS ventas_totales,
            COUNT(*)                          AS transacciones,
            AVG(fv.total_venta)              AS ticket_promedio,
            SUM(fv.cantidad)                 AS unidades_vendidas,
            COUNT(DISTINCT fv.id_producto)   AS productos_unicos,
            COUNT(DISTINCT fv.id_sucursal)   AS sucursales_activas
        FROM fact_ventas fv
    """

    return pd.read_sql(query, engine).iloc[0].to_dict()


def ventas_por_mes_sql():
    """Ventas agrupadas por mes directamente desde SQL."""
    engine = get_engine()

    query = """
        SELECT
            df.anio,
            df.mes,
            df.nombre_mes,
            SUM(fv.total_venta)  AS ventas,
            COUNT(*)              AS transacciones
        FROM fact_ventas fv
        JOIN dim_fecha df ON fv.fecha = df.id_fecha
        GROUP BY df.anio, df.mes, df.nombre_mes
        ORDER BY df.anio, df.mes
    """

    return pd.read_sql(query, engine)


def ventas_por_sucursal_sql():
    """Ventas por sucursal directamente desde SQL."""
    engine = get_engine()

    query = """
        SELECT
            ds.nombre            AS sucursal,
            SUM(fv.total_venta)  AS ventas_totales,
            COUNT(*)              AS transacciones,
            AVG(fv.total_venta)  AS ticket_promedio
        FROM fact_ventas fv
        JOIN dim_sucursal ds ON fv.id_sucursal = ds.id_sucursal
        GROUP BY ds.nombre
        ORDER BY ventas_totales DESC
    """

    return pd.read_sql(query, engine)

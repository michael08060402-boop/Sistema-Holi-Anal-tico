import os
import hashlib
import pandas as pd
from psycopg2.extras import execute_values
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()


def get_engine():
    DATABASE_URL = os.getenv("DATABASE_URL")
    return create_engine(DATABASE_URL)


def cargar_datos():
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


def _crear_historial_si_no_existe(engine):
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS historial_cargas (
                id               SERIAL PRIMARY KEY,
                nombre_archivo   VARCHAR(255),
                fecha_carga      TIMESTAMP DEFAULT NOW(),
                registros_nuevos INTEGER,
                periodo_inicio   DATE,
                periodo_fin      DATE,
                sucursales       INTEGER,
                categorias       INTEGER,
                productos        INTEGER
            )
        """))


def _migrar_esquema(engine):
    with engine.begin() as conn:
        conn.execute(text(
            "ALTER TABLE fact_ventas ALTER COLUMN id_venta TYPE TEXT"
        ))


def guardar_en_neon(df, nombre_archivo):
    engine = get_engine()
    _crear_historial_si_no_existe(engine)
    try:
        _migrar_esquema(engine)
    except Exception:
        pass

    df = df.copy()
    df["FECHA"] = pd.to_datetime(df["FECHA"])

    meses = {1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",
             7:"Julio",8:"Agosto",9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"}
    dias  = {0:"Lunes",1:"Martes",2:"Miércoles",3:"Jueves",
             4:"Viernes",5:"Sábado",6:"Domingo"}

    # DIMENSIONES PEQUEÑAS — row-by-row está bien (≤ 50 filas)
    with engine.begin() as conn:
        for _, row in df[["SUCURSAL"]].drop_duplicates().iterrows():
            conn.execute(text("""
                INSERT INTO dim_sucursal (nombre, distrito)
                VALUES (:nombre, :distrito) ON CONFLICT DO NOTHING
            """), {"nombre": row["SUCURSAL"],
                   "distrito": row["SUCURSAL"].replace("Holi ", "")})

    suc_map = dict(zip(*pd.read_sql(
        "SELECT nombre, id_sucursal FROM dim_sucursal", engine
    ).values.T))

    with engine.begin() as conn:
        for _, row in df[["CATEGORIA"]].drop_duplicates().iterrows():
            conn.execute(text("""
                INSERT INTO dim_categoria (nombre) VALUES (:nombre)
                ON CONFLICT DO NOTHING
            """), {"nombre": row["CATEGORIA"]})

    cat_map = dict(zip(*pd.read_sql(
        "SELECT nombre, id_categoria FROM dim_categoria", engine
    ).values.T))

    with engine.begin() as conn:
        for _, row in df[["PRODUCTO","CATEGORIA"]].drop_duplicates(subset="PRODUCTO").iterrows():
            conn.execute(text("""
                INSERT INTO dim_producto (nombre, id_categoria)
                VALUES (:nombre, :id_categoria) ON CONFLICT DO NOTHING
            """), {"nombre": row["PRODUCTO"], "id_categoria": cat_map[row["CATEGORIA"]]})

    prod_map = dict(zip(*pd.read_sql(
        "SELECT nombre, id_producto FROM dim_producto", engine
    ).values.T))

    with engine.begin() as conn:
        for _, row in df[["METODO_PAGO"]].drop_duplicates().iterrows():
            conn.execute(text("""
                INSERT INTO dim_metodo_pago (nombre) VALUES (:nombre)
                ON CONFLICT DO NOTHING
            """), {"nombre": row["METODO_PAGO"]})

    met_map = dict(zip(*pd.read_sql(
        "SELECT nombre, id_metodo FROM dim_metodo_pago", engine
    ).values.T))

    # DIM_FECHA — bulk insert (puede tener 700+ fechas únicas)
    fecha_tuples = []
    for fecha in df["FECHA"].dt.date.unique():
        f = pd.Timestamp(fecha)
        fecha_tuples.append((
            fecha, f.year, f.month, meses[f.month],
            f.quarter, int(f.isocalendar().week), dias[f.dayofweek],
        ))

    with engine.begin() as conn:
        raw = conn.connection
        with raw.cursor() as cur:
            execute_values(cur, """
                INSERT INTO dim_fecha
                    (id_fecha, anio, mes, nombre_mes, trimestre, semana, dia_semana)
                VALUES %s
                ON CONFLICT DO NOTHING
            """, fecha_tuples)

    # FACT_VENTAS — IDs vectoriales + bulk insert con execute_values
    if "ID_VENTA" in df.columns:
        df["_id"] = df["ID_VENTA"].astype(str)
    else:
        base = (df.reset_index()["index"].astype(str)
                + df["FECHA"].dt.date.astype(str)
                + df["SUCURSAL"] + df["PRODUCTO"]
                + df["CANTIDAD"].astype(str))
        df["_id"] = [hashlib.md5(x.encode()).hexdigest()[:24] for x in base]

    df["_id_sucursal"] = df["SUCURSAL"].map(suc_map)
    df["_id_producto"]  = df["PRODUCTO"].map(prod_map)
    df["_id_metodo"]    = df["METODO_PAGO"].map(met_map)
    df["_fecha"]        = df["FECHA"].dt.date

    cols = ["_id", "_fecha", "_id_sucursal", "_id_producto", "_id_metodo",
            "CANTIDAD", "PRECIO_UNITARIO", "TOTAL_VENTA", "STOCK_ACTUAL"]
    fact_tuples = list(df[cols].itertuples(index=False, name=None))

    count_antes = pd.read_sql("SELECT COUNT(*) AS n FROM fact_ventas", engine).iloc[0, 0]

    with engine.begin() as conn:
        raw = conn.connection
        with raw.cursor() as cur:
            execute_values(cur, """
                INSERT INTO fact_ventas
                    (id_venta, fecha, id_sucursal, id_producto,
                     id_metodo, cantidad, precio_unit, total_venta, stock_actual)
                VALUES %s
                ON CONFLICT DO NOTHING
            """, fact_tuples, page_size=500)

    count_despues = pd.read_sql("SELECT COUNT(*) AS n FROM fact_ventas", engine).iloc[0, 0]
    insertados = int(count_despues - count_antes)

    # HISTORIAL
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO historial_cargas
                (nombre_archivo, registros_nuevos, periodo_inicio, periodo_fin,
                 sucursales, categorias, productos)
            VALUES
                (:nombre, :registros, :inicio, :fin, :suc, :cat, :prod)
        """), {
            "nombre":    nombre_archivo,
            "registros": insertados,
            "inicio":    df["FECHA"].min().date(),
            "fin":       df["FECHA"].max().date(),
            "suc":       df["SUCURSAL"].nunique(),
            "cat":       df["CATEGORIA"].nunique(),
            "prod":      df["PRODUCTO"].nunique(),
        })

    return insertados


def cargar_datos_por_periodo(fecha_inicio, fecha_fin):
    engine = get_engine()
    q = text("""
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
        WHERE df.id_fecha BETWEEN :inicio AND :fin
        ORDER BY df.id_fecha
    """)
    with engine.connect() as conn:
        df = pd.read_sql(q, conn, params={"inicio": str(fecha_inicio), "fin": str(fecha_fin)})
    df["FECHA"] = pd.to_datetime(df["FECHA"])
    return df


def obtener_historial():
    engine = get_engine()
    _crear_historial_si_no_existe(engine)
    return pd.read_sql("""
        SELECT
            nombre_archivo   AS "Archivo",
            fecha_carga      AS "Fecha de carga",
            registros_nuevos AS "Registros nuevos",
            periodo_inicio   AS "Desde",
            periodo_fin      AS "Hasta",
            sucursales       AS "Sucursales",
            categorias       AS "Categorías",
            productos        AS "Productos"
        FROM historial_cargas
        ORDER BY fecha_carga DESC
    """, engine)

import os
import hashlib
import pandas as pd
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


def guardar_en_neon(df, nombre_archivo):
    """
    Carga un DataFrame limpio al esquema estrella de Neon
    y registra la carga en el historial.
    Retorna la cantidad de registros nuevos insertados.
    """
    engine = get_engine()
    _crear_historial_si_no_existe(engine)

    df = df.copy()
    df["FECHA"] = pd.to_datetime(df["FECHA"])

    meses = {1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",
             7:"Julio",8:"Agosto",9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"}
    dias  = {0:"Lunes",1:"Martes",2:"Miércoles",3:"Jueves",
             4:"Viernes",5:"Sábado",6:"Domingo"}

    # DIM_SUCURSAL
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

    # DIM_CATEGORIA
    with engine.begin() as conn:
        for _, row in df[["CATEGORIA"]].drop_duplicates().iterrows():
            conn.execute(text("""
                INSERT INTO dim_categoria (nombre) VALUES (:nombre)
                ON CONFLICT DO NOTHING
            """), {"nombre": row["CATEGORIA"]})

    cat_map = dict(zip(*pd.read_sql(
        "SELECT nombre, id_categoria FROM dim_categoria", engine
    ).values.T))

    # DIM_PRODUCTO
    with engine.begin() as conn:
        for _, row in df[["PRODUCTO","CATEGORIA"]].drop_duplicates(subset="PRODUCTO").iterrows():
            conn.execute(text("""
                INSERT INTO dim_producto (nombre, id_categoria)
                VALUES (:nombre, :id_categoria) ON CONFLICT DO NOTHING
            """), {"nombre": row["PRODUCTO"], "id_categoria": cat_map[row["CATEGORIA"]]})

    prod_map = dict(zip(*pd.read_sql(
        "SELECT nombre, id_producto FROM dim_producto", engine
    ).values.T))

    # DIM_METODO_PAGO
    with engine.begin() as conn:
        for _, row in df[["METODO_PAGO"]].drop_duplicates().iterrows():
            conn.execute(text("""
                INSERT INTO dim_metodo_pago (nombre) VALUES (:nombre)
                ON CONFLICT DO NOTHING
            """), {"nombre": row["METODO_PAGO"]})

    met_map = dict(zip(*pd.read_sql(
        "SELECT nombre, id_metodo FROM dim_metodo_pago", engine
    ).values.T))

    # DIM_FECHA
    with engine.begin() as conn:
        for fecha in df["FECHA"].dt.date.unique():
            f = pd.Timestamp(fecha)
            conn.execute(text("""
                INSERT INTO dim_fecha
                    (id_fecha, anio, mes, nombre_mes, trimestre, semana, dia_semana)
                VALUES
                    (:id_fecha,:anio,:mes,:nombre_mes,:trimestre,:semana,:dia_semana)
                ON CONFLICT DO NOTHING
            """), {
                "id_fecha": fecha, "anio": f.year, "mes": f.month,
                "nombre_mes": meses[f.month], "trimestre": f.quarter,
                "semana": f.isocalendar().week, "dia_semana": dias[f.dayofweek],
            })

    # FACT_VENTAS — inserción en lote
    if "ID_VENTA" in df.columns:
        df["_id"] = df["ID_VENTA"].astype(str)
    else:
        df["_id"] = (df.reset_index()["index"].astype(str)
                     + df["FECHA"].dt.date.astype(str)
                     + df["SUCURSAL"] + df["PRODUCTO"]
                     + df["CANTIDAD"].astype(str))
        df["_id"] = df["_id"].apply(
            lambda x: hashlib.md5(x.encode()).hexdigest()[:24]
        )

    df["_id_sucursal"] = df["SUCURSAL"].map(suc_map)
    df["_id_producto"]  = df["PRODUCTO"].map(prod_map)
    df["_id_metodo"]    = df["METODO_PAGO"].map(met_map)
    df["_fecha"]        = df["FECHA"].dt.date

    registros = [
        {
            "id_venta":    row["_id"],
            "fecha":       row["_fecha"],
            "id_sucursal": row["_id_sucursal"],
            "id_producto": row["_id_producto"],
            "id_metodo":   row["_id_metodo"],
            "cantidad":    int(row["CANTIDAD"]),
            "precio_unit": float(row["PRECIO_UNITARIO"]),
            "total_venta": float(row["TOTAL_VENTA"]),
            "stock_actual":int(row["STOCK_ACTUAL"]),
        }
        for _, row in df.iterrows()
    ]

    count_antes = pd.read_sql("SELECT COUNT(*) AS n FROM fact_ventas", engine).iloc[0, 0]

    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO fact_ventas
                (id_venta, fecha, id_sucursal, id_producto,
                 id_metodo, cantidad, precio_unit, total_venta, stock_actual)
            VALUES
                (:id_venta,:fecha,:id_sucursal,:id_producto,
                 :id_metodo,:cantidad,:precio_unit,:total_venta,:stock_actual)
            ON CONFLICT DO NOTHING
        """), registros)

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

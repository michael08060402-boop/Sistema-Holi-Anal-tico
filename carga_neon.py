"""
================================================================
SCRIPT DE CARGA - Dataset Holi → Neon PostgreSQL
================================================================
Lee el dataset limpio y puebla el esquema estrella en Neon.
Ejecutar UNA sola vez: python carga_neon.py
================================================================
"""

import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

print("Leyendo dataset limpio...")
df = pd.read_excel("dataset_limpio.xlsx")
df["FECHA"] = pd.to_datetime(df["FECHA"], dayfirst=True)

# ================================================================
# 1. DIM_SUCURSAL
# ================================================================
print("Cargando dim_sucursal...")
sucursales = df[["SUCURSAL"]].drop_duplicates().reset_index(drop=True)
sucursales["distrito"] = sucursales["SUCURSAL"].str.replace("Holi ", "", regex=False)
sucursales = sucursales.rename(columns={"SUCURSAL": "nombre"})

with engine.begin() as conn:
    for _, row in sucursales.iterrows():
        conn.execute(text("""
            INSERT INTO dim_sucursal (nombre, distrito)
            VALUES (:nombre, :distrito)
            ON CONFLICT DO NOTHING
        """), {"nombre": row["nombre"], "distrito": row["distrito"]})

suc_map = pd.read_sql("SELECT id_sucursal, nombre FROM dim_sucursal", engine)
suc_map = dict(zip(suc_map["nombre"], suc_map["id_sucursal"]))

# ================================================================
# 2. DIM_CATEGORIA
# ================================================================
print("Cargando dim_categoria...")
categorias = df[["CATEGORIA"]].drop_duplicates().reset_index(drop=True)
categorias = categorias.rename(columns={"CATEGORIA": "nombre"})

with engine.begin() as conn:
    for _, row in categorias.iterrows():
        conn.execute(text("""
            INSERT INTO dim_categoria (nombre)
            VALUES (:nombre)
            ON CONFLICT DO NOTHING
        """), {"nombre": row["nombre"]})

cat_map = pd.read_sql("SELECT id_categoria, nombre FROM dim_categoria", engine)
cat_map = dict(zip(cat_map["nombre"], cat_map["id_categoria"]))

# ================================================================
# 3. DIM_PRODUCTO
# ================================================================
print("Cargando dim_producto...")
productos = df[["PRODUCTO", "CATEGORIA"]].drop_duplicates(subset="PRODUCTO").reset_index(drop=True)

with engine.begin() as conn:
    for _, row in productos.iterrows():
        conn.execute(text("""
            INSERT INTO dim_producto (nombre, id_categoria)
            VALUES (:nombre, :id_categoria)
            ON CONFLICT DO NOTHING
        """), {"nombre": row["PRODUCTO"], "id_categoria": cat_map[row["CATEGORIA"]]})

prod_map = pd.read_sql("SELECT id_producto, nombre FROM dim_producto", engine)
prod_map = dict(zip(prod_map["nombre"], prod_map["id_producto"]))

# ================================================================
# 4. DIM_METODO_PAGO
# ================================================================
print("Cargando dim_metodo_pago...")
metodos = df[["METODO_PAGO"]].drop_duplicates().reset_index(drop=True)
metodos = metodos.rename(columns={"METODO_PAGO": "nombre"})

with engine.begin() as conn:
    for _, row in metodos.iterrows():
        conn.execute(text("""
            INSERT INTO dim_metodo_pago (nombre)
            VALUES (:nombre)
            ON CONFLICT DO NOTHING
        """), {"nombre": row["nombre"]})

metodo_map = pd.read_sql("SELECT id_metodo, nombre FROM dim_metodo_pago", engine)
metodo_map = dict(zip(metodo_map["nombre"], metodo_map["id_metodo"]))

# ================================================================
# 5. DIM_FECHA
# ================================================================
print("Cargando dim_fecha...")
meses = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}
dias = {
    0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves",
    4: "Viernes", 5: "Sábado", 6: "Domingo"
}

fechas = df["FECHA"].dt.date.unique()

with engine.begin() as conn:
    for fecha in fechas:
        f = pd.Timestamp(fecha)
        conn.execute(text("""
            INSERT INTO dim_fecha (id_fecha, anio, mes, nombre_mes, trimestre, semana, dia_semana)
            VALUES (:id_fecha, :anio, :mes, :nombre_mes, :trimestre, :semana, :dia_semana)
            ON CONFLICT DO NOTHING
        """), {
            "id_fecha": fecha,
            "anio": f.year,
            "mes": f.month,
            "nombre_mes": meses[f.month],
            "trimestre": f.quarter,
            "semana": f.isocalendar().week,
            "dia_semana": dias[f.dayofweek]
        })

# ================================================================
# 6. FACT_VENTAS
# ================================================================
print("Cargando fact_ventas...")

with engine.begin() as conn:
    for _, row in df.iterrows():
        conn.execute(text("""
            INSERT INTO fact_ventas
                (id_venta, fecha, id_sucursal, id_producto, id_metodo,
                 cantidad, precio_unit, total_venta, stock_actual)
            VALUES
                (:id_venta, :fecha, :id_sucursal, :id_producto, :id_metodo,
                 :cantidad, :precio_unit, :total_venta, :stock_actual)
            ON CONFLICT DO NOTHING
        """), {
            "id_venta": str(row["ID_VENTA"]),
            "fecha": row["FECHA"].date(),
            "id_sucursal": suc_map[row["SUCURSAL"]],
            "id_producto": prod_map[row["PRODUCTO"]],
            "id_metodo": metodo_map[row["METODO_PAGO"]],
            "cantidad": int(row["CANTIDAD"]),
            "precio_unit": float(row["PRECIO_UNITARIO"]),
            "total_venta": float(row["TOTAL_VENTA"]),
            "stock_actual": int(row["STOCK_ACTUAL"])
        })

print("\nCarga completada exitosamente.")
print(f"  Sucursales:    {len(suc_map)}")
print(f"  Categorias:    {len(cat_map)}")
print(f"  Productos:     {len(prod_map)}")
print(f"  Metodos pago:  {len(metodo_map)}")
print(f"  Fechas:        {len(fechas)}")
print(f"  Transacciones: {len(df)}")

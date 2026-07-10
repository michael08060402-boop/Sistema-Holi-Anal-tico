# Holi Intelligence Platform

Sistema de análisis predictivo de ventas para Supermercados Holi — cadena con 5 sedes en Lima, Perú.

---
## Demo Página: https://sistemaholianaticodeventas.streamlit.app
---

## Página Principal
<img width="1867" height="812" alt="Captura de pantalla 2026-07-10 172734" src="https://github.com/user-attachments/assets/3d20fbf1-d55b-47c0-91c2-d4445bf71d2d" />

## Preddición con Prophet
<img width="1817" height="792" alt="Captura de pantalla 2026-07-10 172909" src="https://github.com/user-attachments/assets/6f70a7e1-3aad-4e83-9d77-116bfeea8196" />

## Resúmen de Predicción
<img width="1487" height="810" alt="Captura de pantalla 2026-07-10 172919" src="https://github.com/user-attachments/assets/9b7657d0-51c3-4c75-9687-da5979f49192" />

## Generador de PDF
<img width="1347" height="962" alt="Captura de pantalla 2026-07-10 172959" src="https://github.com/user-attachments/assets/23fc489f-9ce1-411c-ad7c-677185335943" />


---
## Descripción

Dashboard interactivo que integra un pipeline completo de Big Data:

- **ETL** — limpieza y normalización de datos crudos de ventas
- **Star Schema** — esquema dimensional en la nube (Neon PostgreSQL)
- **Análisis** — KPIs, rankings, clasificación ABC y rotación de inventario
- **Predicción** — modelo Prophet para forecast de demanda
- **Reportes** — exportación a PDF ejecutivo con gráficos

## Arquitectura

```
Excel (datos crudos)
       │
       ▼
   ETL (Python / Pandas)
       │
       ▼
Neon PostgreSQL (star schema)
  ├── dim_fecha
  ├── dim_sucursal
  ├── dim_producto
  ├── dim_categoria
  ├── dim_metodo_pago
  └── fact_ventas
       │
       ▼
Streamlit Dashboard
  ├── Vista General
  ├── Rankings
  ├── Análisis ABC
  ├── Rotación
  ├── Predicción (Prophet)
  └── Reportes PDF
```

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Frontend | Streamlit + Plotly |
| Backend / ETL | Python, Pandas, NumPy |
| Base de datos | Neon PostgreSQL (cloud) |
| ORM / conexión | SQLAlchemy + psycopg2 |
| Machine Learning | Facebook Prophet |
| Reportes | ReportLab + Matplotlib |



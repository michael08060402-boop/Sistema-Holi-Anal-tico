# Holi Intelligence Platform

Sistema de análisis predictivo de ventas para Supermercados Holi — cadena con 5 sedes en Lima, Perú.

**Demo:** https://sistemaholianaticodeventas.streamlit.app

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red?logo=streamlit&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-green?logo=postgresql&logoColor=white)
![Prophet](https://img.shields.io/badge/ML-Prophet-orange)

---

## Página Principal
<img width="1867" height="812" alt="Dashboard principal" src="https://github.com/user-attachments/assets/3d20fbf1-d55b-47c0-91c2-d4445bf71d2d" />

## Predicción con Prophet
<img width="1817" height="792" alt="Predicción de demanda" src="https://github.com/user-attachments/assets/6f70a7e1-3aad-4e83-9d77-116bfeea8196" />

## Resumen de Predicción
<img width="1487" height="810" alt="Resumen predicción" src="https://github.com/user-attachments/assets/9b7657d0-51c3-4c75-9687-da5979f49192" />

## Generador de PDF
<img width="1347" height="962" alt="Reporte PDF" src="https://github.com/user-attachments/assets/23fc489f-9ce1-411c-ad7c-677185335943" />

---

## Descripción

Pipeline completo de Big Data para Supermercados Holi: desde la carga de datos crudos en Excel hasta predicción de demanda con Machine Learning, persistencia en la nube y generación de reportes ejecutivos.

### Funcionalidades principales

- **Carga dinámica de Excel** — cualquier dataset en formato Holi se valida, limpia y analiza automáticamente
- **ETL automático** — detecta y corrige duplicados, nulos, fechas inválidas, categorías mal escritas y cantidades negativas
- **Descarga de Excel limpio** — exporta el dataset procesado tras el ETL
- **Star Schema en la nube** — persiste los datos limpios en Neon PostgreSQL con inserción masiva (bulk insert)
- **Historial de cargas** — registra cada archivo cargado; permite recargar cualquier dataset anterior al dashboard con un clic
- **KPIs y análisis** — ventas totales, ticket promedio, rankings, clasificación ABC y rotación de inventario
- **Predicción con IA** — modelo Prophet para forecast de demanda a 7–90 días con intervalo de confianza al 95%
- **Reporte ejecutivo PDF** — con gráficos de productos, sucursales y clasificación ABC

## Arquitectura

```
Excel (datos crudos)
       │
       ▼
   ETL (Python / Pandas)
   ├── Eliminación de duplicados
   ├── Imputación de nulos
   ├── Normalización de categorías
   └── Validación de fechas y cantidades
       │
       ├──► Excel limpio (descarga directa)
       │
       ▼
Neon PostgreSQL — Star Schema
  ├── dim_fecha
  ├── dim_sucursal
  ├── dim_producto
  ├── dim_categoria
  ├── dim_metodo_pago
  ├── fact_ventas
  └── historial_cargas
       │
       ▼
Streamlit Dashboard
  ├── Vista General (evolución, sucursales, métodos de pago)
  ├── Rankings (top productos, categorías)
  ├── Análisis ABC (Pareto 80/20)
  ├── Rotación de inventario
  ├── Predicción (Prophet)
  ├── Reportes PDF
  └── Historial de cargas
```

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Frontend | Streamlit + Plotly |
| Backend / ETL | Python, Pandas, NumPy |
| Base de datos | Neon PostgreSQL (cloud, São Paulo) |
| ORM / conexión | SQLAlchemy + psycopg2 |
| Bulk insert | psycopg2 `execute_values` |
| Machine Learning | Facebook Prophet |
| Reportes | ReportLab + Matplotlib |
| Exportación | OpenPyXL (Excel limpio) |

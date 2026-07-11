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

## Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/michael08060402-boop/Sistema-Holi-Anal-tico.git
cd Sistema-Holi-Anal-tico

# 2. Crear entorno virtual
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar credenciales — crear archivo .env con:
# DATABASE_URL=postgresql://usuario:contraseña@host/neondb?sslmode=require

# 5. Ejecutar
python -m streamlit run app.py
```

## Equipo

- Quispe Cabrera, Rosa
- Fernandez Caceres, Dayssy
- Bada Ccapia, Meier
- Roman Lugo, Michael
- Bazán Mendoza, Alejandro

# Holi Intelligence Platform

Sistema de análisis predictivo de ventas para Supermercados Holi — cadena con 5 sedes en Lima, Perú.

---
## Demo Página: https://sistemaholianaticodeventas.streamlit.app
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
git clone https://github.com/TU_USUARIO/sistema-holi-ua.git
cd sistema-holi-ua

# 2. Crear entorno virtual
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows
# source venv/bin/activate    # macOS / Linux

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar credenciales
# Crear archivo .env con:
# DATABASE_URL=postgresql://usuario:contraseña@host/neondb?sslmode=require

# 5. Ejecutar
python -m streamlit run app.py
```

## Variables de entorno

Crear un archivo `.env` en la raíz del proyecto:

```
DATABASE_URL=postgresql://...
```

> El archivo `.env` está en `.gitignore` y nunca debe subirse al repositorio.

## Equipo

- Quispe Cabrera, Rosa
- Fernandez Caceres, Dayssy
- Bada Ccapia, Meier
- Roman Lugo, Michael
- Bazán Mendoza, Alejandro

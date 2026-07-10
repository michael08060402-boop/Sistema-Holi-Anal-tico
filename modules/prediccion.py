"""
================================================================
MÓDULO PREDICCIÓN - Modelo de Machine Learning
================================================================
Proyecto: Sistema de Predicción de Demanda - Supermercados Holi
Descripción: Modelo Prophet para predicción de demanda futura
================================================================
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

# ────────────────────────────────────────────────────────────────
# Verificar si Prophet está disponible
# ────────────────────────────────────────────────────────────────
try:
    from prophet import Prophet
    PROPHET_DISPONIBLE = True
except ImportError:
    PROPHET_DISPONIBLE = False


# ================================================================
# FUNCIÓN 1: PREPARAR DATOS PARA PROPHET
# ================================================================
def preparar_serie_temporal(df, producto=None, agrupacion="diaria"):
    """
    Prepara la serie temporal en el formato que requiere Prophet.

    Prophet necesita un DataFrame con dos columnas:
      - 'ds': fecha
      - 'y' : valor a predecir (cantidad vendida)

    Parámetros:
        df: DataFrame con datos limpios
        producto: nombre del producto a predecir (None = todos)
        agrupacion: 'diaria', 'semanal', 'mensual'
    """
    # Filtrar por producto si se especifica
    if producto is not None and producto != "Todos los productos":
        df = df[df["PRODUCTO"] == producto].copy()

    if len(df) == 0:
        return None

    # Agrupar según frecuencia
    if agrupacion == "semanal":
        df = df.copy()
        df["FECHA"] = df["FECHA"].dt.to_period("W").dt.start_time
    elif agrupacion == "mensual":
        df = df.copy()
        df["FECHA"] = df["FECHA"].dt.to_period("M").dt.start_time

    serie = df.groupby("FECHA")["CANTIDAD"].sum().reset_index()
    serie.columns = ["ds", "y"]
    serie = serie.sort_values("ds").reset_index(drop=True)

    return serie


# ================================================================
# FUNCIÓN 2: ENTRENAR Y PREDECIR CON PROPHET
# ================================================================
def predecir_demanda(df, producto=None, dias_prediccion=30, agrupacion="diaria"):
    """
    Entrena un modelo Prophet y genera predicciones futuras.

    Retorna:
        (serie_historica, forecast, mensaje_error)
        Si hay error, los primeros dos son None y se retorna el mensaje.
    """
    if not PROPHET_DISPONIBLE:
        return None, None, "La librería Prophet no está instalada"

    # Preparar la serie temporal
    serie = preparar_serie_temporal(df, producto, agrupacion)

    if serie is None or len(serie) < 10:
        return None, None, "No hay suficientes datos para predecir (mínimo 10 registros)"

    try:
        # Configurar y entrenar el modelo
        modelo = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            interval_width=0.95,  # Intervalo de confianza al 95%
        )

        modelo.fit(serie)

        # Generar fechas futuras
        futuro = modelo.make_future_dataframe(periods=dias_prediccion)

        # Predecir
        forecast = modelo.predict(futuro)

        # Asegurar que las predicciones no sean negativas
        forecast["yhat"] = forecast["yhat"].clip(lower=0)
        forecast["yhat_lower"] = forecast["yhat_lower"].clip(lower=0)
        forecast["yhat_upper"] = forecast["yhat_upper"].clip(lower=0)

        return serie, forecast, None

    except Exception as e:
        return None, None, f"Error al entrenar el modelo: {str(e)}"


# ================================================================
# FUNCIÓN 3: OBTENER SOLO LA PREDICCIÓN FUTURA
# ================================================================
def obtener_prediccion_futura(serie, forecast):
    """
    Extrae únicamente la parte de predicción (sin el histórico).
    """
    if serie is None or forecast is None:
        return None

    fecha_corte = serie["ds"].max()
    futuro = forecast[forecast["ds"] > fecha_corte].copy()

    # Renombrar columnas para presentación
    futuro = futuro[["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()
    futuro.columns = ["Fecha", "Predicción", "Mínimo Esperado", "Máximo Esperado"]

    # Redondear y convertir a enteros (cantidades de productos)
    futuro["Predicción"] = futuro["Predicción"].round(0).astype(int)
    futuro["Mínimo Esperado"] = futuro["Mínimo Esperado"].round(0).astype(int)
    futuro["Máximo Esperado"] = futuro["Máximo Esperado"].round(0).astype(int)

    return futuro.reset_index(drop=True)


# ================================================================
# FUNCIÓN 4: MÉTRICAS DEL MODELO
# ================================================================
def calcular_metricas_modelo(serie, forecast):
    """
    Calcula métricas para evaluar la calidad del modelo.
    """
    if serie is None or forecast is None:
        return None

    # Unir histórico con predicción
    df_compare = serie.merge(
        forecast[["ds", "yhat"]],
        on="ds",
        how="inner"
    )

    if len(df_compare) == 0:
        return None

    # Calcular errores
    df_compare["error"] = df_compare["y"] - df_compare["yhat"]
    df_compare["error_absoluto"] = df_compare["error"].abs()
    df_compare["error_porcentual"] = (
        df_compare["error_absoluto"] / df_compare["y"].replace(0, 1) * 100
    )

    metricas = {
        "MAE": round(df_compare["error_absoluto"].mean(), 2),      # Error Absoluto Medio
        "RMSE": round(np.sqrt((df_compare["error"] ** 2).mean()), 2),  # Raíz del Error Cuadrático
        "MAPE": round(df_compare["error_porcentual"].mean(), 2),   # Error Porcentual Absoluto
        "registros_evaluados": len(df_compare),
    }

    return metricas


# ================================================================
# FUNCIÓN 5: RESUMEN EJECUTIVO DE LA PREDICCIÓN
# ================================================================
def resumen_prediccion(serie, forecast, dias_prediccion):
    """
    Genera un resumen ejecutivo de la predicción.
    """
    if serie is None or forecast is None:
        return None

    fecha_corte = serie["ds"].max()
    futuro = forecast[forecast["ds"] > fecha_corte]

    resumen = {
        "demanda_total_predicha": int(futuro["yhat"].sum()),
        "demanda_promedio_diaria": round(futuro["yhat"].mean(), 1),
        "demanda_maxima": int(futuro["yhat"].max()),
        "demanda_minima": int(futuro["yhat"].min()),
        "dias_predichos": dias_prediccion,
        "fecha_inicio_prediccion": futuro["ds"].min(),
        "fecha_fin_prediccion": futuro["ds"].max(),
        "promedio_historico": round(serie["y"].mean(), 1),
        "variacion_vs_historico": round(
            (futuro["yhat"].mean() - serie["y"].mean()) / serie["y"].mean() * 100, 2
        ),
    }

    return resumen

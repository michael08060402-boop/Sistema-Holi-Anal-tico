"""
================================================================
MÓDULO REPORTES - Generación de PDFs ejecutivos
================================================================
Proyecto: Sistema de Predicción de Demanda - Supermercados Holi
Descripción: Construye reportes en PDF con métricas y análisis
================================================================
"""

from io import BytesIO
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image as RLImage,
)


# ================================================================
# PALETA CORPORATIVA HOLI
# ================================================================
C_PRIMARIO   = HexColor("#D35400")
C_SECUNDARIO = HexColor("#FF9E0F")
C_OSCURO     = HexColor("#5E2638")
C_TEXTO      = HexColor("#3d1f08")
C_GRIS       = HexColor("#fff8f0")
C_GRIS2      = HexColor("#ffe8cc")
C_BLANCO     = white

PALETA = ["#5E2638", "#D35400", "#FF9E0F", "#FFCC99", "#c23a00", "#b05010"]


# ================================================================
# ESTILOS DE TEXTO
# ================================================================
def crear_estilos():
    estilos = getSampleStyleSheet()

    estilos.add(ParagraphStyle(
        name="TituloPrincipal",
        fontSize=26,
        textColor=C_PRIMARIO,
        alignment=TA_CENTER,
        spaceAfter=16,
        spaceBefore=8,
        fontName="Helvetica-Bold",
        leading=32,
    ))
    estilos.add(ParagraphStyle(
        name="Subtitulo",
        fontSize=14,
        textColor=C_OSCURO,
        spaceAfter=10,
        spaceBefore=14,
        fontName="Helvetica-Bold",
    ))
    estilos.add(ParagraphStyle(
        name="TextoNormal",
        fontSize=10,
        textColor=C_TEXTO,
        alignment=TA_JUSTIFY,
        spaceAfter=6,
        leading=14,
        fontName="Helvetica",
    ))
    estilos.add(ParagraphStyle(
        name="Etiqueta",
        fontSize=9,
        textColor=HexColor("#9a7050"),
        alignment=TA_CENTER,
        fontName="Helvetica",
    ))
    estilos.add(ParagraphStyle(
        name="Cabecera",
        fontSize=11,
        textColor=C_TEXTO,
        alignment=TA_CENTER,
        fontName="Helvetica",
        spaceAfter=2,
    ))
    return estilos


# ================================================================
# GRÁFICO: TOP PRODUCTOS (barra horizontal)
# ================================================================
def _grafico_top_productos(df_top, n=10):
    df = df_top.head(n).iloc[::-1].copy()
    fig, ax = plt.subplots(figsize=(9, 4.2))
    fig.patch.set_facecolor("#fff8f0")
    ax.set_facecolor("#fff8f0")

    colores = [PALETA[i % len(PALETA)] for i in range(len(df))]
    bars = ax.barh(df["PRODUCTO"], df["TOTAL_VENTA"], color=colores, height=0.62)

    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"S/ {x:,.0f}"))
    ax.tick_params(axis="both", labelsize=8, colors="#6b4c30")
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color("#dba06a")
    ax.spines["bottom"].set_color("#dba06a")
    ax.set_title("Top 10 Productos por Ventas Totales", fontsize=11,
                 fontweight="bold", color="#3d1f08", pad=10)
    ax.set_xlabel("Ventas (S/)", fontsize=9, color="#8a6040")

    plt.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight",
                facecolor="#fff8f0")
    plt.close(fig)
    buf.seek(0)
    return buf


# ================================================================
# GRÁFICO: DISTRIBUCIÓN ABC (torta)
# ================================================================
def _grafico_abc(resumen_abc):
    colores_abc = {"A": "#5E2638", "B": "#D35400", "C": "#FFCC99"}
    colores = [colores_abc.get(r, "#cccccc") for r in resumen_abc["Clasificación"]]
    labels = [f"Cat. {r}" for r in resumen_abc["Clasificación"]]

    fig, ax = plt.subplots(figsize=(5, 3.5))
    fig.patch.set_facecolor("#fff8f0")

    wedges, texts, autotexts = ax.pie(
        resumen_abc["Porcentaje"],
        labels=labels,
        autopct="%1.1f%%",
        colors=colores,
        startangle=140,
        pctdistance=0.72,
        wedgeprops=dict(linewidth=1.5, edgecolor="white"),
    )
    for t in texts:
        t.set_fontsize(9)
        t.set_color("#3d1f08")
    for at in autotexts:
        at.set_color("white")
        at.set_fontsize(9)
        at.set_fontweight("bold")

    ax.set_title("Distribución ABC", fontsize=11, fontweight="bold",
                 color="#3d1f08", pad=8)

    plt.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight",
                facecolor="#fff8f0")
    plt.close(fig)
    buf.seek(0)
    return buf


# ================================================================
# GRÁFICO: VENTAS POR SUCURSAL (barra vertical)
# ================================================================
def _grafico_sucursales(df_suc):
    fig, ax = plt.subplots(figsize=(7, 3.8))
    fig.patch.set_facecolor("#fff8f0")
    ax.set_facecolor("#fff8f0")

    colores = [PALETA[i % len(PALETA)] for i in range(len(df_suc))]
    ax.bar(df_suc["SUCURSAL"], df_suc["Ventas_Totales"], color=colores, width=0.55)

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"S/ {x:,.0f}"))
    ax.tick_params(axis="x", labelsize=7.5, rotation=10, colors="#6b4c30")
    ax.tick_params(axis="y", labelsize=8, colors="#6b4c30")
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color("#dba06a")
    ax.spines["bottom"].set_color("#dba06a")
    ax.set_title("Ventas por Sucursal", fontsize=11, fontweight="bold",
                 color="#3d1f08", pad=10)
    ax.set_ylabel("Ventas (S/)", fontsize=9, color="#8a6040")

    plt.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight",
                facecolor="#fff8f0")
    plt.close(fig)
    buf.seek(0)
    return buf


# ================================================================
# TABLAS AUXILIARES
# ================================================================
def _tabla_kpis(kpis):
    datos = [
        ["Ventas Totales",     f"S/ {kpis['ventas_totales']:,.2f}"],
        ["Transacciones",      f"{kpis['transacciones']:,}"],
        ["Ticket Promedio",    f"S/ {kpis['ticket_promedio']:,.2f}"],
        ["Unidades Vendidas",  f"{kpis['unidades_vendidas']:,}"],
        ["Productos Únicos",   f"{kpis['productos_unicos']}"],
        ["Sucursales Activas", f"{kpis['sucursales_activas']}"],
        ["Días de Operación",  f"{kpis['dias_operacion']} días"],
    ]
    tabla = Table(datos, colWidths=[8 * cm, 7 * cm])
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), C_GRIS2),
        ("BACKGROUND", (1, 0), (1, -1), C_GRIS),
        ("TEXTCOLOR", (0, 0), (-1, -1), C_TEXTO),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#dba06a")),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [C_GRIS, C_GRIS2]),
    ]))
    return tabla


def _tabla_top_productos(df_top):
    datos = [["#", "Producto", "Ventas (S/)"]]
    for i, (_, row) in enumerate(df_top.head(10).iterrows(), 1):
        datos.append([str(i), str(row["PRODUCTO"])[:38], f"S/ {row['TOTAL_VENTA']:,.2f}"])
    tabla = Table(datos, colWidths=[1.2 * cm, 10 * cm, 4.3 * cm])
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), C_PRIMARIO),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("ALIGN", (1, 1), (1, -1), "LEFT"),
        ("ALIGN", (2, 1), (2, -1), "RIGHT"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, C_GRIS]),
        ("GRID", (0, 0), (-1, -1), 0.4, HexColor("#dba06a")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))
    return tabla


def _tabla_abc(resumen_abc):
    datos = [["Clasificación", "Productos", "Ventas Totales", "Participación"]]
    for _, row in resumen_abc.iterrows():
        datos.append([
            f"Categoría {row['Clasificación']}",
            str(int(row["Productos"])),
            f"S/ {row['Ventas_Totales']:,.2f}",
            f"{row['Porcentaje']:.1f}%",
        ])
    tabla = Table(datos, colWidths=[4 * cm, 3 * cm, 5 * cm, 3.5 * cm])
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), C_OSCURO),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, C_GRIS]),
        ("GRID", (0, 0), (-1, -1), 0.4, HexColor("#dba06a")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
    ]))
    return tabla


# ================================================================
# FUNCIÓN PRINCIPAL
# ================================================================
def generar_pdf_ejecutivo(kpis, df_top_productos, resumen_abc_df,
                          log_etl=None, df_sucursales=None):
    """
    Genera un reporte PDF ejecutivo con métricas, tablas y gráficos.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    elementos = []
    estilos = crear_estilos()
    PAGE_W = A4[0] - 4 * cm  # ancho útil

    # ── PORTADA ──────────────────────────────────────────────────
    elementos.append(Spacer(1, 0.5 * cm))
    elementos.append(Paragraph("Supermercados Holi", estilos["TituloPrincipal"]))
    elementos.append(Spacer(1, 0.3 * cm))
    elementos.append(Paragraph(
        "Reporte Ejecutivo · Análisis de Ventas 2025",
        estilos["Cabecera"],
    ))
    elementos.append(Spacer(1, 0.3 * cm))
    elementos.append(Paragraph(
        f"Generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}",
        estilos["Etiqueta"],
    ))
    elementos.append(Spacer(1, 0.8 * cm))

    # ── KPIs ─────────────────────────────────────────────────────
    elementos.append(Paragraph("Indicadores Clave del Negocio", estilos["Subtitulo"]))
    elementos.append(Paragraph(
        f"Período: <b>{kpis['fecha_inicio'].strftime('%d/%m/%Y')}</b> "
        f"al <b>{kpis['fecha_fin'].strftime('%d/%m/%Y')}</b>",
        estilos["TextoNormal"],
    ))
    elementos.append(Spacer(1, 0.3 * cm))
    elementos.append(_tabla_kpis(kpis))
    elementos.append(Spacer(1, 0.9 * cm))

    # ── TOP PRODUCTOS tabla ───────────────────────────────────────
    elementos.append(Paragraph("Top 10 Productos por Ventas", estilos["Subtitulo"]))
    elementos.append(Paragraph(
        "Productos con mayor aporte a las ventas totales de la cadena.",
        estilos["TextoNormal"],
    ))
    elementos.append(Spacer(1, 0.3 * cm))
    elementos.append(_tabla_top_productos(df_top_productos))
    elementos.append(Spacer(1, 0.6 * cm))

    # ── GRÁFICO: Top productos ────────────────────────────────────
    try:
        img_top = _grafico_top_productos(df_top_productos)
        img_w = PAGE_W
        img_h = img_w * 4.2 / 9
        elementos.append(RLImage(img_top, width=img_w, height=img_h))
    except Exception:
        pass
    elementos.append(Spacer(1, 0.6 * cm))

    # ── PÁGINA 2 ──────────────────────────────────────────────────
    elementos.append(PageBreak())

    # ── GRÁFICO: Sucursales ───────────────────────────────────────
    if df_sucursales is not None:
        elementos.append(Paragraph("Ventas por Sucursal", estilos["Subtitulo"]))
        try:
            img_suc = _grafico_sucursales(df_sucursales)
            img_w = PAGE_W * 0.78
            img_h = img_w * 3.8 / 7
            elementos.append(RLImage(img_suc, width=img_w, height=img_h))
        except Exception:
            pass
        elementos.append(Spacer(1, 0.8 * cm))

    # ── ANÁLISIS ABC ──────────────────────────────────────────────
    elementos.append(Paragraph("Clasificación ABC de Productos", estilos["Subtitulo"]))
    elementos.append(Paragraph(
        "El análisis ABC clasifica los productos según el principio de Pareto (80/20) "
        "para priorizar la gestión de inventario y las decisiones comerciales.",
        estilos["TextoNormal"],
    ))
    elementos.append(Spacer(1, 0.3 * cm))

    # Tabla + gráfico lado a lado
    try:
        img_abc = _grafico_abc(resumen_abc_df)
        img_h_abc = 3.8 * cm
        img_w_abc = img_h_abc * 5 / 3.5
        tabla_abc = _tabla_abc(resumen_abc_df)
        fila = Table(
            [[tabla_abc, RLImage(img_abc, width=img_w_abc, height=img_h_abc)]],
            colWidths=[PAGE_W - img_w_abc - 0.5 * cm, img_w_abc],
        )
        fila.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
        elementos.append(fila)
    except Exception:
        elementos.append(_tabla_abc(resumen_abc_df))

    elementos.append(Spacer(1, 0.5 * cm))
    for linea in [
        "• <b>Categoría A</b>: Productos estrella — generan el 80% de ventas. Stock prioritario.",
        "• <b>Categoría B</b>: Productos importantes — aportan el 15%. Atención regular.",
        "• <b>Categoría C</b>: Baja rotación — aportan el 5%. Candidatos a promoción o descontinuación.",
    ]:
        elementos.append(Paragraph(linea, estilos["TextoNormal"]))
    elementos.append(Spacer(1, 0.8 * cm))

    # ── ETL (opcional) ────────────────────────────────────────────
    if log_etl:
        elementos.append(Paragraph("Proceso ETL Aplicado", estilos["Subtitulo"]))
        elementos.append(Paragraph(
            f"Se procesaron <b>{log_etl.get('registros_iniciales', 0):,}</b> registros, "
            f"eliminándose <b>{log_etl.get('registros_eliminados', 0)}</b> registros problemáticos. "
            f"Dataset final: <b>{log_etl.get('registros_finales', 0):,}</b> transacciones válidas.",
            estilos["TextoNormal"],
        ))
        elementos.append(Spacer(1, 0.3 * cm))
        datos_etl = [
            ["Acción de Limpieza", "Cantidad"],
            ["Duplicados eliminados",           str(log_etl.get("duplicados_eliminados", 0))],
            ["Fechas inválidas eliminadas",      str(log_etl.get("fechas_invalidas_eliminadas", 0))],
            ["Categorías normalizadas",          str(log_etl.get("categorias_normalizadas", 0))],
            ["Sucursales normalizadas",          str(log_etl.get("sucursales_normalizadas", 0))],
            ["Métodos de pago normalizados",     str(log_etl.get("metodos_pago_normalizados", 0))],
            ["Precios imputados (mediana)",      str(log_etl.get("nulos_precio_imputados", 0))],
            ["Stock imputado",                   str(log_etl.get("nulos_stock_imputados", 0))],
            ["Cantidades inválidas eliminadas",  str(log_etl.get("cantidades_invalidas_eliminadas", 0))],
            ["Stock negativo corregido",         str(log_etl.get("stock_negativo_corregido", 0))],
        ]
        t = Table(datos_etl, colWidths=[10 * cm, 5 * cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), C_PRIMARIO),
            ("TEXTCOLOR", (0, 0), (-1, 0), white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (1, 0), (1, -1), "CENTER"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, C_GRIS]),
            ("GRID", (0, 0), (-1, -1), 0.4, HexColor("#dba06a")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
        ]))
        elementos.append(t)
        elementos.append(Spacer(1, 0.8 * cm))

    # ── PIE DE PÁGINA ─────────────────────────────────────────────
    elementos.append(Spacer(1, 1 * cm))
    elementos.append(Paragraph("─" * 70, estilos["Etiqueta"]))
    elementos.append(Paragraph(
        "Holi Intelligence Platform · Supermercados Holi · Lima, Perú",
        estilos["Etiqueta"],
    ))

    doc.build(elementos)
    buffer.seek(0)
    return buffer

# pages/1_Produccion_Biogas.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF # Asumiendo que sigues con fpdf2
from fpdf.enums import XPos, YPos # Para fpdf2
import traceback # Para imprimir tracebacks detallados

# --- CONFIGURACIÓN DE PÁGINA (OPCIONAL AQUÍ SI ESTÁ EN APP_PRINCIPAL.PY) ---
# st.set_page_config(page_title="Producción de Biometano", layout="wide") # Puede estar en app_principal.py

# --- DATOS DE EJEMPLO PREDETERMINADOS ---
default_insumos_data_pg1 = [ 
    {
        "nombre": "Estiércol Vacuno (Líquido)", "volumen": 5000.0, "residuo_ganadero": "Sí",
        "humedad": 90.0, "ts": 10.0, "sv": 80.0, "potencial": 300.0,
        "porcentaje_ch4": 60.0, "rendimiento_upgrading": 95.0
    },
    {
        "nombre": "Residuos de Cosecha (Paja Maíz)", "volumen": 1500.0, "residuo_ganadero": "No",
        "humedad": 15.0, "ts": 85.0, "sv": 75.0, "potencial": 350.0,
        "porcentaje_ch4": 55.0, "rendimiento_upgrading": 96.0
    },
    {
        "nombre": "FORSU (Fracción Orgánica Residuos Sólidos Urbanos)", "volumen": 3000.0, "residuo_ganadero": "No",
        "humedad": 70.0, "ts": 30.0, "sv": 85.0, "potencial": 400.0,
        "porcentaje_ch4": 62.0, "rendimiento_upgrading": 94.0
    }
]
default_num_insumos_pg1 = len(default_insumos_data_pg1)

# --- DEFINICIÓN GLOBAL DE COLUMNAS PARA PDF (USADO EN ESTA PÁGINA) ---
columnas_pdf_export_list_pg1 = [
    "Nombre", "Volumen (t/año)", "TS (t/año)", "SV (t/año)",
    "Biogás Bruto (m3/año)", "Biometano útil (m3/año)", "Biometano final (m3/año)"
]

# --- TÍTULO DE LA PÁGINA ---
st.title("🐖 Cálculo de Producción de Biogás y Biometano (Formulario)")
st.markdown("---")

# --- FORMULARIO DE ENTRADA DE DATOS ---
st.header("Formulario de Insumos")
with st.form("input_form_pg1"): 
    num_insumos = st.number_input(
        "Número de insumos", min_value=1, max_value=10,
        value=default_num_insumos_pg1, step=1, key="pg1_num_insumos"
    )
    datos_pg1 = []
    for i in range(num_insumos):
        st.subheader(f"Insumo {i+1}")
        current_default = {}
        if i < len(default_insumos_data_pg1):
            current_default = default_insumos_data_pg1[i]
        
        residuo_options = ["Sí", "No"]
        default_residuo_index = 0
        if "residuo_ganadero" in current_default:
            try:
                default_residuo_index = residuo_options.index(current_default.get("residuo_ganadero", "Sí"))
            except ValueError: default_residuo_index = 0

        nombre = st.text_input(f"Nombre del insumo {i+1}", value=current_default.get("nombre", f"Insumo {i+1}"), key=f"pg1_nombre_{i}")
        volumen = st.number_input(f"Volumen (t/año) {i+1}", min_value=0.0, value=current_default.get("volumen", 0.0), key=f"pg1_volumen_{i}")
        residuo_ganadero = st.selectbox(f"Residuo ganadero {i+1}", residuo_options, index=default_residuo_index, key=f"pg1_residuo_{i}")
        humedad = st.number_input(f"Humedad (%) {i+1}", 0.0, 100.0, value=current_default.get("humedad", 0.0), key=f"pg1_humedad_{i}")
        ts = st.number_input(f"Sólidos Totales (% de materia húmeda) {i+1}", 0.0, 100.0, value=current_default.get("ts", 0.0), key=f"pg1_ts_{i}")
        sv = st.number_input(f"Sólidos Volátiles (% de SMS) {i+1}", 0.0, 100.0, value=current_default.get("sv", 0.0), key=f"pg1_sv_{i}")
        potencial = st.number_input(f"Potencial de metano (m3CH4/tSV) {i+1}", 0.0, value=current_default.get("potencial", 0.0), key=f"pg1_potencial_{i}")
        porcentaje_ch4 = st.number_input(f"%CH4 {i+1}", 0.0, 100.0, value=current_default.get("porcentaje_ch4", 0.0), key=f"pg1_ch4_{i}")
        rendimiento_upgrading = st.number_input(f"Rendimiento upgrading (%) {i+1}", 0.0, 100.0, value=current_default.get("rendimiento_upgrading", 95.0), key=f"pg1_upgrading_{i}")
        
        datos_pg1.append({
            "Nombre": nombre, "Volumen (t/año)": volumen, "Residuo ganadero": residuo_ganadero,
            "Humedad (%)": humedad, "TS (%)": ts, "SV (%sms)": sv,
            "Potencial (m3CH4/tSV)": potencial, "%CH4": porcentaje_ch4, "Upgrading (%)": rendimiento_upgrading
        })
    submitted_pg1 = st.form_submit_button("Calcular Producción")

# --- FUNCIÓN PARA EXPORTAR PDF (ADAPTADA PARA FPDF2) ---
def exportar_pdf_pg1(df_export, columnas_para_pdf):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt="Resultados de Producción de Biometano", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.ln(5)
    col_widths_config = {
        "Nombre": 55, "Volumen (t/año)": 25, "TS (t/año)": 25, "SV (t/año)": 25,
        "Biogás Bruto (m3/año)": 30, "Biometano útil (m3/año)": 30, "Biometano final (m3/año)": 30,
    }
    page_width = pdf.w - 2 * pdf.l_margin
    defined_widths_sum = sum(col_widths_config.get(col, 0) for col in columnas_para_pdf if col in col_widths_config)
    num_undefined_cols = len([col for col in columnas_para_pdf if col not in col_widths_config])
    remaining_width = page_width - defined_widths_sum
    default_width_for_undefined = (remaining_width / num_undefined_cols) if num_undefined_cols > 0 else 20
    dynamic_col_widths = {col_name: col_widths_config.get(col_name, default_width_for_undefined) for col_name in columnas_para_pdf}
    current_total_width = sum(dynamic_col_widths.values())
    if current_total_width > page_width:
        scale_factor = page_width / current_total_width
        for col_name in dynamic_col_widths: dynamic_col_widths[col_name] *= scale_factor
    elif current_total_width < page_width * 0.95 and current_total_width > 0:
        try:
            scale_factor = (page_width * 0.95) / current_total_width
            for col_name in dynamic_col_widths: dynamic_col_widths[col_name] *= scale_factor
        except ZeroDivisionError: pass
    pdf.set_font("Arial", 'B', 7)
    header_y = pdf.get_y()
    for col_name in columnas_para_pdf:
        pdf.multi_cell(dynamic_col_widths.get(col_name, 20), 8, col_name, border=1, align='C', new_x=XPos.RIGHT, new_y=YPos.TOP, max_line_height=pdf.font_size * 1.2)
    pdf.set_y(header_y + 8)
    pdf.set_font("Arial", '', 7)
    for i in range(len(df_export)):
        row_y_start = pdf.get_y()
        max_h = pdf.font_size * 1.2
        for col_name in columnas_para_pdf:
            valor_txt = f"{df_export.iloc[i][col_name]:.2f}" if isinstance(df_export.iloc[i][col_name], float) else str(df_export.iloc[i][col_name])
            cell_height = pdf.multi_cell(dynamic_col_widths.get(col_name, 20), pdf.font_size * 1.2, valor_txt, border=0, align='L', new_x=XPos.RIGHT, new_y=YPos.TOP, max_line_height=pdf.font_size * 1.2, dry_run=True, output="HEIGHT")
            max_h = max(max_h, cell_height)
        pdf.set_y(row_y_start)
        for col_name in columnas_para_pdf:
            valor_txt = f"{df_export.iloc[i][col_name]:.2f}" if isinstance(df_export.iloc[i][col_name], float) else str(df_export.iloc[i][col_name])
            pdf.multi_cell(dynamic_col_widths.get(col_name, 20), max_h, valor_txt, border=1, align='L', new_x=XPos.RIGHT, new_y=YPos.TOP, max_line_height=pdf.font_size * 1.2)
        pdf.set_y(row_y_start + max_h)
    try:
        pdf_output_result = pdf.output(dest='S')
        if isinstance(pdf_output_result, str): return pdf_output_result.encode('latin-1')
        elif isinstance(pdf_output_result, bytes): return pdf_output_result
        elif isinstance(pdf_output_result, bytearray): return bytes(pdf_output_result)
        else:
            st.error(f"FPDF output (dest='S') devolvió un tipo inesperado: {type(pdf_output_result)}")
            return b""
    except Exception as e:
        st.error(f"Error al generar PDF bytes: {e}\n{traceback.format_exc()}")
        return b""

# --- LÓGICA DE PROCESAMIENTO Y VISUALIZACIÓN DE RESULTADOS ---
if submitted_pg1:
    df_pg1 = pd.DataFrame(datos_pg1)
    df_pg1["TS (t/año)"] = df_pg1["Volumen (t/año)"].astype(float) * df_pg1["TS (%)"].astype(float) / 100
    df_pg1["SV (t/año)"] = df_pg1["TS (t/año)"].astype(float) * df_pg1["SV (%sms)"].astype(float) / 100
    df_pg1["Biogás Bruto (m3/año)"] = df_pg1["SV (t/año)"].astype(float) * df_pg1["Potencial (m3CH4/tSV)"].astype(float)
    df_pg1["Biometano útil (m3/año)"] = df_pg1["Biogás Bruto (m3/año)"].astype(float) * (df_pg1["%CH4"].astype(float) / 100)
    df_pg1["Biometano final (m3/año)"] = df_pg1["Biometano útil (m3/año)"].astype(float) * (df_pg1["Upgrading (%)"].astype(float) / 100)
    
    df_pg1["Agua en Insumo (t/año)"] = df_pg1["Volumen (t/año)"].astype(float) * (df_pg1["Humedad (%)"].astype(float) / 100)
    
    total_volumen_insumos_humedos_t_ano_calc = df_pg1["Volumen (t/año)"].sum()
    total_ts_en_insumos_t_ano_calc = df_pg1["TS (t/año)"].sum()
    total_biogas_bruto_m3_ano_calc = df_pg1["Biogás Bruto (m3/año)"].sum() 

    columns_to_format_display_pg1 = ["TS (t/año)", "SV (t/año)", "Biogás Bruto (m3/año)", "Biometano útil (m3/año)", "Biometano final (m3/año)", "Agua en Insumo (t/año)"]
    for col in columns_to_format_display_pg1:
        if col in df_pg1.columns:
            df_pg1[col] = pd.to_numeric(df_pg1[col], errors='coerce').fillna(0)
    st.success("✅ Cálculos completados")
    st.subheader("Resultados de Producción")
    display_columns_streamlit_pg1 = [
        "Nombre", "Volumen (t/año)", "Humedad (%)", "TS (%)", "SV (%sms)",
        "Potencial (m3CH4/tSV)", "%CH4", "Upgrading (%)",
        "TS (t/año)", "SV (t/año)", "Agua en Insumo (t/año)", "Biogás Bruto (m3/año)",
        "Biometano útil (m3/año)", "Biometano final (m3/año)"
    ]
    display_columns_existing_streamlit_pg1 = [col for col in display_columns_streamlit_pg1 if col in df_pg1.columns]
    format_dict_streamlit_pg1 = {col: "{:.2f}" for col in columns_to_format_display_pg1 if col in df_pg1.columns}
    if display_columns_existing_streamlit_pg1:
        st.dataframe(df_pg1[display_columns_existing_streamlit_pg1].style.format(format_dict_streamlit_pg1), key="pg1_df_results")
    
    st.subheader("Visualización de Producción por Insumo")
    plot_cols_pg1 = ["Biogás Bruto (m3/año)", "Biometano útil (m3/año)", "Biometano final (m3/año)"]
    df_plot_pg1 = df_pg1.dropna(subset=plot_cols_pg1 + ["Nombre"])
    if not df_plot_pg1.empty:
        fig, ax = plt.subplots(figsize=(12, 7))
        n_insumos_plot = len(df_plot_pg1["Nombre"])
        bar_width = 0.25
        index_bars = range(n_insumos_plot)
        ax.bar([i - bar_width for i in index_bars], df_plot_pg1["Biogás Bruto (m3/año)"], bar_width, label='Biogás Bruto')
        ax.bar(index_bars, df_plot_pg1["Biometano útil (m3/año)"], bar_width, label='Biometano útil')
        ax.bar([i + bar_width for i in index_bars], df_plot_pg1["Biometano final (m3/año)"], bar_width, label='Biometano final')
        ax.set_ylabel("Producción (m3/año)"); ax.set_title("Producción por tipo de insumo")
        ax.set_xticks(index_bars); ax.set_xticklabels(df_plot_pg1["Nombre"], rotation=45, ha="right")
        ax.legend(); plt.tight_layout(); st.pyplot(fig) # CORRECCIÓN AQUÍ: SE QUITÓ key="pg1_plot"
    
    st.subheader("Exportar resultados")
    output_excel_pg1 = BytesIO()
    if display_columns_existing_streamlit_pg1:
        df_excel_pg1 = df_pg1[display_columns_existing_streamlit_pg1].copy()
        with pd.ExcelWriter(output_excel_pg1, engine='xlsxwriter') as writer:
            df_excel_pg1.to_excel(writer, index=False, sheet_name='ResultadosProduccion')
        st.download_button("📥 Descargar Excel", output_excel_pg1.getvalue(), "resultados_produccion.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="pg1_dl_excel")
    
    valid_columns_for_pdf_pg1 = [col for col in columnas_pdf_export_list_pg1 if col in df_pg1.columns]
    if valid_columns_for_pdf_pg1:
        df_pdf_export_safe_pg1 = df_pg1[valid_columns_for_pdf_pg1].copy()
        for col in df_pdf_export_safe_pg1.select_dtypes(include=float).columns: df_pdf_export_safe_pg1[col] = df_pdf_export_safe_pg1[col].fillna(0.0)
        for col in df_pdf_export_safe_pg1.select_dtypes(include=object).columns: df_pdf_export_safe_pg1[col] = df_pdf_export_safe_pg1[col].fillna("")
        pdf_data_pg1 = exportar_pdf_pg1(df_pdf_export_safe_pg1, valid_columns_for_pdf_pg1)
        if pdf_data_pg1: st.download_button("📄 Descargar PDF", pdf_data_pg1, "resultados_produccion.pdf", "application/pdf", key="pg1_dl_pdf")

    st.session_state['datos_produccion_biogas_completados'] = True
    st.session_state['total_volumen_insumos_humedos_t_dia'] = total_volumen_insumos_humedos_t_ano_calc / 365.0
    st.session_state['total_ts_en_insumos_t_dia'] = total_ts_en_insumos_t_ano_calc / 365.0
    st.session_state['total_biogas_bruto_m3_dia'] = total_biogas_bruto_m3_ano_calc / 365.0 
    
    st.success("Datos base para Balance de Aguas guardados en sesión.")
# pages/2_Balance_de_Aguas.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go 
from io import BytesIO 

# --- TÍTULO DE LA PÁGINA ---
st.title("💧 Balance de Aguas Detallado para Planta de Biogás")
st.markdown("---")

# --- SECCIÓN 1: DATOS DE ENTRADA DE LOS INSUMOS ---
st.header("🍚 Agua en Insumos de Alimentación")

datos_precargados = False
volumen_total_insumos_t_dia_ss = 0.0
ts_total_insumos_t_dia_ss = 0.0 # Este será TS en t/día
ts_promedio_calculado_ss = 15.0 # Valor por defecto

if 'datos_produccion_biogas_completados' in st.session_state and st.session_state['datos_produccion_biogas_completados']:
    try:
        volumen_total_insumos_t_dia_ss = float(st.session_state.get('total_volumen_insumos_humedos_t_dia', 0))
        ts_total_insumos_t_dia_ss = float(st.session_state.get('total_ts_en_insumos_t_dia', 0))
        
        if volumen_total_insumos_t_dia_ss > 0: # TS total puede ser 0 si el volumen es 0
            datos_precargados = True
            ts_promedio_calculado_ss = (ts_total_insumos_t_dia_ss / volumen_total_insumos_t_dia_ss * 100) if volumen_total_insumos_t_dia_ss > 0 else 0.0
            st.success("Datos de insumos cargados desde la página 'Producción de Biogás'.")
        else:
            st.info("Volumen de insumos desde 'Producción de Biogás' es cero. Ingrese los datos manualmente.")
            datos_precargados = False # Asegurar que no se usen valores cero sin advertencia
    except Exception as e:
        st.warning(f"Error al cargar datos de sesión para insumos: {e}. Ingrese los datos manualmente.")
        datos_precargados = False
else:
    st.info("Calcule primero en 'Producción de Biogás' para precargar datos de insumos, o ingréselos manualmente.")

with st.expander("Ingresar/Modificar Datos Agregados de Insumos", expanded=not datos_precargados):
    col1_ins, col2_ins = st.columns(2)
    volumen_total_insumos_t_dia = col1_ins.number_input(
        "Volumen total de insumos húmedos (toneladas/día)", min_value=0.0,
        value=volumen_total_insumos_t_dia_ss, step=1.0, key="wb_vol_insumos"
    )
    ts_promedio_insumos_percent = col2_ins.number_input(
        "Contenido de Sólidos Totales (TS) promedio de los insumos (%)", min_value=0.0, max_value=100.0,
        value=ts_promedio_calculado_ss, step=0.1, key="wb_ts_insumos_prom"
    )

ts_total_t_dia = volumen_total_insumos_t_dia * (ts_promedio_insumos_percent / 100.0)
agua_en_insumos_t_dia = volumen_total_insumos_t_dia - ts_total_t_dia

st.markdown(f"**Agua total en insumos:** `{agua_en_insumos_t_dia:.2f} m³/día` (asumiendo 1 t ≈ 1 m³ para agua)")
st.markdown(f"**Sólidos totales en insumos:** `{ts_total_t_dia:.2f} toneladas/día`")
st.markdown("---")

# --- SECCIÓN 2: OTRAS ENTRADAS Y PARÁMETROS DE PROCESO ---
st.header("⚙️ Parámetros del Proceso y Otras Entradas de Agua")
col_params1, col_params2 = st.columns(2)
with col_params1:
    st.subheader("Agua Adicional y Objetivo TS")
    agua_dilucion_directa_m3_dia = st.number_input("Agua de dilución directa añadida (m³/día)", 0.0, value=0.0, step=1.0, key="wb_agua_dil_dir")
    agua_limpieza_m3_dia = st.number_input("Agua de limpieza que entra al proceso (m³/día)", 0.0, value=5.0, step=0.5, key="wb_agua_limpieza")
    target_TS_digestor_percent = st.slider("TS objetivo en el digestor (%)", 1.0, 25.0, 10.0, 0.1, key="wb_target_ts_dig")
with col_params2:
    st.subheader("Pérdidas y Separación")
    recirculacion_fraccion = st.slider("Fracción de recirculación del efluente líquido", 0.0, 1.0, 0.3, 0.01, key="wb_recirc_frac")
    evaporacion_perdida_fraccion = st.slider("Fracción de pérdida por evaporación (del total en digestor)", 0.0, 0.1, 0.01, 0.001, format="%.3f", key="wb_evap_frac")
    humedad_torta_solida_percent = st.slider("Humedad de la torta sólida separada (%)", 50.0, 95.0, 75.0, 0.5, key="wb_hum_torta")
    eficiencia_captura_ts_en_torta = st.slider("Eficiencia de captura de TS en torta sólida (%)", 0.0, 100.0, 85.0, 1.0, key="wb_ts_capture_eff") / 100.0


# --- SECCIÓN 3: AGUA EN BIOGÁS (DETALLADO) ---
st.subheader("💧 Agua en Biogás (Condensado)")
biogas_bruto_m3_dia_ss = 0.0
if 'datos_produccion_biogas_completados' in st.session_state and st.session_state['datos_produccion_biogas_completados']:
    try:
        biogas_bruto_m3_dia_ss = float(st.session_state.get('total_biogas_bruto_m3_dia', 0))
        if biogas_bruto_m3_dia_ss > 0:
            st.success(f"Volumen de biogás ({biogas_bruto_m3_dia_ss:.2f} Nm³/día) cargado.")
        else:
            st.info("Volumen de biogás de 'Producción de Biogás' es cero o no disponible. Ingrese manualmente.")
    except Exception as e:
        st.warning(f"Error cargando volumen de biogás: {e}. Ingrese manualmente.")

volumen_biogas_Nm3_dia = st.number_input(
    "Volumen de biogás bruto producido (Nm³/día)", 0.0,
    value=biogas_bruto_m3_dia_ss if biogas_bruto_m3_dia_ss > 0 else 500.0,
    step=10.0, key="wb_vol_biogas"
)
temp_biogas_C = st.number_input("Temperatura del biogás en saturación (°C)", 0.0, 60.0, 35.0, 0.5, key="wb_temp_biogas")

g_agua_por_Nm3_biogas = 0.0
if temp_biogas_C <= 5: g_agua_por_Nm3_biogas = 6.8
elif temp_biogas_C <= 10: g_agua_por_Nm3_biogas = 9.4
elif temp_biogas_C <= 15: g_agua_por_Nm3_biogas = 12.8
elif temp_biogas_C <= 20: g_agua_por_Nm3_biogas = 17.3
elif temp_biogas_C <= 25: g_agua_por_Nm3_biogas = 23.0
elif temp_biogas_C <= 30: g_agua_por_Nm3_biogas = 30.4
elif temp_biogas_C <= 35: g_agua_por_Nm3_biogas = 39.6
elif temp_biogas_C <= 40: g_agua_por_Nm3_biogas = 51.1
elif temp_biogas_C <= 45: g_agua_por_Nm3_biogas = 65.6
elif temp_biogas_C <= 50: g_agua_por_Nm3_biogas = 83.0
else: g_agua_por_Nm3_biogas = 100.0 # Aproximación para T > 50C

g_agua_por_Nm3_biogas_adj = st.number_input(
    f"Contenido de agua en biogás a {temp_biogas_C}°C (g H₂O / Nm³)", 0.0, 200.0,
    value=g_agua_por_Nm3_biogas, step=0.1, key="wb_g_h2o_biogas",
    help="Valores típicos de saturación. Ajuste si tiene datos más precisos."
)
agua_en_biogas_condensado_m3_dia = (volumen_biogas_Nm3_dia * g_agua_por_Nm3_biogas_adj) / 1000000.0
st.markdown(f"**Agua estimada como condensado del biogás:** `{agua_en_biogas_condensado_m3_dia:.3f} m³/día`")
st.markdown("---")

# --- SECCIÓN 4: CÁLCULO Y RESULTADOS DEL BALANCE ---
st.header("🧮 Resultados del Balance de Aguas")
if st.button("Calcular Balance de Aguas", key="wb_calc_balance_button", type="primary"):
    # ENTRADAS DE AGUA
    target_TS_digestor_fraccion = target_TS_digestor_percent / 100.0
    if target_TS_digestor_fraccion <= 0:
        st.error("TS Objetivo en digestor no puede ser 0%."); st.stop()

    masa_total_en_digestor_objetivo_t_dia = ts_total_t_dia / target_TS_digestor_fraccion
    agua_total_requerida_en_digestor_m3_dia = masa_total_en_digestor_objetivo_t_dia - ts_total_t_dia
    agua_ya_presente_m3_dia = agua_en_insumos_t_dia + agua_limpieza_m3_dia + agua_dilucion_directa_m3_dia
    agua_dilucion_calculada_m3_dia = agua_total_requerida_en_digestor_m3_dia - agua_ya_presente_m3_dia
    
    current_ts_before_calc_dilution_percent = 0
    if (agua_ya_presente_m3_dia + ts_total_t_dia) > 0: # Evitar división por cero
        current_ts_before_calc_dilution_percent = (ts_total_t_dia / (agua_ya_presente_m3_dia + ts_total_t_dia)) * 100

    if agua_dilucion_calculada_m3_dia < 0:
        agua_dilucion_calculada_m3_dia = 0
        st.warning(
            f"El TS actual de la mezcla de insumos y agua de proceso ({current_ts_before_calc_dilution_percent:.1f}%) "
            f"ya es igual o inferior al TS objetivo ({target_TS_digestor_percent:.1f}%). "
            "No se calcula agua de dilución adicional. Considere aumentar el TS objetivo o reducir el agua de proceso."
        )

    E1_agua_en_insumos = agua_en_insumos_t_dia
    E2_agua_dilucion_directa = agua_dilucion_directa_m3_dia
    E3_agua_limpieza = agua_limpieza_m3_dia
    E4_agua_dilucion_calculada = agua_dilucion_calculada_m3_dia
    total_agua_entrante_m3_dia = E1_agua_en_insumos + E2_agua_dilucion_directa + E3_agua_limpieza + E4_agua_dilucion_calculada
    total_slurry_en_digestor_m3_dia = ts_total_t_dia + total_agua_entrante_m3_dia

    # SALIDAS DE AGUA
    S1_evaporacion_m3_dia = total_slurry_en_digestor_m3_dia * evaporacion_perdida_fraccion
    S2_condensado_biogas_m3_dia = agua_en_biogas_condensado_m3_dia
    
    slurry_post_perdidas_m3_dia = total_slurry_en_digestor_m3_dia - S1_evaporacion_m3_dia - S2_condensado_biogas_m3_dia
    ts_en_slurry_post_perdidas_t_dia = ts_total_t_dia 

    ts_torta_solida_fraccion = (100.0 - humedad_torta_solida_percent) / 100.0
    ts_en_torta_t_dia = ts_en_slurry_post_perdidas_t_dia * eficiencia_captura_ts_en_torta
    S3_masa_torta_solida_t_dia = ts_en_torta_t_dia / ts_torta_solida_fraccion if ts_torta_solida_fraccion > 0 else 0
    agua_en_torta_solida_m3_dia = S3_masa_torta_solida_t_dia - ts_en_torta_t_dia
    
    masa_efluente_liquido_total_t_dia = slurry_post_perdidas_m3_dia - S3_masa_torta_solida_t_dia
    ts_en_efluente_liquido_total_t_dia = ts_en_slurry_post_perdidas_t_dia - ts_en_torta_t_dia
    agua_en_efluente_liquido_total_m3_dia = masa_efluente_liquido_total_t_dia - ts_en_efluente_liquido_total_t_dia

    S4_agua_recirculada_m3_dia = masa_efluente_liquido_total_t_dia * recirculacion_fraccion 
    # La recirculación devuelve agua y TS. Aquí simplificamos a caudal de líquido.
    # Si recirculamos agua, esta agua vuelve a sumarse a las entradas o reduce la necesidad de dilución.
    # Para este balance, consideramos la recirculación como un flujo interno y nos centramos en el efluente NETO.

    agua_efluente_liquido_neto_m3_dia = agua_en_efluente_liquido_total_m3_dia * (1.0 - recirculacion_fraccion)
    # ts_efluente_liquido_neto_t_dia = ts_en_efluente_liquido_total_t_dia * (1.0 - recirculacion_fraccion) # No es necesario para balance de agua

    total_agua_saliente_m3_dia = S1_evaporacion_m3_dia + S2_condensado_biogas_m3_dia + agua_en_torta_solida_m3_dia + agua_efluente_liquido_neto_m3_dia
    balance_hidrico_m3_dia = total_agua_entrante_m3_dia - total_agua_saliente_m3_dia

    st.subheader("Resumen del Balance Hídrico (m³/día)")
    mcol1, mcol2, mcol3 = st.columns(3)
    mcol1.metric("Total Agua Entrante", f"{total_agua_entrante_m3_dia:.2f}")
    mcol2.metric("Total Agua Saliente (Neta)", f"{total_agua_saliente_m3_dia:.2f}")
    mcol3.metric("Balance (Entradas - Salidas)", f"{balance_hidrico_m3_dia:.2f}", delta=f"{balance_hidrico_m3_dia:.2f}")

    if abs(balance_hidrico_m3_dia) > (0.02 * total_agua_entrante_m3_dia) and total_agua_entrante_m3_dia > 0.01:
        st.warning("El balance hídrico presenta un desajuste mayor al 2%. Revise parámetros.")
    else:
        st.success("El balance hídrico está razonablemente ajustado.")

    data_entradas = {"Concepto Entrada": ["Agua en Insumos", "Agua Dilución Directa", "Agua de Limpieza", "Agua Dilución Necesaria Calculada"],
                     "Flujo (m³/día)": [E1_agua_en_insumos, E2_agua_dilucion_directa, E3_agua_limpieza, E4_agua_dilucion_calculada]}
    df_entradas = pd.DataFrame(data_entradas)
    data_salidas = {"Concepto Salida": ["Evaporación", "Condensado Biogás", "Agua en Torta Sólida", "Agua Efluente Líquido Neto"],
                    "Flujo (m³/día)": [S1_evaporacion_m3_dia, S2_condensado_biogas_m3_dia, agua_en_torta_solida_m3_dia, agua_efluente_liquido_neto_m3_dia]}
    df_salidas = pd.DataFrame(data_salidas)
    
    st.markdown("##### Detalles de Flujos")
    dcol1, dcol2 = st.columns(2)
    with dcol1: st.dataframe(df_entradas.style.format({"Flujo (m³/día)": "{:.2f}"}), hide_index=True, use_container_width=True)
    with dcol2: st.dataframe(df_salidas.style.format({"Flujo (m³/día)": "{:.2f}"}), hide_index=True, use_container_width=True)
    st.write(f"**Agua Recirculada (Interna):** {S4_agua_recirculada_m3_dia:.2f} m³/día")

    st.subheader("Visualización del Balance de Aguas")
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(name='Entradas', x=['Total Flujos'], y=[total_agua_entrante_m3_dia], text=[f"{total_agua_entrante_m3_dia:.2f}"], textposition='auto', marker_color='royalblue'))
    fig_bar.add_trace(go.Bar(name='Salidas (Netas)', x=['Total Flujos'], y=[total_agua_saliente_m3_dia], text=[f"{total_agua_saliente_m3_dia:.2f}"], textposition='auto', marker_color='orangered'))
    fig_bar.update_layout(title_text='Comparación Entradas vs. Salidas Netas de Agua', yaxis_title='Flujo de Agua (m³/día)', barmode='group', legend_title_text='Flujo')
    st.plotly_chart(fig_bar, use_container_width=True)

    labels_sankey = [
        "Agua en Insumos", "Agua Dil. Directa", "Agua Limpieza", "Agua Dil. Calculada", # 0-3
        "Total Agua Entrante al Proceso", # 4
        "Evaporación", "Condensado", "Agua Torta Sólida", "Agua Efluente Líquido Neto", # 5-8
        "Agua Recirculada (Retorno)", #9 (aunque es un loop, aquí lo mostramos como 'salida' del efluente total y 'entrada' al proceso)
        "Efluente Líquido Bruto (antes de recirc.)" #10
    ]
    source_nodes = [0,1,2,3,  4,4,4,   4,                         10,                            10]
    target_nodes = [4,4,4,4,  5,6,10,  S4_agua_recirculada_m3_dia > 0.001 if 9 else 4,  9 if S4_agua_recirculada_m3_dia > 0.001 else 4,8] # Si recirc>0 va a 9, sino a 4 (proceso) o a 8 (salida neta)
                                                                                                                                      # Si recirc > 0, efluente bruto (10) -> recirc (9) y efluente neto (8)
                                                                                                                                      # Si recirc = 0, efluente bruto (10) -> efluente neto (8)
    values = [
        E1_agua_en_insumos, E2_agua_dilucion_directa, E3_agua_limpieza, E4_agua_dilucion_calculada, # A nodo 4
        S1_evaporacion_m3_dia, S2_condensado_biogas_m3_dia, agua_en_efluente_liquido_total_m3_dia, # De nodo 4 a 10 (efluente bruto)
        S4_agua_recirculada_m3_dia, # De nodo 4 (o 10) a 9 (recirculación)
        S4_agua_recirculada_m3_dia, # De nodo 10 a 9
        agua_efluente_liquido_neto_m3_dia # De nodo 10 a 8
    ]
    
    # Simplificación de Sankey para claridad (menos nodos)
    labels_sankey_simple = [
        "Insumos", "Dilución Directa", "Limpieza", "Dilución Calculada", # 0-3 (Fuentes)
        "Proceso Digestor", # 4 (Central)
        "Evaporación", "Condensado", "Torta Sólida", "Efluente Neto", # 5-8 (Salidas Netas)
        "Recirculación" # 9 (Loop, tratado como salida y luego vuelve a entrar o reduce necesidad de dilución)
    ]
    
    s_nodes = [0,1,2,3, # Fuentes -> Proceso
               4,4,4,4, # Proceso -> Salidas/Recirculación
               9]       # Recirculación -> Proceso (conceptual)
    t_nodes = [4,4,4,4, # -> Proceso
               5,6,7,9, # -> Salidas/Recirculación
               4]       # -> Proceso
    v_values = [
        E1_agua_en_insumos, E2_agua_dilucion_directa, E3_agua_limpieza, E4_agua_dilucion_calculada,
        S1_evaporacion_m3_dia, S2_condensado_biogas_m3_dia, agua_en_torta_solida_m3_dia, S4_agua_recirculada_m3_dia, # Salida a recirculación
        S4_agua_recirculada_m3_dia # Recirculación vuelve al proceso
    ]
    # Necesitamos una salida NETA para el Sankey simple, si la recirculación vuelve al proceso
    # El efluente líquido NETO es una salida final.
    s_nodes_final = [0,1,2,3,  4,4,4,4, 9] # El efluente líquido neto es una salida del proceso, después de la recirc.
    t_nodes_final = [4,4,4,4,  5,6,7,8, 4] # Salida a Efluente Neto (8)
    v_values_final = [
        E1_agua_en_insumos, E2_agua_dilucion_directa, E3_agua_limpieza, E4_agua_dilucion_calculada,
        S1_evaporacion_m3_dia, S2_condensado_biogas_m3_dia, agua_en_torta_solida_m3_dia, agua_efluente_liquido_neto_m3_dia, # Salida a Efluente Neto
        S4_agua_recirculada_m3_dia # Recirculación vuelve al proceso
    ]

    # Filtrar flujos con valor cero
    valid_indices = [i for i, v in enumerate(v_values_final) if v > 0.001]
    filtered_s = [s_nodes_final[i] for i in valid_indices]
    filtered_t = [t_nodes_final[i] for i in valid_indices]
    filtered_v = [v_values_final[i] for i in valid_indices]

    if filtered_v:
        fig_sankey = go.Figure(data=[go.Sankey(
            arrangement = "snap", # Alinea los nodos
            node=dict(
                pad=20, thickness=20, line=dict(color="black", width=0.5),
                label=labels_sankey_simple,
                color=["skyblue","skyblue","skyblue","skyblue", "green", "lightcoral","lightcoral","lightcoral","lightcoral", "mediumpurple"]
            ),
            link=dict(source=filtered_s, target=filtered_t, value=filtered_v)
        )])
        fig_sankey.update_layout(title_text="Diagrama de Flujo de Agua Simplificado (Sankey)", font_size=11, height=500)
        st.plotly_chart(fig_sankey, use_container_width=True)
    
    st.subheader("📤 Exportar Resumen del Balance")
    df_export_summary = pd.DataFrame({
        "Concepto": ["Total Agua Entrante", "Total Agua Saliente (Neta)", "Balance (Entradas - Salidas)", "Agua Recirculada"],
        "Flujo (m³/día)": [total_agua_entrante_m3_dia, total_agua_saliente_m3_dia, balance_hidrico_m3_dia, S4_agua_recirculada_m3_dia]
    })
    csv_export_summary = df_export_summary.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ CSV Resumen", csv_export_summary, "water_balance_summary.csv", "text/csv", key="wb_csv_summary_dl")
    try:
        output_excel = BytesIO()
        with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
            df_entradas.to_excel(writer, index=False, sheet_name='EntradasAgua')
            df_salidas.to_excel(writer, index=False, sheet_name='SalidasAgua')
            df_export_summary.to_excel(writer, index=False, sheet_name='ResumenBalance')
        excel_data = output_excel.getvalue()
        st.download_button("⬇️ Excel Detallado", excel_data, "water_balance_detailed.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="wb_excel_detail_dl")
    except ImportError: st.warning("Instale 'openpyxl' para exportar a Excel: pip install openpyxl")
    except Exception as e: st.error(f"Error exportando a Excel: {e}")
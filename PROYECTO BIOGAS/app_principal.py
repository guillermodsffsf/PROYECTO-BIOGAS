# app_principal.py
import streamlit as st

st.set_page_config(
    page_title="Planta de Biogás - Análisis Integral",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.sidebar.success("Seleccione una sección arriba.")

st.markdown(
    """
    # Bienvenido al Sistema de Análisis de Plantas de Biogás 👋
    
    Esta aplicación proporciona herramientas para calcular la producción de biogás
    y realizar un balance de aguas del proceso.

    **👈 Seleccione una de las herramientas en la barra lateral** para comenzar.

    ### Funcionalidades:
    - **Producción de Biogás**: Calcule el biogás y biometano potencial a partir de diversos insumos.
    - **Balance de Aguas**: Analice las entradas y salidas de agua en su proceso.
    """
)
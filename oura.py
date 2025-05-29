import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta

st.set_page_config(page_title="📿 Dashboard Personal – Oura Ring", layout="wide")
st.title("📿 Dashboard Personal – Oura Ring")

# --- Cargar token desde secrets ---
token = st.secrets["oura"]["token"]
headers = {"Authorization": f"Bearer {token}"}

# --- DAILY SUMMARY ---
st.subheader("📆 Resumen Diario (Sleep, Readiness, Actividad)")
summary_url = "https://api.ouraring.com/v2/usercollection/daily_summary"
response = requests.get(summary_url, headers=headers)

df = pd.DataFrame()
if response.status_code == 200:
    data = response.json().get("data", [])
    df = pd.DataFrame(data)
    df["day"] = pd.to_datetime(df["day"])
    
    st.dataframe(df[["day", "sleep_score", "readiness_score", "activity_score"]].set_index("day"))

    fig = px.line(df, x="day", y=["sleep_score", "readiness_score", "activity_score"],
                  title="📊 Evolución de Scores Diarios")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("No se pudo obtener el resumen diario.")

# --- HEARTRATE ---
st.subheader("❤️ Frecuencia Cardíaca Detallada (hora local UTC-3)")

hr_url = "https://api.ouraring.com/v2/usercollection/heartrate"
hr_response = requests.get(hr_url, headers=headers)

if hr_response.status_code == 200:
    hr_data = hr_response.json().get("data", [])
    if hr_data:
        df_hr = pd.DataFrame(hr_data)
        df_hr["timestamp"] = pd.to_datetime(df_hr["timestamp"]) - timedelta(hours=3)
        fig_hr = px.line(df_hr, x="timestamp", y="bpm", title="📈 HR en Hora Argentina (UTC-3)")
        st.plotly_chart(fig_hr, use_container_width=True)
    else:
        df_hr = pd.DataFrame()
        st.info("No hay datos de HR disponibles.")
else:
    df_hr = pd.DataFrame()
    st.warning("No se pudo obtener frecuencia cardíaca.")

# --- TABLA: Respiración y Temperatura ---
st.subheader("📋 Tabla diaria – Respiración y Temperatura Nocturna")

if not df.empty and "respiratory_rate" in df.columns:
    tabla_extra = df[["day", "respiratory_rate", "temperature_deviation"]].dropna()
    tabla_extra["day"] = pd.to_datetime(tabla_extra["day"])
    tabla_extra = tabla_extra.sort_values("day", ascending=False)
    tabla_extra.columns = ["Fecha", "Resp/min", "Temp Δ (°C)"]

    st.dataframe(tabla_extra.set_index("Fecha"), use_container_width=True)
else:
    st.info("No hay datos de respiración o temperatura disponibles.")

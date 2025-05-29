import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="📿 Dashboard Personal – Oura Ring", layout="wide")
st.title("📿 Dashboard Personal – Oura Ring")

# --- Token desde secrets.toml ---
token = st.secrets["oura"]["token"]
headers = {"Authorization": f"Bearer {token}"}


# Convertimos timestamp a hora Argentina
if not df_hr.empty:
    df_hr["timestamp"] = pd.to_datetime(df_hr["timestamp"]) - timedelta(hours=3)
    fig_hr = px.line(df_hr, x="timestamp", y="bpm", title="📈 HR en Hora Argentina (UTC-3)")
    st.plotly_chart(fig_hr, use_container_width=True)
else:
    st.info("No hay datos de HR disponibles.")

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
st.subheader("❤️ Frecuencia Cardíaca (BPM por timestamp)")
hr_url = "https://api.ouraring.com/v2/usercollection/heartrate"
hr_response = requests.get(hr_url, headers=headers)
df_hr = pd.DataFrame()

if hr_response.status_code == 200:
    hr_data = hr_response.json().get("data", [])
    if hr_data:
        df_hr = pd.DataFrame(hr_data)
        df_hr["timestamp"] = pd.to_datetime(df_hr["timestamp"])
        fig_hr = px.line(df_hr, x="timestamp", y="bpm", title="📈 HR Detallado")
        st.plotly_chart(fig_hr, use_container_width=True)
    else:
        st.info("No hay datos de HR disponibles.")
else:
    st.warning("No se pudo obtener frecuencia cardíaca.")

# --- HR + Respiración + Temperatura en un solo gráfico ---
st.subheader("🧠 HR, Respiraciones y Temperatura Nocturna")

# Asegurar existencia de df_hr y df
if df_hr.empty:
    df_hr = pd.DataFrame(columns=["timestamp", "bpm"])
if df.empty:
    df = pd.DataFrame(columns=["day", "respiratory_rate", "temperature_deviation"])

# HR diario promedio
if not df_hr.empty:
    df_hr["date"] = df_hr["timestamp"].dt.date
    df_hr_daily = df_hr.groupby("date")["bpm"].mean().reset_index()
    df_hr_daily["date"] = pd.to_datetime(df_hr_daily["date"])
else:
    df_hr_daily = pd.DataFrame(columns=["date", "bpm"])

# Respiración y temperatura diaria
if not df.empty and "respiratory_rate" in df.columns:
    tabla_extra = df[["day", "respiratory_rate", "temperature_deviation"]].dropna()
    tabla_extra["day"] = pd.to_datetime(tabla_extra["day"])
    tabla_extra = tabla_extra.sort_values("day", ascending=False)
    tabla_extra.columns = ["Fecha", "Resp/min", "Temp Δ (°C)"]

    st.subheader("📋 Tabla diaria – Respiración y Temperatura")
    st.dataframe(tabla_extra.set_index("Fecha"), use_container_width=True)
else:
    st.info("No hay datos de respiración o temperatura disponibles.")

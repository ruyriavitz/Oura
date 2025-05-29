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

# Respiración y temperatura
try:
    df_extra = df[["day", "respiratory_rate", "temperature_deviation"]].dropna()
    df_extra.rename(columns={"day": "date"}, inplace=True)
except:
    df_extra = pd.DataFrame(columns=["date", "respiratory_rate", "temperature_deviation"])

# Unir y graficar
df_all = pd.merge(df_hr_daily, df_extra, on="date", how="outer").sort_values("date")

fig_combo = go.Figure()

# BPM y Respiración (eje Y1)
if "bpm" in df_all.columns:
    fig_combo.add_trace(go.Scatter(x=df_all["date"], y=df_all["bpm"],
                                   mode='lines+markers', name="BPM", yaxis="y1"))

if "respiratory_rate" in df_all.columns:
    fig_combo.add_trace(go.Scatter(x=df_all["date"], y=df_all["respiratory_rate"],
                                   mode='lines+markers', name="Resp/min", yaxis="y1"))

# Temperatura (eje Y2 separado)
if "temperature_deviation" in df_all.columns:
    fig_combo.add_trace(go.Scatter(x=df_all["date"], y=df_all["temperature_deviation"],
                                   mode='lines+markers', name="Temp Δ (°C)", yaxis="y2"))

# Layout con doble eje
fig_combo.update_layout(
    title="📊 HR, Respiraciones y Temperatura Nocturna",
    xaxis=dict(title="Fecha"),
    yaxis=dict(title="BPM / Resp/min", side="left"),
    yaxis2=dict(title="Temp Δ (°C)", overlaying="y", side="right", showgrid=False),
    legend=dict(x=0.01, y=1),
    margin=dict(l=50, r=80, t=50, b=50)
)

st.plotly_chart(fig_combo, use_container_width=True)

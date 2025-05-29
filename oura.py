import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Oura Dashboard", layout="wide")
st.title("📿 Dashboard Personal – Oura Ring")

# --- Secretos ---
token = st.secrets["oura"]["token"]

headers = {"Authorization": f"Bearer {token}"}

# --- Datos diarios ---
st.subheader("📅 Resumen Diario (Sleep, Readiness, Actividad)")
summary_url = "https://api.ouraring.com/v2/usercollection/daily_summary"
summary_response = requests.get(summary_url, headers=headers)

if summary_response.status_code == 200:
    data = summary_response.json().get("data", [])
    df = pd.DataFrame(data)
    df["day"] = pd.to_datetime(df["day"])

    st.dataframe(df[["day", "sleep_score", "readiness_score", "activity_score"]].set_index("day"))

    fig = px.line(df, x="day", y=["sleep_score", "readiness_score", "activity_score"],
                  title="📊 Scores diarios")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("No se pudo obtener resumen diario.")

# --- SPO2 ---
st.subheader("🫁 SPO2 Nocturno")
spo2_url = "https://api.ouraring.com/v2/usercollection/spo2"
spo2_response = requests.get(spo2_url, headers=headers)

if spo2_response.status_code == 200:
    spo2_data = spo2_response.json().get("data", [])
    if spo2_data:
        df_spo2 = pd.DataFrame(spo2_data)
        df_spo2["day"] = pd.to_datetime(df_spo2["day"])
        fig_spo2 = px.line(df_spo2, x="day", y="average",
                           title="📈 SPO2 promedio durante el sueño")
        st.plotly_chart(fig_spo2, use_container_width=True)
    else:
        st.info("No hay datos de SPO2 disponibles.")
else:
    st.warning("No se pudo obtener SPO2.")

# --- FC (solo Gen 3) ---
st.subheader("❤️ Frecuencia Cardíaca (Gen 3)")
hr_url = "https://api.ouraring.com/v2/usercollection/heartrate"
hr_response = requests.get(hr_url, headers=headers)

if hr_response.status_code == 200:
    hr_data = hr_response.json().get("data", [])
    if hr_data:
        df_hr = pd.DataFrame(hr_data)
        df_hr["timestamp"] = pd.to_datetime(df_hr["timestamp"])
        fig_hr = px.line(df_hr, x="timestamp", y="bpm", title="📉 Frecuencia Cardíaca (BPM)")
        st.plotly_chart(fig_hr, use_container_width=True)
    else:
        st.info("No hay datos de FC disponibles.")
else:
    st.warning("No se pudo obtener frecuencia cardíaca.")

import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Oura Dashboard", layout="wide")

st.title("📿 Dashboard Personal – Oura Ring")

# Ingreso de token
token = st.text_input("🔐 Ingresá tu Personal Access Token", type="password")

if token:
    headers = {"Authorization": f"Bearer {token}"}

    # Obtener resumen diario
    url = "https://api.ouraring.com/v2/usercollection/daily_summary"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()["data"]
        df = pd.DataFrame(data)
        df["day"] = pd.to_datetime(df["day"])

        st.subheader("📆 Resumen Diario")
        st.dataframe(df[["day", "sleep_score", "readiness_score", "activity_score"]].set_index("day"))

        fig = px.line(df, x="day", y=["sleep_score", "readiness_score", "activity_score"],
                      labels={"value": "Score", "day": "Día", "variable": "Categoría"},
                      title="📊 Evolución de tus scores")
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.error("No pudimos acceder a tus datos. Verificá el token.")
else:
    st.info("Ingresá tu token arriba para comenzar")

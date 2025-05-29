import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta

st.subheader("❤️ HR Detallado + Respiración y Temperatura (Tabla)")

# Asegurar existencia de df_hr y df
if "df_hr" not in locals():
    df_hr = pd.DataFrame()
if "df" not in locals():
    df = pd.DataFrame()

# Convertimos timestamp a hora Argentina
if not df_hr.empty:
    df_hr["timestamp"] = pd.to_datetime(df_hr["timestamp"]) - timedelta(hours=3)
    fig_hr = px.line(df_hr, x="timestamp", y="bpm", title="📈 HR en Hora Argentina (UTC-3)")
    st.plotly_chart(fig_hr, use_container_width=True)
else:
    st.info("No hay datos de HR disponibles.")

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

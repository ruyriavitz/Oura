import plotly.graph_objects as go

st.subheader("🧠 Ritmo cardíaco, Respiración y Temperatura")

# HR data (alta frecuencia)
if "df_hr" in locals() and not df_hr.empty:
    # Daily averages for HR
    df_hr["date"] = df_hr["timestamp"].dt.date
    df_hr_daily = df_hr.groupby("date")["bpm"].mean().reset_index()
    df_hr_daily["date"] = pd.to_datetime(df_hr_daily["date"])
else:
    df_hr_daily = pd.DataFrame(columns=["date", "bpm"])

# Respiración y temperatura (del daily summary)
try:
    df_extra = df[["day", "respiratory_rate", "temperature_deviation"]].dropna()
    df_extra.rename(columns={"day": "date"}, inplace=True)
except Exception as e:
    st.warning("No se pudo obtener respiración o temperatura")
    st.text(str(e))
    df_extra = pd.DataFrame(columns=["date", "respiratory_rate", "temperature_deviation"])

# Unimos
df_all = pd.merge(df_hr_daily, df_extra, on="date", how="outer").sort_values("date")

# Gráfico multieje
fig = go.Figure()

fig.add_trace(go.Scatter(x=df_all["date"], y=df_all["bpm"],
                         mode='lines+markers', name="BPM", yaxis="y1"))

fig.add_trace(go.Scatter(x=df_all["date"], y=df_all["respiratory_rate"],
                         mode='lines+markers', name="Resp/min", yaxis="y2"))

fig.add_trace(go.Scatter(x=df_all["date"], y=df_all["temperature_deviation"],
                         mode='lines+markers', name="Temp Δ (°C)", yaxis="y3"))

fig.update_layout(
    title="📊 HR, Respiraciones y Temperatura Nocturna",
    xaxis=dict(title="Fecha"),
    yaxis=dict(title="BPM", side="left"),
    yaxis2=dict(title="Resp/min", overlaying="y", side="right", showgrid=False),
    yaxis3=dict(title="Temp Δ", overlaying="y", side="right", position=1.05),
    legend=dict(x=0.01, y=1),
    margin=dict(l=50, r=80, t=50, b=50)
)

st.plotly_chart(fig, use_container_width=True)

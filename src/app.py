import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="EduFin Planner",
    page_icon="💰",
    layout="centered",
)

st.title("💰 EduFin Planner")
st.write("Simulador sencillo de ahorro e interés compuesto para educación financiera.")

st.sidebar.header("Parámetros de la simulación")

capital_inicial = st.sidebar.number_input("Capital inicial (€)", min_value=0.0, value=1000.0, step=100.0)
aportacion_mensual = st.sidebar.number_input("Aportación mensual (€)", min_value=0.0, value=100.0, step=10.0)
rentabilidad_anual = st.sidebar.slider("Rentabilidad anual esperada (%)", 0.0, 15.0, 5.0, 0.5)
anos = st.sidebar.slider("Años de inversión", 1, 40, 20)

if st.button("Calcular simulación"):
    meses = anos * 12
    r_mensual = rentabilidad_anual / 100 / 12

    capital = capital_inicial
    data = []

    for m in range(1, meses + 1):
        capital = capital * (1 + r_mensual) + aportacion_mensual
        if m % 12 == 0:
            year = m // 12
            data.append({
                "Año": year,
                "Capital acumulado": round(capital, 2),
            })

    df = pd.DataFrame(data)

    st.subheader("Resultados")
    st.dataframe(df)

    fig = px.line(df, x="Año", y="Capital acumulado", markers=True,
                  title="Evolución del capital con el tiempo")
    st.plotly_chart(fig, use_container_width=True)

    st.info(
        f"Después de **{anos} años**, con una rentabilidad anual del **{rentabilidad_anual}%**, "
        f"el capital acumulado sería de aproximadamente **{df['Capital acumulado'].iloc[-1]:,.2f} €**."
    )
else:
    st.warning("Configura los parámetros en la barra lateral y pulsa **Calcular simulación**.")

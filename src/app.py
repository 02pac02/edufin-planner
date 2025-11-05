import streamlit as st
import pandas as pd
import plotly.express as px

from calculators import (
    Cashflow,
    emergency_fund_months,
    months_to_goal,
    simulate_retirement,
)
from simulations import monte_carlo_retirement
from transactions import (
    load_transactions,
    monthly_summary,
    category_summary,
    income_expense_summary,
)


st.set_page_config(
    page_title="EduFin Planner",
    page_icon="💰",
    layout="wide",
)

st.title("💰 EduFin Planner")
st.markdown(
    "Herramienta práctica de **planificación financiera personal**. "
    "Pensada para uso real por personas o en aulas de Economía."
)

st.sidebar.header("Navegación")
module = st.sidebar.radio(
    "Selecciona módulo",
    ["Resumen financiero", "Fondo de emergencia", "Jubilación", "Transacciones reales"],
)


# --- MÓDULO 1: RESUMEN FINANCIERO -------------------------------------------
def show_cashflow_module():
    st.subheader("📊 Resumen financiero mensual")

    col1, col2 = st.columns(2)

    with col1:
        income = st.number_input(
            "Ingresos netos mensuales (€)",
            min_value=0.0,
            value=2000.0,
            step=100.0,
        )
        fixed_expenses = st.number_input(
            "Gastos fijos (€)",
            min_value=0.0,
            value=900.0,
            step=50.0,
            help="Alquiler/hipoteca, suministros básicos, seguros..."
        )

    with col2:
        variable_expenses = st.number_input(
            "Gastos variables (€)",
            min_value=0.0,
            value=500.0,
            step=50.0,
            help="Comida, transporte, ocio, compras..."
        )
        other_expenses = st.number_input(
            "Otros gastos (€)",
            min_value=0.0,
            value=100.0,
            step=20.0,
        )

    cashflow = Cashflow(
        income=income,
        fixed_expenses=fixed_expenses,
        variable_expenses=variable_expenses,
        other_expenses=other_expenses,
    )

    st.divider()
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.metric(
            "Gastos totales",
            f"{cashflow.total_expenses:,.2f} €".replace(",", "."),
        )
    with col_b:
        st.metric(
            "Ahorro mensual",
            f"{cashflow.savings:,.2f} €".replace(",", "."),
        )
    with col_c:
        savings_rate_pct = cashflow.savings_rate * 100
        st.metric(
            "Tasa de ahorro",
            f"{savings_rate_pct:,.1f} %",
        )

    st.info(
        "Regla orientativa: una tasa de ahorro del **20 % o más** suele considerarse saludable, "
        "dependiendo de objetivos y situación personal."
    )

    labels = ["Gastos totales", "Ahorro"]
    values = [cashflow.total_expenses, max(cashflow.savings, 0)]
    df = pd.DataFrame({"Concepto": labels, "Importe": values})

    fig = px.pie(df, names="Concepto", values="Importe", title="Distribución de tus ingresos")
    st.plotly_chart(fig, use_container_width=True)


# --- MÓDULO 2: FONDO DE EMERGENCIA -----------------------------------------
def show_emergency_module():
    st.subheader("🛟 Fondo de emergencia")

    col1, col2 = st.columns(2)

    with col1:
        income = st.number_input(
            "Ingresos netos mensuales (€)",
            min_value=0.0,
            value=2000.0,
            step=100.0,
            key="income_emergency",
        )
        fixed_expenses = st.number_input(
            "Gastos fijos mensuales (€)",
            min_value=0.0,
            value=900.0,
            step=50.0,
            key="fixed_emergency",
        )

    with col2:
        variable_expenses = st.number_input(
            "Gastos variables mensuales (€)",
            min_value=0.0,
            value=500.0,
            step=50.0,
            key="variable_emergency",
        )
        other_expenses = st.number_input(
            "Otros gastos mensuales (€)",
            min_value=0.0,
            value=100.0,
            step=20.0,
            key="other_emergency",
        )

    emergency_fund = st.number_input(
        "Cantidad actual en tu fondo de emergencia (€)",
        min_value=0.0,
        value=3000.0,
        step=500.0,
    )

    desired_months = st.slider(
        "Meses objetivo de seguridad",
        min_value=1,
        max_value=24,
        value=6,
        help="Número de meses de gastos que te gustaría tener cubiertos."
    )

    cashflow = Cashflow(
        income=income,
        fixed_expenses=fixed_expenses,
        variable_expenses=variable_expenses,
        other_expenses=other_expenses,
    )

    months_covered = emergency_fund_months(cashflow, emergency_fund)

    st.divider()
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric(
            "Meses que cubre tu fondo",
            f"{months_covered:.1f} meses",
        )
    with col_b:
        st.metric(
            "Objetivo",
            f"{desired_months} meses",
        )

    if months_covered < desired_months:
        missing_months = desired_months - months_covered
        st.warning(
            f"Tu fondo de emergencia es algo justo: te faltan aproximadamente "
            f"**{missing_months:.1f} meses** para alcanzar tu objetivo."
        )
    else:
        st.success(
            "¡Buen trabajo! Tu fondo de emergencia cubre tu objetivo de seguridad "
            "o incluso más."
        )


# --- MÓDULO 3: JUBILACIÓN ---------------------------------------------------
def show_retirement_module():
    st.subheader("🏖️ Planificador de jubilación")

    col1, col2, col3 = st.columns(3)

    with col1:
        current_age = st.number_input(
            "Edad actual",
            min_value=18,
            max_value=80,
            value=30,
        )
        retirement_age = st.number_input(
            "Edad de jubilación",
            min_value=current_age + 1,
            max_value=80,
            value=67,
        )

    with col2:
        initial_capital = st.number_input(
            "Capital inicial (€)",
            min_value=0.0,
            value=5000.0,
            step=500.0,
        )
        monthly_contribution = st.number_input(
            "Aportación mensual (€)",
            min_value=0.0,
            value=200.0,
            step=50.0,
        )

    with col3:
        annual_return = st.slider(
            "Rentabilidad anual esperada (%)",
            min_value=0.0,
            max_value=15.0,
            value=5.0,
            step=0.5,
        )
        goal_capital = st.number_input(
            "Objetivo de capital para jubilación (€)",
            min_value=0.0,
            value=300000.0,
            step=10000.0,
        )

    if st.button("Simular jubilación"):
        history = simulate_retirement(
            current_age=current_age,
            retirement_age=retirement_age,
            initial_capital=initial_capital,
            monthly_contribution=monthly_contribution,
            annual_return=annual_return,
        )

        if not history:
            st.error("Revisa los parámetros: no hay periodo entre la edad actual y la de jubilación.")
            return

        df = pd.DataFrame(history)

        st.subheader("Evolución del capital")
        st.dataframe(df)

        fig = px.line(
            df,
            x="Edad",
            y="Capital acumulado",
            markers=True,
            title="Capital acumulado hasta la jubilación",
        )
        st.plotly_chart(fig, use_container_width=True)

        final_capital = df["Capital acumulado"].iloc[-1]
        st.info(
            f"A los **{retirement_age} años**, con estos parámetros, acumularías "
            f"aproximadamente **{final_capital:,.2f} €**."
        )

        months, _ = months_to_goal(
            starting_capital=initial_capital,
            monthly_contribution=monthly_contribution,
            annual_return=annual_return,
            goal_capital=goal_capital,
        )

        if months is None:
            st.warning(
                "Con estas aportaciones y rentabilidad, es posible que no alcances el objetivo "
                "de capital indicado antes de los 80 años."
            )
        else:
            years = months / 12
            st.success(
                f"Con las condiciones actuales, alcanzarías el objetivo de "
                f"**{goal_capital:,.0f} €** en unos **{years:.1f} años**."
            )

        st.divider()
        st.subheader("Simulación Monte Carlo (escenarios aleatorios)")

        run_mc = st.checkbox("Ejecutar simulación Monte Carlo avanzada")

        if run_mc:
            col_mc1, col_mc2 = st.columns(2)
            with col_mc1:
                volatility = st.slider(
                    "Volatilidad anual (desviación estándar, %)",
                    min_value=1.0,
                    max_value=30.0,
                    value=10.0,
                    step=0.5,
                )
            with col_mc2:
                n_sims = st.slider(
                    "Número de simulaciones",
                    min_value=200,
                    max_value=2000,
                    value=500,
                    step=100,
                )

            years_invested = retirement_age - current_age
            mc_df, stats = monte_carlo_retirement(
                initial_capital=initial_capital,
                monthly_contribution=monthly_contribution,
                years=years_invested,
                mean_return=annual_return,
                std_return=volatility,
                n_sims=n_sims,
            )

            st.write("Distribución de capital final en distintos escenarios de mercado:")
            fig_hist = px.histogram(
                mc_df,
                x="final_capital",
                nbins=40,
                title="Distribución de capital final (Monte Carlo)",
            )
            st.plotly_chart(fig_hist, use_container_width=True)

            p10 = stats["10%"]
            p50 = stats["50%"]
            p90 = stats["90%"]

            col_s1, col_s2, col_s3 = st.columns(3)
            col_s1.metric("Escenario pesimista (P10)", f"{p10:,.0f} €")
            col_s2.metric("Escenario medio (P50)", f"{p50:,.0f} €")
            col_s3.metric("Escenario optimista (P90)", f"{p90:,.0f} €")

            st.caption(
                "Los percentiles indican que, en el 10 % de los escenarios el capital final es igual o inferior "
                "al valor P10, y en el 90 % de los escenarios es igual o inferior al valor P90."
            )
    else:
        st.info("Configura los parámetros y pulsa **Simular jubilación**.")


# --- MÓDULO 4: TRANSACCIONES REALES -----------------------------------------
def show_transactions_module():
    st.subheader("📂 Análisis de transacciones reales (CSV)")

    st.markdown(
        "Sube un archivo **CSV** con tus movimientos bancarios o una exportación de gastos. "
        "La aplicación intentará detectar automáticamente las columnas de fecha, importe, descripción y categoría. "
        "Formato recomendado: `date, description, amount, category`."
    )

    uploaded_file = st.file_uploader(
        "Sube tu archivo CSV",
        type=["csv"],
        help="Por seguridad, el archivo solo se procesa en tu navegador / sesión actual.",
    )

    if not uploaded_file:
        st.info("Aún no has subido ningún archivo. Prueba con un CSV de ejemplo de tus gastos.")
        return

    try:
        df = load_transactions(uploaded_file)
    except Exception as e:
        st.error(
            "No se ha podido leer el archivo. Revisa que tenga al menos columnas de **fecha** e **importe**.\n\n"
            f"Detalle técnico: {e}"
        )
        return

    st.success(f"Archivo cargado correctamente. Filas: {len(df)}")
    with st.expander("Ver primeras filas del archivo"):
        st.dataframe(df.head(20))

    income, expenses, net = income_expense_summary(df)

    col1, col2, col3 = st.columns(3)
    col1.metric("Ingresos totales", f"{income:,.2f} €")
    col2.metric("Gastos totales", f"{expenses:,.2f} €")
    col3.metric("Saldo neto", f"{net:,.2f} €")

    st.divider()
    st.subheader("Evolución mensual")

    monthly = monthly_summary(df)
    fig_month = px.bar(
        monthly,
        x="month",
        y="net_amount",
        title="Saldo neto por mes",
    )
    st.plotly_chart(fig_month, use_container_width=True)

    st.subheader("Gastos por categoría")
    categories = category_summary(df)
    fig_cat = px.bar(
        categories,
        x="total",
        y="category",
        orientation="h",
        title="Importe total por categoría",
    )
    st.plotly_chart(fig_cat, use_container_width=True)


# --- ROUTER DE MÓDULOS ------------------------------------------------------
if module == "Resumen financiero":
    show_cashflow_module()
elif module == "Fondo de emergencia":
    show_emergency_module()
elif module == "Jubilación":
    show_retirement_module()
else:
    show_transactions_module()

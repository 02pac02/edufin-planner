import numpy as np
import pandas as pd


def monte_carlo_retirement(
    initial_capital: float,
    monthly_contribution: float,
    years: int,
    mean_return: float,
    std_return: float,
    n_sims: int = 500,
):
    """
    Simula distintos escenarios de mercado para un plan de jubilación usando Monte Carlo.

    mean_return y std_return están en porcentaje anual (por ejemplo 5.0 y 10.0).
    Devuelve:
      - DataFrame con el capital final de cada simulación.
      - Serie con estadísticas descriptivas (incluyendo percentiles).
    """
    if years <= 0 or n_sims <= 0:
        raise ValueError("Los años y el número de simulaciones deben ser positivos.")

    months = years * 12

    mu_annual = mean_return / 100.0
    sigma_annual = std_return / 100.0

    # Pasamos a parámetros mensuales
    mu_monthly = mu_annual / 12.0
    sigma_monthly = sigma_annual / np.sqrt(12.0)

    final_capitals = []

    for _ in range(n_sims):
        monthly_returns = np.random.normal(mu_monthly, sigma_monthly, months)
        capital = initial_capital
        for r in monthly_returns:
            capital = capital * (1 + r) + monthly_contribution
        final_capitals.append(capital)

    df = pd.DataFrame({"final_capital": final_capitals})
    stats = df["final_capital"].describe(percentiles=[0.1, 0.25, 0.5, 0.75, 0.9])

    return df, stats

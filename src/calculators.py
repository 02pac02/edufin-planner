from dataclasses import dataclass


@dataclass
class Cashflow:
    income: float                # ingresos mensuales netos
    fixed_expenses: float        # alquiler, hipoteca, luz, etc.
    variable_expenses: float     # comida, ocio, transporte variable...
    other_expenses: float = 0.0  # otros

    @property
    def total_expenses(self) -> float:
        return (
            self.fixed_expenses
            + self.variable_expenses
            + self.other_expenses
        )

    @property
    def savings(self) -> float:
        return self.income - self.total_expenses

    @property
    def savings_rate(self) -> float:
        if self.income <= 0:
            return 0.0
        return self.savings / self.income


def emergency_fund_months(cashflow: Cashflow, emergency_fund: float) -> float:
    """
    Devuelve cuántos meses de gastos cubre el fondo de emergencia.
    """
    monthly_expenses = cashflow.total_expenses
    if monthly_expenses <= 0:
        return 0.0
    return emergency_fund / monthly_expenses


def months_to_goal(
    starting_capital: float,
    monthly_contribution: float,
    annual_return: float,
    goal_capital: float,
    max_years: int = 80,
):
    """
    Calcula cuántos meses se tarda en alcanzar un objetivo de capital
    con aportaciones periódicas y rentabilidad compuesta.
    """
    if goal_capital <= starting_capital:
        return 0, starting_capital

    if monthly_contribution <= 0 and annual_return <= 0:
        return None, starting_capital  # imposible llegar

    r = annual_return / 100 / 12
    capital = starting_capital
    months = 0
    max_months = max_years * 12

    while capital < goal_capital and months < max_months:
        capital = capital * (1 + r) + monthly_contribution
        months += 1

    if capital < goal_capital:
        return None, capital

    return months, capital


def simulate_retirement(
    current_age: int,
    retirement_age: int,
    initial_capital: float,
    monthly_contribution: float,
    annual_return: float,
):
    """
    Simula año a año el capital acumulado hasta la jubilación.
    Devuelve una lista de dicts para usar con pandas/DataFrame.
    """
    years = max(retirement_age - current_age, 0)
    months = years * 12
    r = annual_return / 100 / 12

    capital = initial_capital
    history = []

    for m in range(1, months + 1):
        capital = capital * (1 + r) + monthly_contribution
        if m % 12 == 0:
            year = m // 12
            age = current_age + year
            history.append(
                {
                    "Año": year,
                    "Edad": age,
                    "Capital acumulado": round(capital, 2),
                }
            )

    return history

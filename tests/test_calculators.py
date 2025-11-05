import os
import sys

# Añadimos la carpeta src/ al path para que se pueda hacer "from calculators import ..."
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
sys.path.insert(0, SRC_DIR)

from calculators import Cashflow, emergency_fund_months


def test_cashflow_savings_and_rate():
    c = Cashflow(
        income=2000,
        fixed_expenses=900,
        variable_expenses=500,
        other_expenses=100,
    )
    assert c.total_expenses == 1500
    assert c.savings == 500
    assert round(c.savings_rate, 2) == 0.25  # 25 %


def test_emergency_fund_months():
    c = Cashflow(
        income=2000,
        fixed_expenses=1000,
        variable_expenses=500,
        other_expenses=0,
    )
    months = emergency_fund_months(c, emergency_fund=4500)
    assert round(months, 1) == 3.0

import pandas as pd


def load_transactions(file) -> pd.DataFrame:
    """
    Carga un CSV de transacciones e intenta normalizar las columnas.
    Acepta nombres típicos en inglés o español para fecha, importe, descripción y categoría.
    """
    # sep=None + engine="python" intenta adivinar el separador (coma, punto y coma...)
    df = pd.read_csv(file, sep=None, engine="python")
    df.columns = [c.strip().lower() for c in df.columns]

    col_map = {}

    for c in df.columns:
        if "date" in c or "fecha" in c:
            col_map.setdefault("date", c)
        elif "amount" in c or "importe" in c or "cantidad" in c:
            col_map.setdefault("amount", c)
        elif "desc" in c or "concept" in c or "concepto" in c:
            col_map.setdefault("description", c)
        elif "category" in c or "tipo" in c:
            col_map.setdefault("category", c)

    missing = {"date", "amount"} - col_map.keys()
    if missing:
        raise ValueError(
            f"Faltan columnas obligatorias en el CSV: {', '.join(sorted(missing))}."
        )

    df = df.rename(columns={v: k for k, v in col_map.items()})

    # Parseo de fechas (acepta formatos DD/MM/YYYY, YYYY-MM-DD, etc.)
    df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["date"])

    # Normalizamos el importe (quitamos €, comas, espacios…)
    df["amount"] = (
        df["amount"]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .str.replace("€", "", regex=False)
        .str.replace(" ", "", regex=False)
        .astype(float)
    )

    if "description" not in df.columns:
        df["description"] = ""

    if "category" not in df.columns:
        df["category"] = "Sin categoría"

    return df


def monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()
    result = (
        df.groupby("month")["amount"]
        .sum()
        .reset_index()
        .rename(columns={"amount": "net_amount"})
        .sort_values("month")
    )
    return result


def category_summary(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    result = (
        df.groupby("category")["amount"]
        .sum()
        .reset_index()
        .rename(columns={"amount": "total"})
        .sort_values("total", ascending=True)
    )
    return result


def income_expense_summary(df: pd.DataFrame):
    """
    Devuelve (ingresos_totales, gastos_totales, saldo_neto).
    Asume importes positivos para ingresos y negativos para gastos,
    típica estructura de extracto bancario.
    """
    income = df.loc[df["amount"] > 0, "amount"].sum()
    expenses = df.loc[df["amount"] < 0, "amount"].sum()
    net = income + expenses
    return income, expenses, net

from src.profiler import (
    get_constant_columns,
    get_missing_by_column,
    get_outliers_summary,
    get_high_correlations,
)


def classify_score(score: int) -> str:
    if score >= 90:
        return "Excelente"
    if score >= 75:
        return "Boa"
    if score >= 50:
        return "Regular"
    return "Crítica"


def calculate_health_score(df) -> dict:
    score = 100
    penalties = []

    missing_df = get_missing_by_column(df)
    if not missing_df.empty and missing_df["missing_percent"].max() > 20:
        score -= 10
        penalties.append("Há coluna(s) com mais de 20% de valores ausentes (-10).")

    duplicate_percent = round((df.duplicated().sum() / len(df)) * 100, 2) if len(df) > 0 else 0
    if duplicate_percent > 5:
        score -= 10
        penalties.append("Há mais de 5% de linhas duplicadas (-10).")

    constant_columns = get_constant_columns(df)
    if constant_columns:
        penalty = min(len(constant_columns) * 5, 20)
        score -= penalty
        penalties.append(f"Existem {len(constant_columns)} coluna(s) constante(s) (-{penalty}).")

    outliers_df = get_outliers_summary(df)
    severe_outlier_cols = outliers_df[outliers_df["outlier_percent"] > 10]
    if not severe_outlier_cols.empty:
        penalty = min(len(severe_outlier_cols) * 5, 15)
        score -= penalty
        penalties.append(f"Há colunas com excesso de outliers (-{penalty}).")

    high_corr_df = get_high_correlations(df, threshold=0.95)
    if not high_corr_df.empty:
        score -= 5
        penalties.append("Há variáveis com correlação muito alta (-5).")

    score = max(score, 0)

    return {
        "score": score,
        "classification": classify_score(score),
        "penalties": penalties
    }
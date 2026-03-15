from src.profiler import (
    get_constant_columns,
    get_missing_by_column,
    get_outliers_summary,
    get_high_correlations,
)


def generate_alerts(df):
    alerts = []

    missing_df = get_missing_by_column(df)
    for _, row in missing_df.iterrows():
        if row["missing_percent"] > 20:
            alerts.append(
                f"A coluna '{row['column']}' tem {row['missing_percent']}% de valores ausentes."
            )

    duplicate_count = int(df.duplicated().sum())
    duplicate_percent = round((duplicate_count / len(df)) * 100, 2) if len(df) > 0 else 0
    if duplicate_percent > 5:
        alerts.append(
            f"O dataset possui {duplicate_percent}% de linhas duplicadas."
        )

    constant_columns = get_constant_columns(df)
    for col in constant_columns:
        alerts.append(f"A coluna '{col}' é constante e pode não agregar valor analítico.")

    outliers_df = get_outliers_summary(df)
    for _, row in outliers_df.iterrows():
        if row["outlier_percent"] > 10:
            alerts.append(
                f"A coluna '{row['column']}' possui {row['outlier_percent']}% de outliers pelo critério IQR."
            )

    high_corr_df = get_high_correlations(df, threshold=0.95)
    for _, row in high_corr_df.iterrows():
        alerts.append(
            f"As colunas '{row['feature_1']}' e '{row['feature_2']}' têm correlação alta ({row['correlation']})."
        )

    return alerts
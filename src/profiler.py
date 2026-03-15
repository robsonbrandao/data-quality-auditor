import numpy as np
import pandas as pd


def get_dataset_summary(df: pd.DataFrame) -> dict:
    total_missing = int(df.isnull().sum().sum())
    total_cells = int(df.shape[0] * df.shape[1]) if df.shape[0] > 0 and df.shape[1] > 0 else 0
    missing_percent = round((total_missing / total_cells) * 100, 2) if total_cells > 0 else 0

    return {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "duplicates": int(df.duplicated().sum()),
        "duplicates_percent": round((df.duplicated().sum() / len(df)) * 100, 2) if len(df) > 0 else 0,
        "total_missing": total_missing,
        "total_missing_percent": missing_percent,
    }


def get_column_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = pd.DataFrame({
        "column": df.columns,
        "dtype": df.dtypes.astype(str),
        "missing_values": df.isnull().sum().values,
        "missing_percent": ((df.isnull().sum() / len(df)) * 100).round(2).values if len(df) > 0 else 0,
        "unique_values": df.nunique(dropna=False).values,
        "sample_value": [df[col].dropna().iloc[0] if df[col].dropna().shape[0] > 0 else None for col in df.columns]
    })
    return summary


def get_missing_by_column(df: pd.DataFrame) -> pd.DataFrame:
    missing = df.isnull().sum().sort_values(ascending=False)
    missing_percent = ((missing / len(df)) * 100).round(2) if len(df) > 0 else missing * 0

    return pd.DataFrame({
        "column": missing.index,
        "missing_count": missing.values,
        "missing_percent": missing_percent.values
    })


def get_constant_columns(df: pd.DataFrame) -> list:
    return [col for col in df.columns if df[col].nunique(dropna=False) <= 1]


def get_cardinality(df: pd.DataFrame) -> pd.DataFrame:
    cardinality = df.nunique(dropna=False).sort_values(ascending=False)
    return pd.DataFrame({
        "column": cardinality.index,
        "unique_values": cardinality.values
    })


def detect_outliers_iqr(series: pd.Series) -> int:
    clean_series = series.dropna()
    if clean_series.empty:
        return 0

    q1 = clean_series.quantile(0.25)
    q3 = clean_series.quantile(0.75)
    iqr = q3 - q1

    if iqr == 0:
        return 0

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    return int(((clean_series < lower) | (clean_series > upper)).sum())


def get_outliers_summary(df: pd.DataFrame) -> pd.DataFrame:
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

    records = []
    for col in numeric_cols:
        outlier_count = detect_outliers_iqr(df[col])
        outlier_percent = round((outlier_count / len(df)) * 100, 2) if len(df) > 0 else 0
        records.append({
            "column": col,
            "outlier_count": outlier_count,
            "outlier_percent": outlier_percent
        })

    return pd.DataFrame(records).sort_values(by="outlier_count", ascending=False)


def get_correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    numeric_df = df.select_dtypes(include=np.number)
    if numeric_df.shape[1] < 2:
        return pd.DataFrame()
    return numeric_df.corr()


def get_high_correlations(df: pd.DataFrame, threshold: float = 0.9) -> pd.DataFrame:
    corr_matrix = get_correlation_matrix(df)
    if corr_matrix.empty:
        return pd.DataFrame(columns=["feature_1", "feature_2", "correlation"])

    results = []
    cols = corr_matrix.columns

    for i in range(len(cols)):
        for j in range(i):
            corr_value = corr_matrix.iloc[i, j]
            if abs(corr_value) >= threshold:
                results.append({
                    "feature_1": cols[i],
                    "feature_2": cols[j],
                    "correlation": round(corr_value, 4)
                })

    return pd.DataFrame(results).sort_values(by="correlation", ascending=False, key=lambda s: s.abs())
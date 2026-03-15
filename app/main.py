import os
import sys

import plotly.express as px
import plotly.figure_factory as ff
import streamlit as st

# Permite importar a pasta src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.loader import load_csv
from src.profiler import (
    get_dataset_summary,
    get_column_summary,
    get_missing_by_column,
    get_constant_columns,
    get_cardinality,
    get_outliers_summary,
    get_correlation_matrix,
    get_high_correlations,
)
from src.scorer import calculate_health_score
from src.validators import generate_alerts


st.set_page_config(page_title="Data Quality Auditor", layout="wide")

st.title("Data Quality Auditor")
st.caption("Auditoria exploratória da qualidade de datasets tabulares em CSV.")

uploaded_file = st.file_uploader("Faça upload de um arquivo CSV", type=["csv"])

if uploaded_file is not None:
    df = load_csv(uploaded_file)

    st.success("Arquivo carregado com sucesso.")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Overview", "Missing Values", "Data Issues", "Numeric Analysis", "Score"]
    )

    with tab1:
        st.subheader("Visão geral do dataset")

        summary = get_dataset_summary(df)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Linhas", summary["rows"])
        col2.metric("Colunas", summary["columns"])
        col3.metric("Duplicatas", summary["duplicates"])
        col4.metric("Missing (%)", summary["total_missing_percent"])

        st.markdown("### Preview")
        st.dataframe(df.head(20), use_container_width=True)

        st.markdown("### Resumo por coluna")
        column_summary = get_column_summary(df)
        st.dataframe(column_summary, use_container_width=True)

    with tab2:
        st.subheader("Valores ausentes")

        missing_df = get_missing_by_column(df)
        st.dataframe(missing_df, use_container_width=True)

        filtered_missing = missing_df[missing_df["missing_count"] > 0]
        if not filtered_missing.empty:
            fig = px.bar(
                filtered_missing,
                x="column",
                y="missing_percent",
                title="Percentual de missing values por coluna"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Não há valores ausentes no dataset.")

    with tab3:
        st.subheader("Problemas estruturais")

        constant_columns = get_constant_columns(df)
        cardinality_df = get_cardinality(df)
        high_corr_df = get_high_correlations(df, threshold=0.95)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### Colunas constantes")
            if constant_columns:
                st.write(constant_columns)
            else:
                st.success("Nenhuma coluna constante encontrada.")

        with c2:
            st.markdown("### Linhas duplicadas")
            duplicate_count = int(df.duplicated().sum())
            duplicate_percent = round((duplicate_count / len(df)) * 100, 2) if len(df) > 0 else 0
            st.write(f"Quantidade: {duplicate_count}")
            st.write(f"Percentual: {duplicate_percent}%")

        st.markdown("### Cardinalidade")
        st.dataframe(cardinality_df, use_container_width=True)

        st.markdown("### Correlações altas")
        if not high_corr_df.empty:
            st.dataframe(high_corr_df, use_container_width=True)
        else:
            st.info("Não foram encontradas correlações acima do limiar definido.")

        st.markdown("### Alertas automáticos")
        alerts = generate_alerts(df)
        if alerts:
            for alert in alerts:
                st.warning(alert)
        else:
            st.success("Nenhum alerta crítico encontrado.")

    with tab4:
        st.subheader("Análise numérica")

        outliers_df = get_outliers_summary(df)
        if not outliers_df.empty:
            st.markdown("### Outliers por coluna")
            st.dataframe(outliers_df, use_container_width=True)

            fig_outliers = px.bar(
                outliers_df,
                x="column",
                y="outlier_percent",
                title="Percentual de outliers por coluna"
            )
            st.plotly_chart(fig_outliers, use_container_width=True)
        else:
            st.info("O dataset não possui colunas numéricas suficientes para análise de outliers.")

        corr_matrix = get_correlation_matrix(df)
        if not corr_matrix.empty:
            st.markdown("### Matriz de correlação")
            fig_corr = ff.create_annotated_heatmap(
                z=corr_matrix.round(2).values,
                x=list(corr_matrix.columns),
                y=list(corr_matrix.index),
                annotation_text=corr_matrix.round(2).values,
                showscale=True
            )
            st.plotly_chart(fig_corr, use_container_width=True)
        else:
            st.info("Não há colunas numéricas suficientes para calcular correlação.")

    with tab5:
        st.subheader("Dataset Health Score")

        score_result = calculate_health_score(df)

        s1, s2 = st.columns(2)
        with s1:
            st.metric("Score final", score_result["score"])
        with s2:
            st.metric("Classificação", score_result["classification"])

        st.markdown("### Penalidades aplicadas")
        if score_result["penalties"]:
            for penalty in score_result["penalties"]:
                st.write(f"- {penalty}")
        else:
            st.success("Nenhuma penalidade aplicada. Dataset muito saudável.")

else:
    st.info("Envie um arquivo CSV para iniciar a auditoria.")
import pandas as pd


def load_csv(uploaded_file):
    """
    Carrega um arquivo CSV enviado pelo Streamlit.
    Tenta primeiro UTF-8 e depois latin1.
    """
    try:
        df = pd.read_csv(uploaded_file)
    except UnicodeDecodeError:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, encoding="latin1")
    return df
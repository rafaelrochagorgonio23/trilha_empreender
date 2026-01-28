# dashboard.py
import streamlit as st
import pandas as pd
from persistencia import fetch_events

def _carregar_eventos_df(db) -> pd.DataFrame:
    docs = fetch_events(db)
    if not docs:
        return pd.DataFrame(columns=["ts","event","user_id","session_id","props","app_version","runtime","python"])
    df = pd.DataFrame(docs)
    df["ts"] = pd.to_datetime(df["ts"], utc=True, errors="coerce")
    return df

def show_dashboard(db):
    st.header("Dashboard de Uso")
    df = _carregar_eventos_df(db)

    if df.empty:
        st.info("Ainda não há eventos registrados.")
        return

    col1, col2 = st.columns(2)
    with col1:
        eventos_unicos = sorted(df["event"].dropna().unique().tolist())
        sel_eventos = st.multiselect("Filtrar por evento", eventos_unicos, default=eventos_unicos)
    with col2:
        min_ts, max_ts = df["ts"].min(), df["ts"].max()
        intervalo = st.slider("Intervalo de datas",
                              min_value=min_ts.to_pydatetime(),
                              max_value=max_ts.to_pydatetime(),
                              value=(min_ts.to_pydatetime(), max_ts.to_pydatetime()))
    df_f = df[df["event"].isin(sel_eventos)]
    df_f = df_f[(df_f["ts"] >= pd.to_datetime(intervalo[0], utc=True)) &
                (df_f["ts"] <= pd.to_datetime(intervalo[1], utc=True))]

    c1, c2, c3 = st.columns(3)
    c1.metric("Eventos", len(df_f))
    c2.metric("Usuários únicos", df_f["user_id"].nunique())
    c3.metric("Page Views", (df_f["event"] == "page_view").sum())

    st.subheader("Eventos por dia")
    por_dia = df_f.set_index("ts").resample("D").size()
    st.line_chart(por_dia, height=220)

    st.subheader("Top eventos")
    st.bar_chart(df_f["event"].value_counts(), height=220)

    st.subheader("Explorar eventos")
    st.dataframe(df_f.sort_values("ts", ascending=False), use_container_width=True)

# analytics.py
import streamlit as st
from datetime import datetime, timezone
from uuid import uuid4
import platform
from persistencia import insert_event

def get_session_user_id():
    if "user_id" not in st.session_state:
        st.session_state.user_id = str(uuid4())
    return st.session_state.user_id

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def _get_query_params():
    # Funciona em versões novas e antigas do Streamlit
    try:
        return dict(st.query_params)        # Streamlit >= 1.31
    except Exception:
        try:
            return dict(st.experimental_get_query_params())
        except Exception:
            return {}

def log_event(db, name: str, props: dict | None = None):
    user_id = get_session_user_id()
    event = {
        "ts": now_iso(),
        "event": name,
        "user_id": user_id,
        "session_id": st.session_state.get("session_id", user_id),
        "props": props or {},
        "app_version": "v0.1.0",
        "runtime": "streamlit",
        "python": platform.python_version(),
    }
    insert_event(db, event)

def on_app_load(db):
    utm = _get_query_params()  # utm_source, utm_medium, etc., se houver
    log_event(db, "page_view", {"path": "/", "utm": utm})

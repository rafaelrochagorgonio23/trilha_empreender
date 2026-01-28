# persistencia.py
from pathlib import Path
from threading import RLock
from tinydb import TinyDB

DB_DIR = Path("dados")
DB_DIR.mkdir(exist_ok=True)
DB_FILE = DB_DIR / "eventos.json"

_lock = RLock()

def get_db():
    """Instância única de TinyDB para este app."""
    return TinyDB(DB_FILE)

def insert_event(db, event: dict):
    """Insere um evento com lock para evitar condição de corrida entre sessões."""
    with _lock:
        db.table("eventos").insert(event)

def fetch_events(db):
    with _lock:
        return db.table("eventos").all()

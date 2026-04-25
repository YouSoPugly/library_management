"""
setup.py

Jupyter-only helper module for MySQL.

- Creates database connection (SQLAlchemy)
- Provides:
    run_query(query)
    show_query(query)
    %%sqlshow (cell magic)
- Displays results using ITables

NOTE:
Use this only inside Jupyter Notebook.
"""

import os
import warnings
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SAWarning
from IPython import get_ipython
from itables import init_notebook_mode, show, options

__all__ = ["run_query", "show_query"]


options.maxBytes = 1_000_000  # set to 1MB
warnings.filterwarnings("ignore", category=SAWarning)

ENGINE = None


def _init_engine():
    url = (
        f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@"
        f"{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DATABASE')}"
    )
    engine = create_engine(url)
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return engine


def run_query(query: str):
    if ENGINE is None:
        raise RuntimeError("Database not connected.")
    with ENGINE.connect() as conn:
        return pd.read_sql(text(query), conn)


def show_query(query: str):
    df = run_query(query)
    show(df, pageLength=10)


def _sqlshow(line, cell):
    return show_query(cell)


def _register_magic():
    ip = get_ipython()
    if ip:
        ip.register_magic_function(_sqlshow, "cell", "sqlshow")


def _inject_globals():
    ip = get_ipython()
    if ip:
        ip.user_ns["run_query"] = run_query
        ip.user_ns["show_query"] = show_query


# Initialization
try:
    ENGINE = _init_engine()
    init_notebook_mode(all_interactive=True)
    _register_magic()
    _inject_globals()

    print(
        f"[OK] Connected | DB={os.getenv('MYSQL_DATABASE')} "
        f"| User={os.getenv('MYSQL_USER')} "
        f"| Host={os.getenv('MYSQL_HOST')}\n"
        "Functions: run_query(), show_query(), %%sqlshow"
    )

except Exception as e:
    ENGINE = None
    print(f"[ERROR] Connection failed: {e}")
    raise
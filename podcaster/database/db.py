import sqlite3

from flask import g, current_app


def init_app(app):
    # Registra la funzione `close_db` per essere chiamata
    # quando il contesto dell'applicazione viene rimosso.
    # Questo garantisce che il database venga sempre chiuso
    # alla fine di una richiesta.
    # https://flask.palletsprojects.com/en/2.2.x/appcontext/#storing-data
    app.teardown_appcontext(close_db)


def get_connection() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            # Fa in modo che ritorni le row di tipo TIMESTAMP come oggetti datetime
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row

        # Necessario per attivare il supporto alle FOREIGN KEY.
        # Se non viene eseguito, SQLite ignora tutte le FOREIGN KEY nel database.
        g.db.execute("PRAGMA foreign_keys = 1;")

    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

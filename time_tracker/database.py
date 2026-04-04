from contextlib import contextmanager
from pathlib import Path

import sqlite3
import time

from .resources import default_db_path


class DBManager:
    def __init__(self, db_path: str | Path | None = None):
        self.db_path = self._resolve_db_path(db_path)
        self.schema_path = Path(__file__).resolve().parent / "schema.sql"
        self._init_db()

    def _resolve_db_path(self, db_path: str | Path | None) -> Path:
        if db_path is None:
            return default_db_path()

        path = Path(db_path).expanduser()
        if path.is_absolute():
            return path

        return Path.cwd() / path

    def _init_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.schema_path.exists():
            raise FileNotFoundError(f"Missing schema file: {self.schema_path}")

        if not self.db_path.exists():
            schema = self.schema_path.read_text(encoding="utf-8")
            with sqlite3.connect(self.db_path) as conn:
                conn.executescript(schema)

    @contextmanager
    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_clients(self):
        with self._get_conn() as conn:
            return [
                dict(row) for row in conn.execute("SELECT * FROM clients").fetchall()
            ]

    def add_client(self, name, tag):
        try:
            with self._get_conn() as conn:
                cursor = conn.execute(
                    "INSERT INTO clients (name, tag) VALUES (?, ?)", (name, tag)
                )
                client_id = cursor.lastrowid
                conn.execute("INSERT INTO timers (client_id) VALUES (?)", (client_id,))
                return client_id
        except sqlite3.IntegrityError:
            return None

    def get_timers(self):
        query = """
        SELECT t.*, c.name as client_name, c.tag as client_tag 
        FROM timers t
        JOIN clients c ON t.client_id = c.id
        """
        with self._get_conn() as conn:
            return [dict(row) for row in conn.execute(query).fetchall()]

    def start_timer(self, timer_id):
        now = time.time()
        with self._get_conn() as conn:
            conn.execute(
                "UPDATE timers SET start_timestamp = ? WHERE id = ?", (now, timer_id)
            )

    def stop_timer(self, timer_id):
        now = time.time()
        with self._get_conn() as conn:
            timer = conn.execute(
                "SELECT * FROM timers WHERE id = ?", (timer_id,)
            ).fetchone()
            if timer and timer["start_timestamp"]:
                delta = now - timer["start_timestamp"]
                new_total = (timer["accumulated_seconds"] or 0) + delta
                conn.execute(
                    "UPDATE timers SET start_timestamp = NULL, accumulated_seconds = ? WHERE id = ?",
                    (new_total, timer_id),
                )
                return delta
        return 0

    def reset_timer(self, timer_id):
        with self._get_conn() as conn:
            conn.execute(
                "UPDATE timers SET start_timestamp = NULL, accumulated_seconds = 0 WHERE id = ?",
                (timer_id,),
            )

    def log_time(self, client_id, duration_minutes, entry_type="self"):
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO logs (client_id, duration_minutes, entry_type) VALUES (?, ?, ?)",
                (client_id, duration_minutes, entry_type),
            )

    def get_total_minutes(self, client_id):
        with self._get_conn() as conn:
            # Current session minutes + logged minutes
            timer = conn.execute(
                "SELECT start_timestamp, accumulated_seconds FROM timers WHERE client_id = ?",
                (client_id,),
            ).fetchone()
            logs_sum = (
                conn.execute(
                    "SELECT SUM(duration_minutes) FROM logs WHERE client_id = ?",
                    (client_id,),
                ).fetchone()[0]
                or 0
            )

            acc_sec = timer["accumulated_seconds"] if timer else 0
            if timer and timer["start_timestamp"]:
                acc_sec += time.time() - timer["start_timestamp"]

            return (acc_sec / 60.0) + logs_sum

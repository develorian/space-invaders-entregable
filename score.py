import sqlite3
import threading
import time


class Puntajes:
    """Manejador simple de puntajes usando SQLite local.

    Campos: name, kills, play_time, level, score, ts
    """
    def __init__(self, db_path='scores.db'):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._ensure_table()

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def _ensure_table(self):
        with self._lock:
            conn = self._get_conn()
            try:
                cur = conn.cursor()
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS scores (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        kills INTEGER,
                        play_time REAL,
                        level INTEGER,
                        score INTEGER,
                        ts REAL
                    )
                    """
                )
                conn.commit()
            finally:
                conn.close()

    def add_score(self, name, kills, play_time, level, score):
        ts = time.time()
        with self._lock:
            conn = self._get_conn()
            try:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO scores (name, kills, play_time, level, score, ts) VALUES (?, ?, ?, ?, ?, ?)",
                    (name, int(kills), float(play_time), int(level), int(score), float(ts)),
                )
                conn.commit()
            finally:
                conn.close()

    def get_last_scores(self, limit=10):
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT name, kills, play_time, level, score, ts FROM scores ORDER BY ts DESC LIMIT ?", (limit,))
            rows = cur.fetchall()
            return rows
        finally:
            conn.close()

    def get_all_scores(self):
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT name, kills, play_time, level, score, ts FROM scores ORDER BY ts DESC")
            return cur.fetchall()
        finally:
            conn.close()

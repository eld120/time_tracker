import os
import pytest
import time
from time_tracker.database import DBManager


@pytest.fixture
def db():
    # Use a temporary database for testing
    test_db = "test_storage.db"
    if os.path.exists(test_db):
        os.remove(test_db)

    # Initialize with schema
    import sqlite3
    from pathlib import Path

    schema_path = Path(__file__).resolve().parent.parent / "time_tracker" / "schema.sql"
    conn = sqlite3.connect(test_db)
    with open(schema_path, "r") as f:
        conn.executescript(f.read())
    conn.close()

    manager = DBManager(db_path=test_db)
    yield manager

    # Cleanup
    if os.path.exists(test_db):
        os.remove(test_db)


def test_add_client(db):
    client_id = db.add_client("Test Client", "TC-01")
    assert client_id is not None
    clients = db.get_clients()
    assert len(clients) == 1
    assert clients[0]["name"] == "Test Client"

    # Check if timer was created
    timers = db.get_timers()
    assert len(timers) == 1
    assert timers[0]["client_id"] == client_id


def test_timer_logic(db, monkeypatch):
    client_id = db.add_client("Test Client", "TC-01")
    timers = db.get_timers()
    timer_id = timers[0]["id"]

    # Start timer at t=100
    current_time = 100.0
    monkeypatch.setattr(time, "time", lambda: current_time)
    db.start_timer(timer_id)

    # Check total minutes after 60 seconds (t=160)
    current_time = 160.0
    assert db.get_total_minutes(client_id) == 1.0

    # Stop timer at t=220 (2 minutes total)
    current_time = 220.0
    db.stop_timer(timer_id)

    # Check total minutes (should be 2.0)
    assert db.get_total_minutes(client_id) == 2.0

    # Start again at t=300
    current_time = 300.0
    db.start_timer(timer_id)

    # Check at t=360 (2 mins from before + 1 min new = 3 mins)
    current_time = 360.0
    assert db.get_total_minutes(client_id) == 3.0


def test_log_time(db):
    client_id = db.add_client("Test Client", "TC-01")
    db.log_time(client_id, 15.5, "subcontractor")

    # Check total minutes
    assert db.get_total_minutes(client_id) == 15.5

    # Add more logs
    db.log_time(client_id, 10.0, "self")
    assert db.get_total_minutes(client_id) == 25.5


def test_reset_timer(db, monkeypatch):
    client_id = db.add_client("Test Client", "TC-01")
    timers = db.get_timers()
    timer_id = timers[0]["id"]

    current_time = 100.0
    monkeypatch.setattr(time, "time", lambda: current_time)
    db.start_timer(timer_id)

    current_time = 160.0
    db.stop_timer(timer_id)
    assert db.get_total_minutes(client_id) == 1.0

    db.reset_timer(timer_id)
    assert db.get_total_minutes(client_id) == 0.0

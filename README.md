# Time Tracker

Minimal multi-client time tracking with a local SQLite database and a CustomTkinter UI.

## Quickstart

From the repo root:

```bash
uv sync
uv run app.py
```

That is the main supported launch path.

You can also run:

```bash
uv run python app.py
uv run python -m time_tracker
```

## Desktop Shortcut

- macOS: create an alias or small shell script that runs `uv run app.py` from `/Users/hub/Sandbox/time_tracker`
- Windows: create a shortcut or `.bat` file that runs `uv run app.py` from the repo root

## Icon Files

- `assets/icon.png` is used for the app window and macOS dock icon
- `assets/icon.ico` is used for the Windows window/taskbar icon when available
- regenerate them with `uv run python scripts/generate_icon.py`

## Dev Commands

```bash
uv run pytest
uv run ruff check .
uv run ty check time_tracker tests app.py scripts
```

## Notes

- timer state is stored in `storage.db`
- totals are tracked from timestamps plus accumulated seconds to avoid drift
- subcontractor minutes are added manually through the UI

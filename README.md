# Time Tracker

Minimal multi-client time tracking with a local SQLite database and a CustomTkinter UI.

Basically, I was really tired of a bug within the Mac time app and I needed a way to track more than one client at a time as I might bounce between client tasks on any given day.

## Quickstart

From the repo root:

```bash
uv sync
uv run time_tracker
```

or:

```bash
uv run app.py
```

## Desktop Shortcut

- macOS: create an alias or small shell script that runs `uv run time_tracker` from the repo root
- Windows: create a shortcut or `.bat` file that runs `uv run time_tracker` from the repo root

## Build Executables

Build on each target platform with PyInstaller. The build script bundles the app assets and schema, uses a single-file executable on Windows, and a normal app bundle on macOS.

```bash
uv run python scripts/build_executable.py
```

Outputs are written to `dist/`.

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

- timer state is stored in your user data directory as `storage.db`
- set `TIME_TRACKER_DATA_DIR` if you want to override that location
- totals are tracked from timestamps plus accumulated seconds to avoid drift
- subcontractor minutes are added manually through the UI

from __future__ import annotations

import os
import sys
from pathlib import Path


DATA_DIR_NAME = "time_tracker"


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def bundle_root() -> Path:
    if getattr(sys, "frozen", False):
        bundle_dir = getattr(sys, "_MEIPASS", None)
        if bundle_dir:
            return Path(bundle_dir)
        return Path(sys.executable).resolve().parent

    return project_root()


def resource_path(*parts: str) -> Path:
    return bundle_root().joinpath(*parts)


def user_data_dir() -> Path:
    override = os.environ.get("TIME_TRACKER_DATA_DIR")
    if override:
        return Path(override).expanduser()

    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA")
        base_dir = Path(appdata).expanduser() if appdata else Path.home() / "AppData" / "Roaming"
    elif sys.platform == "darwin":
        base_dir = Path.home() / "Library" / "Application Support"
    else:
        xdg_data_home = os.environ.get("XDG_DATA_HOME")
        base_dir = Path(xdg_data_home).expanduser() if xdg_data_home else Path.home() / ".local" / "share"

    return base_dir / DATA_DIR_NAME


def default_db_path() -> Path:
    return user_data_dir() / "storage.db"
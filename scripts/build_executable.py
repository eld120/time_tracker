from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from PyInstaller.__main__ import run as pyinstaller_run
from PyInstaller.utils.hooks import collect_all


ROOT = Path(__file__).resolve().parent.parent
ENTRYPOINT = ROOT / "time_tracker" / "__main__.py"
DIST_DIR = ROOT / "dist"
BUILD_DIR = ROOT / "build" / "pyinstaller"


def add_data_argument(source: Path, destination: str) -> str:
    separator = ";" if os.name == "nt" else ":"
    return f"{source}{separator}{destination}"


def build_arguments(onefile: bool) -> list[str]:
    arguments = [
        str(ENTRYPOINT),
        "--name",
        "time_tracker",
        "--windowed",
        "--noconfirm",
        "--clean",
        "--distpath",
        str(DIST_DIR),
        "--workpath",
        str(BUILD_DIR),
        "--specpath",
        str(BUILD_DIR),
    ]

    if onefile:
        arguments.append("--onefile")

    arguments.extend(["--add-data", add_data_argument(ROOT / "assets", "assets")])
    arguments.extend(
        ["--add-data", add_data_argument(ROOT / "time_tracker" / "schema.sql", "time_tracker")]
    )

    customtkinter_datas, customtkinter_binaries, customtkinter_hiddenimports = collect_all(
        "customtkinter"
    )

    for source, destination in customtkinter_datas:
        arguments.extend(["--add-data", add_data_argument(Path(source), destination)])

    for source, destination in customtkinter_binaries:
        arguments.extend(["--add-binary", add_data_argument(Path(source), destination)])

    for hidden_import in customtkinter_hiddenimports:
        arguments.extend(["--hidden-import", hidden_import])

    if sys.platform == "darwin":
        arguments.extend(["--hidden-import", "AppKit"])
        arguments.extend(["--osx-bundle-identifier", "com.open.timetracker"])
    else:
        arguments.extend(["--icon", str(ROOT / "assets" / "icon.ico")])

    return arguments


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a desktop executable with PyInstaller.")
    parser.add_argument(
        "--onefile",
        action="store_true",
        default=sys.platform == "win32",
        help="Build a single-file executable instead of a bundled directory.",
    )
    parser.add_argument(
        "--onedir",
        action="store_true",
        help="Build a directory bundle instead of a single-file executable.",
    )
    args = parser.parse_args()

    onefile = args.onefile and not args.onedir
    pyinstaller_run(build_arguments(onefile))


if __name__ == "__main__":
    main()
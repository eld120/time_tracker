from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from time_tracker.main import main

if __name__ == "__main__":
    main()

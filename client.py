"""A CLI for the evohome-sync2 library."""

import sys

try:
    from evohomeasync2.client import main

except ModuleNotFoundError:
    from pathlib import Path

    sys.path.append(f"{Path(__file__).parent(__file__)}/src")

    from evohomeasync2.client import main

if __name__ == "__main__":
    main()

"""Einstiegspunkt: python -m stromkostenrechner [--cli]"""

import sys


def main() -> None:
    if "--cli" in sys.argv:
        from . import cli

        cli.main()
    else:
        from . import gui

        gui.main()


if __name__ == "__main__":
    main()

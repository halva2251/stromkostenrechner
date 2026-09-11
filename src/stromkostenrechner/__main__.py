"""Einstiegspunkt: python -m stromkostenrechner [--cli]"""

import sys


def main() -> int:
    if "--cli" in sys.argv:
        from . import cli

        return cli.main()

    from . import gui

    return gui.main()


if __name__ == "__main__":
    sys.exit(main())

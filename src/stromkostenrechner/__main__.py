"""Einstiegspunkt: python -m stromkostenrechner [--cli] [--debug]"""

import logging
import sys


def main(argumente: list[str] | None = None) -> int:
    argumente = sys.argv[1:] if argumente is None else argumente
    # Protokoll nur auf stderr, keine Logdatei: die Applikation soll auf dem
    # Rechner der Lehrperson keine Dateien anlegen. --debug zeigt Details.
    logging.basicConfig(
        level=logging.DEBUG if "--debug" in argumente else logging.WARNING,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    log = logging.getLogger("stromkostenrechner")

    try:
        if "--cli" in argumente:
            from . import cli

            return cli.main()

        from . import gui

        return gui.main()
    except Exception:
        # Letzte Sicherung: unerwartete Fehler protokollieren statt mit
        # rohem Traceback abzubrechen (Anforderung 10, kein Absturz).
        log.exception("Unerwarteter Fehler")
        print("Ein unerwarteter Fehler ist aufgetreten. Details mit --debug.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

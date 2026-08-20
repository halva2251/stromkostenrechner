"""Einlesen der Tarifdaten aus der CSV-Datei.

Fallstricke der mitgelieferten Datei:
- Sie beginnt mit einem UTF-8 BOM. Mit encoding='utf-8' landet dieser im
  ersten Spaltennamen. Richtig ist encoding='utf-8-sig'.
- Trennzeichen ist das Semikolon.
- Im Feld 'annahme' des IWB-Datensatzes steht ein Semikolon innerhalb von
  Anfuehrungszeichen. Selbst geschriebenes Aufteilen per split(';') zerlegt
  die Zeile falsch, das Modul csv erledigt das korrekt.
- Zeilenenden sind CRLF. Beim Oeffnen newline='' setzen.
- Zahlen sind als Text vorhanden und muessen zu Decimal werden, nicht zu float.
"""

from pathlib import Path

from .modelle import Tarif

STANDARD_PFAD = Path(__file__).resolve().parents[2] / "data" / "Tarifdaten_Stromkosten_2026.csv"


def lade_tarife(pfad: Path = STANDARD_PFAD) -> list[Tarif]:
    """Liest alle Tarifdatensaetze aus der CSV-Datei."""
    raise NotImplementedError


def tarif_nach_id(tarife: list[Tarif], tarif_id: str) -> Tarif:
    """Sucht einen Tarif anhand seiner ID."""
    raise NotImplementedError

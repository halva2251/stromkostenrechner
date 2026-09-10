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

import csv
from decimal import Decimal
from pathlib import Path

from .modelle import Tarif

STANDARD_PFAD = Path(__file__).resolve().parents[2] / "data" / "Tarifdaten_Stromkosten_2026.csv"


def lade_tarife(pfad: Path = STANDARD_PFAD) -> list[Tarif]:
    """Liest alle Tarifdatensaetze aus der CSV-Datei."""
    with open(pfad, encoding="utf-8-sig", newline="") as datei:
        zeilen = csv.DictReader(datei, delimiter=";")
        return [_zeile_zu_tarif(zeile) for zeile in zeilen]


def _zeile_zu_tarif(zeile: dict[str, str]) -> Tarif:
    return Tarif(
        tarif_id=zeile["tarif_id"],
        netzbetreiber=zeile["netzbetreiber"],
        tarifname=zeile["tarifname"],
        verbrauch_max_kwh=int(zeile["verbrauch_max_kwh"]),
        energie_q1_rp_kwh=Decimal(zeile["energie_q1_rp_kwh"]),
        energie_q2_rp_kwh=Decimal(zeile["energie_q2_rp_kwh"]),
        energie_q3_rp_kwh=Decimal(zeile["energie_q3_rp_kwh"]),
        energie_q4_rp_kwh=Decimal(zeile["energie_q4_rp_kwh"]),
        netznutzung_rp_kwh=Decimal(zeile["netznutzung_rp_kwh"]),
        weitere_abgaben_rp_kwh=Decimal(zeile["weitere_abgaben_rp_kwh"]),
        grundtarif_chf_monat=Decimal(zeile["grundtarif_chf_monat"]),
        messtarif_chf_monat=Decimal(zeile["messtarif_chf_monat"]),
        mwst_prozent=Decimal(zeile["mwst_prozent"]),
        quelle=zeile["quelle"],
    )


def tarif_nach_id(tarife: list[Tarif], tarif_id: str) -> Tarif:
    """Sucht einen Tarif anhand seiner ID."""
    for tarif in tarife:
        if tarif.tarif_id == tarif_id:
            return tarif
    raise KeyError(f"Kein Tarif mit ID '{tarif_id}' gefunden.")

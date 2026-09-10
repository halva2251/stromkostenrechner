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
import logging
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from .modelle import Tarif

STANDARD_PFAD = Path(__file__).resolve().parents[2] / "data" / "Tarifdaten_Stromkosten_2026.csv"

PFLICHTSPALTEN = (
    "tarif_id", "netzbetreiber", "tarifname", "gueltig_ab", "gueltig_bis",
    "verbrauch_max_kwh", "energie_q1_rp_kwh", "energie_q2_rp_kwh",
    "energie_q3_rp_kwh", "energie_q4_rp_kwh", "netznutzung_rp_kwh",
    "weitere_abgaben_rp_kwh", "grundtarif_chf_monat", "messtarif_chf_monat",
    "mwst_prozent", "preise_inkl_mwst", "quelle",
)

log = logging.getLogger(__name__)


class TarifdatenError(Exception):
    """Die Tarifdatei fehlt oder ist inhaltlich nicht verwendbar."""


def lade_tarife(pfad: Path = STANDARD_PFAD) -> list[Tarif]:
    """Liest alle Tarifdatensaetze aus der CSV-Datei."""
    try:
        with open(pfad, encoding="utf-8-sig", newline="") as datei:
            leser = csv.DictReader(datei, delimiter=";")
            fehlend = [s for s in PFLICHTSPALTEN if s not in (leser.fieldnames or [])]
            if fehlend:
                raise TarifdatenError(f"Spalten fehlen in {pfad.name}: {', '.join(fehlend)}")
            tarife = [_zeile_zu_tarif(zeile, nr) for nr, zeile in enumerate(leser, start=2)]
    except OSError as fehler:
        raise TarifdatenError(f"Tarifdatei konnte nicht gelesen werden: {pfad}") from fehler

    if not tarife:
        raise TarifdatenError(f"Tarifdatei enthaelt keine Datensaetze: {pfad}")
    log.info("%d Tarife aus %s geladen", len(tarife), pfad)
    return tarife


def tarif_nach_id(tarife: list[Tarif], tarif_id: str) -> Tarif:
    """Sucht einen Tarif anhand seiner ID."""
    for tarif in tarife:
        if tarif.tarif_id == tarif_id:
            return tarif
    raise KeyError(f"Unbekannte Tarif-ID: {tarif_id}")


def _zeile_zu_tarif(zeile: dict[str, str], zeilennummer: int) -> Tarif:
    # Die Berechnung rechnet die MWST aus Bruttobetraegen heraus. Ein
    # Datensatz mit Nettopreisen wuerde still ein falsches Resultat liefern,
    # deshalb wird er hier abgelehnt statt spaeter falsch verrechnet.
    if zeile["preise_inkl_mwst"].strip().lower() != "true":
        raise TarifdatenError(f"Zeile {zeilennummer}: nur Preise inkl. MWST werden unterstuetzt")
    try:
        return Tarif(
            tarif_id=zeile["tarif_id"].strip(),
            netzbetreiber=zeile["netzbetreiber"].strip(),
            tarifname=zeile["tarifname"].strip(),
            gueltig_ab=date.fromisoformat(zeile["gueltig_ab"]),
            gueltig_bis=date.fromisoformat(zeile["gueltig_bis"]),
            verbrauch_max_kwh=int(zeile["verbrauch_max_kwh"]),
            energie_q1_rp_kwh=_decimal(zeile["energie_q1_rp_kwh"]),
            energie_q2_rp_kwh=_decimal(zeile["energie_q2_rp_kwh"]),
            energie_q3_rp_kwh=_decimal(zeile["energie_q3_rp_kwh"]),
            energie_q4_rp_kwh=_decimal(zeile["energie_q4_rp_kwh"]),
            netznutzung_rp_kwh=_decimal(zeile["netznutzung_rp_kwh"]),
            weitere_abgaben_rp_kwh=_decimal(zeile["weitere_abgaben_rp_kwh"]),
            grundtarif_chf_monat=_decimal(zeile["grundtarif_chf_monat"]),
            messtarif_chf_monat=_decimal(zeile["messtarif_chf_monat"]),
            mwst_prozent=_decimal(zeile["mwst_prozent"]),
            quelle=zeile["quelle"].strip(),
        )
    except (ValueError, InvalidOperation) as fehler:
        raise TarifdatenError(f"Zeile {zeilennummer}: ungueltiger Wert ({fehler})") from fehler


def _decimal(text: str) -> Decimal:
    # Decimal direkt aus dem Text, nie ueber float: Decimal(14.38) waere
    # bereits 14.3800000000000007815970093361102044582366943359375.
    wert = Decimal(text.strip())
    if not wert.is_finite() or wert < 0:
        raise ValueError(f"'{text}' ist kein gueltiger Tarifwert")
    return wert

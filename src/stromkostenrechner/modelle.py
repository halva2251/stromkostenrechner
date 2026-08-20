"""Datenklassen fuer Tarife und Berechnungsergebnisse.

Enthaelt keine Logik ausser einfachen Ableitungen.
"""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Tarif:
    """Ein Tarifdatensatz aus der CSV-Datei.

    Verbrauchsabhaengige Werte in Rappen pro kWh, feste Werte in Franken
    pro Monat. Alle Werte enthalten Mehrwertsteuer.
    """

    tarif_id: str
    netzbetreiber: str
    tarifname: str
    verbrauch_max_kwh: int
    energie_q1_rp_kwh: Decimal
    energie_q2_rp_kwh: Decimal
    energie_q3_rp_kwh: Decimal
    energie_q4_rp_kwh: Decimal
    netznutzung_rp_kwh: Decimal
    weitere_abgaben_rp_kwh: Decimal
    grundtarif_chf_monat: Decimal
    messtarif_chf_monat: Decimal
    mwst_prozent: Decimal
    quelle: str


@dataclass(frozen=True)
class Kostenaufstellung:
    """Ergebnis einer Berechnung fuer genau einen Tarif.

    Alle Betraege in Franken, ungerundet. Gerundet wird erst bei der Ausgabe.
    """

    tarif: Tarif
    jahresverbrauch_kwh: int
    energiekosten: Decimal
    netznutzung: Decimal
    weitere_abgaben: Decimal
    grundtarif: Decimal
    messtarif: Decimal
    mwst_anteil: Decimal
    total: Decimal

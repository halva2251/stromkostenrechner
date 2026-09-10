"""Datenklassen fuer Tarife und Berechnungsergebnisse.

Enthaelt keine Logik ausser einfachen Ableitungen.
"""

from dataclasses import dataclass
from datetime import date
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
    gueltig_ab: date
    gueltig_bis: date
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

    @property
    def bezeichnung(self) -> str:
        """Kurzname fuer die Anzeige, zum Beispiel 'EKZ 2026'.

        Das Jahr stammt aus der CSV-Datei statt aus einer Konstante, damit
        ein Tarifdatensatz eines anderen Jahres nicht falsch beschriftet wird.
        """
        return f"{self.netzbetreiber} {self.gueltig_ab.year}"

    @property
    def energiepreise_rp_kwh(self) -> tuple[Decimal, Decimal, Decimal, Decimal]:
        return (
            self.energie_q1_rp_kwh,
            self.energie_q2_rp_kwh,
            self.energie_q3_rp_kwh,
            self.energie_q4_rp_kwh,
        )


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

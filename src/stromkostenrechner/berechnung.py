"""Berechnungslogik.

Dieses Modul kennt weder Konsole noch grafische Oberflaeche und importiert
weder cli noch gui noch tkinter.
"""

from decimal import Decimal

from .modelle import Kostenaufstellung, Tarif

VERBRAUCH_MIN_KWH = 0
VERBRAUCH_MAX_KWH = 12_999
VERBRAUCH_VORGABE_KWH = 2_500
MONATE_PRO_JAHR = 12
QUARTALE_PRO_JAHR = 4


class UngueltigerVerbrauchError(ValueError):
    """Wird ausgeloest, wenn der Jahresverbrauch ausserhalb des gueltigen Bereichs liegt."""


def pruefe_verbrauch(jahresverbrauch_kwh: int) -> None:
    """Prueft den Jahresverbrauch gegen den gueltigen Bereich 0 bis 12999 kWh."""
    raise NotImplementedError


def berechne(tarif: Tarif, jahresverbrauch_kwh: int) -> Kostenaufstellung:
    """Berechnet alle Kostenbestandteile fuer einen Tarif.

    Der Verbrauch wird gleichmaessig auf vier Quartale verteilt. Beim
    IWB-Einfachtarif sind alle vier Quartalspreise gleich, wodurch dieselbe
    Formel gilt.
    """
    raise NotImplementedError


def berechne_mwst_anteil(bruttobetrag: Decimal, mwst_prozent: Decimal) -> Decimal:
    """Rechnet den in einem Bruttobetrag enthaltenen Mehrwertsteueranteil heraus.

    Achtung: die Tarifwerte enthalten die Mehrwertsteuer bereits. Der Anteil
    ist deshalb nicht Brutto mal Satz, sondern muss herausgerechnet werden.
    """
    raise NotImplementedError


def vergleiche(links: Kostenaufstellung, rechts: Kostenaufstellung) -> tuple[Kostenaufstellung, Decimal]:
    """Gibt die guenstigere Aufstellung und die Kostendifferenz zurueck.

    Die Differenz wird aus den ungerundeten Totalbetraegen gebildet und erst
    danach gerundet. Rundet man zuerst die beiden Totale und subtrahiert dann,
    entsteht bei der Kontrollrechnung 312.14 statt der geforderten 312.15.
    """
    raise NotImplementedError

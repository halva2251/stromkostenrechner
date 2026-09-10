"""Berechnungslogik.

Dieses Modul kennt weder Konsole noch grafische Oberflaeche und importiert
weder cli noch gui noch tkinter.
"""

from decimal import Decimal

from .geld import rp_in_chf
from .modelle import Kostenaufstellung, Tarif

VERBRAUCH_MIN_KWH = 0
VERBRAUCH_MAX_KWH = 12_999
VERBRAUCH_VORGABE_KWH = 2_500
MONATE_PRO_JAHR = 12
QUARTALE_PRO_JAHR = 4
PROZENT_BASIS = Decimal("100")


class UngueltigerVerbrauchError(ValueError):
    """Wird ausgeloest, wenn der Jahresverbrauch ausserhalb des gueltigen Bereichs liegt."""


def pruefe_verbrauch(jahresverbrauch_kwh: int) -> None:
    """Prueft den Jahresverbrauch gegen den gueltigen Bereich 0 bis 12999 kWh."""
    if not VERBRAUCH_MIN_KWH <= jahresverbrauch_kwh <= VERBRAUCH_MAX_KWH:
        raise UngueltigerVerbrauchError(
            f"Jahresverbrauch muss zwischen {VERBRAUCH_MIN_KWH} und "
            f"{VERBRAUCH_MAX_KWH} kWh liegen, war {jahresverbrauch_kwh}."
        )


def berechne(tarif: Tarif, jahresverbrauch_kwh: int) -> Kostenaufstellung:
    """Berechnet alle Kostenbestandteile fuer einen Tarif.

    Der Verbrauch wird gleichmaessig auf vier Quartale verteilt. Beim
    IWB-Einfachtarif sind alle vier Quartalspreise gleich, wodurch dieselbe
    Formel gilt.
    """
    pruefe_verbrauch(jahresverbrauch_kwh)
    verbrauch = Decimal(jahresverbrauch_kwh)
    verbrauch_pro_quartal = verbrauch / QUARTALE_PRO_JAHR
    quartalspreise = (
        tarif.energie_q1_rp_kwh,
        tarif.energie_q2_rp_kwh,
        tarif.energie_q3_rp_kwh,
        tarif.energie_q4_rp_kwh,
    )

    energiekosten = rp_in_chf(sum((verbrauch_pro_quartal * preis for preis in quartalspreise), Decimal("0")))
    netznutzung = rp_in_chf(verbrauch * tarif.netznutzung_rp_kwh)
    weitere_abgaben = rp_in_chf(verbrauch * tarif.weitere_abgaben_rp_kwh)
    grundtarif = tarif.grundtarif_chf_monat * MONATE_PRO_JAHR
    messtarif = tarif.messtarif_chf_monat * MONATE_PRO_JAHR
    total = energiekosten + netznutzung + weitere_abgaben + grundtarif + messtarif

    return Kostenaufstellung(
        tarif=tarif,
        jahresverbrauch_kwh=jahresverbrauch_kwh,
        energiekosten=energiekosten,
        netznutzung=netznutzung,
        weitere_abgaben=weitere_abgaben,
        grundtarif=grundtarif,
        messtarif=messtarif,
        mwst_anteil=berechne_mwst_anteil(total, tarif.mwst_prozent),
        total=total,
    )


def berechne_mwst_anteil(bruttobetrag: Decimal, mwst_prozent: Decimal) -> Decimal:
    """Rechnet den in einem Bruttobetrag enthaltenen Mehrwertsteueranteil heraus.

    Achtung: die Tarifwerte enthalten die Mehrwertsteuer bereits. Der Anteil
    ist deshalb nicht Brutto mal Satz, sondern muss herausgerechnet werden.
    """
    return bruttobetrag * mwst_prozent / (PROZENT_BASIS + mwst_prozent)


def vergleiche(links: Kostenaufstellung, rechts: Kostenaufstellung) -> tuple[Kostenaufstellung, Decimal]:
    """Gibt die guenstigere Aufstellung und die Kostendifferenz zurueck.

    Die Differenz wird aus den ungerundeten Totalbetraegen gebildet und erst
    danach gerundet. Rundet man zuerst die beiden Totale und subtrahiert dann,
    entsteht bei der Kontrollrechnung 312.14 statt der geforderten 312.15.
    """
    guenstigere = links if links.total < rechts.total else rechts
    differenz = abs(links.total - rechts.total)
    return guenstigere, differenz

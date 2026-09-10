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


class UngueltigerVerbrauchError(ValueError):
    """Wird ausgeloest, wenn der Jahresverbrauch ausserhalb des gueltigen Bereichs liegt."""


def pruefe_verbrauch(jahresverbrauch_kwh: int) -> None:
    """Prueft den Jahresverbrauch gegen den gueltigen Bereich 0 bis 12999 kWh."""
    # bool ist in Python eine Unterklasse von int, True wuerde sonst als 1 kWh
    # durchgehen. Kommazahlen sind nicht vorgesehen: Zaehlerstaende werden in
    # ganzen kWh abgelesen, und die Aufgabe spricht von Werten 0 bis 12'999.
    if isinstance(jahresverbrauch_kwh, bool) or not isinstance(jahresverbrauch_kwh, int):
        raise UngueltigerVerbrauchError("Der Jahresverbrauch muss eine ganze Zahl sein.")
    if not VERBRAUCH_MIN_KWH <= jahresverbrauch_kwh <= VERBRAUCH_MAX_KWH:
        raise UngueltigerVerbrauchError(
            f"Der Jahresverbrauch muss zwischen {VERBRAUCH_MIN_KWH} und {VERBRAUCH_MAX_KWH} kWh liegen."
        )


def berechne(tarif: Tarif, jahresverbrauch_kwh: int) -> Kostenaufstellung:
    """Berechnet alle Kostenbestandteile fuer einen Tarif.

    Der Verbrauch wird gleichmaessig auf vier Quartale verteilt. Beim
    IWB-Einfachtarif sind alle vier Quartalspreise gleich, wodurch dieselbe
    Formel gilt.
    """
    pruefe_verbrauch(jahresverbrauch_kwh)
    verbrauch = Decimal(jahresverbrauch_kwh)
    verbrauch_quartal = verbrauch_pro_quartal(jahresverbrauch_kwh)

    energiekosten = sum(
        (verbrauch_quartal * rp_in_chf(preis) for preis in tarif.energiepreise_rp_kwh),
        Decimal("0"),
    )
    netznutzung = verbrauch * rp_in_chf(tarif.netznutzung_rp_kwh)
    weitere_abgaben = verbrauch * rp_in_chf(tarif.weitere_abgaben_rp_kwh)
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


def verbrauch_pro_quartal(jahresverbrauch_kwh: int) -> Decimal:
    """Verbrauch eines Quartals bei gleichmaessiger Verteilung, ungerundet.

    Decimal statt Ganzzahldivision: bei 2501 kWh sind es 625.25 kWh, nicht 625.
    """
    return Decimal(jahresverbrauch_kwh) / QUARTALE_PRO_JAHR


def berechne_mwst_anteil(bruttobetrag: Decimal, mwst_prozent: Decimal) -> Decimal:
    """Rechnet den in einem Bruttobetrag enthaltenen Mehrwertsteueranteil heraus.

    Achtung: die Tarifwerte enthalten die Mehrwertsteuer bereits. Der Anteil
    ist deshalb nicht Brutto mal Satz, sondern muss herausgerechnet werden.
    Bei 8.1 %: Brutto * 8.1 / 108.1.
    """
    return bruttobetrag * mwst_prozent / (Decimal("100") + mwst_prozent)


def vergleiche(links: Kostenaufstellung, rechts: Kostenaufstellung) -> tuple[Kostenaufstellung, Decimal]:
    """Gibt die guenstigere Aufstellung und die Kostendifferenz zurueck.

    Die Differenz wird aus den ungerundeten Totalbetraegen gebildet und erst
    danach gerundet. Rundet man zuerst die beiden Totale und subtrahiert dann,
    entsteht bei der Kontrollrechnung 312.14 statt der geforderten 312.15.

    Bei exakt gleichem Total wird links zurueckgegeben und die Differenz ist
    null. Die Oberflaeche muss diesen Fall selbst als "gleich teuer" anzeigen.
    """
    guenstiger = rechts if rechts.total < links.total else links
    return guenstiger, abs(links.total - rechts.total)

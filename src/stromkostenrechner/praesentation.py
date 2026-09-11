"""Gemeinsame Bausteine der beiden Oberflaechen.

Enthaelt das Umwandeln der Texteingabe und die Beschriftung der Ausgabe,
damit Konsole und GUI dieselben Regeln und dieselben Texte verwenden.
Keine Berechnungslogik, kein tkinter.
"""

from decimal import Decimal

from .berechnung import (
    VERBRAUCH_MAX_KWH,
    VERBRAUCH_MIN_KWH,
    UngueltigerVerbrauchError,
    pruefe_verbrauch,
)
from .geld import formatieren, formatieren_kwh
from .modelle import Kostenaufstellung, Tarif

HINWEIS_MODELLVERGLEICH = "Es handelt sich um einen Modellvergleich."
FEHLER_VERBRAUCH = (
    f"Ungültige Eingabe. Bitte eine Zahl zwischen {formatieren_kwh(VERBRAUCH_MIN_KWH)} "
    f"und {formatieren_kwh(VERBRAUCH_MAX_KWH)} eingeben."
)


def verbrauch_aus_text(text: str) -> int:
    """Wandelt eine Benutzereingabe in kWh um und prueft den Bereich.

    Apostroph und Leerzeichen werden als Tausendertrennzeichen akzeptiert,
    weil Benutzende in der Schweiz 2'500 so schreiben.
    Loest UngueltigerVerbrauchError aus, auch bei Text wie 'abc'.
    """
    bereinigt = text.strip().replace("'", "").replace("’", "").replace(" ", "")
    try:
        verbrauch = int(bereinigt)
    except ValueError as fehler:
        raise UngueltigerVerbrauchError(FEHLER_VERBRAUCH) from fehler
    pruefe_verbrauch(verbrauch)
    return verbrauch


def hat_quartalspreise(tarif: Tarif) -> bool:
    """True, wenn sich die Energiepreise zwischen den Quartalen unterscheiden."""
    return len(set(tarif.energiepreise_rp_kwh)) > 1


def kostenzeilen(aufstellung: Kostenaufstellung) -> list[tuple[str, str]]:
    """Beschriftung und formatierter Betrag aller Kostenbestandteile."""
    return [
        ("Energiekosten", formatieren(aufstellung.energiekosten)),
        ("Netznutzung", formatieren(aufstellung.netznutzung)),
        ("Weitere Abgaben", formatieren(aufstellung.weitere_abgaben)),
        ("Grundtarif", formatieren(aufstellung.grundtarif)),
        ("Messtarif", formatieren(aufstellung.messtarif)),
        ("davon MWST-Anteil", formatieren(aufstellung.mwst_anteil)),
        ("Total", formatieren(aufstellung.total)),
    ]


def vergleichstext(guenstiger: Kostenaufstellung, differenz: Decimal) -> str:
    if differenz == 0:
        return "Beide Tarife sind gleich teuer."
    return (
        f"Differenz: CHF {formatieren(differenz)}. "
        f"Günstigerer Tarif: {guenstiger.tarif.bezeichnung}."
    )

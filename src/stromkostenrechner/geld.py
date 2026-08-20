"""Geldbetraege und Rundung.

Einzige Stelle im Projekt, an der gerundet wird. Siehe docs/CODERICHTLINIEN.md.
"""

from decimal import Decimal, ROUND_HALF_UP

RAPPEN_PRO_FRANKEN = Decimal("100")


def rp_in_chf(rappen: Decimal) -> Decimal:
    """Rechnet einen Rappenbetrag in Franken um, ohne zu runden."""
    return Decimal(rappen) / RAPPEN_PRO_FRANKEN


def runden(betrag: Decimal) -> Decimal:
    """Rundet auf zwei Nachkommastellen, kaufmaennisch aufwaerts.

    Wird ausschliesslich fuer die Ausgabe verwendet, nie fuer
    Zwischenergebnisse. Die eingebaute Funktion round() ist hier nicht
    geeignet: sie rundet zur naechsten geraden Ziffer, wodurch 693.925 zu
    693.92 statt zu den geforderten 693.93 wird.
    """
    return Decimal(betrag).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def formatieren(betrag: Decimal) -> str:
    """Formatiert einen Betrag fuer die Anzeige, zum Beispiel '693.93'."""
    return f"{runden(betrag):.2f}"

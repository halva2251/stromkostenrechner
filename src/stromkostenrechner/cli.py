"""Konsolenoberflaeche. Enthaelt keine Berechnungslogik.

Die Texte entsprechen der Testfallspezifikation (Testfaelle 1.1 bis 10.2).
"""

from collections.abc import Callable

from . import berechnung
from .berechnung import UngueltigerVerbrauchError
from .geld import formatieren_kwh
from .modelle import Kostenaufstellung, Tarif
from .praesentation import (
    FEHLER_VERBRAUCH,
    HINWEIS_MODELLVERGLEICH,
    hat_quartalspreise,
    kostenzeilen,
    verbrauch_aus_text,
    vergleichstext,
)
from .tarif_repository import TarifdatenError, lade_tarife

Eingabe = Callable[[str], str]


def main(eingabe: Eingabe = input, ausgabe: Callable[[str], None] = print) -> int:
    """Startet die Konsolenversion. Gibt den Exit-Code zurueck."""
    try:
        tarife = lade_tarife()
    except TarifdatenError as fehler:
        ausgabe(f"Fehler: {fehler}")
        return 1

    ausgabe("Stromkostenrechner 2026")
    ausgabe("")
    try:
        verbrauch = frage_verbrauch(eingabe, ausgabe)
        auswahl = frage_auswahl(tarife, eingabe, ausgabe)
    except (EOFError, KeyboardInterrupt):
        # Ctrl+C oder Ctrl+D soll das Programm beenden, ohne Traceback.
        ausgabe("")
        ausgabe("Abgebrochen.")
        return 1

    aufstellungen = [berechnung.berechne(tarif, verbrauch) for tarif in auswahl]
    for aufstellung in aufstellungen:
        ausgabe("")
        zeige_aufstellung(aufstellung, ausgabe)

    if len(aufstellungen) == 2:
        guenstiger, differenz = berechnung.vergleiche(*aufstellungen)
        ausgabe("")
        ausgabe(vergleichstext(guenstiger, differenz))
        ausgabe(f"Hinweis: «{HINWEIS_MODELLVERGLEICH}»")
    return 0


def frage_verbrauch(eingabe: Eingabe, ausgabe: Callable[[str], None]) -> int:
    standard = berechnung.VERBRAUCH_VORGABE_KWH
    text = eingabe(f"Geben Sie Ihren Jahresverbrauch 2026 in kWh ein (Standard: {standard}): ")
    while True:
        if text.strip() == "":
            ausgabe(f"Verwendeter Jahresverbrauch: {formatieren_kwh(standard)} kWh.")
            return standard
        try:
            verbrauch = verbrauch_aus_text(text)
        except UngueltigerVerbrauchError:
            text = eingabe(FEHLER_VERBRAUCH.removesuffix(".") + ": ")
            continue
        ausgabe(f"Eingabe akzeptiert: {formatieren_kwh(verbrauch)} kWh.")
        return verbrauch


def frage_auswahl(tarife: list[Tarif], eingabe: Eingabe, ausgabe: Callable[[str], None]) -> list[Tarif]:
    # Die Optionen werden aus der CSV erzeugt, nicht fest einprogrammiert.
    # Der Vergleich ist nur fuer genau zwei Tarife definiert (Aufgabenstellung).
    optionen = {str(nr): [tarif] for nr, tarif in enumerate(tarife, start=1)}
    beschriftung = [f"{nr} = {tarif.bezeichnung}" for nr, tarif in enumerate(tarife, start=1)]
    if len(tarife) == 2:
        nr_vergleich = str(len(tarife) + 1)
        optionen[nr_vergleich] = list(tarife)
        beschriftung.append(f"{nr_vergleich} = Vergleich beider Tarife")

    frage = f"Wählen Sie den Netzbetreiber ({', '.join(beschriftung)}): "
    text = eingabe(frage)
    while text.strip() not in optionen:
        text = eingabe(f"Ungültige Auswahl. {frage}")

    auswahl = optionen[text.strip()]
    if len(auswahl) == 2:
        ausgabe(
            f"Modus «Vergleich» aktiviert: {auswahl[0].bezeichnung} und "
            f"{auswahl[1].bezeichnung} werden berechnet."
        )
    else:
        ausgabe(f"Gewählter Tarif: {auswahl[0].bezeichnung}.")
    return auswahl


def zeige_aufstellung(aufstellung: Kostenaufstellung, ausgabe: Callable[[str], None]) -> None:
    tarif = aufstellung.tarif
    ausgabe(f"{tarif.bezeichnung} – {tarif.tarifname}")
    ausgabe(f"Jahresverbrauch: {formatieren_kwh(aufstellung.jahresverbrauch_kwh)} kWh")
    if hat_quartalspreise(tarif):
        quartal = formatieren_kwh(berechnung.verbrauch_pro_quartal(aufstellung.jahresverbrauch_kwh), 2)
        teile = ", ".join(f"Q{nr} = {quartal} kWh" for nr in range(1, 5))
        ausgabe(f"Verbrauch pro Quartal ({tarif.netzbetreiber}): {teile}.")
    for beschriftung, betrag in kostenzeilen(aufstellung):
        ausgabe(f"  {beschriftung:<20} CHF {betrag:>10}")

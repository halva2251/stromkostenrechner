"""Grafische Oberflaeche mit tkinter. Enthaelt keine Berechnungslogik.

Aufbau gemaess GUI-Wireframes: oben Eingabe (Jahresverbrauch, Netzbetreiber,
Berechnen), darunter Ausgabe als Einzeltarif oder als Vergleich.
"""

import logging
import sys

from . import berechnung
from .berechnung import UngueltigerVerbrauchError
from .geld import formatieren_kwh
from .modelle import Kostenaufstellung, Tarif
from .praesentation import (
    HINWEIS_MODELLVERGLEICH,
    hat_quartalspreise,
    kostenzeilen,
    verbrauch_aus_text,
    vergleichstext,
)
from .tarif_repository import TarifdatenError, lade_tarife

log = logging.getLogger(__name__)

MODUS_VERGLEICH = "vergleich"
FARBE_FEHLER = "#b00020"


def main() -> int:
    """Startet die grafische Oberflaeche. Gibt den Exit-Code zurueck."""
    try:
        import tkinter as tk
        from tkinter import messagebox
    except ImportError:
        # Risiko 3 im Technologieentscheid: tkinter fehlt auf manchen Linux-Systemen.
        print(
            "tkinter ist nicht installiert. Starten Sie die Konsolenversion mit\n"
            "  python -m stromkostenrechner --cli",
            file=sys.stderr,
        )
        return 1

    try:
        tarife = lade_tarife()
    except TarifdatenError as fehler:
        log.error("Tarifdaten nicht lesbar: %s", fehler)
        wurzel = tk.Tk()
        wurzel.withdraw()
        messagebox.showerror("Stromkostenrechner 2026", f"Die Tarifdaten konnten nicht geladen werden.\n\n{fehler}")
        wurzel.destroy()
        return 1

    wurzel = tk.Tk()
    Hauptfenster(wurzel, tarife)
    wurzel.mainloop()
    return 0


class Hauptfenster:
    def __init__(self, wurzel, tarife: list[Tarif]) -> None:
        import tkinter as tk
        from tkinter import ttk

        self._tk = tk
        self._ttk = ttk
        self.tarife = tarife
        self.wurzel = wurzel
        wurzel.title("Stromkostenrechner 2026")
        wurzel.minsize(560, 660)

        rahmen = ttk.Frame(wurzel, padding=16)
        rahmen.pack(fill="both", expand=True)
        ttk.Label(rahmen, text="Stromkostenrechner 2026", font=("TkDefaultFont", 16, "bold")).pack(anchor="w")

        eingabe = ttk.LabelFrame(rahmen, text="Eingabe", padding=12)
        eingabe.pack(fill="x", pady=(12, 8))

        ttk.Label(eingabe, text="Jahresverbrauch (kWh)").grid(row=0, column=0, sticky="w")
        self.verbrauch = tk.StringVar(value=str(berechnung.VERBRAUCH_VORGABE_KWH))
        feld = ttk.Entry(eingabe, textvariable=self.verbrauch, width=12)
        feld.grid(row=0, column=1, sticky="w", padx=(8, 0))
        feld.bind("<Return>", lambda _e: self.berechnen())
        feld.focus_set()

        self.fehler = ttk.Label(eingabe, text="", foreground=FARBE_FEHLER, wraplength=320)
        self.fehler.grid(row=1, column=1, sticky="w", padx=(8, 0), pady=(4, 0))

        ttk.Label(eingabe, text="Netzbetreiber").grid(row=2, column=0, sticky="nw", pady=(8, 0))
        self.modus = tk.StringVar(value=tarife[0].tarif_id)
        optionen = ttk.Frame(eingabe)
        optionen.grid(row=2, column=1, sticky="w", padx=(8, 0), pady=(8, 0))
        for tarif in tarife:
            ttk.Radiobutton(optionen, text=tarif.bezeichnung, value=tarif.tarif_id, variable=self.modus).pack(anchor="w")
        # Der Vergleich ist nur fuer genau zwei Tarife definiert (Aufgabenstellung).
        if len(tarife) == 2:
            ttk.Radiobutton(
                optionen, text="Vergleich beider Tarife", value=MODUS_VERGLEICH, variable=self.modus
            ).pack(anchor="w")

        ttk.Button(eingabe, text="Berechnen", command=self.berechnen).grid(row=3, column=1, sticky="w", padx=(8, 0), pady=(12, 0))

        self.ausgabe = ttk.LabelFrame(rahmen, text="Ausgabe", padding=12)
        self.ausgabe.pack(fill="both", expand=True)
        ttk.Label(self.ausgabe, text="Noch keine Berechnung.").pack(anchor="w")

    def berechnen(self) -> None:
        try:
            verbrauch = verbrauch_aus_text(self.verbrauch.get())
        except UngueltigerVerbrauchError as fehler:
            # Kein Resultat stehen lassen, das nicht mehr zur Eingabe passt.
            self.fehler.config(text=str(fehler))
            self._leere_ausgabe()
            self.ausgabe.config(text="Ausgabe")
            self._ttk.Label(self.ausgabe, text="Keine Berechnung, die Eingabe ist ungültig.").pack(anchor="w")
            return

        self.fehler.config(text="")
        if self.modus.get() == MODUS_VERGLEICH:
            links, rechts = (berechnung.berechne(t, verbrauch) for t in self.tarife)
            self._zeige_vergleich(links, rechts)
        else:
            tarif = next(t for t in self.tarife if t.tarif_id == self.modus.get())
            self._zeige_einzeltarif(berechnung.berechne(tarif, verbrauch))

    def _leere_ausgabe(self) -> None:
        for kind in self.ausgabe.winfo_children():
            kind.destroy()

    def _zeige_einzeltarif(self, aufstellung: Kostenaufstellung) -> None:
        ttk = self._ttk
        self._leere_ausgabe()
        self.ausgabe.config(text="Ausgabe – Modus: Einzeltarif")
        tarif = aufstellung.tarif
        ttk.Label(
            self.ausgabe,
            text=f"{tarif.bezeichnung} · {tarif.tarifname} · Jahresverbrauch "
            f"{formatieren_kwh(aufstellung.jahresverbrauch_kwh)} kWh",
            font=("TkDefaultFont", 10, "bold"),
            wraplength=480,
        ).pack(anchor="w")
        self._quartalshinweis(self.ausgabe, aufstellung)

        tabelle = ttk.Frame(self.ausgabe)
        tabelle.pack(anchor="w", pady=(8, 0))
        for zeile, (beschriftung, betrag) in enumerate(kostenzeilen(aufstellung)):
            fett = ("TkDefaultFont", 10, "bold") if beschriftung == "Total" else None
            ttk.Label(tabelle, text=beschriftung, font=fett).grid(row=zeile, column=0, sticky="w", padx=(0, 24))
            ttk.Label(tabelle, text=f"CHF {betrag}", font=fett).grid(row=zeile, column=1, sticky="e")

    def _zeige_vergleich(self, links: Kostenaufstellung, rechts: Kostenaufstellung) -> None:
        ttk = self._ttk
        self._leere_ausgabe()
        self.ausgabe.config(text="Ausgabe – Modus: Vergleich")
        ttk.Label(
            self.ausgabe,
            text=f"Jahresverbrauch {formatieren_kwh(links.jahresverbrauch_kwh)} kWh",
            font=("TkDefaultFont", 10, "bold"),
        ).pack(anchor="w")

        tabelle = ttk.Frame(self.ausgabe)
        tabelle.pack(anchor="w", pady=(8, 0))
        ttk.Label(tabelle, text="").grid(row=0, column=0)
        for spalte, aufstellung in enumerate((links, rechts), start=1):
            ttk.Label(tabelle, text=aufstellung.tarif.bezeichnung, font=("TkDefaultFont", 10, "bold")).grid(
                row=0, column=spalte, sticky="e", padx=(24, 0)
            )
            ttk.Label(tabelle, text=aufstellung.tarif.tarifname, wraplength=160, justify="right").grid(
                row=1, column=spalte, sticky="e", padx=(24, 0)
            )
        zeilen_links = kostenzeilen(links)
        zeilen_rechts = kostenzeilen(rechts)
        for nr, ((beschriftung, betrag_l), (_, betrag_r)) in enumerate(zip(zeilen_links, zeilen_rechts), start=2):
            fett = ("TkDefaultFont", 10, "bold") if beschriftung == "Total" else None
            ttk.Label(tabelle, text=beschriftung, font=fett).grid(row=nr, column=0, sticky="w")
            ttk.Label(tabelle, text=f"CHF {betrag_l}", font=fett).grid(row=nr, column=1, sticky="e", padx=(24, 0))
            ttk.Label(tabelle, text=f"CHF {betrag_r}", font=fett).grid(row=nr, column=2, sticky="e", padx=(24, 0))

        guenstiger, differenz = berechnung.vergleiche(links, rechts)
        ttk.Label(self.ausgabe, text=vergleichstext(guenstiger, differenz), font=("TkDefaultFont", 10, "bold")).pack(
            anchor="w", pady=(12, 0)
        )
        ttk.Label(self.ausgabe, text=f"Hinweis: {HINWEIS_MODELLVERGLEICH}").pack(anchor="w", pady=(4, 0))
        for aufstellung in (links, rechts):
            self._quartalshinweis(self.ausgabe, aufstellung)

    def _quartalshinweis(self, eltern, aufstellung: Kostenaufstellung) -> None:
        if hat_quartalspreise(aufstellung.tarif):
            quartal = formatieren_kwh(berechnung.verbrauch_pro_quartal(aufstellung.jahresverbrauch_kwh), 2)
            self._ttk.Label(
                eltern,
                text=f"{aufstellung.tarif.netzbetreiber}: Verbrauch gleichmässig verteilt, {quartal} kWh pro Quartal",
            ).pack(anchor="w")

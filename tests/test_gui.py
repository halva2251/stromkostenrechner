"""Rauchtest der GUI. Wird uebersprungen, wenn tkinter oder ein Bildschirm fehlt.

Ersetzt die manuellen End-to-End-Tests nicht, faengt aber Abstuerze ab.
"""

import pytest

tk = pytest.importorskip("tkinter")

from stromkostenrechner import gui  # noqa: E402
from stromkostenrechner.tarif_repository import lade_tarife  # noqa: E402


@pytest.fixture
def fenster():
    try:
        wurzel = tk.Tk()
    except tk.TclError:
        pytest.skip("kein Bildschirm verfuegbar")
    wurzel.withdraw()
    yield gui.Hauptfenster(wurzel, lade_tarife())
    wurzel.destroy()


def texte(widget) -> list[str]:
    gefunden = []
    for kind in widget.winfo_children():
        try:
            gefunden.append(str(kind.cget("text")))
        except tk.TclError:
            pass
        gefunden.extend(texte(kind))
    return gefunden


def test_vorgabewert_2500(fenster):
    assert fenster.verbrauch.get() == "2500"


def test_vergleich_zeigt_differenz(fenster):
    fenster.modus.set(gui.MODUS_VERGLEICH)
    fenster.berechnen()
    alle = texte(fenster.ausgabe)
    assert "Differenz: CHF 312.15. Günstigerer Tarif: EKZ 2026." in alle
    assert "CHF 1'006.07" in alle


def test_ungueltige_eingabe_zeigt_fehler_ohne_resultat(fenster):
    fenster.berechnen()
    fenster.verbrauch.set("abc")
    fenster.berechnen()
    assert "Ungültige Eingabe" in fenster.fehler.cget("text")
    assert not any(t.startswith("CHF") for t in texte(fenster.ausgabe))

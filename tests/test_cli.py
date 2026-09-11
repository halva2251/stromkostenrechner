"""Tests der Konsolenoberflaeche mit simulierten Eingaben.

Decken die Testfaelle 1.1, 1.2, 2.1, 3.1, 8.1, 9.1 und 10.1 der
Testfallspezifikation automatisiert ab. Die manuellen Tests ersetzen sie nicht.
"""

import pytest

from stromkostenrechner import cli
from stromkostenrechner.praesentation import verbrauch_aus_text
from stromkostenrechner.berechnung import UngueltigerVerbrauchError


def starte(*eingaben: str) -> tuple[int, str]:
    antworten = iter(eingaben)
    zeilen: list[str] = []

    def eingabe(frage: str) -> str:
        zeilen.append(frage)
        return next(antworten)

    code = cli.main(eingabe=eingabe, ausgabe=zeilen.append)
    return code, "\n".join(zeilen)


def test_standardwert_bei_leerer_eingabe():
    code, text = starte("", "1")
    assert code == 0
    assert "Verwendeter Jahresverbrauch: 2'500 kWh." in text


def test_vergleich_zeigt_differenz_und_hinweis():
    _, text = starte("2500", "3")
    assert "Modus «Vergleich» aktiviert: EKZ 2026 und IWB 2026 werden berechnet." in text
    assert "Differenz: CHF 312.15. Günstigerer Tarif: EKZ 2026." in text
    assert "Modellvergleich" in text
    assert "1'006.07" in text


def test_einzeltarif_iwb_ohne_vergleich():
    _, text = starte("2500", "2")
    assert "Gewählter Tarif: IWB 2026." in text
    assert "Differenz" not in text
    assert "Verbrauch pro Quartal" not in text


def test_ekz_zeigt_quartalsverteilung():
    _, text = starte("2500", "1")
    assert "Q1 = 625.00 kWh, Q2 = 625.00 kWh, Q3 = 625.00 kWh, Q4 = 625.00 kWh" in text


def test_ungueltige_eingaben_werden_wiederholt_abgefragt():
    code, text = starte("abc", "15000", "-1", "2500", "7", "1")
    assert code == 0
    assert text.count("Ungültige Eingabe.") == 3
    assert "Ungültige Auswahl." in text
    assert "Eingabe akzeptiert: 2'500 kWh." in text


def test_abbruch_mit_ctrl_d_ohne_traceback():
    def eingabe(_frage: str) -> str:
        raise EOFError

    assert cli.main(eingabe=eingabe, ausgabe=lambda _t: None) == 1


@pytest.mark.parametrize("text, erwartet", [("2500", 2500), (" 2'500 ", 2500), ("12 999", 12999), ("0", 0)])
def test_eingabe_mit_tausendertrennzeichen(text, erwartet):
    assert verbrauch_aus_text(text) == erwartet


@pytest.mark.parametrize("text", ["", "abc", "2500.5", "2,5", "-1", "13000"])
def test_ungueltige_texteingaben(text):
    with pytest.raises(UngueltigerVerbrauchError):
        verbrauch_aus_text(text)

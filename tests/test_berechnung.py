"""Testfaelle fuer die zentrale Berechnung.

Die Sollwerte stammen aus der verbindlichen Kontrollrechnung der
Aufgabenstellung und duerfen nicht angepasst werden.

Die Tests schlagen fehl, solange berechnung.py nicht implementiert ist.
Das ist beabsichtigt: sie dienen als ausfuehrbare Spezifikation.
"""

from decimal import Decimal

import pytest

from stromkostenrechner import berechnung
from stromkostenrechner.geld import runden
from stromkostenrechner.tarif_repository import lade_tarife, tarif_nach_id


@pytest.fixture
def tarife():
    return lade_tarife()


@pytest.fixture
def ekz(tarife):
    return tarif_nach_id(tarife, "EKZ_2026_BASIS")


@pytest.fixture
def iwb(tarife):
    return tarif_nach_id(tarife, "IWB_2026_SMALL_ET")


# Testfall 1: Kontrollrechnung EKZ bei 2500 kWh
def test_kontrollrechnung_ekz(ekz):
    ergebnis = berechnung.berechne(ekz, 2500)
    assert runden(ergebnis.energiekosten) == Decimal("301.38")
    assert runden(ergebnis.netznutzung) == Decimal("202.75")
    assert runden(ergebnis.weitere_abgaben) == Decimal("86.00")
    assert runden(ergebnis.grundtarif) == Decimal("38.88")
    assert runden(ergebnis.messtarif) == Decimal("64.92")
    assert runden(ergebnis.mwst_anteil) == Decimal("52.00")
    assert runden(ergebnis.total) == Decimal("693.93")


# Testfall 2: Kontrollrechnung IWB bei 2500 kWh
def test_kontrollrechnung_iwb(iwb):
    ergebnis = berechnung.berechne(iwb, 2500)
    assert runden(ergebnis.energiekosten) == Decimal("300.00")
    assert runden(ergebnis.netznutzung) == Decimal("376.25")
    assert runden(ergebnis.weitere_abgaben) == Decimal("271.50")
    assert runden(ergebnis.grundtarif) == Decimal("0.00")
    assert runden(ergebnis.messtarif) == Decimal("58.32")
    assert runden(ergebnis.mwst_anteil) == Decimal("75.39")
    assert runden(ergebnis.total) == Decimal("1006.07")


# Testfall 3: Vergleich der beiden Tarife
def test_vergleich_ekz_guenstiger(ekz, iwb):
    guenstiger, differenz = berechnung.vergleiche(
        berechnung.berechne(ekz, 2500),
        berechnung.berechne(iwb, 2500),
    )
    assert guenstiger.tarif.netzbetreiber == "EKZ"
    assert runden(differenz) == Decimal("312.15")


# Testfall 4: Verbrauch null, es bleiben nur die fixen Kosten
def test_verbrauch_null_nur_fixkosten(ekz):
    ergebnis = berechnung.berechne(ekz, 0)
    assert runden(ergebnis.energiekosten) == Decimal("0.00")
    assert runden(ergebnis.netznutzung) == Decimal("0.00")
    assert runden(ergebnis.weitere_abgaben) == Decimal("0.00")
    assert runden(ergebnis.total) == runden(ergebnis.grundtarif + ergebnis.messtarif)


# Testfall 5: Grenzen des gueltigen Eingabebereichs
@pytest.mark.parametrize("verbrauch", [0, 2500, 12999])
def test_gueltige_verbrauchswerte(verbrauch):
    berechnung.pruefe_verbrauch(verbrauch)


@pytest.mark.parametrize("verbrauch", [-1, 13000, 50000])
def test_ungueltige_verbrauchswerte(verbrauch):
    with pytest.raises(berechnung.UngueltigerVerbrauchError):
        berechnung.pruefe_verbrauch(verbrauch)


# Zusaetzliche Tests ueber die fuenf dokumentierten Testfaelle hinaus


def test_quartalsverteilung_2500():
    """Anforderung 4: bei 2500 kWh je 625 kWh pro Quartal."""
    assert berechnung.verbrauch_pro_quartal(2500) == Decimal("625")


def test_quartalsverteilung_ohne_ganzzahldivision():
    assert berechnung.verbrauch_pro_quartal(2501) == Decimal("625.25")


@pytest.mark.parametrize("wert", [True, 2500.0, "2500", None])
def test_nur_ganze_zahlen_gueltig(wert):
    with pytest.raises(berechnung.UngueltigerVerbrauchError):
        berechnung.pruefe_verbrauch(wert)


def test_berechne_lehnt_ungueltigen_verbrauch_ab(ekz):
    with pytest.raises(berechnung.UngueltigerVerbrauchError):
        berechnung.berechne(ekz, 13000)


def test_iwb_guenstiger_bei_kleinem_verbrauch(ekz, iwb):
    """Wegen des EKZ-Grundtarifs kippt der Vergleich zwischen 317 und 318 kWh."""
    guenstiger, _ = berechnung.vergleiche(berechnung.berechne(ekz, 317), berechnung.berechne(iwb, 317))
    assert guenstiger.tarif.netzbetreiber == "IWB"
    guenstiger, _ = berechnung.vergleiche(berechnung.berechne(ekz, 318), berechnung.berechne(iwb, 318))
    assert guenstiger.tarif.netzbetreiber == "EKZ"


def test_vergleich_reihenfolge_egal(ekz, iwb):
    a = berechnung.berechne(ekz, 2500)
    b = berechnung.berechne(iwb, 2500)
    assert berechnung.vergleiche(a, b) == berechnung.vergleiche(b, a)


def test_gleich_teuer_differenz_null(ekz):
    a = berechnung.berechne(ekz, 2500)
    guenstiger, differenz = berechnung.vergleiche(a, a)
    assert guenstiger is a
    assert differenz == 0


def test_total_ist_summe_der_bestandteile(iwb):
    e = berechnung.berechne(iwb, 12999)
    assert e.total == e.energiekosten + e.netznutzung + e.weitere_abgaben + e.grundtarif + e.messtarif

"""Tests fuer die zentrale Rundung."""

from decimal import Decimal

from stromkostenrechner.geld import formatieren, formatieren_kwh, runden


def test_rundet_kaufmaennisch_aufwaerts():
    """693.925 muss zu 693.93 werden, nicht zu 693.92.

    Dieser Fall tritt in der verbindlichen Kontrollrechnung tatsaechlich auf.
    """
    assert runden(Decimal("693.925")) == Decimal("693.93")


def test_rundet_halbe_rappen_konsistent():
    assert runden(Decimal("0.005")) == Decimal("0.01")
    assert runden(Decimal("0.015")) == Decimal("0.02")


def test_rundet_nicht_wenn_bereits_zwei_stellen():
    assert runden(Decimal("1006.07")) == Decimal("1006.07")


def test_formatieren_mit_tausendertrennzeichen():
    assert formatieren(Decimal("1006.07")) == "1'006.07"
    assert formatieren(Decimal("693.925")) == "693.93"
    assert formatieren(Decimal("0")) == "0.00"


def test_formatieren_kwh():
    assert formatieren_kwh(2500) == "2'500"
    assert formatieren_kwh(Decimal("625"), 2) == "625.00"
    assert formatieren_kwh(Decimal("3249.75"), 2) == "3'249.75"

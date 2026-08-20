"""Tests fuer die zentrale Rundung."""

from decimal import Decimal

from stromkostenrechner.geld import runden


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

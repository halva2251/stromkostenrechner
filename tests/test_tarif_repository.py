"""Tests fuer das Einlesen der CSV-Datei."""

from decimal import Decimal

import pytest

from stromkostenrechner.tarif_repository import (
    STANDARD_PFAD,
    TarifdatenError,
    lade_tarife,
    tarif_nach_id,
)


def test_liest_beide_tarife():
    assert len(lade_tarife()) == 2


def test_bom_landet_nicht_im_ersten_feld():
    """Bei encoding='utf-8' statt 'utf-8-sig' beginnt die ID mit \\ufeff."""
    tarife = lade_tarife()
    assert not tarife[0].tarif_id.startswith("\ufeff")
    assert tarife[0].tarif_id == "EKZ_2026_BASIS"


def test_semikolon_im_anfuehrungszeichen_zerlegt_zeile_nicht():
    """Das Feld 'annahme' des IWB-Datensatzes enthaelt ein Semikolon."""
    iwb = tarif_nach_id(lade_tarife(), "IWB_2026_SMALL_ET")
    assert iwb.messtarif_chf_monat == Decimal("4.86")
    assert iwb.quelle.startswith("https://")


def test_zahlen_sind_decimal_nicht_float():
    ekz = tarif_nach_id(lade_tarife(), "EKZ_2026_BASIS")
    assert isinstance(ekz.energie_q1_rp_kwh, Decimal)


def test_bezeichnung_nimmt_jahr_aus_csv():
    ekz = tarif_nach_id(lade_tarife(), "EKZ_2026_BASIS")
    assert ekz.bezeichnung == "EKZ 2026"


def test_fehlende_datei_meldet_tarifdatenfehler(tmp_path):
    with pytest.raises(TarifdatenError):
        lade_tarife(tmp_path / "gibt_es_nicht.csv")


def test_nettopreise_werden_abgelehnt(tmp_path):
    original = STANDARD_PFAD.read_text(encoding="utf-8-sig")
    kopie = tmp_path / "netto.csv"
    kopie.write_text(original.replace(";true;", ";false;", 1), encoding="utf-8-sig")
    with pytest.raises(TarifdatenError):
        lade_tarife(kopie)


def test_unbekannte_id_meldet_keyerror():
    with pytest.raises(KeyError):
        tarif_nach_id(lade_tarife(), "GIBT_ES_NICHT")

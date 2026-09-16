# Coderichtlinien und Firmenstandards

Gilt fuer das Repository stromkostenrechner (Gruppe IDPA_2026_b).
Dient zugleich als Deklaration der benuetzten Firmenstandards.

## Sprache
Bezeichner, Kommentare und Commit-Nachrichten auf Deutsch, ohne Umlaute
in Bezeichnern. Fachbegriffe wie in der Aufgabenstellung (Energiekosten,
Netznutzung, weitere Abgaben, Grundtarif, Messtarif).

## Formatierung
PEP 8, vier Leerzeichen, hoechstens 100 Zeichen pro Zeile.
Typannotationen bei allen oeffentlichen Funktionen.

## Kommentare
Kommentare erklaeren, warum etwas so geloest ist, nicht was der Code tut.

## Geldbetraege
Nur decimal.Decimal, nie float. Decimal immer aus Text erzeugen.
Gerundet wird nur in geld.py (ROUND_HALF_UP) und nur fuer die Ausgabe.
round() ist fuer Betraege verboten: round(693.925, 2) ergibt 693.92.

## Schichten
berechnung.py importiert weder cli, gui, praesentation noch tkinter und
liest keine Dateien. Texte fuer die Anzeige stehen in praesentation.py.

## Fehler
Erwartete Fehler als eigene Ausnahme (UngueltigerVerbrauchError,
TarifdatenError). Keine nackten except-Bloecke ausser in __main__.py.

## Commits
Format: <art>(<bereich>): <beschreibung>, z. B.
  feat(berechnung): MWST-Anteil aus Bruttobetrag herausrechnen
Ein Commit pro abgeschlossenem Schritt, alle Tests gruen.
Keine Nachrichten wie "update", "fix" oder "final" ohne Inhalt.

## Branches
main ist jederzeit lauffaehig. Arbeit auf feature/<name>, Zusammenfuehrung
per Pull Request mit Review durch eine zweite Person.
Abweichung im Vorprojekt: die Realisierung wurde direkt auf main committet.

## Tests
Neue Funktionen nur zusammen mit Tests. Die Sollwerte der Kontrollrechnung
duerfen nicht angepasst werden, um Tests gruen zu bekommen.

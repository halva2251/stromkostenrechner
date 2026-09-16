# Stromkostenrechner 2026

Vorprojekt IDPA, Klasse I3b, Gruppe IDPA_2026_b.
Applikation zur Berechnung und zum Vergleich jaehrlicher Stromkosten anhand
der Tarifdatensaetze EKZ 2026 und IWB 2026.

## Installation

Voraussetzung: Python 3.11 oder neuer (tkinter ist im Standardinstaller enthalten).

```bash
python --version          # muss >= 3.11 sein
python -m venv .venv
```

Virtuelle Umgebung aktivieren:

```bash
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # macOS / Linux
```

Abhaengigkeiten und die Applikation selbst installieren (der Befehl muss im
Projektordner ausgefuehrt werden, `requirements.txt` enthaelt `-e .`):

```bash
pip install -r requirements.txt
```

Unter Linux fehlt tkinter teilweise, zum Beispiel unter Ubuntu:
`sudo apt install python3-tk`. Die Konsolenversion funktioniert auch ohne.

## Starten

```bash
python -m stromkostenrechner            # grafische Oberflaeche
python -m stromkostenrechner --cli      # Konsolenversion
python -m stromkostenrechner --debug    # zusaetzliche Protokollausgabe
```

Die Applikation laeuft ohne Internetverbindung. Die Tarifdaten liegen
unveraendert unter `data/Tarifdaten_Stromkosten_2026.csv`.

## Tests

```bash
pytest
```

## Projektstruktur

| Pfad | Inhalt |
| --- | --- |
| `src/stromkostenrechner/geld.py` | Geldtyp und zentrale Rundung |
| `src/stromkostenrechner/modelle.py` | Datenklassen Tarif und Berechnungsergebnis |
| `src/stromkostenrechner/tarif_repository.py` | Einlesen der CSV-Datei |
| `src/stromkostenrechner/berechnung.py` | Berechnungslogik, ohne Ein- und Ausgabe |
| `src/stromkostenrechner/praesentation.py` | Eingabe umwandeln, Ausgabetexte, gemeinsam fuer CLI und GUI |
| `src/stromkostenrechner/cli.py` | Konsolenoberflaeche |
| `src/stromkostenrechner/gui.py` | tkinter-Oberflaeche |
| `tests/` | Unit-Tests |
| `data/` | Tarifdaten, unveraendert uebernommen |
| `docs/` | Entscheide und Coderichtlinien |

Die Berechnungslogik in `berechnung.py` kennt weder Konsole noch GUI. Beide
Oberflaechen rufen dieselben Funktionen auf.

## Dokumentation

Die Projektdokumentation wird ausserhalb dieses Repositories gefuehrt und als
PDF abgegeben. Dieses Repository enthaelt den Quellcode, die Tarifdaten und
die Startanleitung.

# Einnahmen- & Kostenrechner (Streamlit)

**Update v2:** Eingaben im Data-Editor werden jetzt sofort übernommen (kein „zweiter Versuch“ nötig).
Außerdem wird ein Datei-Import nur **einmal pro Datei** ausgeführt, damit man danach sauber manuell anpassen kann.

## Features

- Flexible **Einnahmen-Kalkulation** (Positionen, Preise, Mengen; Zeilen dynamisch)
- **Betrachtungshorizont**: Arbeitstage / Wochen / Monate / Custom (Tage → Arbeitstage)
- **Mitarbeiteranzahl** frei wählbar, Kosten je MA pro Arbeitstag × Arbeitstage
- Fixkosten & sonstige variable Kosten
- Ergebnis & Marge
- Szenario Export/Import (JSON)
- Optionaler CSV/XLSX-Import (Vorbelegung typischer Mengen-Spalten)

## Installation

```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## Start

```bash
streamlit run app.py
```

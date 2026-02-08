# Einnahmen- & Kostenrechner (Streamlit)

Diese Streamlit-App erlaubt dir:

- **Einnahmen** zu berechnen: du legst **Mengen je Position** selbst fest (und kannst **Preise** überschreiben).
- **Betrachtungshorizont** zu wählen: Arbeitstage / Wochen / Monate / Custom (Tage → in Arbeitstage umgerechnet).
- **Ausgaben** zu berechnen: Anzahl Mitarbeiter frei wählbar, Kosten pro Arbeitstag je Mitarbeiter, plus Fixkosten & sonstige variable Kosten.
- **Einnahmen vs. Ausgaben**: Ergebnis und Marge werden automatisch berechnet.
- **Szenarien** als JSON exportieren/importieren (für Vergleiche, Kolonne vs. 2er-Team etc.).
- Optional: **CSV/XLSX importieren** (z. B. Leistungsübersichten) um Mengen vorzubefüllen (sofern Spalten erkannt werden).

## Installation

```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

pip install -r requirements.txt
```

## Start

```bash
streamlit run app.py
```

## Hinweise

- Die Default-Preise entsprechen den im Konditionsblatt (Anlage 3, gültig ab 01.07.2024) genannten Werten.
- Für andere Regionen / spätere Preisstände: einfach in der Tabelle überschreiben oder eigene Positionen hinzufügen.
- Import erkennt (falls vorhanden) typische Spaltennamen wie `Montagen`, `Ablesungen`, `Wartungen`, `Anfahrten Tarif 1-4`, `Regieleistung in Min.`

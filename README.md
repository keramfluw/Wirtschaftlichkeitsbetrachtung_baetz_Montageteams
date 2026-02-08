# Einnahmen- & Kostenrechner (Streamlit) – v3

**Fix für „erst beim zweiten Mal“ in der Mengen-Spalte:**
- Der `st.data_editor` wird jetzt als **Single Source of Truth** direkt über seinen `key` in `st.session_state` geführt.
- Dadurch wird der Editor-State beim ersten Enter/Rerun nicht mehr durch ein parallel gepflegtes DataFrame „zurückgesetzt“.

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

## Tipp zur Bedienung (Streamlit-Standard)
- Werte werden sicher übernommen, sobald die Zelle **verlassen** wird (z. B. Klick außerhalb).
- Mit v3 sollten auch schnelle Edits mit Enter zuverlässig stehen bleiben.

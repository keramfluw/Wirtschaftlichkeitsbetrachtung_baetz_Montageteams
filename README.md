# Einnahmen- & Kostenrechner (Streamlit) – v4 (Bugfix)

## Was war kaputt?

In Streamlit 1.54 (wie in deinen Logs) ist es **nicht erlaubt**, einen Wert direkt über
`st.session_state["<widget_key>"] = ...` zu setzen, wenn `<widget_key>` gleichzeitig als `key=...`
für ein Widget (z. B. `st.data_editor`) verwendet wird. Das führt zu:

- `StreamlitValueAssignmentNotAllowedError: Values for the widget with key ... cannot be set using st.session_state`

Genau das ist in deinen Logs sichtbar. fileciteturn1file0

## Fix

- Der Dataframe wird unter **positions_df** / **employees_df** gespeichert.
- Die Widget-Keys (`positions_editor`, `employees_editor`) werden **nicht** direkt beschrieben.
- Der Editor gibt ein Dataframe zurück, das wir in **positions_df** speichern.

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

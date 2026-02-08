import streamlit as st
import pandas as pd
import json
from io import StringIO

st.set_page_config(page_title="Einnahmen- & Kostenrechner", layout="wide")

st.title("Einnahmen- & Kostenrechner (Thermomess / BAETZ – flexibel)")

# Defaults (aus Konditionsblatt, gültig ab 01.07.2024 – Bayern)
DEFAULT_POSITIONS = [
    {"Position": "Ablesung je HKV, WZ, WMZ", "Einheit": "Stk", "Preis_EUR": 1.05, "Menge": 0},
    {"Position": "Mindestsatz Hauptablesung (nur Kleinanlagen <20 Ablesungen)", "Einheit": "pauschal", "Preis_EUR": 21.00, "Menge": 0},
    {"Position": "Zwischenablesung inkl. Anfahrt (ZWABL)", "Einheit": "Stk", "Preis_EUR": 34.10, "Menge": 0},
    {"Position": "Nachablesung inkl. Anfahrt (NABL)", "Einheit": "Stk", "Preis_EUR": 34.10, "Menge": 0},
    {"Position": "Schweiß-/Schraubmontage/Demontage HKV, Aufmaß, Aufnahme", "Einheit": "Stk", "Preis_EUR": 4.30, "Menge": 0},
    {"Position": "Anfahrt Hauptablesung je Anlage (auch HKV-Montagen & RWM-Wartungen)", "Einheit": "Stk", "Preis_EUR": 21.30, "Menge": 0},
    {"Position": "Anfahrt 2. Sammeltermin (einmalig)", "Einheit": "Stk", "Preis_EUR": 21.30, "Menge": 0},
    {"Position": "Anfahrt Tarif 1 (W01)", "Einheit": "Stk", "Preis_EUR": 21.30, "Menge": 0},
    {"Position": "Anfahrt Tarif 2 (W02)", "Einheit": "Stk", "Preis_EUR": 30.50, "Menge": 0},
    {"Position": "Anfahrt Tarif 3 (W03)", "Einheit": "Stk", "Preis_EUR": 42.00, "Menge": 0},
    {"Position": "Anfahrt Tarif 4 (W04)", "Einheit": "Stk", "Preis_EUR": 57.80, "Menge": 0},
    {"Position": "Messkapselzähler (Neumontage/Austausch inkl. Ablesung & Aushang)", "Einheit": "Stk", "Preis_EUR": 10.50, "Menge": 0},
    {"Position": "Verschraubungszähler (Neumontage/Austausch inkl. Ablesung & Aushang)", "Einheit": "Stk", "Preis_EUR": 12.70, "Menge": 0},
    {"Position": "Ventilanschluss-/Badewannenzähler (Neumontage/Austausch)", "Einheit": "Stk", "Preis_EUR": 17.10, "Menge": 0},
    {"Position": "Mehrstrahl-WZ ab QN 3,5", "Einheit": "Stk", "Preis_EUR": 17.10, "Menge": 0},
    {"Position": "Wohnungs-WMZ, Kapsel-WMZ", "Einheit": "Stk", "Preis_EUR": 16.00, "Menge": 0},
    {"Position": "Mehrstrahl-WMZ ab QN 3,5", "Einheit": "Stk", "Preis_EUR": 30.30, "Menge": 0},
    {"Position": "Montage RWM inkl. Funktionsprüfung (DIN 14676) inkl. Doku", "Einheit": "Stk", "Preis_EUR": 5.50, "Menge": 0},
    {"Position": "Wartung RWM Sicht-/Funktionsprüfung (DIN 14676) inkl. Doku", "Einheit": "Stk", "Preis_EUR": 1.10, "Menge": 0},
    {"Position": "Nachträgliche RWM-Wartung inkl. Anfahrt (NARWM)", "Einheit": "Stk", "Preis_EUR": 34.10, "Menge": 0},
    {"Position": "Regiearbeit (je 15 Min; 44 €/h)", "Einheit": "15 Min", "Preis_EUR": 11.00, "Menge": 0},
]

def money(x: float) -> str:
    try:
        return f"{x:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return str(x)

def to_number(val):
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip()
    if s == "":
        return 0.0
    s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except Exception:
        return 0.0

# -----------------------------
# Session init
# -----------------------------
if "positions_df" not in st.session_state:
    st.session_state.positions_df = pd.DataFrame(DEFAULT_POSITIONS)

if "employees_df" not in st.session_state:
    st.session_state.employees_df = pd.DataFrame(
        [
            {"Mitarbeiter": "MA 1", "Kosten_pro_Arbeitstag_EUR": 0.0},
            {"Mitarbeiter": "MA 2", "Kosten_pro_Arbeitstag_EUR": 0.0},
        ]
    )

# Sidebar: Betrachtungshorizont
with st.sidebar:
    st.header("Betrachtungshorizont")
    horizon_mode = st.selectbox("Modus", ["Arbeitstage", "Wochen", "Monate", "Custom (Tage)"], index=0, key="horizon_mode")
    if horizon_mode == "Arbeitstage":
        workdays = st.number_input("Arbeitstage", min_value=0, value=20, step=1, key="workdays_input")
        horizon_label = f"{workdays} Arbeitstage"
    elif horizon_mode == "Wochen":
        weeks = st.number_input("Wochen", min_value=0, value=4, step=1, key="weeks_input")
        workdays = weeks * 5
        horizon_label = f"{weeks} Wochen (~{workdays} Arbeitstage)"
    elif horizon_mode == "Monate":
        months = st.number_input("Monate", min_value=0, value=1, step=1, key="months_input")
        workdays = months * 20
        horizon_label = f"{months} Monate (~{workdays} Arbeitstage)"
    else:
        days = st.number_input("Tage", min_value=0, value=30, step=1, key="days_input")
        workdays = int(round(days * 5 / 7))
        horizon_label = f"{days} Tage (~{workdays} Arbeitstage)"

    st.caption(f"Aktiver Horizont: **{horizon_label}**")
    st.divider()
    st.header("Szenario")
    st.caption("Du kannst den aktuellen Zustand als JSON exportieren und später wieder importieren.")

# Optional: Import (CSV/XLSX) zur Vorbelegung der Mengen
with st.expander("Optional: Datei-Import (CSV/XLSX) zum Vorbelegen von Mengen", expanded=False):
    st.write(
        "Wenn du eine Leistungsübersicht hochlädst, kannst du Mengen automatisch übernehmen. "
        "Die App versucht typische Spalten zu erkennen (z. B. Montagen, Ablesungen, Wartungen, "
        "Anfahrten Tarif 1–4, Regieleistung in Min.)."
    )
    upl = st.file_uploader("Datei auswählen (CSV oder XLSX)", type=["csv", "xlsx"], key="upl_file")
    import_info = st.empty()

def maybe_import(upl_file):
    # Wichtig: Import nur EINMAL pro Datei ausführen, damit man danach manuell editieren kann,
    # ohne dass beim nächsten Rerun die Werte wieder überschrieben werden.
    if upl_file is None:
        return
    file_id = f"{upl_file.name}-{upl_file.size}"
    if st.session_state.get("last_import_file_id") == file_id:
        return  # schon importiert
    try:
        if upl_file.name.lower().endswith(".csv"):
            raw = upl_file.getvalue().decode("utf-8", errors="ignore")
            sep = ";" if raw.count(";") >= raw.count(",") else ","
            df_in = pd.read_csv(StringIO(raw), sep=sep)
        else:
            df_in = pd.read_excel(upl_file)

        df_in.columns = [c.strip() for c in df_in.columns]
        cols = list(df_in.columns)
        colmap = {c.lower(): c for c in cols}

        def pick(*names):
            for n in names:
                if n.lower() in colmap:
                    return colmap[n.lower()]
            return None

        c_mont = pick("Montagen")
        c_abl = pick("Ablesungen")
        c_wart = pick("Wartungen")
        c_a1 = pick("Anfahrten Tarif 1", "Anfahrten Tarif1", "Anfahrt Tarif 1")
        c_a2 = pick("Anfahrten Tarif 2", "Anfahrten Tarif2", "Anfahrt Tarif 2")
        c_a3 = pick("Anfahrten Tarif 3", "Anfahrten Tarif3", "Anfahrt Tarif 3")
        c_a4 = pick("Anfahrten Tarif 4", "Anfahrten Tarif4", "Anfahrt Tarif 4")
        c_regmin = pick("Regieleistung in Min.", "Regieleistung in Min", "Regie in Min", "Regieleistung")

        def sum_col(c):
            if c is None:
                return 0.0
            return pd.to_numeric(df_in[c], errors="coerce").fillna(0).sum()

        sums = {
            "Schweiß-/Schraubmontage/Demontage HKV, Aufmaß, Aufnahme": sum_col(c_mont),
            "Ablesung je HKV, WZ, WMZ": sum_col(c_abl),
            "Wartung RWM Sicht-/Funktionsprüfung (DIN 14676) inkl. Doku": sum_col(c_wart),
            "Anfahrt Tarif 1 (W01)": sum_col(c_a1),
            "Anfahrt Tarif 2 (W02)": sum_col(c_a2),
            "Anfahrt Tarif 3 (W03)": sum_col(c_a3),
            "Anfahrt Tarif 4 (W04)": sum_col(c_a4),
        }
        if c_regmin is not None:
            reg_min = sum_col(c_regmin)
            sums["Regiearbeit (je 15 Min; 44 €/h)"] = reg_min / 15.0

        df_pos = st.session_state.positions_df.copy()
        for k, v in sums.items():
            mask = df_pos["Position"] == k
            if mask.any():
                df_pos.loc[mask, "Menge"] = float(v)

        st.session_state.positions_df = df_pos
        st.session_state.last_import_file_id = file_id
        import_info.success("Import erfolgreich: Mengen wurden vorbefüllt. (Ab jetzt kannst du manuell ändern.)")
    except Exception as e:
        import_info.error(f"Import fehlgeschlagen: {e}")

maybe_import(upl)

# Einnahmen
st.subheader("1) Einnahmen (Positionen & Mengen)")
colA, colB = st.columns([2, 1], gap="large")

with colA:
    st.caption("Tipp: Nach Eingabe kurz außerhalb der Zelle klicken (Commit).")
    edited_positions = st.data_editor(
        st.session_state.positions_df,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key="positions_editor",
        column_config={
            "Position": st.column_config.TextColumn(width="large"),
            "Einheit": st.column_config.TextColumn(width="small"),
            "Preis_EUR": st.column_config.NumberColumn(format="%.2f", step=0.05),
            "Menge": st.column_config.NumberColumn(step=1),
        },
    )
    # wichtig: NICHT wieder neu bauen; einfach übernehmen
    st.session_state.positions_df = edited_positions.copy()

with colB:
    df_pos = st.session_state.positions_df.copy()
    df_pos["Preis_EUR"] = df_pos["Preis_EUR"].apply(to_number)
    df_pos["Menge"] = df_pos["Menge"].apply(to_number)
    df_pos["Umsatz_EUR"] = df_pos["Preis_EUR"] * df_pos["Menge"]
    total_revenue = float(df_pos["Umsatz_EUR"].sum())

    st.metric("Einnahmen gesamt", money(total_revenue))
    st.write("**Top-Positionen (nach Umsatz):**")
    top = df_pos.sort_values("Umsatz_EUR", ascending=False).head(8)[["Position", "Umsatz_EUR"]]
    top["Umsatz_EUR"] = top["Umsatz_EUR"].apply(money)
    st.dataframe(top, use_container_width=True, hide_index=True)

# Ausgaben
st.subheader("2) Ausgaben (Mitarbeiter, Arbeitstage, Fixkosten)")
c1, c2, c3 = st.columns([1.2, 1.2, 1.0], gap="large")

with c1:
    num_employees = st.number_input("Anzahl Mitarbeiter", min_value=0, value=max(2, len(st.session_state.employees_df)), step=1, key="num_employees")
    emp = st.session_state.employees_df.copy()

    # resize to num_employees
    if len(emp) < num_employees:
        for i in range(len(emp) + 1, num_employees + 1):
            emp = pd.concat([emp, pd.DataFrame([{"Mitarbeiter": f"MA {i}", "Kosten_pro_Arbeitstag_EUR": 0.0}])], ignore_index=True)
    elif len(emp) > num_employees:
        emp = emp.iloc[:num_employees].reset_index(drop=True)

    edited_emp = st.data_editor(
        emp,
        num_rows="fixed",
        use_container_width=True,
        hide_index=True,
        key="employees_editor",
        column_config={
            "Mitarbeiter": st.column_config.TextColumn(width="medium"),
            "Kosten_pro_Arbeitstag_EUR": st.column_config.NumberColumn(
                format="%.2f",
                step=5.0,
                help="z. B. Lohnkosten + Nebenkosten + Fahrzeug/Overhead je Arbeitstag",
            ),
        },
    )
    st.session_state.employees_df = edited_emp.copy()

with c2:
    st.write("**Arbeitstage (aus Horizont):**")
    st.metric("Arbeitstage", int(workdays))
    fixed_costs = st.number_input("Fixkosten im Horizont (EUR)", min_value=0.0, value=0.0, step=50.0, key="fixed_costs")
    variable_other = st.number_input("Sonstige variable Kosten (EUR)", min_value=0.0, value=0.0, step=50.0, key="variable_other")

with c3:
    emp2 = st.session_state.employees_df.copy()
    if len(emp2) == 0:
        total_labor = 0.0
        emp2["Kosten_Horizont_EUR"] = []
    else:
        emp2["Kosten_pro_Arbeitstag_EUR"] = emp2["Kosten_pro_Arbeitstag_EUR"].apply(to_number)
        emp2["Kosten_Horizont_EUR"] = emp2["Kosten_pro_Arbeitstag_EUR"] * float(workdays)
        total_labor = float(emp2["Kosten_Horizont_EUR"].sum())

    total_costs = total_labor + float(fixed_costs) + float(variable_other)
    profit = total_revenue - total_costs
    margin = (profit / total_revenue) if total_revenue != 0 else 0.0

    st.metric("Personalkosten (Horizont)", money(total_labor))
    st.metric("Gesamtkosten (Horizont)", money(total_costs))
    st.metric("Ergebnis (Einnahmen - Kosten)", money(profit))
    st.metric("Marge", f"{margin*100:,.1f} %".replace(",", "X").replace(".", ",").replace("X", "."))

with st.expander("Details: Umsatz- & Kosten-Tabelle", expanded=True):
    left, right = st.columns(2, gap="large")
    with left:
        df_show = df_pos.copy()
        df_show["Preis_EUR"] = df_show["Preis_EUR"].apply(money)
        df_show["Umsatz_EUR"] = df_show["Umsatz_EUR"].apply(money)
        st.write("**Einnahmen nach Position:**")
        st.dataframe(df_show[["Position", "Einheit", "Preis_EUR", "Menge", "Umsatz_EUR"]], use_container_width=True, hide_index=True)
    with right:
        emp_show = emp2.copy()
        if len(emp_show) == 0:
            emp_show = pd.DataFrame([{"Mitarbeiter": "—", "Kosten_pro_Arbeitstag_EUR": 0.0, "Kosten_Horizont_EUR": 0.0}])
        emp_show["Kosten_pro_Arbeitstag_EUR"] = emp_show["Kosten_pro_Arbeitstag_EUR"].apply(money)
        emp_show["Kosten_Horizont_EUR"] = emp_show["Kosten_Horizont_EUR"].apply(money)
        st.write("**Kosten nach Mitarbeiter:**")
        st.dataframe(emp_show[["Mitarbeiter", "Kosten_pro_Arbeitstag_EUR", "Kosten_Horizont_EUR"]], use_container_width=True, hide_index=True)
        st.write("**Zusatzkosten:**")
        st.write(f"- Fixkosten: {money(float(fixed_costs))}")
        st.write(f"- Sonstige variable Kosten: {money(float(variable_other))}")

# Szenario Export/Import
scenario = {
    "horizon_mode": horizon_mode,
    "workdays": int(workdays),
    "positions": st.session_state.positions_df.to_dict(orient="records"),
    "employees": st.session_state.employees_df.to_dict(orient="records"),
    "fixed_costs": float(fixed_costs),
    "variable_other": float(variable_other),
}

with st.sidebar:
    scenario_bytes = json.dumps(scenario, ensure_ascii=False, indent=2).encode("utf-8")
    st.download_button(
        label="Szenario als JSON herunterladen",
        data=scenario_bytes,
        file_name="szenario.json",
        mime="application/json",
        use_container_width=True,
    )
    up_scn = st.file_uploader("Szenario JSON importieren", type=["json"], key="scenario_upl")
    if up_scn is not None:
        try:
            scn = json.loads(up_scn.getvalue().decode("utf-8"))
            if "positions" in scn:
                st.session_state.positions_df = pd.DataFrame(scn["positions"])
                # reset editor widget so values show instantly
                st.session_state["positions_editor"] = st.session_state.positions_df
            if "employees" in scn:
                st.session_state.employees_df = pd.DataFrame(scn["employees"])
                st.session_state["employees_editor"] = st.session_state.employees_df
            if "fixed_costs" in scn:
                st.session_state["fixed_costs"] = float(scn["fixed_costs"])
            if "variable_other" in scn:
                st.session_state["variable_other"] = float(scn["variable_other"])
            st.success("Szenario importiert.")
        except Exception as e:
            st.error(f"Import fehlgeschlagen: {e}")

st.caption("Hinweis: Preise sind Defaultwerte; du kannst sie jederzeit anpassen.")

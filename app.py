"""Streamlit UI:  streamlit run app.py"""
import datetime as dt
import pandas as pd
import streamlit as st
import analytics as an
import storage as db

st.set_page_config(page_title="Trade Journal & P&L Analyzer", layout="wide")
con = db.connect()
page = st.sidebar.radio("Menu", ["Dashboard", "Add Trade", "Journal", "Import CSV"])
capital = st.sidebar.number_input("Starting capital", 1000.0, value=100000.0, step=1000.0)

if page == "Add Trade":
    st.header("Log a closed trade")
    with st.form("add"):
        c1, c2, c3 = st.columns(3)
        symbol = c1.text_input("Symbol (e.g. TCS)")
        side = c2.selectbox("Side", ["LONG", "SHORT"])
        qty = c3.number_input("Quantity", 1.0, value=10.0)
        entry = c1.number_input("Entry price", 0.01, value=100.0)
        exit_ = c2.number_input("Exit price", 0.01, value=105.0)
        fees = c3.number_input("Fees", 0.0, value=0.0)
        date = c1.date_input("Exit date", dt.date.today())
        strat = c2.text_input("Strategy")
        notes = c3.text_input("Notes")
        if st.form_submit_button("Save trade"):
            try:
                db.add_trade(con, symbol, side, qty, entry, exit_, date, fees, strat, notes)
                st.success(f"Saved. P&L = {an.trade_pnl(side, qty, entry, exit_, fees)}")
            except ValueError as e:
                st.error(str(e))

elif page == "Journal":
    st.header("Trade Journal")

    rows = db.list_trades(con)

    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)

        st.subheader("Edit Trade")

        trade_ids = [r["id"] for r in rows]
        selected_id = st.selectbox("Select Trade ID", trade_ids)

        trade = next(r for r in rows if r["id"] == selected_id)

        with st.form("edit_trade"):
            c1, c2, c3 = st.columns(3)

            symbol = c1.text_input("Symbol", trade["symbol"])
            side = c2.selectbox(
                "Side", ["LONG", "SHORT"],
                index=["LONG", "SHORT"].index(trade["side"])
            )
            qty = c3.number_input(
                "Quantity", min_value=0.01,
                value=float(trade["qty"])
            )

            entry = c1.number_input(
                "Entry Price", min_value=0.01,
                value=float(trade["entry_price"])
            )
            exit_ = c2.number_input(
                "Exit Price", min_value=0.01,
                value=float(trade["exit_price"])
            )
            fees = c3.number_input(
                "Fees", min_value=0.0,
                value=float(trade["fees"])
            )

            date = c1.date_input(
                "Exit Date",
                dt.date.fromisoformat(trade["exit_date"])
            )
            strat = c2.text_input(
                "Strategy", trade["strategy"]
            )
            notes = c3.text_input(
                "Notes", trade["notes"]
            )

            if st.form_submit_button("Update Trade"):
                try:
                    db.update_trade(
                        con, selected_id, symbol, side,
                        qty, entry, exit_, date,
                        fees, strat, notes
                    )
                    st.success("Trade updated successfully!")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))

        st.divider()
        st.subheader("Delete Trade")

        tid = st.selectbox("Select Trade to Delete", trade_ids)

        if st.button("Delete Selected Trade"):
            if db.delete_trade(con, int(tid)):
                st.success("Trade deleted!")
                st.rerun()

    else:
        st.info("No trades available. Add a trade first.")

elif page == "Import CSV":
    st.header("Import Trades from CSV")

    up = st.file_uploader("Choose CSV file", type="csv")

    if up and st.button("Import Trades"):
        try:
            with open("_upload.csv", "wb") as f:
                f.write(up.getbuffer())

            imported, errors = db.import_csv(con, "_upload.csv")

            st.success(
                f"Successfully imported {imported} trades!"
            )

            if errors:
                st.warning(
                    f"{len(errors)} rows could not be imported."
                )

                for error in errors:
                    st.error(error)

        except (ValueError, OSError) as e:
            st.error(str(e))
else:
    st.header("Dashboard")
    rows = db.list_trades(con)
    if not rows:
        st.info("No trades yet. Add one or import sample_trades.csv.")
        st.stop()
    df = pd.DataFrame(rows)
    pnls = df["pnl"].tolist()
    s = an.summarize(pnls, capital)
    k = st.columns(5)
    k[0].metric("Total P&L", s["total_pnl"])
    k[1].metric("Return %", s["total_return_pct"])
    k[2].metric("Win rate %", s["win_rate_pct"])
    k[3].metric("Max drawdown %", s["max_drawdown_pct"])
    k[4].metric("Profit factor", s["profit_factor"])
    eq = an.equity_curve(pnls, capital)
    a, b = st.columns(2)
    a.subheader("Equity curve"); a.line_chart(eq)
    b.subheader("Drawdown %"); b.area_chart(an.drawdown_series(eq))
    c, d = st.columns(2)
    c.subheader("P&L by symbol"); c.bar_chart(df.groupby("symbol")["pnl"].sum())
    df["month"] = df["exit_date"].str[:7]
    d.subheader("Monthly P&L"); d.bar_chart(df.groupby("month")["pnl"].sum())
    st.subheader("All metrics"); st.json(s)

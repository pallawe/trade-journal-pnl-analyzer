"""Streamlit UI:  streamlit run app.py"""
import datetime as dt
import pandas as pd
import streamlit as st
import analytics as an
import storage as db
import auth

st.set_page_config(
    page_title="Trade Journal | Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional dark theme styling
st.markdown("""
<style>
    .stApp {
        background-color: #0B1120;
        color: #E5E7EB;
    }

    section[data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #263244;
    }

    section[data-testid="stSidebar"] h1 {
        color: #F8FAFC;
    }

    h1, h2, h3 {
        color: #F8FAFC !important;
    }

    div[data-testid="stMetric"] {
        background-color: #172235;
        border: 1px solid #29374D;
        padding: 18px;
        border-radius: 12px;
    }

    div[data-testid="stMetricLabel"] {
        color: #9CA3AF;
    }

    div[data-testid="stMetricValue"] {
        color: #F8FAFC;
    }

    .stButton > button {
        background-color: #16A34A;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 8px 18px;
        font-weight: 600;
    }

    .stButton > button:hover {
        background-color: #15803D;
        color: white;
        border: none;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #29374D;
        border-radius: 10px;
    }

    hr {
        border-color: #29374D;
    }
</style>
""", unsafe_allow_html=True)

# Authentication check
if "user" not in st.session_state:
    auth.show_auth_page()
    st.stop()

# Connect to database only after login
user_id = st.session_state["user"].id
con = db.connect()

with st.sidebar:
    st.markdown("# 📈 TradePro")
    st.caption("Your personal trading analytics platform")
    st.caption(f"Logged in as:{st.session_state['user'].email}")
    st.divider()

    page = st.radio(
        "NAVIGATION",
        ["Dashboard", "Add Trade", "Journal", "Import CSV"],
        label_visibility="visible"
    )

    st.divider()
    capital = st.number_input(
        "Starting capital (₹)",
        min_value=1000.0,
        value=100000.0,
        step=1000.0
    )

    st.divider()

    if st.button("Log Out", use_container_width=True):
        auth.sign_out()
        st.session_state.pop("user", None)
        st.rerun()

st.markdown(
    "<h1>Trade Journal & P&L Analyzer</h1>"
    "<p style='color:#94A3B8;'>Track your trades. Understand your performance. "
    "Improve your strategy.</p>",
    unsafe_allow_html=True
)
st.divider()

if page == "Add Trade":
    st.subheader("➕ Add a New Trade")
    st.caption("Record your completed trade and track its performance.")

    st.markdown("### Trade Information")

    with st.form("add"):
        c1, c2 = st.columns(2)

        with c1:
            symbol = st.text_input(
                "Stock / Asset Symbol",
                placeholder="e.g. TCS, INFY, RELIANCE"
            )

            side = st.selectbox(
                "Trade Direction",
                ["LONG", "SHORT"]
            )

            qty = st.number_input(
                "Quantity",
                min_value=0.01,
                value=10.0,
                step=1.0
            )

        with c2:
            date = st.date_input(
                "Exit Date",
                dt.date.today()
            )

            strat = st.selectbox(
                "Trading Strategy",
                [
                    "Intraday",
                    "Swing",
                    "Breakout",
                    "Reversal",
                    "Scalping",
                    "Other"
                ]
            )

            notes = st.text_input(
                "Trade Notes",
                placeholder="Describe your trade..."
            )

        st.divider()
        st.markdown("### Execution Details")

        p1, p2, p3 = st.columns(3)

        entry = p1.number_input(
            "Entry Price (₹)",
            min_value=0.01,
            value=100.0
        )

        exit_ = p2.number_input(
            "Exit Price (₹)",
            min_value=0.01,
            value=105.0
        )

        fees = p3.number_input(
            "Fees (₹)",
            min_value=0.0,
            value=0.0
        )

        submitted = st.form_submit_button(
            "💾 Save Trade",
            use_container_width=True
        )

        if submitted:
            try:
                db.add_trade(
                    con, user_id,symbol, side, qty,
                    entry, exit_, date, fees,
                    strat, notes
                )

                pnl = an.trade_pnl(
                    side, qty, entry, exit_, fees
                )

                st.success(
                    f"Trade saved successfully! Net P&L: ₹{pnl:,.2f}"
                )

            except ValueError as e:
                st.error(str(e))
elif page == "Journal":
    st.header("📒 Trade Journal")

    rows = db.list_trades(con, user_id)

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
                        con, selected_id, user_id, symbol, side,
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
            if db.delete_trade(con, int(tid), user_id):
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

            imported, errors = db.import_csv(con, "_upload.csv", user_id)

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
    st.subheader("📊 Performance Overview")

    rows = db.list_trades(con, user_id)

    if not rows:
        st.info("No trades yet. Add a trade or import sample_trades.csv.")
        st.stop()

    df = pd.DataFrame(rows)
    pnls = df["pnl"].tolist()
    s = an.summarize(pnls, capital)

    # Trade statistics
    total_trades = len(df)
    winning_trades = int((df["pnl"] > 0).sum())
    losing_trades = int((df["pnl"] < 0).sum())

    # Main performance metrics
    st.markdown("### Financial Performance")

    k1, k2, k3 = st.columns(3)

    k1.metric("Net P&L", f"₹{s['total_pnl']:,.2f}")
    k2.metric("Return", f"{s['total_return_pct']:.2f}%")
    k3.metric("Win Rate", f"{s['win_rate_pct']:.2f}%")

    k4, k5 = st.columns(2)

    k4.metric("Max Drawdown", f"{s['max_drawdown_pct']:.2f}%")
    k5.metric("Profit Factor", f"{s['profit_factor']:.2f}") 
    
    st.divider()

    # Trade statistics
    st.markdown("### Trade Statistics")

    a, b, c = st.columns(3)

    a.metric("Total Trades", total_trades)
    b.metric("Winning Trades", winning_trades)
    c.metric("Losing Trades", losing_trades)

    st.divider()

    # Performance charts
    st.markdown("### Performance Analytics")

    eq = an.equity_curve(pnls, capital)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📈 Equity Curve")
        st.caption("Tracks how your trading capital changes after each trade.")
        st.line_chart(eq, use_container_width=True)

    with col2:
        st.markdown("#### 📉 Drawdown Analysis")
        st.caption("Shows how far your portfolio falls below its previous peak.")
        st.area_chart(
            an.drawdown_series(eq),
            use_container_width=True
        )

    col3, col4 = st.columns(2)

    with col3:
        st.markdown("#### 💹 P&L by Symbol")
        st.caption("Compares total profit or loss generated by each traded stock.")
        symbol_pnl = df.groupby("symbol")["pnl"].sum().sort_values()
        st.bar_chart(symbol_pnl, use_container_width=True)

    with col4:
        st.markdown("#### 📅 Monthly P&L")
        st.caption("Tracks your trading profit or loss month by month.")
        df["month"] = df["exit_date"].str[:7]
        monthly_pnl = df.groupby("month")["pnl"].sum().sort_index()
        st.bar_chart(monthly_pnl, use_container_width=True)

    st.divider()

    # Recent trades
    st.markdown("### 🕒 Recent Trades")

    recent = df.sort_values(
    ["exit_date", "id"],
    ascending=False
).head(5)

    display_columns = [
        "symbol",
        "side",
        "qty",
        "entry_price",
        "exit_price",
        "pnl",
        "exit_date"
    ]

    st.dataframe(
        recent[display_columns],
        use_container_width=True,
        hide_index=True
    )
    
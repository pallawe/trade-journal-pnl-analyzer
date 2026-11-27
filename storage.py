"""PostgreSQL persistence layer for Trade Journal."""

import csv
import streamlit as st
import pg8000.dbapi

from urllib.parse import urlsplit, unquote
from analytics import trade_pnl


def connect():
    """Connect to Supabase PostgreSQL database."""

    url = st.secrets["DATABASE_URL"]
    parsed = urlsplit(url)

    con = pg8000.dbapi.connect(
        user=unquote(parsed.username),
        password=unquote(parsed.password),
        host=parsed.hostname,
        port=parsed.port or 5432,
        database=parsed.path.lstrip("/"),
        ssl_context=True
    )

    return con


def add_trade(con, user_id, symbol, side, qty, entry, exit_, exit_date,
              fees=0.0, strategy="", notes=""):

    if not str(symbol).strip():
        raise ValueError("symbol is required")

    pnl = trade_pnl(side, qty, entry, exit_, fees)

    cur = con.cursor()

    cur.execute(
        """INSERT INTO trades
        (symbol, side, qty, entry_price, exit_price, fees,
         exit_date, strategy, notes, pnl)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id""",
        (user_id,symbol.strip().upper(), side.upper(), qty, entry,
         exit_, fees, str(exit_date), strategy, notes, pnl)
    )

    trade_id = cur.fetchone()[0]
    con.commit()
    cur.close()

    return trade_id


def list_trades(con, user_id):

    cur = con.cursor()

    cur.execute(
        "SELECT * FROM trades WHERE user_id = %s ORDER BY exit_date, id", (user_id,)
    )

    columns = [desc[0] for desc in cur.description]
    rows = cur.fetchall()

    result = [dict(zip(columns, row)) for row in rows]

    cur.close()
    return result

def delete_trade(con, trade_id, user_id):

    cur = con.cursor()

    cur.execute(
        "DELETE FROM trades WHERE id = %s AND user_id = %s",
        (trade_id, user_id)
    )

    deleted = cur.rowcount > 0

    con.commit()
    cur.close()

    return deleted


def update_trade(con, trade_id, user_id, symbol, side, qty, entry, exit_,
                 exit_date, fees=0.0, strategy="", notes=""):

    if not str(symbol).strip():
        raise ValueError("symbol is required")

    pnl = trade_pnl(side, qty, entry, exit_, fees)

    cur = con.cursor()

    cur.execute(
        """UPDATE trades
           SET symbol=%s, side=%s, qty=%s, entry_price=%s,
               exit_price=%s, fees=%s, exit_date=%s,
               strategy=%s, notes=%s, pnl=%s
           WHERE id=%s""",
        (symbol.strip().upper(), side.upper(), qty, entry,
         exit_, fees, str(exit_date), strategy, notes,
         pnl, trade_id, user_id)
    )

    updated = cur.rowcount > 0

    con.commit()
    cur.close()

    return updated



    

def import_csv(con, path, user_id):
    """Import trades from a CSV file."""

    count = 0
    errors = []

    required = [
        "symbol", "side", "qty", "entry_price",
        "exit_price", "exit_date"
    ]

    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        if not reader.fieldnames:
            raise ValueError("CSV file is empty or has no headers.")

        reader.fieldnames = [
            h.strip().lower() for h in reader.fieldnames
        ]

        missing = [
            col for col in required
            if col not in reader.fieldnames
        ]

        if missing:
            raise ValueError(
                f"Missing CSV columns: {', '.join(missing)}"
            )

        for row_num, r in enumerate(reader, start=2):

            if not any(r.values()):
                continue

            try:
                add_trade(
                    con,
                    user_id,
                    r["symbol"],
                    r["side"],
                    float(r["qty"]),
                    float(r["entry_price"]),
                    float(r["exit_price"]),
                    r["exit_date"],
                    float(r.get("fees") or 0),
                    r.get("strategy") or "",
                    r.get("notes") or ""
                )

                count += 1

            except (ValueError, TypeError, KeyError) as e:
                errors.append(f"Row {row_num}: {e}")

    return count, errors
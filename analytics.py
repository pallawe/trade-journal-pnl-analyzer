"""Pure calculation logic (no UI, no database) so it is easy to unit-test."""

VALID_SIDES = ("LONG", "SHORT")


def trade_pnl(side, qty, entry, exit_, fees=0.0):
    """Net P&L of one closed trade = gross move * quantity - fees."""
    side = str(side).upper()
    if side not in VALID_SIDES:
        raise ValueError("side must be LONG or SHORT")
    if qty <= 0 or entry <= 0 or exit_ <= 0:
        raise ValueError("qty, entry and exit price must be positive")
    if fees < 0:
        raise ValueError("fees cannot be negative")
    gross = (exit_ - entry) * qty if side == "LONG" else (entry - exit_) * qty
    return round(gross - fees, 2)


def equity_curve(pnls, start_capital):
    """Account balance after each trade, starting from start_capital."""
    if start_capital <= 0:
        raise ValueError("start_capital must be positive")
    curve, bal = [float(start_capital)], float(start_capital)
    for p in pnls:
        bal += p
        curve.append(round(bal, 2))
    return curve


def drawdown_series(equity):
    """Percentage drop from the running peak at every point."""
    peak, out = equity[0], []
    for v in equity:
        peak = max(peak, v)
        out.append(round((peak - v) / peak * 100, 2))
    return out


def max_drawdown(equity):
    """Returns (max drop in currency, max drop in % of peak)."""
    peak, max_abs, max_pct = equity[0], 0.0, 0.0
    for v in equity:
        peak = max(peak, v)
        max_abs = max(max_abs, peak - v)
        max_pct = max(max_pct, (peak - v) / peak * 100)
    return round(max_abs, 2), round(max_pct, 2)


def summarize(pnls, start_capital):
    """All headline metrics shown on the dashboard."""
    n = len(pnls)
    eq = equity_curve(pnls, start_capital)
    dd_abs, dd_pct = max_drawdown(eq)
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p < 0]
    gross_win, gross_loss = sum(wins), -sum(losses)
    total = round(sum(pnls), 2)
    return {
        "trades": n,
        "total_pnl": total,
        "total_return_pct": round(total / start_capital * 100, 2),
        "win_rate_pct": round(len(wins) / n * 100, 2) if n else 0.0,
        "avg_win": round(gross_win / len(wins), 2) if wins else 0.0,
        "avg_loss": round(-gross_loss / len(losses), 2) if losses else 0.0,
        "profit_factor": round(gross_win / gross_loss, 2) if gross_loss else None,
        "expectancy": round(total / n, 2) if n else 0.0,
        "best_trade": max(pnls) if n else 0.0,
        "worst_trade": min(pnls) if n else 0.0,
        "max_drawdown": dd_abs,
        "max_drawdown_pct": dd_pct,
        "final_balance": eq[-1],
    }

def win_loss_analysis(pnls):
    """Calculate winning, losing and breakeven trade statistics."""
    total = len(pnls)

    wins = sum(1 for p in pnls if p > 0)
    losses = sum(1 for p in pnls if p < 0)
    breakeven = sum(1 for p in pnls if p == 0)

    return {
        "total_trades": total,
        "winning_trades": wins,
        "losing_trades": losses,
        "breakeven_trades": breakeven,
        "win_rate_pct": round(wins / total * 100, 2) if total else 0,
        "loss_rate_pct": round(losses / total * 100, 2) if total else 0,
        "breakeven_rate_pct": round(breakeven / total * 100, 2) if total else 0,
    }

import os, sys, pytest
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import analytics as an
import storage as db

@pytest.fixture
def con(tmp_path):
    return db.connect(str(tmp_path / "t.db"))

def test_tc01_long_profit():      assert an.trade_pnl("LONG", 10, 100, 110) == 100
def test_tc02_short_profit():     assert an.trade_pnl("SHORT", 10, 100, 90) == 100
def test_tc03_fees_deducted():    assert an.trade_pnl("LONG", 10, 100, 110, 15) == 85
def test_tc04_loss_negative():    assert an.trade_pnl("LONG", 5, 100, 90) == -50
def test_tc05_bad_side():
    with pytest.raises(ValueError): an.trade_pnl("BUY", 1, 1, 1)
def test_tc06_zero_qty():
    with pytest.raises(ValueError): an.trade_pnl("LONG", 0, 1, 1)
def test_tc07_equity_curve():     assert an.equity_curve([100, -50], 1000) == [1000, 1100, 1050]
def test_tc08_max_drawdown():     assert an.max_drawdown([1000, 1200, 900, 1300]) == (300, 25.0)
def test_tc09_no_drawdown():      assert an.max_drawdown([100, 110, 120]) == (0, 0)
def test_tc10_win_rate():         assert an.summarize([10, -5, 20, -5], 1000)["win_rate_pct"] == 50.0
def test_tc11_return_pct():       assert an.summarize([100, -50], 1000)["total_return_pct"] == 5.0
def test_tc12_profit_factor():    assert an.summarize([30, -10, -5], 1000)["profit_factor"] == 2.0
def test_tc13_empty_journal():
    s = an.summarize([], 1000); assert s["trades"] == 0 and s["win_rate_pct"] == 0
def test_tc14_all_wins_pf_none(): assert an.summarize([10, 20], 1000)["profit_factor"] is None
def test_tc15_db_add_list(con):
    db.add_trade(con, "tcs", "LONG", 10, 100, 110, "2026-05-01")
    rows = db.list_trades(con); assert rows[0]["symbol"] == "TCS" and rows[0]["pnl"] == 100
def test_tc16_db_rejects_invalid(con):
    with pytest.raises(ValueError): db.add_trade(con, "", "LONG", 1, 1, 1, "2026-05-01")
    assert db.list_trades(con) == []
def test_tc17_db_delete(con):
    i = db.add_trade(con, "ITC", "SHORT", 5, 50, 45, "2026-05-01")
    assert db.delete_trade(con, i) and not db.delete_trade(con, i)
def test_tc18_csv_import(con):
    p = os.path.join(os.path.dirname(__file__), "..", "sample_trades.csv")
    assert db.import_csv(con, p) == 40

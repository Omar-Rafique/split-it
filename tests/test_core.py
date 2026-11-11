import pytest

from splitit import Group, Transfer, format_money, parse_money, settle
from splitit.cli import main


def test_even_split_balances():
    g = Group("trip")
    g.add_expense("Dinner", "Ali", 3000, ["Ali", "Sara", "Omar"])
    assert g.balances() == {"Ali": 2000, "Sara": -1000, "Omar": -1000}


def test_uneven_split_keeps_totals_exact():
    g = Group("trip")
    g.add_expense("Snacks", "Sara", 100, ["Ali", "Sara", "Omar"])
    bal = g.balances()
    assert sum(bal.values()) == 0
    assert bal == {"Sara": 67, "Ali": -34, "Omar": -33}


def test_settle_up_minimal_transfers():
    g = Group("flat")
    g.add_expense("Rent", "Ali", 90000, ["Ali", "Sara", "Omar"])
    g.add_expense("Groceries", "Sara", 6000, ["Ali", "Sara", "Omar"])
    transfers = g.settle_up()
    assert transfers == [
        Transfer("Omar", "Ali", 32000),
        Transfer("Sara", "Ali", 26000),
    ]


def test_settle_nothing_when_even():
    assert settle({"A": 0, "B": 0}) == []


def test_settle_rejects_unbalanced():
    with pytest.raises(ValueError):
        settle({"A": 10, "B": -5})


@pytest.mark.parametrize(
    "text,expected",
    [("150", 15000), ("150.5", 15050), ("150.50", 15050), ("1,200", 120000), (".75", 75)],
)
def test_parse_money(text, expected):
    assert parse_money(text) == expected


@pytest.mark.parametrize("text", ["", "-5", "abc", "1.234", "1.x"])
def test_parse_money_invalid(text):
    with pytest.raises(ValueError):
        parse_money(text)


def test_format_money():
    assert format_money(123456) == "Rs 1,234.56"
    assert format_money(5) == "Rs 0.05"


def test_invalid_expense():
    g = Group("x")
    with pytest.raises(ValueError):
        g.add_expense("bad", "A", 0, ["A"])
    with pytest.raises(ValueError):
        g.add_expense("bad", "A", 100, [])


def test_cli_round_trip(tmp_path, capsys):
    f = tmp_path / "expenses.json"
    assert main(["--file", str(f), "add", "Dinner", "--paid-by", "Ali",
                 "--amount", "3000", "--between", "Ali", "Sara", "Omar"]) == 0
    assert main(["--file", str(f), "settle"]) == 0
    out = capsys.readouterr().out
    assert "Sara pays Ali Rs 1,000.00" in out
    assert "Omar pays Ali Rs 1,000.00" in out

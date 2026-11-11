# split-it 💸

![CI](https://github.com/Omar-Rafique/split-it/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A small Python tool for splitting shared expenses (trips, flat rent, group dinners)
and working out **the fewest payments needed to settle up**.

```text
$ split-it add "Rent" --paid-by Ali --amount 90000 --between Ali Sara Omar
$ split-it add "Groceries" --paid-by Sara --amount 6000 --between Ali Sara Omar
$ split-it settle
Omar pays Ali Rs 32,000.00
Sara pays Ali Rs 26,000.00
```

## Features

- Record expenses with who paid and who shares them
- Net balance per person (who is owed, who owes)
- Settle-up plan with at most *n − 1* payments (greedy matching of biggest debtor ↔ biggest creditor)
- Money stored as integer paisa, so there are no floating-point rounding bugs; leftover paisa from uneven splits are distributed fairly
- Expenses saved to a JSON file so a group can keep adding over time
- No dependencies outside the standard library

## Getting started

```bash
git clone https://github.com/Omar-Rafique/split-it.git
cd split-it
pip install -e ".[dev]"

split-it add "Dinner" --paid-by Ali --amount 3000 --between Ali Sara Omar
split-it list
split-it balances
split-it settle
```

Use `--file trip.json` to keep separate groups in separate files.

## Using it as a library

```python
from splitit import Group

g = Group("trip")
g.add_expense("Hotel", paid_by="Sara", amount=1500000, split_between=["Ali", "Sara", "Omar"])
for transfer in g.settle_up():
    print(transfer)
```

## How settling works

1. Each expense adds its amount to the payer's balance and subtracts an equal share from everyone it is split between.
2. People with a negative balance are debtors; positive are creditors.
3. The largest debtor pays the largest creditor as much as possible, and repeat until everyone is at zero.

## Running tests

```bash
pytest
```

Tests run automatically on every push via GitHub Actions on Python 3.10–3.13.

## Project structure

```text
splitit/
  core.py   # Expense, Group, settle() - the core logic
  cli.py    # argparse command-line interface
tests/
  test_core.py
```

## Roadmap

- [ ] Unequal splits (by percentage or exact amounts)
- [ ] Export settle-up plan to CSV
- [ ] REST API with FastAPI
- [ ] Web frontend

## License

MIT

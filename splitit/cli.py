"""Command-line interface.

Expenses are stored in a small JSON file so a group can keep adding to it.

    split-it add "Dinner" --paid-by Ali --amount 3000 --between Ali Sara Omar
    split-it balances
    split-it settle
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core import Group, format_money, parse_money

DEFAULT_FILE = Path("expenses.json")


def load_group(path: Path) -> Group:
    group = Group(name=path.stem)
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        for item in data.get("expenses", []):
            group.add_expense(
                item["description"], item["paid_by"], item["amount"], item["split_between"]
            )
    return group


def save_group(group: Group, path: Path) -> None:
    data = {
        "expenses": [
            {
                "description": e.description,
                "paid_by": e.paid_by,
                "amount": e.amount,
                "split_between": list(e.split_between),
            }
            for e in group.expenses
        ]
    }
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="split-it", description="Split shared expenses and settle up."
    )
    parser.add_argument(
        "--file", type=Path, default=DEFAULT_FILE, help="expenses file (default: expenses.json)"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="record a new expense")
    add.add_argument("description")
    add.add_argument("--paid-by", required=True)
    add.add_argument("--amount", required=True, help="e.g. 1500 or 1500.50")
    add.add_argument("--between", nargs="+", required=True, metavar="NAME")

    sub.add_parser("list", help="show all expenses")
    sub.add_parser("balances", help="show what each person is owed or owes")
    sub.add_parser("settle", help="show the payments needed to settle up")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    group = load_group(args.file)

    try:
        if args.command == "add":
            exp = group.add_expense(
                args.description, args.paid_by, parse_money(args.amount), args.between
            )
            save_group(group, args.file)
            print(f"Added '{exp.description}' ({format_money(exp.amount)}) paid by {exp.paid_by}")
        elif args.command == "list":
            if not group.expenses:
                print("No expenses yet.")
            for e in group.expenses:
                people = ", ".join(e.split_between)
                print(f"- {e.description}: {format_money(e.amount)} by {e.paid_by} [{people}]")
        elif args.command == "balances":
            for person, bal in sorted(group.balances().items()):
                status = "is owed" if bal > 0 else "owes" if bal < 0 else "is settled"
                print(f"{person:<12} {status:<10} {format_money(abs(bal))}")
        elif args.command == "settle":
            transfers = group.settle_up()
            if not transfers:
                print("Everyone is settled up!")
            for t in transfers:
                print(t)
    except ValueError as err:
        print(f"error: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Core logic: track shared expenses and work out who owes whom.

All money is stored as integer minor units (e.g. paisa / cents) so that
rounding errors never creep in.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Expense:
    """A single shared expense."""

    description: str
    paid_by: str
    amount: int  # minor units, e.g. 1500 = Rs 15.00
    split_between: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.amount <= 0:
            raise ValueError("amount must be positive")
        if not self.split_between:
            raise ValueError("an expense must be split between at least one person")
        if len(set(self.split_between)) != len(self.split_between):
            raise ValueError("split_between contains duplicate names")


@dataclass(frozen=True)
class Transfer:
    """A payment that settles part of the group's debts."""

    sender: str
    receiver: str
    amount: int

    def __str__(self) -> str:
        return f"{self.sender} pays {self.receiver} {format_money(self.amount)}"


@dataclass
class Group:
    """A group of people sharing expenses."""

    name: str
    expenses: list[Expense] = field(default_factory=list)

    def add_expense(
        self, description: str, paid_by: str, amount: int, split_between: list[str]
    ) -> Expense:
        expense = Expense(description, paid_by, amount, tuple(split_between))
        self.expenses.append(expense)
        return expense

    def balances(self) -> dict[str, int]:
        """Net balance per person: positive = is owed money, negative = owes."""
        net: dict[str, int] = {}
        for exp in self.expenses:
            net[exp.paid_by] = net.get(exp.paid_by, 0) + exp.amount
            share, remainder = divmod(exp.amount, len(exp.split_between))
            # Spread any leftover paisa over the first people so totals stay exact.
            for i, person in enumerate(exp.split_between):
                owed = share + (1 if i < remainder else 0)
                net[person] = net.get(person, 0) - owed
        return net

    def settle_up(self) -> list[Transfer]:
        return settle(self.balances())


def settle(balances: dict[str, int]) -> list[Transfer]:
    """Turn net balances into a short list of transfers.

    Greedy approach: repeatedly match the person who owes the most with the
    person who is owed the most. This produces at most n - 1 transfers.
    """
    if sum(balances.values()) != 0:
        raise ValueError("balances must sum to zero")

    debtors = sorted(
        ([p, -b] for p, b in balances.items() if b < 0), key=lambda x: (-x[1], x[0])
    )
    creditors = sorted(
        ([p, b] for p, b in balances.items() if b > 0), key=lambda x: (-x[1], x[0])
    )

    transfers: list[Transfer] = []
    i = j = 0
    while i < len(debtors) and j < len(creditors):
        debtor, owes = debtors[i]
        creditor, owed = creditors[j]
        amount = min(owes, owed)
        transfers.append(Transfer(debtor, creditor, amount))
        debtors[i][1] -= amount
        creditors[j][1] -= amount
        if debtors[i][1] == 0:
            i += 1
        if creditors[j][1] == 0:
            j += 1
    return transfers


def parse_money(text: str) -> int:
    """Parse '150', '150.5' or '150.50' into minor units (15050)."""
    text = text.strip().replace(",", "")
    if not text:
        raise ValueError("empty amount")
    if text.startswith("-"):
        raise ValueError("amount must be positive")
    whole, _, frac = text.partition(".")
    if not whole.isdigit() and whole != "":
        raise ValueError(f"invalid amount: {text!r}")
    if frac and (not frac.isdigit() or len(frac) > 2):
        raise ValueError(f"invalid amount: {text!r}")
    return int(whole or "0") * 100 + int(frac.ljust(2, "0") or "0")


def format_money(minor: int) -> str:
    sign = "-" if minor < 0 else ""
    minor = abs(minor)
    return f"{sign}Rs {minor // 100:,}.{minor % 100:02d}"

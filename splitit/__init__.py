"""split-it: split shared expenses and settle up with the fewest payments."""

from .core import Expense, Group, Transfer, format_money, parse_money, settle

__all__ = ["Expense", "Group", "Transfer", "format_money", "parse_money", "settle"]
__version__ = "0.1.0"

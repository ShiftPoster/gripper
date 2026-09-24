from enum import StrEnum, auto
from pathlib import Path

PACKAGE: str = Path(__file__).parent.name


class HttpTag(StrEnum):
    span = auto()
    th = auto()
    td = auto()
    tr = auto()
    table_header = th
    table_data = td
    table_row = tr

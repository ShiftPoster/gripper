from enum import StrEnum, auto


class HttpTag(StrEnum):
    span = auto()
    th = auto()
    td = auto()
    tr = auto()
    table_header = th
    table_data = td
    table_row = tr

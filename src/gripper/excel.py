from dataclasses import dataclass
from pathlib import Path

import pandas
from loguru import logger
from pydantic import BaseModel
from rapidfuzz.process import extractOne


@dataclass
class FuzzMatch:
    value: str
    score: float
    index: int

    @classmethod
    def extract(cls, query: str, choices: list[str]):
        return cls(*extractOne(query, choices))


class ExcelSettings(BaseModel):
    sheet: str | int = 0
    column: str = "gene"
    rows: int | None = 5

    def read(self, file: Path) -> pandas.Series:
        with pandas.ExcelFile(file) as frame:
            logger.debug(f"{frame.sheet_names}")
            if isinstance(self.sheet, int):
                sheet = frame.sheet_names[self.sheet]
            else:
                strsheets = [_ for _ in frame.sheet_names if isinstance(_, str)]
                sheet_match = FuzzMatch.extract(self.sheet, strsheets)
                logger.debug(f"{sheet_match = }")
                sheet = sheet_match.value

            sheet = frame.parse(frame.sheet_names[0])
            column_match = FuzzMatch.extract(self.column, sheet.columns.to_list())
            logger.debug(f"{column_match = }")

            if self.rows:
                genes = sheet[column_match.value][: self.rows]
            else:
                genes = sheet[column_match.value]
        return genes

    def write(self, file: Path, data: dict[str, str]): ...

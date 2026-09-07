from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Any


class AutoStrEnum(StrEnum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values) -> str:
        return name


class MainABC(ABC):
    @abstractmethod
    def main(self) -> Any: ...

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, ClassVar, TypeVar

from pydantic import HttpUrl
from pydantic_settings import BaseSettings, get_subcommand

from gripper.common import MainABC


class GripperSubcommand(MainABC, ABC):
    @abstractmethod
    def main(self, *args, **kwargs) -> Any: ...


# NOTE: will probably need return abc type for main
class UpstreamSubcommand(GripperSubcommand):
    host: ClassVar[HttpUrl]
    verify: bool = True
    proxy: HttpUrl | None = None
    load: Path | None = None


C = TypeVar("C", bound=GripperSubcommand)


class GripperSuperCommand(BaseSettings, MainABC):
    def get_subcommand(
        self,
        cmdtype: type[C] = GripperSubcommand,
        is_required: bool = True,
        cli_exit_on_error: bool | None = None,
    ) -> C:
        subcommand = get_subcommand(
            self, is_required=is_required, cli_exit_on_error=cli_exit_on_error
        )
        if not isinstance(subcommand, cmdtype):
            raise TypeError(f"Expected {cmdtype} not {type(subcommand)}")
        return subcommand

    def handle_subcommand(self, subcommand: GripperSubcommand, *args, **kwargs):
        if not isinstance(subcommand, GripperSubcommand):
            raise TypeError(type(subcommand))
        subcommand.main(*args, **kwargs)


class BaseApp(GripperSuperCommand):
    def cli_cmd(self):
        self.main()

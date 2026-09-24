from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, ClassVar, TypeVar

from pydantic import BaseModel, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict, get_subcommand

from gripper.common import MainABC


class GripperSubparser(MainABC, ABC):
    @abstractmethod
    def main(self, *args, **kwargs) -> Any: ...


class UpstreamSettings(BaseModel):
    host: ClassVar[HttpUrl]
    verify: bool = True
    proxy: HttpUrl | None = None
    load: Path | None = None


C = TypeVar("C", bound=GripperSubparser)


class GripperSuperCommand(BaseSettings, MainABC):
    def get_subcommand(
        self,
        cmdtype: type[C] = GripperSubparser,
        is_required: bool = True,
        cli_exit_on_error: bool | None = None,
    ) -> C:
        subcommand = get_subcommand(
            self, is_required=is_required, cli_exit_on_error=cli_exit_on_error
        )
        if not isinstance(subcommand, cmdtype):
            raise TypeError(f"Expected {cmdtype} not {type(subcommand)}")
        return subcommand

    def handle_subcommand(self, subcommand: GripperSubparser, *args, **kwargs):
        if not isinstance(subcommand, GripperSubparser):
            raise TypeError(type(subcommand))
        subcommand.main(*args, **kwargs)


def settings_config(
    cli_avoid_json: bool = True,
    **kwargs
):
    return SettingsConfigDict(cli_avoid_json=cli_avoid_json, **kwargs)


class BaseApp(GripperSuperCommand):
    model_config = settings_config()

    def model_post_init(self, context: Any) -> None:
        print(self.model_dump())

    def cli_cmd(self):
        self.main()

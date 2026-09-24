from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import CliApp, CliPositionalArg, CliSubCommand
from rich import print

from gripper.app import BaseApp, GripperSubcommand
from gripper.atlas import CliAtlas
from gripper.excel import ExcelSettings


class CliPeek(BaseModel, GripperSubcommand):
    excel: ExcelSettings = Field(default_factory=ExcelSettings)
    file: CliPositionalArg[Path]

    def main(self, *a, **k):
        genes = self.excel.read(self.file)
        print(genes)


class GripperApp(BaseApp):
    atlas: CliSubCommand[CliAtlas]
    peek: CliSubCommand[CliPeek]

    def main(self):
        subcommand = self.get_subcommand()
        subcommand.main()


def main():
    CliApp.run(GripperApp)

from pathlib import Path

from loguru import logger
from pydantic import BaseModel, Field
from pydantic_settings import CliApp, CliPositionalArg, CliSubCommand
from rich import print

from gripper.app import BaseApp, GripperSubparser
from gripper.atlas import AtlasSettings
from gripper.excel import ExcelSettings


class CliAtlas(BaseModel, GripperSubparser):
    file: CliPositionalArg[Path]
    atlas: AtlasSettings = Field(default_factory=AtlasSettings)
    excel: ExcelSettings = Field(default_factory=ExcelSettings)

    def main(self, *args, **kwargs):
        genes = self.excel.read(self.file)
        for gene in genes:
            try:
                table = self.atlas.search(gene)
                logger.info(f"Reults for {gene}")
                print(table)
            except ValueError:
                logger.error(f"Failed to fetch {gene}")


class CliPeek(BaseModel, GripperSubparser):
    file: CliPositionalArg[Path]
    excel: ExcelSettings = Field(default_factory=ExcelSettings)

    def main(self, *args, **kwargs):
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

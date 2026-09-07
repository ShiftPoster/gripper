from pydantic_settings import CliApp, CliPositionalArg, CliSubCommand
from rich import print

from gripper.app import BaseApp
from gripper.atlas import CliAtlas


class GripperApp(BaseApp):
    # file: CliPositionalArg[Path]
    gene: CliPositionalArg[str]
    atlas: CliSubCommand[CliAtlas]

    def main(self):
        atlas = self.get_subcommand(CliAtlas)
        print(atlas.main(self.gene.upper()))


def main():
    CliApp.run(GripperApp)

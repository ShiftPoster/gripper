import re
from dataclasses import dataclass, field
from enum import StrEnum
from typing import ClassVar

from bs4 import BeautifulSoup, Tag
from pydantic import BaseModel, HttpUrl

from gripper.app import UpstreamSubcommand
from gripper.constants import HttpTag
from gripper.session import GripperSession


class TableKey(StrEnum):
    tissue_profile = "Tissue profile"
    tissue_specificity = "Tissue specificity (MS)"
    cell_type = "Cell type specificity (DVP)"
    subcellular = "Subcellular location"
    location = "Predicted location"


class TableTitle(StrEnum):
    expression = "PROTEIN EXPRESSION AND LOCALIZATION"


@dataclass
class AtlasTable:
    body: Tag = field(repr=False)
    title: str = field(init=False)
    rows: dict[str, str | None] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.parse()

    def parse(self):
        rows = self.body.find_all(HttpTag.table_row)
        for row in rows:
            header = row.find(HttpTag.table_header)
            # filter empty row
            if header and header.text:
                # if the header has an 'i' link, there will be a lot
                key = header.text.strip().split("\n", 1).pop(0)
                data = row.find(HttpTag.table_data)
                if data is None:
                    self.title = key
                else:
                    self.rows[key] = data.text.strip()


class CliAtlas(BaseModel, UpstreamSubcommand):
    host: ClassVar[HttpUrl] = HttpUrl("https://www.proteinatlas.org")

    @staticmethod
    def find_reference(gene: str, string: str) -> str:
        # <a href="/ENSG00000010610-CD4/interaction" title="<b>
        pattern = re.escape('<a href="/') + "(.*)" + re.escape(f'-{gene}"')
        matches = set(re.findall(pattern, string))
        if 1 != len(matches):
            raise ValueError(matches)
        return matches.pop()

    @staticmethod
    def get_table(soup: BeautifulSoup, title: TableKey | str) -> Tag | None:
        body = None
        title_element = soup.find(HttpTag.th, string=title)
        if title_element and title_element.parent and title_element.parent.parent:
            body = title_element.parent.parent
        return body

    def request(self, gene: str) -> str:
        if self.load:
            content = self.load.read_text()
        else:
            if self.proxy:
                # TODO: log message
                url = self.proxy
            else:
                # TODO: log message
                url = self.host
            with GripperSession() as session:
                session.verify = self.verify
                search_rsp = session.rget(f"{url}search/{gene}")
                reference = self.find_reference(gene, search_rsp.text)
                gene_rsp = session.rget(f"{url}{reference}")
                content = gene_rsp.text
        return content

    def main(self, gene: str, *args, **kwargs):
        soup = BeautifulSoup(self.request(gene), "html.parser")
        table_body = self.get_table(soup, TableTitle.expression)
        return AtlasTable(table_body) if table_body else None

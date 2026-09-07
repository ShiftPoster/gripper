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
    title: str = "MISSING"
    rows: dict[str, str | None] = field(default_factory=dict)

    @classmethod
    def parse(cls, body: Tag):
        title = "MISSING"
        parsed = {}
        rows = body.find_all(HttpTag.table_row)
        for row in rows:
            header = row.find(HttpTag.table_header)
            # filter empty footer row
            if header and header.text:
                # if the header has an 'i' link, ignore that
                # force formatting with CRLF for easier split
                text = header.get_text(separator="\r\n", strip=True)
                key = text.split("\r\n", 1).pop(0)
                data = row.find(HttpTag.table_data)
                if data is None:
                    title = key
                else:
                    parsed[key] = data.get_text(separator=" ", strip=True)
        return cls(title=title, rows=parsed)


class CliAtlas(BaseModel, UpstreamSubcommand):
    host: ClassVar[HttpUrl] = HttpUrl("https://www.proteinatlas.org")

    @staticmethod
    def find_reference(gene: str, string: str) -> str:
        # <a href="/ENSG00000010610-CD4/interaction" title="<b>
        pattern = re.escape('<a href="/') + "([a-zA-Z0-9]+)" + re.escape(f'-{gene}"')
        matches = set(re.findall(pattern, string))
        if 1 != len(matches):
            raise ValueError(matches)
        return matches.pop()

    @staticmethod
    def get_table(content: str, title: TableKey | str) -> Tag | None:
        body = None
        soup = BeautifulSoup(content, "html.parser")
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

    def main(self, gene: str, *args, **kwargs) -> AtlasTable | None:
        content = self.request(gene)
        table_body = self.get_table(content, TableTitle.expression)
        return AtlasTable.parse(table_body) if table_body else None

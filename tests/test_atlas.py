from pathlib import Path

from gripper.atlas import CliAtlas

SEARCH: Path = Path.cwd() / "tests" / "data" / "atlas_search.html"
CD4: Path = Path.cwd() / "tests" / "data" / "atlas_cd4.html"


def test_reference():
    refernce = CliAtlas.find_reference("CD4", SEARCH.read_text())
    assert "ENSG00000010610" == refernce


def test_table():
    ...

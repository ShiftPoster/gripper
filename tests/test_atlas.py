from pathlib import Path

import pytest

from gripper.atlas import AtlasTable, CliAtlas, TableTitle

SEARCH1: Path = Path.cwd() / "tests" / "data" / "atlas_search1.html"
SEARCH2: Path = Path.cwd() / "tests" / "data" / "atlas_search2.html"
CD4_1: Path = Path.cwd() / "tests" / "data" / "atlas_cd4_1.html"
CD4_2: Path = Path.cwd() / "tests" / "data" / "atlas_cd4_2.html"
SOLUTION_TABLE: AtlasTable = AtlasTable(
    title='PROTEIN EXPRESSION AND LOCALIZATION',
    rows={
        'Tissue profile': 'Selective cytoplasmic expression in peripheral lymphocytes and subsets of cells in lymphoid tissues.',
        'Tissue specificity (MS)': 'Tissue enhanced (Lymphoid tissue)',
        'Cell type specificity (DVP)': 'Group enriched (B-cells, Macrophages, T-cells)',
        'Subcellular location': 'Localized to the Plasma membrane',
        'Predicted location': 'Membrane,  Intracellular (different isoforms)'
    }
)


@pytest.mark.parametrize("file", (SEARCH1, SEARCH2))
def test_reference(file: Path):
    refernce = CliAtlas.find_reference("CD4", file.read_text())
    assert "ENSG00000010610" == refernce


@pytest.mark.parametrize("file", (CD4_1, CD4_2))
def test_table(file: Path):
    table = CliAtlas.get_table(file.read_text(), TableTitle.expression)
    assert table
    assert AtlasTable.parse(table).rows == SOLUTION_TABLE.rows

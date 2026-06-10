# finance/grids/registry.py

from finance.grids.input_grid import INPUT_GRID_COLUMNS
from finance.grids.summary_grid import SUMMARY_GRID_COLUMNS

FINANCE_GRIDS = {
    "input": {
        "label": "Lançamentos",
        "columns": INPUT_GRID_COLUMNS,
    },
    "summary": {
        "label": "Resumo",
        "columns": SUMMARY_GRID_COLUMNS,
    },
}
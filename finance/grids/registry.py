# finance/grids/registry.py

from finance.grids.input_grid import INPUT_GRID_COLUMNS
from finance.grids.summary_grid import SUMMARY_GRID_COLUMNS
from finance.grids.constants_grid import CONSTANTS_GRID_ROWS

FINANCE_GRIDS = {
    "input": {
        "label": "Dados",
        "columns": INPUT_GRID_COLUMNS,
    },
    "summary": {
        "label": "Cálculos",
        "columns": SUMMARY_GRID_COLUMNS,
    },
}

CONSTANTS_GRIDS = {
    "constants": {
        "label": "Parâmetros",
        "rows": CONSTANTS_GRID_ROWS,
    }
}
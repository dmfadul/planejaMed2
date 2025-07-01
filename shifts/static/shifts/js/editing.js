// Initialize state from localStorage or use default state if not present
let state = JSON.parse(localStorage.getItem('tableState')) || {
    editing: false,
    tableType: null, // 'BASE', 'MONTH' or null
    action: null, // 'add', 'remove' or null
    center: null,
    month: null,
    year: null,
    status: null, // 'BASE, 'ORIGINAL' or 'REALIZED'
    selectedCells: [],
};

// Save state to localStorage whenever it changes
function saveState() {
    localStorage.setItem('tableState', JSON.stringify(state));
}

function clearState() {
    localStorage.removeItem('tableState');
    state = {
        editing: false,
        tableType: null,
        action: null,
        center: null,
        month: null,
        year: null,
        selectedCells: [],
    };
}

function toggleEditing() {
    state.editing = !state.editing;
    state.tableType = tableData["table_type"];
    
    const editButton = document.getElementById('edit-button');
    const defaultButtons = document.getElementById('default-buttons');
    const editButtons = document.getElementById('edit-buttons');

    if (state.editing) {
        editButton.textContent = "Fechar";
        editButton.classList.add("editing-active");
        defaultButtons.style.display = "none";
        editButtons.style.display = "flex"; // flex or block, depending on layout
    } else {
        editButton.textContent = "Editar";
        editButton.classList.remove("editing-active");
        defaultButtons.style.display = "flex";
        editButtons.style.display = "none";

        state.action = null; // Reset action when editing is finished
        clearSelectedCells();
        clearState(); // Clear state when editing is finished
    }

    saveState(); // Save state to localStorage
}

// Restore UI state when the page loads
function restoreUI() {
    const editButton = document.getElementById('edit-button');
    const defaultButtons = document.getElementById('default-buttons');
    const editButtons = document.getElementById('edit-buttons');

    if (state.editing) {
        editButton.textContent = "Editar";
        editButton.classList.add("editing-active");
        defaultButtons.style.display = "none";
        editButtons.style.display = "flex";
    } else {
        editButton.textContent = "Editar";
        editButton.classList.remove("editing-active");
        defaultButtons.style.display = "flex";
        editButtons.style.display = "none";
    }

    // Restore selected cells' visual state
    state.selectedCells.forEach(cellData => {
        const cell = document.getElementById(cellData.cellID);
        if (cell) {
            cell.classList.add("selected");
            cell.style.backgroundColor = "gray";
        }
    });
}

function clickCell(cell) {
    if (!state.editing) return;

    let currentlySelected = cell.classList.contains("selected");
    if (currentlySelected) {
        cell.classList.remove("selected");
        cell.style.backgroundColor = ""; // Reset background color
        // Remove cell from selectedCells
        state.selectedCells = state.selectedCells.filter(c => c.cellID !== cell.id);
    } else {
        cell.classList.add("selected");
        cell.style.backgroundColor = "gray"; // Highlight selected cell
        getCellData(cell); // Add cell data to state.selectedCells
    }

    saveState(); // Save state to localStorage
}

function clickName(name) {
    // Save state before navigating
    saveState();
    window.location.href = `/shifts/basetable/${tableData.center}/${name.id}/`;
    // TODO: this is the cause of the return button bug
}

function clickHeader(header) {
    console.log("Header clicked:", header.textContent);
}

function clearSelectedCells() {
    document.querySelectorAll('.selected').forEach(cell => {
        cell.classList.remove('selected');
        cell.style.backgroundColor = ""; // Reset background color
    });
    state.selectedCells = []; // Clear selected cells in state
    saveState(); // Save state to localStorage
}

function executeEdit(action) {
    if (!state.editing) return;
    
    state.action = action;
    getData();
    
    if (state.selectedCells.length === 0) return;
    
    if (action === "add") {
        openModalAdd(state.selectedCells);
    } else if (action === "remove") {
        sendData();
    } else {
        console.log("an error occurred, invalid action");
    }

    saveState(); // Save state to localStorage
}

function getData() {
    state.selectedCells = []; // Clear selected cells

    document.querySelectorAll('.selected').forEach(cell => {
        getCellData(cell);
    });

    // Get table data
    state.center = tableData["center"];
    state.month = tableData["month"];
    state.year = tableData["year"];
    state.status = tableData["status"];
    
    saveState(); // Save state to localStorage
}

function getCellData(cell) {
    // Collect data from the cell
    let doctorCRM = cell.closest("tr").querySelector("td").getAttribute("id");
    let doctorName = cell.closest("tr").querySelector("td").textContent.trim();
    let weekDay = cell.closest("table").querySelectorAll("tr")[0].cells[cell.cellIndex].textContent;
    let monthDay = cell.closest("table").querySelectorAll("tr")[1].cells[cell.cellIndex].textContent;

    // Add cell data to state.selectedCells
    state.selectedCells.push({
        weekDay: weekDay,
        monthDay: monthDay,
        doctorCRM: doctorCRM,
        doctorName: doctorName,
        hourValue: cell.textContent,
        cellID: cell.id,
    });
}

// Run restoreUI when the page loads
document.addEventListener('DOMContentLoaded', restoreUI);
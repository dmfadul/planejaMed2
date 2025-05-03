let state = {
    editing: false,
    tableType: null, // 'BASE', 'MONTH' or null
    action: null, // 'add', 'remove' or null
    center: null,
    month: null,
    year: null,
    selectedCells: [],
};

function toggleEditing() {
    state.editing = !state.editing;
    state.tableType = tableData["table_type"];

    const editButton = document.getElementById('edit-button');
    const defaultButtons = document.getElementById('default-buttons');
    const editButtons = document.getElementById('edit-buttons');

    if (state.editing) {
        editButton.textContent = "Finalizar";
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
    }
}


function clickCell(cell) {
    if (!state.editing) return;

    let currentlySelected = cell.classList.contains("selected");
    if (currentlySelected) {
        cell.classList.remove("selected");
        cell.style.backgroundColor = ""; // Reset background color
    } else {
        cell.classList.add("selected");
        cell.style.backgroundColor = "gray"; // Highlight selected cell
    }
}


function clearSelectedCells() {
    document.querySelectorAll('.selected').forEach(cell => {
        cell.classList.remove('selected');
        cell.style.backgroundColor = ""; // Reset background color
    });
}


function executeEdit(action) {
    if (!state.editing) return;
    
    state.action = action;
    getData();
    
    if (state.selectedCells.length === 0) return;
    openModalAdd(state.selectedCells);
}


function getData() {
    state.selectedCells = []; // empty selected cells, no need to clear them as they should be empty

    document.querySelectorAll('.selected').forEach(cell => {
        getCellData(cell);
    });

    // get table data
    state.center = tableData["center"];
    state.month = tableData["month"];
    state.year = tableData["year"];
}


function getCellData(cell) {
    // collect data from the cell
    let doctorCRM = cell.closest("tr").querySelector("td").getAttribute("id");
    let doctorName = cell.closest("tr").querySelector("td").textContent.trim();
    let weekDay = cell.closest("table").querySelectorAll("tr")[0].cells[cell.cellIndex].textContent;
    let monthDay = cell.closest("table").querySelectorAll("tr")[1].cells[cell.cellIndex].textContent;


    // add cell data to state.selectedCells
    state.selectedCells.push({
        weekDay: weekDay,
        monthDay: monthDay,
        doctorCRM: doctorCRM,
        doctorName: doctorName,
        hourValue: cell.textContent,
        cellID: cell.id,
    });
}

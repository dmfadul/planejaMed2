let state = {
    editing: false,
    action: null, // 'add', 'remove' or null
    center: null,
    month: null,
    year: null,
    selectedCells: [],
};

function toggleEditing() {
    state.editing = !state.editing;

    const editButton = document.getElementById('edit-button');
    const defaultButtons = document.getElementById('default-buttons');
    const editButtons = document.getElementById('edit-buttons');

    if (state.editing) {
        editButton.textContent = "Finalizar";
        editButton.classList.add("editing-active");
        defaultButtons.style.display = "none";
        editButtons.style.display = "flex"; // flex or block, depending on layout

        state.center = centerValue;
        state.month = monthValue;
        state.year = yearValue;
        state.selectedCells = []; // Clear selected cells when starting editing

    } else {
        editButton.textContent = "Editar";
        editButton.classList.remove("editing-active");
        defaultButtons.style.display = "flex";
        editButtons.style.display = "none";


        state.action = null; // Reset action when editing is finished
    }
}

let editing = false;

let state = {
    mode: null, // 'edit' or null
    action: null, // 'add', 'remove' or null
    center: null,
    month: null,
    year: null,
    selectedCells: [],
};

function toggleEditing() {
    editing = !editing;

    const editButton = document.getElementById('edit-button');
    const defaultButtons = document.getElementById('default-buttons');
    const editButtons = document.getElementById('edit-buttons');

    if (editing) {
        editButton.textContent = "Finalizar";
        editButton.classList.add("editing-active");
        defaultButtons.style.display = "none";
        editButtons.style.display = "flex"; // flex or block, depending on layout
        startEditing();
    } else {
        editButton.textContent = "Editar";
        editButton.classList.remove("editing-active");
        defaultButtons.style.display = "flex";
        editButtons.style.display = "none";
        exitEditing();
    }
}

function startEditing() {
    console.log("Editing started");
    state.mode = "edit";
    console.log(state);
}

function exitEditing(){
    console.log("Editing exited");
    state.mode = null;
    console.log(state);
}

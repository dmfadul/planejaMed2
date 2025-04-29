function openModalAdd(cells) {
    const dynamicInputs = document.getElementById('dynamicInputs');
    dynamicInputs.innerHTML = ''; // clear

    cells.array.forEach(cell => {
       const inputGroup = document.createElement('div');
       inputGroup.className = 'mb-3';
       
       inputGroup.innerHTML = `
            <select class="form-select" id="${cell.cellID}" name="${cell.cellID}">
                <option value="">---</option>
                <option value="d">d</option>
                <option value="n">n</option>
                <option value="m">m</option>
                <option value="t">t</option>
                <option value="c">c</option>
                <option value="v">v</option>
            </select>
       `;

       dynamicInputs.appendChild(inputGroup);
    });
    let modal = new bootstrap.Modal(document.getElementById('modal_add'));
    modal.show();
}


function submitModalAdd() {
    const form = document.getElementById('modalAddForm');
    const formData = new FormData(form);

    state.selectedCells.forEach(cell => {
        const value = formData.get(cell.cellID)
        cell.newValue = value;
    });

    bootstrap.Modal.getInstance(document.getElementById('modal_add')).hide();

    sendData();
}
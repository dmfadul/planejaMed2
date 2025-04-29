function openModalAdd(cells) {
    const dynamicInputs = document.getElementById('dynamicInputs');
    dynamicInputs.innerHTML = ''; // clear
    
    cells.forEach(cell => {
       const inputGroup = document.createElement('div');
       inputGroup.className = 'row align-items-center mb-2';
       
       inputGroup.innerHTML = `
            <div class="col-7">
                <label for="${cell.cellID}" class="form-label fw-bold fs-6">
                    ${cell.doctorCRM} – Dia ${cell.monthDay} (${cell.weekDay})
                </label>
            </div>
            <div class="col-5">
                <select class="form-select" id="${cell.cellID}" name="${cell.cellID}">
                    <option value="">---</option>
                    <option value="d">d</option>
                    <option value="n">n</option>
                    <option value="m">m</option>
                    <option value="t">t</option>
                    <option value="c">c</option>
                    <option value="v">v</option>
                </select>
            </div>
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
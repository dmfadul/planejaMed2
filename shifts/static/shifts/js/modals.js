function openModalAdd(cells) {
    const dynamicInputs = document.getElementById('dynamicInputs');
    dynamicInputs.innerHTML = ''; // clear
    
    cells.forEach((cell, index) => {
        let message = `${cell.doctorCRM} – Dia ${cell.monthDay} (${cell.weekDay})`;

        const inputGroup = document.createElement('div');
        inputGroup.className = 'row align-items-center mb-2';

        let div = document.createElement('div');
        div.className = 'col-7';
        div.innerHTML = `<label for="${cell.cellID}" class="form-label fw-bold fs-6">${message}</label>`;

        dropdown1 = createDropdown(cell.id, shiftCodes);
        
        let div2 = document.createElement('div');
        div2.className = 'col-5';
        
        div2.appendChild(dropdown1);
        
        inputGroup.appendChild(div);
        inputGroup.appendChild(div2);

        dynamicInputs.appendChild(inputGroup);
    });

    let modal = new bootstrap.Modal(document.getElementById('modal_add'));
    modal.show();
}


function submitModalAdd() {
    const form = document.getElementById('modalAddForm');
    const formData = new FormData(form);

    const newValues = {};
    state.selectedCells.forEach(cell => {
        newValues[cell.cellID] = formData.get(cell.cellID);
    });

    state['newValues'] = newValues;
    bootstrap.Modal.getInstance(document.getElementById('modal_add')).hide();

    sendData();
}


function createDropdown(id, options) {
    let dropdown = document.createElement('select');
    dropdown.classList.add('form-select');
    dropdown.id = id;

    options.forEach(option => {
        let opt = document.createElement('option');
        opt.value = option;
        opt.textContent = option;
        dropdown.appendChild(opt);
    });

    return dropdown;
}
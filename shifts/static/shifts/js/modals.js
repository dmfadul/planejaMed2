function openModalAdd(cells) {
    const dynamicInputs = document.getElementById('dynamicInputs');
    dynamicInputs.innerHTML = ''; // clear
    
    cells.forEach((cell, index) => {
        let message = `${cell.doctorCRM} – Dia ${cell.monthDay} (${cell.weekDay})`;

        const inputGroup = document.createElement('div');
        inputGroup.className = 'row align-items-center mb-2';

        let message_div = document.createElement('div');
        message_div.className = 'col-5';
        message_div.innerHTML = `<label for="${cell.cellID}" class="form-label fw-bold fs-6">${message}</label>`;

        dropdown1 = createDropdown(`dp1_${index}`, shiftCodes);
        dropdown2 = createDropdown(`dp2_${index}`, hourRange);
        dropdown3 = createDropdown(`dp3_${index}`, hourRange);
        
        let div1 = document.createElement('div');
        let div2 = document.createElement('div');
        let div3 = document.createElement('div');

        div1.className = 'col-2';
        div2.className = 'col-2';
        div3.className = 'col-2';
                
        div1.appendChild(dropdown1);
        div2.appendChild(dropdown2);
        div3.appendChild(dropdown3);
        
        inputGroup.appendChild(message_div);
        inputGroup.appendChild(div1);
        inputGroup.appendChild(div2);
        inputGroup.appendChild(div3);

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
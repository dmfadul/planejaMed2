function openModalAdd(cells) {
    const dynamicInputs = document.getElementById('dynamicInputs');
    dynamicInputs.innerHTML = ''; // clear
    
    cells.forEach(cell => {
        let message = `${cell.doctorName}&nbsp;&nbsp; –&nbsp;&nbsp; ${cell.monthDay}º ${cell.weekDay} do Mês: `;

        const inputGroup = document.createElement('div');
        inputGroup.className = 'row align-items-center mb-2';

        let message_div = document.createElement('div');
        message_div.className = 'col-5';
        message_div.innerHTML = `<label for="${cell.cellID}" class="form-label fw-bold fs-6">${message}</label>`;
        
        let hourRangeNoEnd = tableData["hour_range"].slice(0, -1);

        const dropdown1 = createDropdown(`${cell.cellID}_shift`, tableData["shift_codes"]);
        const dropdown2 = createDropdown(`${cell.cellID}_start`, hourRangeNoEnd, tableData["hour_values"]);
        const dropdown3 = createDropdown(`${cell.cellID}_end`, tableData["hour_range"], tableData["hour_values"]);

        dropdown1.addEventListener('change', () => handleDropdownChange(dropdown1, dropdown2, dropdown3));
        dropdown2.addEventListener('change', () => handleDropdownChange(dropdown1, dropdown2, dropdown3));

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
        handleDropdownChange(dropdown1, dropdown2, dropdown3);
    });

    let modal = new bootstrap.Modal(document.getElementById('modal_add'));
    modal.show();
}


function submitModalAdd() {
    const form = document.getElementById('modalAddForm');
    const formData = new FormData(form);

    const newValues = {};
    state.selectedCells.forEach(cell => {
        newValues[cell.cellID] = {
            shiftCode: formData.get(`${cell.cellID}_shift`),
            startTime: formData.get(`${cell.cellID}_start`),
            endTime: formData.get(`${cell.cellID}_end`)
        };
    });

    state['newValues'] = newValues;
    bootstrap.Modal.getInstance(document.getElementById('modal_add')).hide();

    sendData();
}


function createDropdown(id, options, values={}) {
    let dropdown = document.createElement('select');
    dropdown.classList.add('form-select');
    dropdown.id = id;
    dropdown.name = id;

    options.forEach(option => {
        let opt = document.createElement('option');
        if(Object.keys(values).length > 0){
            opt.value = values[option];
        } else{
            opt.value = option;
        }
        opt.textContent = option;
        dropdown.appendChild(opt);
    });

    return dropdown;
}


function handleDropdownChange(dropdown1, dropdown2, dropdown3) {
    if (dropdown1.value !== '-') {
        dropdown2.disabled = true;
        dropdown3.disabled = true;
        dropdown2.style.backgroundColor = "#a0a0a0"; // Gray out the dropdown
        dropdown3.style.backgroundColor = "#a0a0a0"; // Gray out the dropdown
        dropdown2.selectedIndex = -1;
        dropdown3.selectedIndex = -1;
    } else {
        dropdown2.disabled = false;
        dropdown3.disabled = false;
        dropdown2.style.backgroundColor = ""; // Reset background color
        dropdown3.style.backgroundColor = ""; // Reset background color
        dropdown3.selectedIndex = 1;

        const selectedIndex = dropdown2.selectedIndex;

        Array.from(dropdown3.options).forEach((option, index) => {
            if (index <= selectedIndex) {
                option.style.display = "none"; // Hide options in dropdown3 that are less than or equal to selectedIndex
            } else {
                option.style.display = "block"; // Show options in dropdown3 that are greater than selectedIndex
            }
        });
        dropdown3.selectedIndex = selectedIndex + 1; // Select the next option in dropdown3
    }
}
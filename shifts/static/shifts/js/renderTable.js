function renderTable(tableData){
    const table = document.getElementById('shift-table');
    table.innerHTML = ''; // Clear any previous content

    if (["basetable", "month_table", "sum_days_base", "sum_days_month"].includes(tableData.template)) {
        renderNormalTable(tableData, table);
    } else if (tableData.template === "doctor_basetable") {
        renderDoctorTable(tableData, table);
    }
}

function renderHeaders(data, table, twoHeaders=true) {
    const thead = document.createElement('thead');
    const row1 = document.createElement('tr');
    data.header1.forEach((cell, idx) => {
        const th = document.createElement('th');
        th.textContent = cell.label;
        th.id = cell.cellID;
        if (idx === 0) th.classList.add('first-col', 'corner');
        else th.classList.add('normal-col', 'header');
        row1.appendChild(th);
    });

    thead.appendChild(row1);

    if (twoHeaders) {
        const row2 = document.createElement('tr');
        data.header2.forEach((cell, idx) => {
            const th = document.createElement('th');
            th.textContent = cell.label;
            th.id = cell.cellID;
            if (idx === 0) th.classList.add('first-col', 'corner');
            else th.classList.add('normal-col', 'header');
            row2.appendChild(th);
        });
        
        thead.appendChild(row2);
    }

    table.appendChild(thead);
}


function renderNormalTable(data, table) {
    // Create the header of the table
    renderHeaders(data, table, true);

    // Create the body of the table
    const tbody = document.createElement('tbody');
    data.doctors.forEach(doctor => {
        const tr = document.createElement('tr');

        const nameTd = document.createElement('td');
        nameTd.className = 'first-col name-col';
        nameTd.id = doctor.crm;
        nameTd.style.cursor = "pointer";
        nameTd.textContent = doctor.abbr_name;
        nameTd.title = `${doctor.name} - ${doctor.crm}`;
        
        tr.appendChild(nameTd);

        data.header1.slice(1).forEach(cell => {
            const cellId = `cell-${doctor.crm}-${cell.cellID}`;
            const td = document.createElement('td');
            td.id = cellId;
            td.className = 'normal-col cell-col';
            td.textContent = doctor.shifts[cellId] || '';
            tr.appendChild(td);
        });

        tbody.appendChild(tr);
    });

    table.appendChild(tbody);
}


function renderDoctorTable(data, table) {
    // Create the header of the table
    renderHeaders(data, table, false);

    // Create the body of the table
    const tbody = document.createElement('tbody');
    data.weekdays.forEach(day => {
        const tr = document.createElement('tr');

        const nameTd = document.createElement('td');
        nameTd.className = 'first-col small-col';
        nameTd.id = day.dayID;
        nameTd.style.cursor = "pointer";
        nameTd.title = day.label;
        nameTd.textContent = day.label;

        tr.appendChild(nameTd);

        data.header1.slice(1).forEach(h => {
            const cellId = `cell-${tableData.doctor.crm}-${day.dayID}-${h.cellID}`;
            const td = document.createElement('td');
            td.id = cellId;
            td.className = 'normal-col cell-col';
            td.textContent = tableData.doctor.shifts[cellId] || '';
            tr.appendChild(td);
        });

        tbody.appendChild(tr);
    });

    table.appendChild(tbody);
}
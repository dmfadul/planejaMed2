function renderTable(tableData){
    if (tableData.template === "basetable") {
        renderNormalTable(tableData);
    } else if (tableData.template === "doctor_basetable") {
        renderDoctorTable(tableData);
    }
}

function renderNormalTable(data) {
    const table = document.getElementById('shift-table');
    table.innerHTML = ''; // Clear any previous content

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

    const row2 = document.createElement('tr');
    data.header2.forEach((cell, idx) => {
        const th = document.createElement('th');
        th.textContent = cell.label;
        th.id = cell.cellID;
        if (idx === 0) th.classList.add('first-col', 'corner');
        else th.classList.add('normal-col', 'header');
        row2.appendChild(th);
    });

    thead.appendChild(row1);
    thead.appendChild(row2);
    table.appendChild(thead);

    const tbody = document.createElement('tbody');
    data.doctors.forEach(doctor => {
        const tr = document.createElement('tr');

        const nameTd = document.createElement('td');
        nameTd.className = 'first-col name-col';
        nameTd.id = doctor.crm;
        nameTd.style.cursor = "pointer";
        nameTd.onclick = () => window.location.href = `/shifts/basetable/${data.center}/${doctor.crm}/`;

        const link = document.createElement('a');
        link.href = `/shifts/basetable/${data.center}/${doctor.crm}/`;
        link.title = `${doctor.name} - ${doctor.crm}`;
        link.textContent = doctor.abbr_name;
        nameTd.appendChild(link);

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


function renderDoctorTable(data) {
    const table = document.getElementById('shift-table');
    table.innerHTML = ''; // Clear any previous content

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
    table.appendChild(thead);

    const tbody = document.createElement('tbody');
    data.weekdays.forEach(day => {
        const tr = document.createElement('tr');

        const nameTd = document.createElement('td');
        nameTd.className = 'small-first-col day-col';
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
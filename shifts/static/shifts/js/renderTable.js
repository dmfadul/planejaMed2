function renderTable(tableData){
    console.log("Rendering table with data:");
    const table = document.getElementById('shift-table');
    table.innerHTML = ''; // Clear any previous content

    if (["basetable", "month_table", "sum_doctors_base", "sum_doctors_month"].includes(tableData.template)) {
        renderNormalTable(tableData, table);
    } else if (["sum_days_base", "sum_days_month"].includes(tableData.template)){ 
        renderSumTable(tableData, table);
    } else if (tableData.template === "doctor_basetable") {
        renderDoctorTable(tableData, table);
    } else if (tableData.template === "balance") {
        renderBalanceTable(tableData, table);
    }
}

function renderBalanceTable(data, table) {
    const tbody = document.createElement('tbody');
    const balance = data.balance || {};
    const centers = Object.keys(balance);

    if (!centers.length) {
        renderEmptyBalanceMessage(table, "No balance data found.");
        return;
    }

    centers.forEach(centerName => {
        const centerDays = balance[centerName] || {};
        const days = Object.keys(centerDays).sort((a, b) => Number(a) - Number(b));

        if (!days.length) return;

        // Center title row
        const centerRow = document.createElement('tr');
        const centerCell = document.createElement('th');
        centerCell.colSpan = 4;
        centerCell.textContent = centerName;
        centerCell.className = 'balance-center-title';
        centerRow.appendChild(centerCell);
        tbody.appendChild(centerRow);

        // Header row
        const headerRow = document.createElement('tr');
        ['Dia', 'Manhã', 'Tarde', 'Noite'].forEach((label, idx) => {
            const th = document.createElement('th');
            th.textContent = label;
            th.className = idx === 0
                ? 'first-col balance-subheader'
                : 'balance-subheader';
            headerRow.appendChild(th);
        });
        tbody.appendChild(headerRow);

        // Data rows
        days.forEach(day => {
            const shifts = centerDays[day] || {};
            const tr = document.createElement('tr');

            const dayTd = document.createElement('td');
            dayTd.textContent = day;
            dayTd.className = 'first-col name-col';
            tr.appendChild(dayTd);

            ['morning', 'afternoon', 'night'].forEach(period => {
                const td = document.createElement('td');
                const value = shifts[period];

                td.textContent = value !== undefined ? value : '--';
                td.className = 'normal-col cell-col text-center';

                if (value !== undefined) {
                    if (value < 0) {
                        td.classList.add('balance-negative');
                    } else if (value > 0) {
                        td.classList.add('balance-positive');
                    } else {
                        td.classList.add('balance-neutral');
                    }
                } else {
                    td.classList.add('balance-missing');
                }

                tr.appendChild(td);
            });

            tbody.appendChild(tr);
        });

        // Spacer row
        const spacerRow = document.createElement('tr');
        const spacerCell = document.createElement('td');
        spacerCell.colSpan = 4;
        spacerCell.className = 'balance-spacer';
        spacerRow.appendChild(spacerCell);
        tbody.appendChild(spacerRow);
    });

    if (!tbody.children.length) {
        renderEmptyBalanceMessage(table, "No balance data found.");
        return;
    }

    table.appendChild(tbody);
}

function renderEmptyBalanceMessage(table, message) {
    const tbody = document.createElement('tbody');
    const tr = document.createElement('tr');
    const td = document.createElement('td');

    td.colSpan = 4;
    td.textContent = message;
    td.className = 'text-center p-3';

    tr.appendChild(td);
    tbody.appendChild(tr);
    table.appendChild(tbody);
}

function renderHeaders(data, table, twoHeaders=true, showTitle=false) {
    const thead = document.createElement('thead');
    const row1 = document.createElement('tr');
    data.header1.forEach((cell, idx) => {
        let cellDay = null;
        if (typeof cell.cellID === 'string' && cell.cellID.includes('-')) {
            cellDay = cell.cellID.split('-')[1];
        } else {
            cellDay = cell.cellID;
        }
        const th = document.createElement('th');
        th.textContent = cell.label;
        th.id = cell.cellID;
        if (idx === 0) th.classList.add('first-col', 'corner');
        else th.classList.add('normal-col', 'header');
        
        if (['SAB', 'DOM'].includes(cell.label)) th.classList.add('weekend');
        if (cellDay && data.holidays.includes(Number(cellDay))) th.classList.add('holiday');
        
        if (showTitle) {
            th.title = cell.title || '';
        }
        row1.appendChild(th);
    });

    thead.appendChild(row1);

    if (twoHeaders) {
        const row2 = document.createElement('tr');
        data.header2.forEach((cell, idx) => {
            const cellDay = cell.cellID.split('-')[1];

            const th = document.createElement('th');
            th.textContent = cell.label;
            th.id = cell.cellID;
            if (idx === 0) th.classList.add('first-col', 'corner');
            else th.classList.add('normal-col', 'header');

            const header1Text = thead.rows[0].cells[idx].textContent;    
            if (['SAB', 'DOM'].includes(header1Text)) th.classList.add('weekend');
            if (cellDay && data.holidays.includes(Number(cellDay))) th.classList.add('holiday');

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
        const doctorIndex = data.doctors.indexOf(doctor) + 1; // Start index from 1 for display purposes
        const tr = document.createElement('tr');

        const nameTd = document.createElement('td');
        nameTd.className = 'first-col name-col';
        nameTd.id = doctor.crm;
        nameTd.style.cursor = "pointer";
        nameTd.textContent = doctor.abbr_name;
        nameTd.title = `${doctorIndex} - ${doctor.name} (${doctor.crm})`;
        
        tr.appendChild(nameTd);

        data.header1.slice(1).forEach(cell => {
            const cellDay = cell.cellID.split('-')[1];

            const cellId = `cell-${doctor.crm}-${cell.cellID}`;
            const td = document.createElement('td');
            td.id = cellId;
            
            td.className = 'normal-col cell-col';
            if (['SAB', 'DOM'].includes(cell.label)) td.className += ' weekend';
            if (cellDay && data.holidays.includes(Number(cellDay))) td.classList.add('holiday');
            
            let txtContent = null;
            if (doctor.shifts[cellId] === undefined) {
                txtContent = '';
            } else {
                txtContent = doctor.shifts[cellId];
            }
            td.textContent = txtContent;
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

function renderSumTable(data, table) {
    // Create the header of the table
    renderHeaders(data, table, true, true);
    
    const hours_by_day = data.days || [];
    const first_col = [["DIA:", "day"], ["NOITE:", "night"]];
    
    // Create the body of the table
    const tbody = document.createElement('tbody');

    first_col.forEach(name => {
        const tr = document.createElement('tr');
        const nameTd = document.createElement('td');
        nameTd.className = 'first-col name-col';
        nameTd.id = name[1];
        nameTd.style.cursor = "pointer";
        nameTd.textContent = name[0];
        tr.appendChild(nameTd);

        data.header1.slice(1).forEach(cell => {
            const cellId = `cell-${name[1]}-${cell.cellID}`;
            const td = document.createElement('td');
            td.id = cellId;
            td.className = 'normal-col cell-col';
            td.textContent = hours_by_day[cell.cellID][name[1]] || 0;

            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
    table.appendChild(tbody);
}
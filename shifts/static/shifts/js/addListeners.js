function addListeners() {
    const cells = document.querySelectorAll('.cell-col');
    const names = document.querySelectorAll('.name-col');
    const h_days = document.querySelectorAll('.header');
    const addButton = document.getElementById('edit-add-button');
    const remButton = document.getElementById('edit-rem-button');
    const sumButton = document.getElementById('sum-hours-button');
    const backButton = document.getElementById('back-button');

    console.log("✅ addListeners running after table render. Found:", cells.length);

    document.getElementById("print-button").addEventListener("click", function() {
        var center = tableData.center;
        var month = tableData.month_number;
        var year = tableData.year;
        var printUrl = `/shifts/printable/${center}/`;
        if (month && year) {
            printUrl += `${month}/${year}/`;
        }
        window.open(printUrl, '_blank');
    });


    cells.forEach(cell => {
        cell.addEventListener('click', () => {
            clickCell(cell);
        });
    });

    names.forEach(name => {
        name.addEventListener('click', () => {
            console.log("name");
            clickName(name);
        });
    });
    
    if (h_days.length > 0) {
        h_days.forEach(header => {
            header.addEventListener('click', () => {
                clickHeader(header);
            });
        });
    }

    if (addButton) {
        addButton.addEventListener('click', () => executeEdit('add'));
    }

    if (remButton) {
        remButton.addEventListener('click', () => executeEdit('remove'));
    }

    if (backButton) {
        backButton.addEventListener('click', () => {
            if (tableData.template == "sum_days_base") {
                window.location.href = `/shifts/basetable/${tableData.center}/`;
            } else if (tableData.template == "sum_days_month") {
                window.location.href = `/shifts/monthtable/${tableData.center}/${tableData.month_number}/${tableData.year}/`;
            } else if (tableData.template == "doctor_basetable") {
                window.location.href = `/shifts/basetable/${tableData.center}/`;
            } else {
                console.error("Unknown template type:", tableData.template);
            }
        });
    }

    if (sumButton) {
        sumButton.addEventListener('click', () => {
            console.log(tableData);
            if (tableData.template == "basetable") {
                window.location.href = `/shifts/sum-days/${tableData.center}/`;
            }else if (tableData.template == "month_table") {
                window.location.href = `/shifts/sum-days/${tableData.center}/${tableData.month_number}/${tableData.year}/`;
            }else{
                console.error("Unknown template type:", tableData.template);
            }
        })
    }
}

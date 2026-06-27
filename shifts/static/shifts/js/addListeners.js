function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value;
}

function showToast(message, type = "success") {
    const toast = document.getElementById("successToast");
    toast.textContent = message;

    toast.style.background = type === "success" ? "#2ecc71" : "#e74c3c";

    toast.classList.add("show");

    clearTimeout(window.__toastTimer);
    window.__toastTimer = setTimeout(() => {
        toast.classList.remove("show");
    }, 5000);
}

function formatApiErrors(data) {
    if (data.detail) {
        return data.detail;
    }

    return Object.entries(data)
        .map(([field, messages]) => {
            if (Array.isArray(messages)) {
                return `${messages.join(", ")}`;
            }

            return `${messages}`;
        })
        .join("<br>");
}

document.getElementById('balance-confirm-button').addEventListener('click', async () => {
    if (!selectedBalanceCell) return;

    const payload = {
        action: selectedBalanceCell.dataset.action,
        cardCRM: selectedBalanceCell.dataset.cardcrm,
        shift: selectedBalanceCell.dataset.shift,
        center: selectedBalanceCell.dataset.center,
        day: selectedBalanceCell.dataset.day,
        month: selectedBalanceCell.dataset.monthNumber,
        startHour: selectedBalanceCell.dataset.startHour,
        endHour: selectedBalanceCell.dataset.endHour,
    };

    const response = await fetch('/api/user-requests/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok) {
        const errorBox = document.getElementById('balance-modal-errors');
        
        errorBox.innerHTML = formatApiErrors(data);
        errorBox.classList.remove('d-none');
        
        return;
    }
    
    const modalElement = document.getElementById('balanceConfirmModal');
    const modal = bootstrap.Modal.getInstance(modalElement);
    modal.hide();
    console.log("✅ Balance request sent successfully:", data);
    showPageMessage("Pedido de inclusão enviado com sucesso!", "success");

    selectedBalanceCell.classList.add("balance-confirmed");
    selectedBalanceCell = null;
});


function addListeners() {
    const cells = document.querySelectorAll('.cell-col');
    const balanceCells = document.querySelectorAll('.balance-cell');
    const names = document.querySelectorAll('.name-col');
    const h_days = document.querySelectorAll('.header');
    const addButton = document.getElementById('edit-add-button');
    const remButton = document.getElementById('edit-rem-button');
    const sumButton = document.getElementById('sum-hours-button');
    const backButton = document.getElementById('back-button');
    const printButton = document.getElementById('print-button');

    const template = tableData.template;

    console.log("✅ addListeners running after table render.");


    if (printButton) {
        printButton.addEventListener("click", function() {
            const center = tableData.center;
            const month = tableData.month_number;
            const year = tableData.year;

            let printUrl = `/shifts/printable/${center}/`;

            if (month && year) {
                printUrl += `${month}/${year}/`;
            }
        
            window.open(printUrl, '_blank');
        });
    }

    cells.forEach(cell => {
        cell.addEventListener('click', () => {
            clickCell(cell);
        });
    });

    balanceCells.forEach(cell => {
        cell.addEventListener('click', () => {
            clickBalanceCell(cell);
        });
    });

    names.forEach(name => {
        name.addEventListener('click', () => {
            clickName(name, template);
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

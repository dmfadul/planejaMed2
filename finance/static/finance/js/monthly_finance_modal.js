function setText(id, value) {
    const element = document.getElementById(id);

    if (element) {
        element.textContent = value;
    }
}

function formatHours(value) {
    const number = Number(value || 0);

    if (Number.isInteger(number)) {
        return `${number}h`;
    }

    return `${number.toFixed(1)}h`;
}

function getCenterTotal(center) {
    return Number(center.routine_hours || 0) + Number(center.overtime_hours || 0);
}

function renderCenters(centers) {
    const container = document.getElementById("financeCentersList");
    container.innerHTML = "";

    if (!centers.length) {
        container.innerHTML = `
            <div class="finance-empty-state">
                Horas não encontradas para este mês.
            </div>
        `;
        return;
    }

    centers.forEach(center => {
        const routineHours = Number(center.routine_hours || 0);
        const overtimeHours = Number(center.overtime_hours || 0);
        const totalHours = routineHours + overtimeHours;

        container.insertAdjacentHTML("beforeend", `
            <article class="finance-center-row">
                <div class="finance-center-main">
                    <div>
                        <h6>${center.abbreviation}</h6>
                        <span class="finance-muted-label">Total do Centro</span>
                    </div>

                    <strong class="finance-center-total">${formatHours(totalHours)}</strong>
                </div>

                <div class="finance-hours-breakdown">
                    <div class="finance-hour-pill">
                        <span>Routine</span>
                        <strong>${formatHours(routineHours)}</strong>
                    </div>

                    <div class="finance-hour-pill">
                        <span>Overtime</span>
                        <strong>${formatHours(overtimeHours)}</strong>
                    </div>
                </div>
            </article>
        `);
    });
}

function renderFinanceModal(data) {
    setText("financeModalSubtitle", `${data.doctor || ""} — ${data.month || ""}`);

    const centers = data.centers || [];
    const totalHours = centers.reduce((sum, center) => {
        return sum + getCenterTotal(center);
    }, 0);

    setText("financeTotalHours", formatHours(totalHours));

    renderCenters(centers);
}

document.addEventListener("DOMContentLoaded", () => {
    const button = document.getElementById("openFinanceModal");

    if (!button) {
        console.error("Button with ID 'openFinanceModal' not found.");
        return;
    }

    button.addEventListener("click", async event => {
        event.preventDefault();

        const modalElement = document.getElementById("monthlyFinanceModal");
        const modal = new bootstrap.Modal(modalElement);

        const loading = document.getElementById("financeModalLoading");
        const error = document.getElementById("financeModalError");
        const content = document.getElementById("financeModalContent");

        loading.classList.remove("d-none");
        error.classList.add("d-none");
        content.classList.add("d-none");

        modal.show();

        try {
            const response = await fetch(button.dataset.financeUrl, {
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                },
            });

            if (!response.ok) {
                throw new Error("Could not load finance data.");
            }

            const data = await response.json();

            renderFinanceModal(data);

            loading.classList.add("d-none");
            content.classList.remove("d-none");
        } catch (err) {
            loading.classList.add("d-none");
            error.textContent = "Could not load finance data.";
            error.classList.remove("d-none");
        }
    });
});
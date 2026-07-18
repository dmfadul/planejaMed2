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

    return `${number.toFixed(1).replace(".", ",")}h`;
}

function renderCenters(centers) {
    const container = document.getElementById("financeCentersList");
    const empty = document.getElementById("financeModalEmpty");

    container.innerHTML = "";
    empty.classList.add("d-none");

    if (!centers || centers.length === 0) {
        empty.classList.remove("d-none");
        return;
    }

    centers.forEach(center => {
        const routineHours = Number(center.routine_hours || 0);
        const urgencyHours = Number(center.urgency_hours || 0);
        const totalHours = routineHours + urgencyHours;

        container.insertAdjacentHTML("beforeend", `
            <article class="finance-center-card">
                <div class="finance-center-top">
                    <h6>${center.name}</h6>
                    <span class="finance-total-hours">${formatHours(totalHours)}</span>
                </div>

                <div class="finance-hours-split">
                    <div class="finance-hour-box">
                        <span>Rotina</span>
                        <strong>${formatHours(routineHours)}</strong>
                    </div>

                    <div class="finance-hour-box">
                        <span>Urgência</span>
                        <strong>${formatHours(urgencyHours)}</strong>
                    </div>
                </div>
            </article>
        `);
    });
}

function renderFinanceModal(data) {
    setText("financeModalSubtitle", `${data.doctor || ""} ${data.month ? "— " + data.month : ""}`);
    renderCenters(data.centers || []);
}

document.addEventListener("DOMContentLoaded", () => {
    const button = document.getElementById("openFinanceModal");

    if (!button) {
        return;
    }

    button.addEventListener("click", async event => {
        event.preventDefault();

        const modalElement = document.getElementById("monthlyFinanceModal");
        const modal = new bootstrap.Modal(modalElement);

        const loading = document.getElementById("financeModalLoading");
        const error = document.getElementById("financeModalError");
        const content = document.getElementById("financeModalContent");
        const empty = document.getElementById("financeModalEmpty");

        loading.classList.remove("d-none");
        error.classList.add("d-none");
        content.classList.add("d-none");
        empty.classList.add("d-none");

        modal.show();

        try {
            const response = await fetch(button.dataset.financeUrl, {
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                },
            });

            if (!response.ok) {
                throw new Error("Não foi possível carregar os horários.");
            }

            const data = await response.json();

            renderFinanceModal(data);

            loading.classList.add("d-none");
            content.classList.remove("d-none");

        } catch (err) {
            loading.classList.add("d-none");
            error.textContent = err.message;
            error.classList.remove("d-none");
        }
    });
});
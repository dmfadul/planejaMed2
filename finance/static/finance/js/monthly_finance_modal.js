function formatCurrency(value) {
    return Number(value || 0).toLocaleString("pt-BR", {
        style: "currency",
        currency: "BRL",
    });
}

function setText(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = value;
    }
}

function renderCenters(centers) {
    const container = document.getElementById("financeCentersList");
    container.innerHTML = "";

    centers.forEach(center => {
        container.insertAdjacentHTML("beforeend", `
            <div class="col-12 col-md-6 col-xl-4">
                <div class="finance-card">
                    <h6>${center.name}</h6>

                    <div class="finance-line">
                        <span>Routine hours</span>
                        <strong>${center.routine_hours}</strong>
                    </div>

                    <div class="finance-line">
                        <span>Urgency hours</span>
                        <strong>${center.urgency_hours}</strong>
                    </div>

                    <div class="finance-line">
                        <span>Total payment</span>
                        <strong>${formatCurrency(center.total_payment)}</strong>
                    </div>
                </div>
            </div>
        `);
    });
}

function renderFinanceModal(data) {
    setText("financeModalSubtitle", `${data.doctor} — ${data.month}`);

    setText("financeTotalPayment", formatCurrency(data.total_payment));
    setText("financeBonuses", formatCurrency(data.bonuses));
    setText("financeExtras", formatCurrency(data.extras));

    renderCenters(data.centers || []);

    setText("ecoDirect", formatCurrency(data.eco?.direct_private));
    setText("ecoUnimed", formatCurrency(data.eco?.unimed));
    setText("ecoCopan", formatCurrency(data.eco?.copan));

    setText("huamDirect", formatCurrency(data.huam?.direct_private));
    setText("huamUnimed", formatCurrency(data.huam?.unimed));
    setText("huamCopan", formatCurrency(data.huam?.copan));

    setText("privateProcedures", data.procedures?.private || 0);
    setText("insuranceProcedures", data.procedures?.insurance || 0);
    setText("erProcedures", data.procedures?.er || 0);
    setText("treatedAih", data.procedures?.treated_aih || 0);
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
            const response = await fetch(button.dataset.financeUrl);

            if (!response.ok) {
                throw new Error("Could not load finance data.");
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
const API = (() => {
    const ENDPOINT = '/api/submit_user_request/';

    // build payload
    function buildPayload({ action, requesteeCRM, ctx, selectedHour = null, meta = {}}) {
        // meta is for future use
        const timePart = selectedHour.substring(selectedHour.indexOf(" ") + 1).trim(); 
        const [start, end] = timePart.split(' - ').map(h => h.trim());       
    
        const center = ctx.center;
        const year = ctx.year;
        const monthNumber = ctx.monthNumber;
        const day = ctx.day;

        const startHour = parseInt(start.split(":")[0], 10);
        const endHour   = parseInt(end.split(":")[0], 10);
        
        return {
            action,
            requesteeCRM,
            center,
            year,
            monthNumber,
            day,
            startHour,
            endHour,
            ...meta
        };
    }

    // POST helper with CSRF, timeout, uniform error handling
    async function post(body, { timeout = 10000, signal } = {}) {
        const controller = new AbortController();
        const timer = setTimeout(() => controller.abort(), timeout);

        try {
            const resp = await fetch(ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')  // Ensure CSRF token is included
                },
                credentials: 'same-origin', // Include cookies in the request
                body: JSON.stringify(body),
                signal: signal ?? controller.signal,
            });

            const raw = await resp.text();
            const data = raw ? JSON.parse(raw) : null;

            if (!resp.ok) {
                const err = new Error((data && (data.detail || data.errors)) || resp.statusText);
                err.status = resp.status;
                err.data = data;
                throw err;
            }
            return data;
        } finally {
            clearTimeout(timer);
        }
    }

    // Convenience wrapper specialized for user requests
    async function submitUserRequest({action, ctx, selectedHour = null, meta = {}, options = {} }) {
        const payload = buildPayload({ action, ctx, selectedHour, meta });
        return post(payload, options);
    }

    return { submitUserRequest, buildPayload, post };
})();

function withBusyButton(btn, fn) {
  return async (...args) => {
    const prev = btn.disabled;
    btn.disabled = true;
    btn.dataset.originalText = btn.textContent;
    btn.textContent = 'Sending...';
    try {
      return await fn(...args);
    } finally {
      btn.disabled = prev;
      btn.textContent = btn.dataset.originalText || 'Submit';
    }
  };
}

function populateSelect(selectId, options, values = []) {
    const container = document.getElementById('dynamicInputs');
    container.innerHTML = '';               // 1) clear out any old <select>
    
    const select = document.createElement('select');
    select.className = 'form-select mb-3';  // Bootstrap styling
    select.id = selectId;
    select.name = selectId;
  
    // 2) proper forEach callback signature
    options.forEach((item, index) => {
      const opt = document.createElement('option');
      // 3) if values[index] exists use it, otherwise fall back to the label
      opt.value = values[index] !== undefined ? values[index] : item;
      opt.textContent = item;
      select.appendChild(opt);
    });
  
    container.appendChild(select);
  }

function processCalRequest(crm, action, center, year, monthNumber, day) {
    const currentUserCrm = parseInt(document.getElementById('calendarData').dataset.currentUserCrm, 10);
    const crmNumber = parseInt(crm, 10);

    const ctx = {
        center: center,
        year: year,
        monthNumber: monthNumber,
        day: day,
        currentUserCrm: currentUserCrm,
        cardCrm: crmNumber,
    };

    if (action === "include") {
        handleCalInclude(ctx);
    } else if(action === "exclude") {
        handleCalExclude(ctx);
    } else if(action === "donate") {
        handleCalDonate(ctx);
    } else if(action === "exchange") {
        handleCalExchange(ctx);
    } else {
        console.error("Unknown action: " + action);
    }
}

function handleCalInclude(ctx) {
}

function handleCalExclude(ctx) {
}

function handleCalDonate(ctx) {
    if (ctx.cardCrm === ctx.currentUserCrm) {
        handleOfferingDonation(ctx);
    } else {
        handleRequestingDonation(ctx);
    }
}

function handleOfferingDonation(ctx) {
    
    let modal = new bootstrap.Modal(document.getElementById('modalRequests'));
    modal.show();
}

function handleRequestingDonation(ctx) {
    fetch(`/api/hours/?crm=${ctx.cardCrm}&year=${ctx.year}&month=${ctx.monthNumber}&center=${ctx.center}&day=${ctx.day}/`)
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(rawData => {
        let data = rawData.data;
        let modal = new bootstrap.Modal(document.getElementById('modalRequests'));

        const modalLabel = document.getElementById('modalRequestsLabel');
        modalLabel.textContent = "Escolha a hora que deseja pedir: ";

        populateSelect('requestHours', data[ctx.cardCrm]["hours"], data[ctx.cardCrm]["hours"]);
        modal.show();

        const submitButton = document.getElementById('submitRequestButton');       
        submitButton.onclick = withBusyButton(submitButton, async function () {
            const selectElement = document.getElementById('requestHours');
            const selectedHour = selectElement.value;
            const requesteeCRM = ctx.cardCrm;

            console.log("requesting donation for hour: ", selectedHour, "ctx: ", ctx);

            try {
                const result = await API.submitUserRequest({
                    action: 'donation',
                    requesteeCRM: requesteeCRM,
                    ctx: ctx,
                    selectedHour: selectedHour,
                    options: { timeout: 15000 }
                });
            
                console.log("submitted donation request, result: ", result);
                modal.hide();

            } catch (e) {
                console.error("server error:", e);
                alert(e.data?.detail || "Um erro ocorreu ao enviar o pedido. Tente novamente mais tarde.");
            }
        });
      })
      .catch(error => {
        console.error("Fetch error:", error);
      });
}

function handleCalExchange(ctx) {
    let modal = new bootstrap.Modal(document.getElementById('modalRequests'));
    modal.show();
}

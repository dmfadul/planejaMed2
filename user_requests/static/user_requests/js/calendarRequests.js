const API = (() => {
    const ENDPOINT = '/api/submit_user_request/';

    // build payload
    function buildPayload({ action, requesteeCRM, selectedHour = null, meta = {}}) {
        // meta is for future use
        
        const [shift, startHourStr, endHourStr] = selectedHour.split("|").map(s => s.trim());
        const startHour = parseInt(startHourStr.split(":")[0], 10);
        const endHour   = parseInt(endHourStr.split(":")[0], 10);

        return {
            action,
            requesteeCRM,
            shift,
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
              'X-CSRFToken': getCookie('csrftoken'),
            },
            credentials: 'same-origin',
            body: JSON.stringify(body),
            signal: signal ?? controller.signal,
          });
      
          // Try to parse JSON; server might return empty body on 201
          let data = null;
          const raw = await resp.text();
          if (raw) {
            try { data = JSON.parse(raw); } catch { /* keep as null */ }
          }
      
          if (!resp.ok) {
            // DRF commonly returns either a dict of field errors or {"detail": "..."} or {"errors": {...}}
            const errors = data?.errors ?? data ?? { detail: resp.statusText };
            const message = humanizeErrors(errors);
            const err = new Error(message);
            err.status = resp.status;
            err.data = errors;
            throw err;
          }
      
          return data;
        } finally {
          clearTimeout(timer);
        }
    }

    // Convenience wrapper specialized for user requests
    async function submitUserRequest({action, requesteeCRM, selectedHour = null, meta = {}, options = {} }) {
        const payload = buildPayload({ action, requesteeCRM, selectedHour, meta });
        return post(payload, options);
    }

    return { submitUserRequest, buildPayload, post };
})();

function humanizeErrors(errors) {
  if (!errors) return "Unknown error.";
  if (typeof errors === "string") return errors;

  // DRF sometimes puts a single message under "detail"
  if (errors.detail) return Array.isArray(errors.detail) ? errors.detail.join("\n") : String(errors.detail);

  // DRF field errors / non_field_errors
  const out = [];
  if (errors.non_field_errors) {
    out.push([].concat(errors.non_field_errors).join("\n"));
  }
  // Other field-specific errors
  for (const [field, msgs] of Object.entries(errors)) {
    if (field === "non_field_errors") continue;
    const line = `${field}: ${Array.isArray(msgs) ? msgs.join(", ") : String(msgs)}`;
    out.push(line);
  }
  return out.join("\n");
}

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
    console.log("selID", selectId, "opt", options, "vals", values);
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
    fetch(`/api/hours/?crm=${ctx.cardCrm}&year=${ctx.year}&month=${ctx.monthNumber}&center=${ctx.center}&day=${ctx.day}`)
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(rawData => {
        let data = rawData;
        let modal = new bootstrap.Modal(document.getElementById('modalRequests'));

        const errorBox = document.getElementById('requestErrors');
        
        // ✅ Clear any previous error before sending request
        errorBox.classList.add('d-none');
        errorBox.textContent = '';

        const modalLabel = document.getElementById('modalRequestsLabel');
        modalLabel.textContent = "Escolha a hora que deseja pedir: ";

        const hoursArray = formatHourRange(data);
        populateSelect('requestHours', hoursArray[0], hoursArray[1]);
        modal.show();

        const submitButton = document.getElementById('submitRequestButton');       
        submitButton.onclick = withBusyButton(submitButton, async function () {
            const selectElement = document.getElementById('requestHours');
            const selectedHour = selectElement.value;
            const requesteeCRM = ctx.cardCrm;

            console.log("requesting donation for hour: ", selectedHour, "ctx: ", ctx);

            try {
                const result = await API.submitUserRequest({
                    action: 'donation_required', // vs 'donation_offered'
                    requesteeCRM: requesteeCRM,
                    selectedHour: selectedHour,
                    options: { timeout: 15000 }
                });
            
                console.log("submitted donation request, result: ", result);
                modal.hide();

                showToast("Pedido enviado com sucesso!", "success");

            } catch (e) {
                console.error("server error:", e);
                errorBox.textContent = e.message || "Um erro ocorreu ao enviar o pedido.";
                errorBox.classList.remove('d-none');
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

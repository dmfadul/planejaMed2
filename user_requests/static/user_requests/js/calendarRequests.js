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
        submitButton.onclick = function() {
            const selectElement = document.getElementById('requestHours');
            const selectedHour = selectElement.value;
            console.log(`Requesting hour: ${selectedHour} from CRM: ${ctx.cardCrm}`);
            // Here you can add the logic to send the request to the server
            modal.hide();
        };

        // displayDaySchedule(data);
      })
      .catch(error => {
        console.error("Fetch error:", error);
      });
}

function handleCalExchange(ctx) {
    let modal = new bootstrap.Modal(document.getElementById('modalRequests'));
    modal.show();
}

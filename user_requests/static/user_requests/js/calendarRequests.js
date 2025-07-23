function processCalRequest(crm, action) {
    const crmNumber = parseInt(crm, 10);
    if (action === "include") {
        handleCalInclude(crmNumber);
    } else if(action === "exclude") {
        handleCalExclude(crmNumber);
    } else if(action === "donate") {
        handleCalDonate(crmNumber);
    } else if(action === "exchange") {
        handleCalExchange(crmNumber);
    } else {
        console.error("Unknown action: " + action);
    }
}

function handleCalInclude(crm) {
}

function handleCalExclude(crm) {
}

function handleCalDonate(crm) {
    console.log(typeof crm, typeof currentUserCrm)
    if (crm === currentUserCrm) {
        handleOfferingDonation(crm);
    } else {
        handleRequestingDonation(crm);
    }
}

function handleOfferingDonation(crm) {
    let modal = new bootstrap.Modal(document.getElementById('modalRequests'));
    modal.show();
}

function handleRequestingDonation(crm) {
}

function handleCalExchange(crm) {
}

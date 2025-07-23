function processCalRequest(crm, action) {
    if(action === "include") {
    } else if(action === "exclude") {
    } else if(action === "donate") {
    } else if(action === "exchange") {
    }
}


function includeCalRequest(crm) {
    let modal = new bootstrap.Modal(document.getElementById('modalRequests'));
    modal.show();
}
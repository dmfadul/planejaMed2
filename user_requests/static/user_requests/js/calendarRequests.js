function processCalRequest(crm, action) {
    let modal = new bootstrap.Modal(document.getElementById('modalRequests'));
    modal.show();
    console.log(`Processing ${action} for CRM: ${currentUserCrm}`);
}
function showToast(message, type = "success") {
    const toastEl = document.getElementById('successToast');
    toastEl.querySelector('.toast-body').textContent = message;

    // Switch style if needed (success, danger, info, etc.)
    toastEl.className = `toast align-items-center text-bg-${type} border-0`;

    const toast = new bootstrap.Toast(toastEl);
    toast.show();
}

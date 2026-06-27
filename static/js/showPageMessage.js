function showPageMessage(message, type = "success", duration = 3000) {
    const container = document.getElementById("page-message-container");

    if (!container) {
        console.warn("Missing #page-message-container");
        return;
    }

    container.innerHTML = "";

    const messageDiv = document.createElement("div");
    messageDiv.className = `page-message ${type}`;
    messageDiv.textContent = message;

    container.appendChild(messageDiv);

    if (duration) {
        clearTimeout(window.__pageMessageTimer);

        window.__pageMessageTimer = setTimeout(() => {
            messageDiv.remove();
        }, duration);
    }
}
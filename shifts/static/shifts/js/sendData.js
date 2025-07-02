async function sendData() {
    try {
        const response = await fetch('/shifts/update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify(state)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Server responded with status ${response.status}`);
        }

        const data = await response.json(); // Expecting { updates: [{ cellID, newValue }, ...] }

        data.updates.forEach(update => {
            const cell = document.getElementById(update.cellID);
            if (cell) {
                cell.textContent = update.newValue;

                cell.style.transition = "background-color 0.5s";
                cell.style.backgroundColor = state.action === 'add' ? "green" : "red";
            }
        });

        console.log("Appointments updated successfully!");

    } catch (error) {
        console.error('Error:', error);
        alert(error.message);  // 🟥 Shows backend error message here
    } finally {
        setTimeout(() => {
            clearSelectedCells();
        }, 500); 
    }
}

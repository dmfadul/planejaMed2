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
            throw new Error(`Server responded with status ${response.status}`);
        }

        const data = await response.json(); // Expecting { updates: [{ cellID, newValue }, ...] }

        data.updates.forEach(update => {
            const cell = document.getElementById(update.cellID);
            if (cell) {
                cell.textContent = update.newValue;

                cell.style.transition = "background-color 1s";
                cell.style.backgroundColor = state.action === 'add' ? "green" : "red";
                setTimeout(() => {
                    cell.style.backgroundColor = "";
                }, 1000);
            }
        });

        console.log("Appointments updated successfully!");

    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while updating appointments. Please try again.');
    } finally {
        state['selectedCells'] = []; // clear selected cells
        clearSelectedCells();
    }
}

function confirmData() {
    state.selectedCells.forEach(cell => {
        delete cell.weekDay;
        delete cell.monthDay;
        delete cell.doctorCRM;
    });
    return Promise.resolve()
}


async function sendData() {
    try {
        await confirmData();

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

        const data = await response.json(); // Expecting { updates: [{ cellId, newValue }, ...] }
        
        data.updates.forEach(update => {
            const cell = document.getElementById(update.cellID);
            if (cell) {
                cell.textContent = update.newValue;

                cell.style.transition = "background-color 1s";
                cell.style.backgroundColor = state.action === 'add' ? "green" : "red"; // Highlight selected cells based on action
                setTimeout(() => {
                    cell.style.backgroundColor = ""; // Reset background color after 2 seconds
                }, 1000);
            }
        });

        console.log("Appointments updated succefully!");

    } catch (error) {
        if (error !== "User cancelled the operation") {
            console.error('Error:', error);
            alert('An error ocurred while updating appointments. Please Try Again.')
        } else {
            console.log('Operation Cacelled by the user.');
        }

    } finally {
        clearSelectedCells();
    }
}

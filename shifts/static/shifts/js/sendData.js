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
        //apply updates

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



function confirmData() {
    return Promise.resolve()
}

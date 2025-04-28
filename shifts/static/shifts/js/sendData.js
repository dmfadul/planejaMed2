function sendData() {
    confirmData()
        .then(() => {
            return fetch("/shifts/update", {});
        })

    clearSelectedCells();
}

function confirmData() {
    return Promise.resolve()
}

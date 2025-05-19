function addListeners() {
    const cells = document.querySelectorAll('.cell-col');
    const names = document.querySelectorAll('.name-col');
    const addButton = document.getElementById('edit-add-button');
    const remButton = document.getElementById('edit-rem-button');

    console.log("✅ addListeners running after table render. Found:", cells.length);

    cells.forEach(cell => {
        cell.addEventListener('click', () => {
            clickCell(cell);
        });
    });

    names.forEach(name => {
        name.addEventListener('click', () => {
            clickName(name);
        });
    });

    if (addButton) {
        addButton.addEventListener('click', () => executeEdit('add'));
    }

    if (remButton) {
        remButton.addEventListener('click', () => executeEdit('remove'));
    }
}

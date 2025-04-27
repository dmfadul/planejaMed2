// Event listeners
const cells = document.querySelectorAll('.cell-col');
const names = document.querySelectorAll('.name-col');
const headers = document.querySelectorAll('.header');
const corners = document.querySelectorAll('.corner');

const addButton = document.getElementById('edit-add-button');
const remButton = document.getElementById('edit-rem-button');


cells.forEach(cell => {
    cell.addEventListener('click', () => {
        clickCell(cell);
    })
});


addButton.addEventListener('click', () => {
    executeEdit('add');
});


remButton.addEventListener('click', () => {
    executeEdit('remove');
});
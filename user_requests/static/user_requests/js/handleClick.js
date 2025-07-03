document.addEventListener('DOMContentLoaded', function() {
    console.log('handleClick.js loaded');
    function handleDayClick(event) {
        const clickedDay = event.target;
        // Check if clicked element is a day (a TD element with a number)
        if (clickedDay.tagName === "TD" && !isNaN(clickedDay.innerText) && clickedDay.innerText !== '') {
            document.querySelectorAll('.calendar td').forEach(td => {
                td.classList.remove('day-clicked');
            });

            clickedDay.classList.add('day-clicked');   
            day = clickedDay.innerText;

            const xhr = new XMLHttpRequest();
            xhr.open('GET', `/get-day-data?day=${encodeURIComponent(day)}&center=${encodeURIComponent(openCenter)}`, true);

            xhr.onload = function() {
                if (this.status === 200) {
                    const response = JSON.parse(this.responseText);
                    // console.log(response);
                    displayDayData(response);
                } else {
                    console.error('Error fetching day data');
                }
                xhr.onerror = function() {
                    console.error('Error fetching day data');
                }
            }
            xhr.send();
        }
    }

    // Add the click event listener to the table
    const calendarTable = document.querySelector('.calendar');
    calendarTable.addEventListener('click', handleDayClick);
});

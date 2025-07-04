document.addEventListener('DOMContentLoaded', function() {
    const dataEl = document.getElementById("calendarData");

    const openCenter = dataEl.dataset.openCenter;
    const monthNumber = parseInt(dataEl.dataset.monthNumber);
    const year = parseInt(dataEl.dataset.year);
    
    function handleDayClick(event) {
        const clickedDay = event.target;
        // Check if clicked element is a day (a TD element with a number)
        if (clickedDay.tagName === "TD" && !isNaN(clickedDay.innerText) && clickedDay.innerText !== '') {
            document.querySelectorAll('.calendar td').forEach(td => {
                td.classList.remove('day-clicked');
            });

            clickedDay.classList.add('day-clicked');   
            day = parseInt(clickedDay.innerText);

            fetch(`/api/day_schedule/${openCenter}/${year}/${monthNumber}/${day}/`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log("Received data:", data);
                // You can now use `data` however you want
              })
              .catch(error => {
                console.error("Fetch error:", error);
              });
        }
    }

    // Add the click event listener to the table
    const calendarTable = document.querySelector('.calendar');
    calendarTable.addEventListener('click', handleDayClick);
});

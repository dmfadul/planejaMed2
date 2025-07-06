function displayDaySchedule(dayDict) {
    let output = '<ul>'
    output += `
    <li id="item-0" class="card">
        INCLUSÃO
        <div class="kebab-menu">
            <div class="kebab-content">
                <a href="#" onclick="processCalRequest('0', 'include')" data-action="include">Inclusão</a>
            </div>
        </div>
    </li>`;

    for (const [crm, info] of Object.entries(dayDict)) {
        console.log(`${crm}: `);
        for (const [key, values] of Object.entries(info)) {
            console.log(`${key}: ${values}`);
        }
    }

    output += '</ul>';  // Close the unordered list
    
    document.getElementById('dictData').innerHTML = output;
}

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
                displayDaySchedule(data);
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

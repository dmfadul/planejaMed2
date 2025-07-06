function displayDaySchedule(dayDict) {
    dayArray = dayDict["schedule"];
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
    
    

    dayArray.forEach(info => {
        const cardContent = info["cardLine"];
        const crm = info["crm"];
        
        output += `
        <li id="${crm}" class="card">
            ${cardContent}
            <div class="kebab-menu">
                <div class="kebab-content">
                <a href="#" onclick="processCalRequest('${crm}', 'exclude')" data-action="exclude">Exclusão</a>
                <a href="#" onclick="processCalRequest('${crm}', 'donate')" data-action="donation">Doação</a>
                <a href="#" onclick="processCalRequest('${crm}', 'exchange')" data-action="exchange">Troca</a>
                </div>
            </div>
        </li>`;
    });

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

document.addEventListener('click', function(event) {
    let card = event.target.closest('.card');
    let openMenus = document.querySelectorAll('.kebab-content');
    let allCards = document.querySelectorAll('#dictData li');

    // Hide all menus and remove active class from all cards
    for (let menu of openMenus) {
        menu.style.display = 'none';
    }
    for (let li of allCards) {
        li.classList.remove('active');
    }

    // If clicked inside a card, show its kebab-content and add active class
    if (card) {
        let kebab = card.querySelector('.kebab-content');
        if (kebab) {
            kebab.style.display = 'block';
            card.classList.add('active'); // Add active class to parent li
        }
    }
});
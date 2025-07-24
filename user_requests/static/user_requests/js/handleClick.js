(() => {
    // ---------- State ----------
    const ctx = {
        openCenter: null,
        year: null,
        month: null,
        day: null,        // currently selected day
    };

    // ---------- Init ----------
    document.addEventListener('DOMContentLoaded', function() {
        const dataEl = document.getElementById("calendarData");
        ctx.openCenter = dataEl.dataset.openCenter;
        ctx.monthNumber = parseInt(dataEl.dataset.monthNumber);
        ctx.year = parseInt(dataEl.dataset.year);

        // Delegation targets
        const calendarTable = document.querySelector('.calendar');
        calendarTable.addEventListener('click', onCalendarClick);
    });

    // ---------- Calendar day click ----------
    async function onCalendarClick(e) {
        const td = e.target.closest('td');
        if (!td) return;

        const txt = td.innerText.trim();
        if (!txt || isNaN(txt)) return; // Ignore empty or non-numeric cells

        document.querySelectorAll('.calendar td').forEach(el => el.classList.remove('day-clicked'));
        td.classList.add('day-clicked');

        ctx.day = parseInt(txt, 10);

        try {
            const res = await fetch(`/api/day_schedule/${ctx.openCenter}/${ctx.year}/${ctx.monthNumber}/${ctx.day}/`);
            if (!res.ok) throw new Error(res.statusText);
            const data = await res.json();
            displayDaySchedule(data);
        } catch (err) {
            console.error('Fetch error:', err);
        }

    }

    // ---------- Render list ----------
    function displayDaySchedule(dayDict) {
        const ulAttrs = `
          data-open-center="${ctx.openCenter}"
          data-year="${ctx.year}"
          data-month="${ctx.month}"
          data-day="${ctx.day}"`;

        const includeLi = `
        <li id="item-0" class="card">
            INCLUSÃO
            <div class="kebab-menu">
                <div class="kebab-content">
                    <a href="#" data-action="include">Inclusão</a>
                </div>
            </div>
        </li>`;

        const items = dayDict.schedule.map(({ cardLine, crm }) => `
        <li class="card" data-crm="${crm}">
            ${cardLine}
            <div class="kebab-menu">
                <div class="kebab-content">
                    <a href="#" data-action="exclude">Exclusão</a>
                    <a href="#" data-action="donate">Doação</a>
                    <a href="#" data-action="exchange">Troca</a>
                </div>
            </div>
        `).join('');

        document.getElementById('dictData').innerHTML = `<ul ${ulAttrs}>${includeLi}${items}</ul>`;
    }

    // ---------- Action click (exclude/donate/exchange/include) + kebab show ----------

    document.addEventListener('click', function(event) {
        const openMenus = document.querySelectorAll('.kebab-content');
        const allCards = document.querySelectorAll('#dictData li');

        // Hide all menus and remove active class from all cards
        for (let menu of openMenus) {
            menu.style.display = 'none';
        }
        for (let li of allCards) {
            li.classList.remove('active');
        }

        const card = event.target.closest('.card');

        // If clicked inside a card, show its kebab-content and add active class
        if (card) {
            const kebab = card.querySelector('.kebab-content');

            if (kebab) {
                kebab.style.display = 'block';
                card.classList.add('active'); // Add active class to parent li
            }
        }

        const link = event.target.closest('a[data-action]');
        if (link) {
            const crm    = card?.dataset.crm || null;
            const action = link.dataset.action;

            processCalRequest(
                crm,
                action,
                ctx.openCenter,
                ctx.year,
                ctx.monthNumber,
                ctx.day
            );
        }
    });
})();
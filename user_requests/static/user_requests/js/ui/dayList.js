// Renders the right-side list for a selected day.

export function renderDaySchedule(containerId, { openCenter, year, monthNumber, day, schedule }) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const ulAttrs = `
    data-open-center="${openCenter}"
    data-year="${year}"
    data-month-number="${monthNumber}"
    data-day="${day}"`;

  const includeLi = `
    <li id="item-0" class="card">
      INCLUSÃO
      <div class="kebab-menu">
        <div class="kebab-content">
          <a href="#" data-action="include">Inclusão</a>
        </div>
      </div>
    </li>`;

  const items = (schedule || []).map(({ cardLine, crm }) => `
    <li class="card" data-crm="${crm}">
      ${cardLine}
      <div class="kebab-menu">
        <div class="kebab-content">
          <a href="#" data-action="exclude">Exclusão</a>
          <a href="#" data-action="donate">Doação</a>
          <a href="#" data-action="exchange" class="disabled">Troca</a>
        </div>
      </div>
    </li>
  `).join('');

  container.innerHTML = `<ul ${ulAttrs}>${includeLi}${items}</ul>`;
}

/** Utility to clear “active” card and hide all kebab menus */
export function resetKebabUI() {
  document.querySelectorAll('.kebab-content').forEach(menu => (menu.style.display = 'none'));
  document.querySelectorAll('#dictData li').forEach(li => li.classList.remove('active'));
}

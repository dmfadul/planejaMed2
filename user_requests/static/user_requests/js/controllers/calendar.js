// controllers/calendar.js
// Owns state + event wiring for the calendar table and action clicks.

import { fetchDaySchedule } from '../data/days.js';
import { renderDaySchedule, resetKebabUI } from '../ui/dayList.js';
import { processCalRequest } from './requests.js'; // from earlier split

const state = {
  openCenter: null,
  year: null,
  monthNumber: null,
  day: null, // currently selected day
};

export function initCalendar({
  calendarSelector = '.calendar',
  dictContainerId = 'dictData',
  dataElId = 'calendarData',
} = {}) {
  // Bootstrap state from #calendarData
  const dataEl = document.getElementById(dataElId);
  if (!dataEl) return;

  state.openCenter  = dataEl.dataset.openCenter;
  state.monthNumber = parseInt(dataEl.dataset.monthNumber, 10);
  state.year        = parseInt(dataEl.dataset.year, 10);

  // Calendar day click
  const calendarTable = document.querySelector(calendarSelector);
  if (calendarTable) {
    calendarTable.addEventListener('click', (e) => onCalendarClick(e, dictContainerId));
  }

  // Action click + kebab toggle (global delegation)
  document.addEventListener('click', (event) => onDocumentClick(event, dictContainerId));
}

async function onCalendarClick(e, dictContainerId) {
  const td = e.target.closest('td');
  if (!td) return;

  const txt = (td.textContent || '').trim();
  if (!txt || isNaN(txt)) return; // ignore empty/non-numeric cells

  document.querySelectorAll('.calendar td').forEach(el => el.classList.remove('day-clicked'));
  td.classList.add('day-clicked');

  state.day = parseInt(txt, 10);

  try {
    const data = await fetchDaySchedule({
      center: state.openCenter,
      year: state.year,
      monthNumber: state.monthNumber,
      day: state.day,
    });
    renderDaySchedule(dictContainerId, {
      openCenter: state.openCenter,
      year: state.year,
      monthNumber: state.monthNumber,
      day: state.day,
      schedule: data.schedule || [],
    });
  } catch (err) {
    console.error('Fetch error (day schedule):', err);
    // You can show a toast/error box here if desired.
  }
}

function onDocumentClick(event, dictContainerId) {
  // Always reset first
  resetKebabUI();

  const card = event.target.closest('.card');
  if (card) {
    const kebab = card.querySelector('.kebab-content');
    if (kebab) {
      kebab.style.display = 'block';
      card.classList.add('active');
    }
  }

  const link = event.target.closest('a[data-action]');
  if (!link) return;

  const action = link.dataset.action;
  const crm    = card?.dataset.crm || null;

  // Guard: do nothing if no day selected yet
  if (!state.day) return;

  processCalRequest(
    crm,
    action,
    state.openCenter,
    state.year,
    state.monthNumber,
    state.day
  );
}

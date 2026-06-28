// main.js
// Entry point. Expose processCalRequest for inline HTML usage.

import { processCalRequest } from './controllers/requests.js';
import { initCalendar } from './controllers/calendar.js';

// If you still call from HTML onclick handlers:
window.processCalRequest = processCalRequest;

// Modules are deferred by default, but DOMContentLoaded keeps it robust
document.addEventListener('DOMContentLoaded', () => {
  initCalendar();
});

// If you prefer unobtrusive JS, you could also attach listeners here.
// Example (optional):
// document.addEventListener('click', (e) => {
//   const el = e.target.closest('[data-cal-request]');
//   if (!el) return;
//   const { crm, action, center, year, month, day } = el.dataset;
//   processCalRequest(crm, action, center, Number(year), Number(month), Number(day));
// });


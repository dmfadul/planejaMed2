// main.js
// Entry point. Expose processCalRequest for inline HTML usage.

import { processCalRequest } from './controllers/requests.js';

// If you still call from HTML onclick handlers:
window.processCalRequest = processCalRequest;

// If you prefer unobtrusive JS, you could also attach listeners here.
// Example (optional):
// document.addEventListener('click', (e) => {
//   const el = e.target.closest('[data-cal-request]');
//   if (!el) return;
//   const { crm, action, center, year, month, day } = el.dataset;
//   processCalRequest(crm, action, center, Number(year), Number(month), Number(day));
// });


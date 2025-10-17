// main.js
// Entry point. Expose processSchRequest for inline HTML usage.

import { processSchRequest } from './controllers/requests.js';
import { initSchedule } from './controllers/calendar.js';

// If you still call from HTML onclick handlers:
window.processSchRequest = processSchRequest;

// Modules are deferred by default, but DOMContentLoaded keeps it robust
document.addEventListener('DOMContentLoaded', () => {
  // TODO: fix toast
  initSchedule();
});
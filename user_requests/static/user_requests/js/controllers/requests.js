// requests.js — thin delegator to the single "wizard" modal flow

import { submitUserRequest } from '../api.js';
import { fetchHours } from '../data/hours.js';
import { fetchNamesList } from '../data/days.js';
import { ACTIONS } from '../domain/actions.js';

// Import the wizard-based handler from your new ui/modal.js
// (We alias it to avoid name collisions with this file's exported handleAction)
import { handleAction as handleActionWizard } from '../ui/modal.js';

/**
 * Temporary dependency injection:
 * The wizard code (ui/modal.js) expects these to be accessible in its scope.
 * Until you refactor ui/modal.js to import them directly, we expose them on window.
 * This keeps the change localized to this file.
 */
if (typeof window !== 'undefined') {
  window.ACTIONS = window.ACTIONS || ACTIONS;
  window.fetchHours = window.fetchHours || fetchHours;
  window.fetchNamesList = window.fetchNamesList || fetchNamesList;
  window.submitUserRequest = window.submitUserRequest || submitUserRequest;
  // showToast is usually already global. If yours is a module, attach it here too.
  // window.showToast = window.showToast || yourShowToastImport;
}

/**
 * Public API used by the rest of your app.
 * Now it simply forwards to the wizard-based implementation.
 */
export async function handleAction(action, ctx) {
  return handleActionWizard(action, ctx);
}


export function processSchRequest(action, shiftId, center, day, str_hour, end_hour) {
  handleAction(action, {
    shiftId,
    center, day,
    str_hour, end_hour,
  });
}

/**
 * Calendar entrypoint: normalizes "donate" into ask/offer and forwards to the handler.
 */
export function processCalRequest(crm, action, center, year, monthNumber, day) {
  const currentUserCrm = +document.getElementById('calendarData').dataset.currentUserCrm;
  let adjustedAction = action;

  if (action === 'donate' && +crm === +currentUserCrm) {
    adjustedAction = 'offer_donation';
  } else if (action === 'donate' && +crm !== +currentUserCrm) {
    adjustedAction = 'ask_for_donation';
  }

  handleAction(adjustedAction, {
    center, year, monthNumber, day,
    currentUserCrm,
    cardCrm: +crm,
  });
}

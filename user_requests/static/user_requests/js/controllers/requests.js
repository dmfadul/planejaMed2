import { submitUserRequest } from '../api.js';
import { fetchHours } from '../data/hours.js';
import { ACTIONS } from '../domain/actions.js';
import { runRequestModal } from '../ui/modal.js';
import { runShiftHourModal } from '../ui/modal.js';
import { fetchNamesList } from '../data/days.js';
import { runNamesModal } from '../ui/modal.js';


export async function handleAction(action, ctx) {
  const cfg = ACTIONS[action];
  if (!cfg) return console.error('Unknown action:', action);

  try {
    const title    = cfg.title;
    const needsHr  = cfg.needsHour;

    let submitted = false;
    let selectedHour = null;
    let shiftCode = null;
    let startTime = null;
    let endTime   = null;
    let selectUserCRM = null;

    if (needsHr) {
      const hours    = await fetchHours({ crm: cfg.hoursCRM(ctx), ...ctx });
      ({ submitted, selectedHour } = await runRequestModal({ title, hours }));
    } else {
      const nameData = await fetchNamesList();
      const names = nameData.map(item => item.name);
      const crms = nameData.map(item => item.crm);

      ({ submitted, selectedValue: selectUserCRM } = await runNamesModal({ title, names, values: crms }));
      if (!submitted) return;
      ({ submitted, shiftCode, startTime, endTime } = await runShiftHourModal());
    }
    
    if (!submitted) return;
    
    const cardCRM = ctx.cardCrm || selectUserCRM;
    await submitUserRequest({
      action: cfg.endpointAction,
      cardCRM,
      selectedHour,
      shiftCode,
      startTime,
      endTime,      
      options: { timeout: 15000 },
    });
    showToast("Pedido enviado com sucesso!", "success");
    bootstrap.Modal.getInstance(document.getElementById('modalRequests'))?.hide();
  } catch (e) {
    // minimal surface area for error UI here (or delegate to ui/modal.js)
    const box = document.getElementById('requestErrors');
    box.textContent = e.message || "Um erro ocorreu ao enviar o pedido.";
    box.classList.remove('d-none');
  }
}

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

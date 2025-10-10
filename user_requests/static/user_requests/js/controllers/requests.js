import { submitUserRequest } from '../api.js';
import { runRequestModal } from '../ui/modal.js';
import { fetchHours } from '../data/hours.js';
import { ACTIONS } from '../domain/actions.js';

export async function handleAction(action, ctx) {
  const cfg = ACTIONS[action];
  if (!cfg) return console.error('Unknown action:', action);

  try {
    const title    = cfg.title;
    const needsHr  = cfg.needsHour;
    const hours    = needsHr ? await fetchHours({ crm: cfg.hoursCRM(ctx), ...ctx }) : null;
    
    const { submitted, selectedHour } = await runRequestModal({ title, hours });
    if (!submitted) return;

    await submitUserRequest({
      action: cfg.endpointAction,
      requesteeCRM: ctx.cardCrm,
      selectedHour: selectedHour,
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
    adjustedAction = 'request_donation';
  }

  handleAction(adjustedAction, {
    center, year, monthNumber, day,
    currentUserCrm,
    cardCrm: +crm,
  });
}

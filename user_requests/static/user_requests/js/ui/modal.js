import { formatHourRange } from '../data/hours.js';

/* ===========================
 * Small DOM / UI utilities
 * =========================== */

/** Resolve when a Bootstrap modal element is fully hidden */
function waitHidden(modalEl) {
  return new Promise(resolve => {
    modalEl.addEventListener('hidden.bs.modal', () => resolve(), { once: true });
  });
}

/** When shiftCode !== '-', disable hour selects and auto-fill; also enforce end > start */
function handleDropdownChange(dropdown1, dropdown2, dropdown3) {
  if (dropdown1.value !== '-') {
    dropdown2.disabled = true;
    dropdown3.disabled = true;
    dropdown2.style.backgroundColor = '#a0a0a0';
    dropdown3.style.backgroundColor = '#a0a0a0';
    dropdown2.selectedIndex = -1;
    dropdown3.selectedIndex = -1;
  } else {
    dropdown2.disabled = false;
    dropdown3.disabled = false;
    dropdown2.style.backgroundColor = '';
    dropdown3.style.backgroundColor = '';
    dropdown3.selectedIndex = 1;

    const selectedIndex = dropdown2.selectedIndex;

    Array.from(dropdown3.options).forEach((option, index) => {
      if (index <= selectedIndex) {
        option.style.display = 'none';
      } else {
        option.style.display = 'block';
      }
    });
    dropdown3.selectedIndex = selectedIndex + 1;
  }
}

function createDropdown(id, options, values = {}) {
  const dropdown = document.createElement('select');
  dropdown.classList.add('form-select');
  dropdown.id = id;
  dropdown.name = id;

  options.forEach(option => {
    const opt = document.createElement('option');
    if (Object.keys(values).length > 0) {
      opt.value = values[option];
    } else {
      opt.value = option;
    }
    opt.textContent = option;
    dropdown.appendChild(opt);
  });

  return dropdown;
}

/** Button busy-state wrapper (local to UI) */
function withBusyButton(fn) {
  return async (ev) => {
    const btn = ev?.currentTarget ?? ev?.target;
    if (!(btn instanceof HTMLElement)) {
      return fn();
    }
    const prevDisabled = btn.disabled;
    const prevText = btn.textContent;
    btn.disabled = true;
    btn.textContent = 'Sending...';
    try {
      return await fn();
    } finally {
      btn.disabled = prevDisabled;
      btn.textContent = prevText || 'Submit';
    }
  };
}

/** Create and fill a <select> inside #dynamicInputs */
export function populateSelect(selectId, options, values = []) {
  const container = document.getElementById('dynamicInputs');
  container.innerHTML = '';

  const select = document.createElement('select');
  select.className = 'form-select mb-3';
  select.id = selectId;
  select.name = selectId;

  options.forEach((item, index) => {
    const opt = document.createElement('option');
    opt.value = values[index] !== undefined ? values[index] : item;
    opt.textContent = item;
    select.appendChild(opt);
  });

  container.appendChild(select);
}

/** Show an error message inside the currently visible modal (fallback to toast/console) */
function showModalError(msg) {
  const anyModalShown = document.querySelector('.modal.show');

  // Prefer #requestErrors if present inside the shown modal
  const box = anyModalShown?.querySelector('#requestErrors');
  if (box) {
    box.textContent = msg;
    box.classList.remove('d-none');
    return;
  }

  // Otherwise, find a generic .alert/.error element inside the shown modal
  const alt = anyModalShown?.querySelector('.alert, .error');
  if (alt) {
    alt.textContent = msg;
    alt.classList.remove('d-none');
    return;
  }

  // Fallbacks
  if (typeof showToast === 'function') {
    showToast(msg, 'danger');
  } else {
    console.error(msg);
  }
}

/* ===========================
 * Modal Runners
 * =========================== */

/**
 * Show a select list of names/crms in #modalRequests and resolve once.
 * Returns: { submitted:boolean, selectedLabel:string|null, selectedValue:string|null, selectedIndex:number }
 * Stays OPEN on submit; caller decides when to close (on success).
 * Cancelling/closing the modal resolves with submitted=false.
 */
export async function runNamesModal({ title, names = [], values = [] }) {
  const modalEl   = document.getElementById('modalRequests');
  const errorBox  = document.getElementById('requestErrors');
  const labelEl   = document.getElementById('modalRequestsLabel');
  const submitBtn = document.getElementById('submitRequestButton');

  if (!modalEl || !labelEl || !submitBtn) {
    throw new Error('Modal elements not found. Check your template IDs.');
  }
  if (!Array.isArray(names) || !Array.isArray(values)) {
    throw new Error('names and values must be arrays.');
  }
  if (names.length !== values.length) {
    throw new Error('names and values must have the same length.');
  }
  if (names.length === 0) {
    throw new Error('names/values cannot be empty.');
  }

  const modal = new bootstrap.Modal(modalEl);

  // Reset UI
  errorBox?.classList.add('d-none');
  if (errorBox) errorBox.textContent = '';
  labelEl.textContent = title;

  const dynamic = document.getElementById('dynamicInputs');
  dynamic?.replaceChildren();

  // Build select group
  const group = document.createElement('div');
  group.className = 'mb-3';

  const label = document.createElement('label');
  label.className = 'form-label fw-semibold';
  label.setAttribute('for', 'requestSelect');
  label.textContent = '';

  const select = document.createElement('select');
  select.id = 'requestSelect';
  select.className = 'form-select';

  for (let i = 0; i < names.length; i++) {
    const opt = document.createElement('option');
    opt.textContent = names[i];
    opt.value = values[i];
    select.appendChild(opt);
  }

  group.appendChild(label);
  group.appendChild(select);
  dynamic?.appendChild(group);

  let resolved = false;

  const result = await new Promise(resolve => {
    const finalize = (payload) => {
      if (resolved) return;
      resolved = true;
      resolve(payload);
    };

    const onHidden = () => finalize({
      submitted: false,
      selectedLabel: null,
      selectedValue: null,
      selectedIndex: -1
    });
    modalEl.addEventListener('hidden.bs.modal', onHidden, { once: true });

    const clickHandlerCore = async () => {
      const el = document.getElementById('requestSelect');
      const idx = el?.selectedIndex ?? -1;
      const submitted = idx >= 0;
      const selectedLabel = submitted ? names[idx] : null;
      const selectedValue = submitted ? values[idx] : null;
      finalize({ submitted, selectedLabel, selectedValue, selectedIndex: idx });
    };

    const clickHandler = (typeof withBusyButton === 'function')
      ? withBusyButton(clickHandlerCore)
      : clickHandlerCore;

    submitBtn.addEventListener('click', clickHandler, { once: true });
    modal.show();
  });

  return result;
}

/**
 * Show #modalRequests optionally with an hours select; resolve once.
 * Returns: { submitted:boolean, selectedHour:string|null }
 * Stays OPEN on submit; caller decides when to close (on success).
 * Cancelling/closing the modal resolves with submitted=false.
 */
export async function runRequestModal({ title, hours = null }) {
  const modalEl   = document.getElementById('modalRequests');
  const errorBox  = document.getElementById('requestErrors');
  const labelEl   = document.getElementById('modalRequestsLabel');
  const submitBtn = document.getElementById('submitRequestButton');

  if (!modalEl || !labelEl || !submitBtn) {
    throw new Error('Modal elements not found. Check your template IDs.');
  }

  const modal = new bootstrap.Modal(modalEl);

  // Reset UI
  errorBox?.classList.add('d-none');
  if (errorBox) errorBox.textContent = '';
  labelEl.textContent = title;
  document.getElementById('dynamicInputs')?.replaceChildren();

  if (hours && hours.length) {
    const [labels, values] = formatHourRange(hours);
    populateSelect('requestHours', labels, values);
  }

  let resolved = false;

  const result = await new Promise(resolve => {
    const finalize = (payload) => {
      if (resolved) return;
      resolved = true;
      resolve(payload);
    };

    const onHidden = () => finalize({ submitted: false, selectedHour: null });
    modalEl.addEventListener('hidden.bs.modal', onHidden, { once: true });

    const clickHandler = withBusyButton(async () => {
      const val = document.getElementById('requestHours')?.value ?? null;
      finalize({ submitted: true, selectedHour: val });
    });

    submitBtn.addEventListener('click', clickHandler, { once: true });
    modal.show();
  });

  return result;
}

/**
 * Show #modal_gen to collect { shiftCode, startTime, endTime } and resolve once.
 * Returns: { submitted:boolean, shiftCode:string|null, startTime:string|null, endTime:string|null }
 * Stays OPEN on submit; caller decides when to close (on success).
 * Cancelling/closing resolves with submitted=false.
 */
export async function runShiftHourModal() {
  // Build 07:00..23:00 then 00:00..07:00 (wrap)
  const HOUR_RANGE =
    Array.from({ length: 17 }, (_, i) => i + 7)   // 7..23
      .concat(Array.from({ length: 8 }, (_, i) => i)); // 0..7
  const hourRange = HOUR_RANGE.map(x => `${String(x).padStart(2, '0')}:00`);
  const hourRangeNoEnd = hourRange.slice(0, -1);

  // Modal elements
  const modalRoot = document.getElementById('modal_gen');
  if (!modalRoot) throw new Error('#modal_gen not found');
  const modalBody = modalRoot.querySelector('.modal-body');
  if (!modalBody) throw new Error('#modal_gen .modal-body not found');

  const submitBtn = document.getElementById('submitShiftButton');
  if (!submitBtn) throw new Error('#submitShiftButton not found');

  // Clear and render fields
  modalBody.innerHTML = '';
  const row = document.createElement('div');
  row.className = 'row align-items-center g-2';

  const dropdown1 = createDropdown('shiftCode', ['-', 'dn', 'd', 'n', 'm', 't', 'c', 'v']);
  const dropdown2 = createDropdown('startTime', hourRangeNoEnd);
  const dropdown3 = createDropdown('endTime',   hourRange);

  const wrap = (el) => {
    const d = document.createElement('div');
    d.className = 'col-4';
    d.appendChild(el);
    return d;
  };
  row.appendChild(wrap(dropdown1));
  row.appendChild(wrap(dropdown2));
  row.appendChild(wrap(dropdown3));
  modalBody.appendChild(row);

  dropdown1.addEventListener('change', () => handleDropdownChange(dropdown1, dropdown2, dropdown3));
  dropdown2.addEventListener('change', () => handleDropdownChange(dropdown1, dropdown2, dropdown3));
  handleDropdownChange(dropdown1, dropdown2, dropdown3);

  const bsModal = new bootstrap.Modal(modalRoot);

  const result = await new Promise((resolve) => {
    let settled = false;
    const finalize = (payload) => {
      if (settled) return;
      settled = true;
      resolve(payload);
    };

    const onHidden = () => finalize({
      submitted: false, shiftCode: null, startTime: null, endTime: null
    });
    modalRoot.addEventListener('hidden.bs.modal', onHidden, { once: true });

    const onSubmit = withBusyButton(async () => {
      const shiftCode = document.getElementById('shiftCode')?.value ?? null;
      const startTime = document.getElementById('startTime')?.value ?? null;
      const endTime   = document.getElementById('endTime')?.value   ?? null;
      finalize({ submitted: true, shiftCode, startTime, endTime });
    });

    submitBtn.addEventListener('click', onSubmit, { once: true });
    bsModal.show();
  });

  return result;
}

/* ===========================
 * Orchestration
 * =========================== */

/**
 * Handle a high-level action by gathering inputs via modals and submitting.
 * - Modals remain OPEN on submit; we only CLOSE them after a successful request.
 * - On failure, we display the error in the currently visible modal and allow retry.
 *
 * Expects external globals/utilities:
 *   - ACTIONS: { [action]: { title, needsHour, hoursCRM(ctx), endpointAction } }
 *   - fetchHours(params), fetchNamesList(), submitUserRequest(payload)
 *   - showToast(type='success'|'danger'...), bootstrap
 */
export async function handleAction(action, ctx) {
  const cfg = ACTIONS[action];
  if (!cfg) return console.error('Unknown action:', action);

  try {
    const title    = cfg.title;
    const needsHr  = cfg.needsHour;

    let submitted = false;
    let center = ctx.center || null;
    let day = ctx.day || null;
    let selectedHour = null;
    let shiftCode = null;
    let startTime = null;
    let endTime   = null;
    let selectUserCRM = null;

    if (needsHr) {
      const hours = await fetchHours({ crm: cfg.hoursCRM(ctx), ...ctx });

      // Retry loop: keep modal open, re-resolve on each submit. Exit on cancel or success.
      // eslint-disable-next-line no-constant-condition
      while (true) {
        ({ submitted, selectedHour } = await runRequestModal({ title, hours }));
        if (!submitted) return; // user cancelled/closed

        try {
          const cardCRM = ctx.cardCrm;
          await submitUserRequest({
            action: cfg.endpointAction,
            cardCRM,
            selectedHour,
            center,
            day,
            options: { timeout: 15000 },
          });

          showToast('Pedido enviado com sucesso!', 'success');
          // Close the modal ONLY now
          bootstrap.Modal.getOrCreateInstance(document.getElementById('modalRequests'))?.hide();
          break;
        } catch (e) {
          showModalError(e?.message || 'Um erro ocorreu ao enviar o pedido.');
          // keep looping; modal stays open
        }
      }
    } else {
      const nameData = await fetchNamesList();
      const names = nameData.map(item => item.name);
      const crms  = nameData.map(item => item.crm);

      // Step 1: choose user (names modal). Exit if canceled.
      ({ submitted, selectedValue: selectUserCRM } = await runNamesModal({ title, names, values: crms }));
      if (!submitted) return;

      // Step 2: choose shift/hours with retry on submission failure
      // eslint-disable-next-line no-constant-condition
      while (true) {
        ({ submitted, shiftCode, startTime, endTime } = await runShiftHourModal());
        if (!submitted) return; // user cancelled

        try {
          const cardCRM = ctx.cardCrm || selectUserCRM;
          await submitUserRequest({
            action: cfg.endpointAction,
            cardCRM,
            shiftCode,
            center,
            day,
            startTime,
            endTime,
            options: { timeout: 15000 },
          });

          showToast('Pedido enviado com sucesso!', 'success');
          // Close both modals on success (hours first, then names)
          const modalHours = document.getElementById('modal_gen');
          const modalNames = document.getElementById('modalRequests');
          bootstrap.Modal.getOrCreateInstance(modalHours)?.hide();
          bootstrap.Modal.getOrCreateInstance(modalNames)?.hide();
          break;
        } catch (e) {
          showModalError(e?.message || 'Um erro ocorreu ao enviar o pedido.');
          // continue loop for retry
        }
      }
    }
  } catch (e) {
    showModalError(e?.message || 'Um erro ocorreu ao enviar o pedido.');
  }
}

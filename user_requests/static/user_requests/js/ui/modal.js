// ui/modal.js
// UI-only concerns: modal, select creation, and submit flow

import { formatHourRange } from '../data/hours.js';

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

/**
 * Run the request modal, rendering a title and (optionally) an hours <select>.
 * Resolves with { submitted: boolean, selectedHour: string|null }.
 * If user closes the modal without pressing submit, submitted=false.
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

  // Optional hours select
  if (hours && hours.length) {
    const [labels, values] = formatHourRange(hours);
    populateSelect('requestHours', labels, values);
  }

  // Promise that resolves on submit or on close
  let resolved = false;

  const result = await new Promise(resolve => {
    const finalize = (payload) => {
      if (resolved) return;
      resolved = true;
      resolve(payload);
    };

    const clickHandler = withBusyButton(async () => {
      const val = document.getElementById('requestHours')?.value ?? null;
      finalize({ submitted: true, selectedHour: val });
    });

    // Attach once for this run
    submitBtn.addEventListener('click', clickHandler, { once: true });

    // If user closes via 'x' or Cancel (data-bs-dismiss), treat as not submitted
    const onHidden = () => finalize({ submitted: false, selectedHour: null });
    modalEl.addEventListener('hidden.bs.modal', onHidden, { once: true });

    modal.show();
  });

  try {} catch {}

  return result;
}

/** Button busy state wrapper (local to UI) */
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

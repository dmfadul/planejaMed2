import { formatHourRange } from '../data/hours.js';

// TODO: change modals' buttons texts
function waitHidden(modalEl) {
  return new Promise(resolve => {
    modalEl.addEventListener('hidden.bs.modal', () => resolve(), { once: true });
  });
}

function handleDropdownChange(dropdown1, dropdown2, dropdown3) {
    if (dropdown1.value !== '-') {
        dropdown2.disabled = true;
        dropdown3.disabled = true;
        dropdown2.style.backgroundColor = "#a0a0a0"; // Gray out the dropdown
        dropdown3.style.backgroundColor = "#a0a0a0"; // Gray out the dropdown
        dropdown2.selectedIndex = -1;
        dropdown3.selectedIndex = -1;
    } else {
        dropdown2.disabled = false;
        dropdown3.disabled = false;
        dropdown2.style.backgroundColor = ""; // Reset background color
        dropdown3.style.backgroundColor = ""; // Reset background color
        dropdown3.selectedIndex = 1;

        const selectedIndex = dropdown2.selectedIndex;

        Array.from(dropdown3.options).forEach((option, index) => {
            if (index <= selectedIndex) {
                option.style.display = "none"; // Hide options in dropdown3 that are less than or equal to selectedIndex
            } else {
                option.style.display = "block"; // Show options in dropdown3 that are greater than selectedIndex
            }
        });
        dropdown3.selectedIndex = selectedIndex + 1; // Select the next option in dropdown3
    }
}


function createDropdown(id, options, values={}) {
    let dropdown = document.createElement('select');
    dropdown.classList.add('form-select');
    dropdown.id = id;
    dropdown.name = id;

    options.forEach(option => {
        let opt = document.createElement('option');
        if(Object.keys(values).length > 0){
            opt.value = values[option];
        } else{
            opt.value = option;
        }
        opt.textContent = option;
        dropdown.appendChild(opt);
    });

    return dropdown;
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

  // Populate options
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

    // define so we can remove it on successful submit
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
    
      // prevent cancel path from firing during normal submit
      modalEl.removeEventListener('hidden.bs.modal', onHidden);
    
      // Hide and wait until fully closed before resolving
      const m = bootstrap.Modal.getOrCreateInstance(modalEl);
      m.hide();
      await waitHidden(modalEl);
    
      finalize({ submitted, selectedLabel, selectedValue, selectedIndex: idx });
    };

    // const clickHandlerCore = async () => {
    //   const el = document.getElementById('requestSelect');
    //   const idx = el?.selectedIndex ?? -1;
    //   const submitted = idx >= 0;
    //   const selectedLabel = submitted ? names[idx] : null;
    //   const selectedValue = submitted ? values[idx] : null;

    //   // // Start hiding the modal first
    //   // modal.hide();

    //   // // Wait until it's *fully* hidden before resolving
    //   // await waitHidden(modalEl);

    //   finalize({ submitted, selectedLabel, selectedValue, selectedIndex: idx });
    // };

    // Support existing withBusyButton helper if present; otherwise use plain handler
    const clickHandler = (typeof withBusyButton === 'function')
      ? withBusyButton(clickHandlerCore)
      : clickHandlerCore;

    submitBtn.addEventListener('click', clickHandler, { once: true });

    // const onHidden = () => finalize({
    //   submitted: false,
    //   selectedLabel: null,
    //   selectedValue: null,
    //   selectedIndex: -1
    // });
    // modalEl.addEventListener('hidden.bs.modal', onHidden, { once: true });

    modal.show();
  });

  try {} catch {}

  return result;
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

    // const clickHandler = withBusyButton(async () => {
    //   const val = document.getElementById('requestHours')?.value ?? null;
    //   finalize({ submitted: true, selectedHour: val });
    // });

    const onHidden = () => finalize({ submitted: false, selectedHour: null });
    modalEl.addEventListener('hidden.bs.modal', onHidden, { once: true });

    const clickHandler = withBusyButton(async () => {
      const val = document.getElementById('requestHours')?.value ?? null;
      // prevent cancel path during normal submit
      modalEl.removeEventListener('hidden.bs.modal', onHidden);
      const m = bootstrap.Modal.getOrCreateInstance(modalEl);
      m.hide();
      await waitHidden(modalEl);
      finalize({ submitted: true, selectedHour: val });
    });

    // Attach once for this run
    submitBtn.addEventListener('click', clickHandler, { once: true });

    // // If user closes via 'x' or Cancel (data-bs-dismiss), treat as not submitted
    // const onHidden = () => finalize({ submitted: false, selectedHour: null });
    // modalEl.addEventListener('hidden.bs.modal', onHidden, { once: true });

    modal.show();
  });

  try {} catch {}

  return result;
}

// Single-use: show 3 dropdowns (shift + start + end) and resolve once.
// Returns: { submitted: true, shiftCode, startTime, endTime } or { submitted:false }
// Returns a Promise<{ submitted: boolean, shiftCode: string|null, startTime: string|null, endTime: string|null }>
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

  // Find a submit button scoped to this modal.
  // Prefer an element with id="submitShiftButton" inside #modal_gen.
  const submitBtn = document.getElementById('submitShiftButton');
    
  // Clear and render fields
  modalBody.innerHTML = '';
  const row = document.createElement('div');
  row.className = 'row align-items-center g-2';

  const dropdown1 = createDropdown('shiftCode', ['-','dn','d','n','m','t','c','v']);
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

  // Wire up constraints (disable start/end if shiftCode !== '-'; enforce end > start)
  dropdown1.addEventListener('change', () => handleDropdownChange(dropdown1, dropdown2, dropdown3));
  dropdown2.addEventListener('change', () => handleDropdownChange(dropdown1, dropdown2, dropdown3));
  // Initialize state after insertion
  handleDropdownChange(dropdown1, dropdown2, dropdown3);

  // Show & resolve like runRequestModal
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
      // finalize({ submitted: true, shiftCode, startTime, endTime });
      // bsModal.hide();
      // avoid cancel path, then hide and await
      modalRoot.removeEventListener('hidden.bs.modal', onHidden);
      bsModal.hide();
      await waitHidden(modalRoot);
      finalize({ submitted: true, shiftCode, startTime, endTime });
    });

    submitBtn.addEventListener('click', onSubmit, { once: true });

    // const onHidden = () => finalize({
    //   submitted: false, shiftCode: null, startTime: null, endTime: null
    // });
    // modalRoot.addEventListener('hidden.bs.modal', onHidden, { once: true });

    bsModal.show();
  });
  
  return result;
}


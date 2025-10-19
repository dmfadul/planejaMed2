import { formatHourRange } from '../data/hours.js';

/* ===========================
 * Utilities
 * =========================== */

function withBusyButton(fn) {
  return async (ev) => {
    const btn = ev?.currentTarget ?? ev?.target;
    const el = btn instanceof HTMLElement ? btn : null;
    const old = el ? { t: el.textContent, d: el.disabled } : null;
    if (el) { el.disabled = true; el.textContent = 'Sending...'; }
    try { return await fn(); }
    finally { if (el) { el.disabled = old.d; el.textContent = old.t || 'Submit'; } }
  };
}

function showWizardError(msg) {
  const box = document.getElementById('wizardError');
  if (!box) return console.error(msg);
  box.textContent = msg;
  box.classList.remove('d-none');
}
function clearWizardError() {
  const box = document.getElementById('wizardError');
  if (box) { box.textContent = ''; box.classList.add('d-none'); }
}

function mkSelect({ id, className = 'form-select', options, values }) {
  const sel = document.createElement('select');
  sel.id = id; sel.name = id; sel.className = className;
  options.forEach((label, i) => {
    const opt = document.createElement('option');
    opt.textContent = label;
    opt.value = values ? values[i] : label;
    sel.appendChild(opt);
  });
  return sel;
}

function enforceShiftRules(drop1, drop2, drop3) {
  if (drop1.value !== '-') {
    drop2.disabled = true; drop3.disabled = true;
    drop2.style.background = '#a0a0a0'; drop3.style.background = '#a0a0a0';
    drop2.selectedIndex = -1; drop3.selectedIndex = -1;
  } else {
    drop2.disabled = false; drop3.disabled = false;
    drop2.style.background = ''; drop3.style.background = '';
    const startIdx = drop2.selectedIndex;
    Array.from(drop3.options).forEach((opt, idx) => {
      opt.style.display = idx <= startIdx ? 'none' : 'block';
    });
    drop3.selectedIndex = Math.max(0, startIdx + 1);
  }
}

function buildHourLists() {
  const H = Array.from({ length: 17 }, (_, i) => i + 7).concat(Array.from({ length: 8 }, (_, i) => i));
  const hourRange = H.map(x => `${String(x).padStart(2, '0')}:00`);
  return { hourRange, hourRangeNoEnd: hourRange.slice(0, -1) };
}

/* ===========================
 * Wizard DOM
 * =========================== */

function getWizardDom() {
  const root     = document.getElementById('modalWizard');
  const titleEl  = document.getElementById('modalWizardLabel');
  const body     = root?.querySelector('.modal-body');
  const backBtn  = document.getElementById('wizardBackBtn');
  const submitBt = document.getElementById('wizardSubmitBtn');
  if (!root || !titleEl || !body || !backBtn || !submitBt) {
    throw new Error('Wizard modal DOM not found. Check #modalWizard structure.');
  }
  return { root, titleEl, body, backBtn, submitBt };
}

/* ===========================
 * Steps
 * =========================== */

function makeStepHours({ hours }) {
  const state = { selectedHour: null };
  return {
    name: 'hours',
    render(container) {
      const lbl = document.createElement('label');
      lbl.className = 'form-label fw-semibold';
      lbl.textContent = 'Selecione o horário';
      container.appendChild(lbl);

      const [labels, values] = formatHourRange(hours || []);
      const sel = mkSelect({ id: 'wizardHour', options: labels, values });
      sel.addEventListener('change', () => state.selectedHour = sel.value);
      container.appendChild(sel);

      if (sel.options.length) { sel.selectedIndex = 0; state.selectedHour = sel.value; }
    },
    collect() { return { selectedHour: state.selectedHour }; },
    validate(data) { return data.selectedHour ? null : 'Selecione um horário.'; },
    footer({ backBtn, submitBtn }) { backBtn.style.display = 'none'; submitBtn.textContent = 'Enviar'; }
  };
}

function makeStepNames({ nameData }) {
  const state = { selectedIdx: -1, selectedLabel: null, selectedValue: null };
  const names = nameData.map(x => x.name);
  const crms  = nameData.map(x => x.crm);

  return {
    name: 'names',
    render(container) {
      const lbl = document.createElement('label');
      lbl.className = 'form-label fw-semibold';
      lbl.textContent = 'Selecione o usuário';
      container.appendChild(lbl);

      const sel = mkSelect({ id: 'wizardName', options: names, values: crms });
      sel.addEventListener('change', () => {
        state.selectedIdx   = sel.selectedIndex;
        state.selectedLabel = names[sel.selectedIndex] ?? null;
        state.selectedValue = crms[sel.selectedIndex] ?? null;
      });
      container.appendChild(sel);

      if (sel.options.length) { sel.selectedIndex = 0; sel.dispatchEvent(new Event('change')); }
    },
    collect() { return { selectedIndex: state.selectedIdx, selectedLabel: state.selectedLabel, selectedValue: state.selectedValue }; },
    validate(data) { return data.selectedIndex >= 0 ? null : 'Selecione um usuário.'; },
    footer({ backBtn, submitBtn }) { backBtn.style.display = 'none'; submitBtn.textContent = 'Continuar'; }
  };
}

function makeStepShift() {
  const state = { shiftCode: '-', startTime: null, endTime: null };
  return {
    name: 'shift',
    render(container) {
      const row = document.createElement('div');
      row.className = 'row align-items-center g-2';
      container.appendChild(row);

      const col = () => { const d = document.createElement('div'); d.className = 'col-4'; return d; };

      const codeSel = mkSelect({ id: 'wizardShift', options: ['-','dn','d','n','m','t','c','v'] });
      const { hourRange, hourRangeNoEnd } = buildHourLists();
      const startSel = mkSelect({ id: 'wizardStart', options: hourRangeNoEnd });
      const endSel   = mkSelect({ id: 'wizardEnd',   options: hourRange });

      codeSel.addEventListener('change', () => { state.shiftCode = codeSel.value; enforceShiftRules(codeSel, startSel, endSel); });
      startSel.addEventListener('change', () => { state.startTime = startSel.value; enforceShiftRules(codeSel, startSel, endSel); });
      endSel  .addEventListener('change', () => { state.endTime   = endSel.value; });

      const c1 = col(); c1.appendChild(codeSel);
      const c2 = col(); c2.appendChild(startSel);
      const c3 = col(); c3.appendChild(endSel);
      row.appendChild(c1); row.appendChild(c2); row.appendChild(c3);

      // init
      state.shiftCode = codeSel.value = '-';
      startSel.selectedIndex = 0;
      state.startTime = startSel.value;
      enforceShiftRules(codeSel, startSel, endSel);
      state.endTime = endSel.value;
    },
    collect() { return { ...state }; },
    validate(data) {
      if (data.shiftCode === '-') {
        if (!data.startTime || !data.endTime) return 'Selecione início e fim.';
      }
      return null;
    },
    footer({ backBtn, submitBtn }) { backBtn.style.display = ''; submitBtn.textContent = 'Enviar'; }
  };
}

/** Centers step — accepts strings OR objects ({ name, abbr|id|slug }) */
function makeStepCenters({ centers }) {
  const labels = centers.map(c => typeof c === 'string' ? c : (c.name ?? c.abbr ?? String(c)));
  const values = centers.map(c => {
    if (typeof c === 'string') return c;
    return c.abbr ?? c.id ?? c.slug ?? c.name; // pick your preferred identifier
  });

  const state = { idx: -1, label: null, value: null };

  return {
    name: 'centers',
    render(container) {
      const lbl = document.createElement('label');
      lbl.className = 'form-label fw-semibold';
      lbl.textContent = 'Selecione o centro';
      container.appendChild(lbl);

      const sel = mkSelect({ id: 'wizardCenter', options: labels, values });
      sel.addEventListener('change', () => {
        state.idx   = sel.selectedIndex;
        state.label = labels[sel.selectedIndex] ?? null;
        state.value = values[sel.selectedIndex] ?? null;
      });
      container.appendChild(sel);

      if (sel.options.length) { sel.selectedIndex = 0; sel.dispatchEvent(new Event('change')); }
    },
    collect() { return { selectedCenterIndex: state.idx, selectedCenterLabel: state.label, selectedCenter: state.value }; },
    validate(data) { return data.selectedCenter ? null : 'Selecione um centro.'; },
    footer({ backBtn, submitBtn }) { backBtn.style.display = 'none'; submitBtn.textContent = 'Continuar'; }
  };
}


/* ===========================
 * Day step (1–31)
 * =========================== */
function makeStepDays() {
  const state = { selectedDay: null };

  return {
    name: 'days',
    render(container) {
      const lbl = document.createElement('label');
      lbl.className = 'form-label fw-semibold';
      lbl.textContent = 'Selecione o dia';
      container.appendChild(lbl);

      const days = Array.from({ length: 31 }, (_, i) => (i + 1).toString());
      const sel = mkSelect({ id: 'wizardDay', options: days, values: days });

      sel.addEventListener('change', () => {
        state.selectedDay = sel.value;
      });
      container.appendChild(sel);

      // Default to current day or first day
      const today = new Date().getDate();
      sel.selectedIndex = Math.min(today - 1, days.length - 1);
      state.selectedDay = sel.value;
    },
    collect() {
      return { selectedDay: state.selectedDay };
    },
    validate(data) {
      return data.selectedDay ? null : 'Selecione um dia.';
    },
    footer({ backBtn, submitBtn }) {
      backBtn.style.display = 'none';
      submitBtn.textContent = 'Continuar';
    },
  };
}

/* ===========================
 * Wizard Runner (single instance; retries inside)
 * =========================== */

function renderStep(step, dom, ctx) {
  dom.body.innerHTML = '';
  clearWizardError();
  const hdr = document.createElement('div');
  hdr.className = 'mb-2';
  hdr.innerHTML = `<div class="small text-muted">${ctx.stepIndex + 1} / ${ctx.steps.length}</div>`;
  dom.body.appendChild(hdr);
  const content = document.createElement('div');
  dom.body.appendChild(content);
  step.render(content);
}

async function runWizardOnce({ title, steps, onSubmit }) {
  // onSubmit(data) should throw or return string on error; resolve/void on success
  const dom = getWizardDom();
  dom.titleEl.textContent = title;

  // Safety: remove stray backdrops from any previous broken run
  document.querySelectorAll('.modal-backdrop').forEach(b => b.remove());
  dom.root.classList.remove('modal-static');

  const modal = bootstrap.Modal.getOrCreateInstance(dom.root);
  let stepIndex = 0;
  const ctx = { steps, stepIndex };

  let submitHandler = null;
  let backHandler = null;
  let hiddenHandler = null;

  function cleanup() {
    if (submitHandler) dom.submitBt.removeEventListener('click', submitHandler);
    if (backHandler)   dom.backBtn.removeEventListener('click', backHandler);
    if (hiddenHandler) dom.root.removeEventListener('hidden.bs.modal', hiddenHandler);
    document.querySelectorAll('.modal-backdrop').forEach(b => b.remove());
  }

  function attachHandlers() {
    if (submitHandler) dom.submitBt.removeEventListener('click', submitHandler);
    if (backHandler)   dom.backBtn.removeEventListener('click', backHandler);

    steps[stepIndex].footer?.({ backBtn: dom.backBtn, submitBtn: dom.submitBt });

    submitHandler = withBusyButton(async () => {
      clearWizardError();
      const data = steps[stepIndex].collect?.() ?? {};
      const err  = steps[stepIndex].validate?.(data);
      if (err) { showWizardError(err); return; }

      if (stepIndex < steps.length - 1) {
        stepIndex += 1;
        ctx.stepIndex = stepIndex;
        renderStep(steps[stepIndex], dom, ctx);
        attachHandlers();
        return;
      }

      // Final submit
      const payload = {};
      for (const s of steps) Object.assign(payload, s.collect?.() ?? {});
      try {
        const res = await onSubmit(payload);
        if (typeof res === 'string' && res) { showWizardError(res); return; }
        modal.hide();
      } catch (e) {
        showWizardError(e?.message || 'Um erro ocorreu ao enviar o pedido.');
      }
    });

    backHandler = () => {
      if (stepIndex === 0) return;
      stepIndex -= 1;
      ctx.stepIndex = stepIndex;
      renderStep(steps[stepIndex], dom, ctx);
      attachHandlers();
    };

    dom.submitBt.addEventListener('click', submitHandler);
    dom.backBtn.addEventListener('click', backHandler);
  }

  const result = await new Promise((resolve) => {
    hiddenHandler = () => resolve(null); // cancel/close
    dom.root.addEventListener('hidden.bs.modal', hiddenHandler, { once: true });

    renderStep(steps[0], dom, ctx);
    attachHandlers();
    modal.show();
  });

  cleanup();
  modal.dispose();
  return result; // null if user closed; otherwise we closed on success
}

/* ===========================
 * Orchestration (compose steps per action)
 * =========================== */

export async function handleAction(action, ctx) {
  console.log("Handling action:", action, ctx);
  const cfg = ACTIONS[action];
  if (!cfg) return console.error('Unknown action:', action);

  const title   = cfg.title;
  const center  = ctx.center ?? null;   // default center from context (if any)
  const day     = ctx.day ?? null;
  const shiftId = ctx.shiftId ?? null;

  try {
    let steps = [];
    let onSubmitFunction = null;

    if (cfg.needsHour && !cfg.needsNames && !cfg.needsCenter) {
      // Hours-only flow
      const hours = await fetchHours({ crm: cfg.hoursCRM?.(ctx), ...ctx });
      steps = [ makeStepHours({ hours }) ];

      onSubmitFunction = async ({ selectedHour }) => {
        await submitUserRequest({
          action: cfg.endpointAction,
          cardCRM: ctx.cardCrm || null,
          selectedHour,
          center, day, shiftId,
          options: { timeout: 15000 },
        });
      };
    } else if (cfg.needsHour && cfg.needsNames) {
      // Hours + Names flow
      const hours   = await fetchHours({ crm: cfg.hoursCRM?.(ctx), ...ctx });
      const nameData = await fetchNamesList();
      steps = [ makeStepHours({ hours }), makeStepNames({ nameData }) ];

      onSubmitFunction = async ({ selectedValue, selectedHour }) => {
        const cardCRM = selectedValue || null;
        await submitUserRequest({
          action: cfg.endpointAction,
          cardCRM,
          selectedHour,
          center, day, shiftId,
          options: { timeout: 15000 },
        });
      };
    } else if (cfg.needsNames) {
      // Names + Shift flow
      const nameData = await fetchNamesList();
      steps = [ makeStepNames({ nameData }), makeStepShift() ];

      onSubmitFunction = async ({ selectedValue, shiftCode, startTime, endTime }) => {
        const cardCRM = ctx.cardCrm || selectedValue;
        await submitUserRequest({
          action: cfg.endpointAction,
          cardCRM,
          shiftCode,
          startTime,
          endTime,
          center, day,
          options: { timeout: 15000 },
        });
      };

    } else if (cfg.needsCenter && cfg.needsHour) {
      // Center + Hour flow (order can be swapped if you prefer)
      const centers = await fetchCenterList(); // strings or objects ok
      const hours   = await fetchHours({ crm: cfg.hoursCRM?.(ctx), ...ctx });
      steps = [ makeStepCenters({ centers }), makeStepHours({ hours }) ];

      onSubmitFunction = async ({ selectedCenter, selectedHour }) => {
        await submitUserRequest({
          action: cfg.endpointAction,
          cardCRM: ctx.cardCrm || null,
          center: selectedCenter,        // <-- chosen center
          selectedHour,
          day, shiftId,
          options: { timeout: 15000 },
        });
      };

    } else if (action === 'SCHinclude') {
      const centers = await fetchCenterList();
      steps = [ makeStepCenters({ centers }), makeStepDays(), makeStepShift() ];

      onSubmitFunction = async ({ selectedCenter, selectedDay, shiftCode, startTime, endTime }) => {
        const cardCRM = ctx.cardCrm || null;
        await submitUserRequest({
          action: cfg.endpointAction,
          cardCRM,
          center: selectedCenter,        // <-- chosen center
          shiftCode,
          startTime,
          endTime,
          day: selectedDay,            // <-- chosen day
          options: { timeout: 15000 },
        });
      };

    } else {
      throw new Error('No step configuration matched for this action.');
    }

    const cancelled = await runWizardOnce({ title, steps, onSubmit: onSubmitFunction });
    if (cancelled === null) return; // user closed
    if (typeof showToast === 'function') showToast('Pedido enviado com sucesso!', 'success');

  } catch (e) {
    showWizardError(e?.message || 'Um erro ocorreu ao enviar o pedido.');
  }
}

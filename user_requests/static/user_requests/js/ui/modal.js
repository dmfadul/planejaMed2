import { formatHourRange } from '../data/hours.js';

/* =========================================================
 * Utilities
 * ========================================================= */

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

/* Simple factory: <select> */
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

/* shift dropdown state rules */
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

/* Build wrapped hour list 07:00..23:00 then 00:00..07:00 */
function buildHourLists() {
  const H = Array.from({ length: 17 }, (_, i) => i + 7).concat(Array.from({ length: 8 }, (_, i) => i));
  const hourRange = H.map(x => `${String(x).padStart(2, '0')}:00`);
  return { hourRange, hourRangeNoEnd: hourRange.slice(0, -1) };
}

/* =========================================================
 * Wizard (single modal, multi-step)
 * ========================================================= */

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

/**
 * Renders a step into the wizard body.
 * Step is an object with:
 * - name: string
 * - render(container): void
 * - collect(): any   (returns current step selections)
 * - validate(data): string|null  (error msg or null)
 */
function renderStep(step, dom, ctx) {
  dom.body.innerHTML = '';
  clearWizardError();

  // Optional: small step header or context
  const hdr = document.createElement('div');
  hdr.className = 'mb-2';
  hdr.innerHTML = `<div class="small text-muted">${ctx.stepIndex + 1} / ${ctx.steps.length}</div>`;
  dom.body.appendChild(hdr);

  const content = document.createElement('div');
  dom.body.appendChild(content);

  step.render(content);
}

/* --------------------------
 * Step factories
 * -------------------------- */

function makeStepHours({ title, hours }) {
  const state = { selectedHour: null };

  return {
    name: 'hours',
    render(container) {
      // Title can stay in modal header; we add a label here if desired
      const lbl = document.createElement('label');
      lbl.className = 'form-label fw-semibold';
      lbl.textContent = 'Select hour';
      container.appendChild(lbl);

      const [labels, values] = formatHourRange(hours || []);
      const sel = mkSelect({ id: 'wizardHour', options: labels, values });
      sel.addEventListener('change', () => state.selectedHour = sel.value);
      container.appendChild(sel);

      // initialize
      if (sel.options.length) { sel.selectedIndex = 0; state.selectedHour = sel.value; }
    },
    collect() { return { selectedHour: state.selectedHour }; },
    validate(data) {
      if (!data.selectedHour) return 'Selecione um horário.';
      return null;
    },
    footer({ backBtn, submitBtn }) {
      backBtn.style.display = 'none';
      submitBtn.textContent = 'Enviar';
    }
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

      // init
      if (sel.options.length) { sel.selectedIndex = 0; sel.dispatchEvent(new Event('change')); }
    },
    collect() {
      return {
        selectedIndex: state.selectedIdx,
        selectedLabel: state.selectedLabel,
        selectedValue: state.selectedValue
      };
    },
    validate(data) {
      if (data.selectedIndex < 0) return 'Selecione um usuário.';
      return null;
    },
    footer({ backBtn, submitBtn }) {
      backBtn.style.display = 'none';
      submitBtn.textContent = 'Continuar';
    }
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

      codeSel.addEventListener('change', () => {
        state.shiftCode = codeSel.value;
        enforceShiftRules(codeSel, startSel, endSel);
      });
      startSel.addEventListener('change', () => {
        state.startTime = startSel.value;
        enforceShiftRules(codeSel, startSel, endSel);
      });
      endSel.addEventListener('change',   () => { state.endTime = endSel.value; });

      const c1 = col(); c1.appendChild(codeSel);
      const c2 = col(); c2.appendChild(startSel);
      const c3 = col(); c3.appendChild(endSel);
      row.appendChild(c1); row.appendChild(c2); row.appendChild(c3);

      // init defaults
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
    footer({ backBtn, submitBtn }) {
      backBtn.style.display = '';
      submitBtn.textContent = 'Enviar';
    }
  };
}

/* --------------------------
 * Wizard Runner
 * -------------------------- */

async function runWizard({ title, steps }) {
  const dom = getWizardDom();
  dom.titleEl.textContent = title;

  const modal = new bootstrap.Modal(dom.root);
  let stepIndex = 0;

  // wire buttons once
  let submitHandler = null;
  let backHandler = null;

  const ctx = { steps, stepIndex };

  function attachHandlers() {
    // cleanup previous
    if (submitHandler) dom.submitBt.removeEventListener('click', submitHandler);
    if (backHandler)   dom.backBtn.removeEventListener('click', backHandler);

    // footer config per step
    steps[stepIndex].footer?.({ backBtn: dom.backBtn, submitBtn: dom.submitBt });

    submitHandler = withBusyButton(async () => {
      clearWizardError();
      const data = steps[stepIndex].collect?.() ?? {};
      const err  = steps[stepIndex].validate?.(data);
      if (err) return showWizardError(err);

      if (stepIndex < steps.length - 1) {
        // advance step
        stepIndex += 1;
        ctx.stepIndex = stepIndex;
        renderStep(steps[stepIndex], dom, ctx);
        attachHandlers();
      } else {
        // final step -> return collected payload across steps
        const payload = {};
        for (const s of steps) Object.assign(payload, s.collect?.() ?? {});
        resolvePromise(payload);
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

  let resolver = null;
  const p = new Promise((resolve) => { resolver = resolve; });
  const resolvePromise = (x) => resolver(x);

  // initial render + handlers + show
  renderStep(steps[stepIndex], dom, ctx);
  attachHandlers();
  modal.show();

  // If user manually closes, resolve null
  const onHidden = () => resolver(null);
  dom.root.addEventListener('hidden.bs.modal', onHidden, { once: true });

  const result = await p;
  dom.root.removeEventListener('hidden.bs.modal', onHidden);

  return { result, modal };
}

/* =========================================================
 * Orchestration API (single-modal)
 * =========================================================
 * External deps expected:
 *   - ACTIONS: { [action]: { title, needsHour, hoursCRM(ctx), endpointAction } }
 *   - fetchHours(params), fetchNamesList(), submitUserRequest(payload)
 *   - showToast(msg, type)
 */

export async function handleAction(action, ctx) {
  const cfg = ACTIONS[action];
  if (!cfg) return console.error('Unknown action:', action);

  const title    = cfg.title;
  const needsHr  = cfg.needsHour;
  const center   = ctx.center ?? null;
  const day      = ctx.day ?? null;

  try {
    if (needsHr) {
      const hours = await fetchHours({ crm: cfg.hoursCRM(ctx), ...ctx });
      const stepH = makeStepHours({ title, hours });

      while (true) {
        // Run wizard with a single step (still benefits from unified UI + error area)
        const { result, modal } = await runWizard({ title, steps: [stepH] });
        if (!result) return; // user cancelled/closed

        try {
          await submitUserRequest({
            action: cfg.endpointAction,
            cardCRM: ctx.cardCrm,
            selectedHour: result.selectedHour,
            center, day,
            options: { timeout: 15000 },
          });
          showToast('Pedido enviado com sucesso!', 'success');
          modal.hide();
          break;
        } catch (e) {
          showWizardError(e?.message || 'Um erro ocorreu ao enviar o pedido.');
          // Loop: modal stays open; user can adjust/retry (e.g., change hour)
        }
      }
    } else {
      const nameData = await fetchNamesList();
      const stepN = makeStepNames({ nameData });
      const stepS = makeStepShift();

      while (true) {
        const { result, modal } = await runWizard({ title, steps: [stepN, stepS] });
        if (!result) return; // user cancelled/closed

        try {
          const cardCRM = ctx.cardCrm || result.selectedValue;
          await submitUserRequest({
            action: cfg.endpointAction,
            cardCRM,
            shiftCode: result.shiftCode,
            startTime: result.startTime,
            endTime:   result.endTime,
            center, day,
            options: { timeout: 15000 },
          });
          showToast('Pedido enviado com sucesso!', 'success');
          modal.hide();
          break;
        } catch (e) {
          showWizardError(e?.message || 'Um erro ocorreu ao enviar o pedido.');
          // Loop: user can click Back (to change person) or adjust shift and retry
        }
      }
    }
  } catch (e) {
    showWizardError(e?.message || 'Um erro ocorreu ao enviar o pedido.');
  }
}

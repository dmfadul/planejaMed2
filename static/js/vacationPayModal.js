// static/js/vacation_pay.js

(function () {
  function showError(msg) {
    const el = document.getElementById('vacPayError');
    if (!el) return;
    el.textContent = msg;
    el.classList.remove('d-none');
  }

  function hideError() {
    const el = document.getElementById('vacPayError');
    if (!el) return;
    el.textContent = '';
    el.classList.add('d-none');
  }

  function showResult(objOrString) {
    const wrap = document.getElementById('vacPayResult');
    const pre = document.getElementById('vacPayResultPre');
    if (!wrap || !pre) return;

    const text =
      typeof objOrString === 'string'
        ? objOrString
        : JSON.stringify(objOrString, null, 2);

    pre.textContent = text;
    wrap.classList.remove('d-none');
  }

  function hideResult() {
    const wrap = document.getElementById('vacPayResult');
    const pre = document.getElementById('vacPayResultPre');
    if (!wrap || !pre) return;

    pre.textContent = '';
    wrap.classList.add('d-none');
  }

  function resetForm() {
    const form = document.getElementById('vacPayForm');
    if (form) form.reset();
    hideError();
    hideResult();
  }

  function openVacationPayModal() {
    resetForm();
    new bootstrap.Modal('#modalVacationPay').show();
  }

  function buildErrorMessage(data) {
    if (!data) return 'Falha ao calcular. Tente novamente.';
    if (typeof data === 'string') return data;
    if (data.detail) return data.detail;

    if (typeof data === 'object') {
      const lines = [];
      for (const [field, errors] of Object.entries(data)) {
        const label = field === 'non_field_errors' ? '' : `${field}: `;
        if (Array.isArray(errors)) lines.push(label + errors.join(', '));
        else lines.push(label + String(errors));
      }
      if (lines.length) return lines.join('\n');
    }

    return 'Falha ao calcular. Tente novamente.';
  }

  function parseIntStrict(value) {
    const n = Number.parseInt(String(value), 10);
    return Number.isFinite(n) ? n : NaN;
  }

  async function submitVacationPay(btn) {
    hideError();
    hideResult();

    const monthRaw = document.getElementById('vacPayMonth')?.value || '';
    const yearRaw = document.getElementById('vacPayYear')?.value || '';

    const month = parseIntStrict(monthRaw);
    const year = parseIntStrict(yearRaw);

    if (!monthRaw || !yearRaw) return showError('Preencha mês e ano.');
    if (!Number.isInteger(month) || month < 1 || month > 12) return showError('Selecione um mês válido.');
    if (!Number.isInteger(year) || year < 1900 || year > 3000) return showError('Informe um ano válido.');

    btn.disabled = true;
    const old = btn.textContent;
    btn.textContent = 'Calculando…';

    try {
      // Read-only calculation endpoint (GET)
      // Example: GET /api/vacations/pay/?month=2&year=2026
      const url = `/api/vacations/pay/?month=${encodeURIComponent(month)}&year=${encodeURIComponent(year)}`;

      const res = await fetch(url, {
        method: 'GET',
        headers: { 'Accept': 'application/json' },
      });

      let data = null;
      try { data = await res.json(); } catch (_) {}

      if (res.ok) {
        showResult(data ?? 'Cálculo concluído.');
        return;
      }

      showError(buildErrorMessage(data));

    } catch (e) {
      showError('Erro de rede. Tente novamente.');
    } finally {
      btn.disabled = false;
      btn.textContent = old;
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    const openLink = document.getElementById('calculatePay');
    if (openLink) {
      openLink.addEventListener('click', (e) => {
        e.preventDefault();
        openVacationPayModal();
      });
    }

    const submitBtn = document.getElementById('vacPaySubmitBtn');
    if (submitBtn) {
      submitBtn.addEventListener('click', (e) => submitVacationPay(e.currentTarget));
    }

    const modalEl = document.getElementById('modalVacationPay');
    if (modalEl) {
      modalEl.addEventListener('hidden.bs.modal', resetForm);
    }
  });
})();

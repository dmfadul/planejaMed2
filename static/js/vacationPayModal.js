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

  async function submitVacationPay(btn) {
    hideError();
    hideResult();

    const start = document.getElementById('vacPayStartDate')?.value || '';
    const end = document.getElementById('vacPayEndDate')?.value || '';

    if (!start || !end) return showError('Preencha as duas datas.');
    if (end < start) return showError('A data final não pode ser anterior à inicial.');

    btn.disabled = true;
    const old = btn.textContent;
    btn.textContent = 'Calculando…';

    try {
      // Read-only calculation endpoint (GET)
      // Example: GET /api/vacations/pay/?start=2026-02-01&end=2026-02-10
      const url = `/api/vacations/pay/?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`;

      const res = await fetch(url, {
        method: 'GET',
        headers: { 'Accept': 'application/json' },
        // credentials default is "same-origin" in most browsers, but you can force it:
        // credentials: 'same-origin',
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

// static/js/vacation_pay.js

(function () {
  // --- Small helpers ---
  function getCookie(name) {
    const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return v ? v.pop() : '';
  }

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

    let text = '';
    if (typeof objOrString === 'string') {
      text = objOrString;
    } else {
      // pretty JSON for now (easy while backend is evolving)
      text = JSON.stringify(objOrString, null, 2);
    }

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

  // Build a readable message from DRF-like errors
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
      // Pick one approach:
      // A) GET with query params (nice for "calculation" that doesn’t change state)
      // const url = `/api/vacations/pay/?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`;

      // B) POST JSON (nice if you’ll do validations / permissions / complex payload)
      const url = '/api/vacations/pay/';

      const res = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ startDate: start, endDate: end }),
      });

      let data = null;
      try { data = await res.json(); } catch (_) {}

      if (res.ok) {
        // Your backend should return the calculation payload:
        // e.g. { days: 30, gross: 1234.56, net: 1000.00, breakdown: {...} }
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

  // --- Wire up events safely (only if elements exist on the page) ---
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

    // Optional: when modal closes, reset it
    const modalEl = document.getElementById('modalVacationPay');
    if (modalEl) {
      modalEl.addEventListener('hidden.bs.modal', resetForm);
    }
  });
})();

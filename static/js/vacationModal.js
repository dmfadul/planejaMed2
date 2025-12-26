const openBenefits = (mode = 'solicitation') => {
  document.getElementById('benefitsForm').reset();
  hideError();

  document.getElementById('benefitsMode').value = mode;

  new bootstrap.Modal('#modalBenefits').show();
};
document.getElementById('benefitsSolicitar').addEventListener('click', e => {
  e.preventDefault();
  openBenefits(e.currentTarget.dataset.benefitsMode || 'solicitation');
});

const registrar = document.getElementById('benefitsRegistrar');
if (registrar) {
  registrar.addEventListener('click', e => {
  e.preventDefault();
  openBenefits(e.currentTarget.dataset.benefitsMode);
  });
}

function showError(msg){ const el = document.getElementById('benefitsError'); el.textContent = msg; el.classList.remove('d-none'); }
function hideError(){ const el = document.getElementById('benefitsError'); el.textContent = ''; el.classList.add('d-none'); }

// (Optional) CSRF helper for Django
function getCookie(name){
  const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)'); return v ? v.pop() : '';
}

async function submitBenefits(btn){
  console.log("submitBenefits called");
  hideError();
  const mode = document.getElementById('benefitsMode').value; // NEW
  const type  = document.getElementById('benefitType').value;
  const start = document.getElementById('startDate').value;
  const end   = document.getElementById('endDate').value;

  if (!type || !start || !end) return showError('Preencha todos os campos.');
  if (end < start) return showError('A data final não pode ser anterior à inicial.');

  btn.disabled = true;
  const old = btn.textContent;
  btn.textContent = 'Enviando…';

  try {
    const res = await fetch('/api/vacation-requests/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: JSON.stringify({
        mode,
        type,
        startDate: start,
        endDate: end
        // use the field names your serializer expects (e.g. start_date/end_date)
      })
    });

    let data = null;
    try {
      data = await res.json();   // try to parse JSON even on errors
    } catch (_) {
      // response might not be JSON (500, etc.)
    }

    if (res.ok) {
      bootstrap.Modal
        .getInstance(document.getElementById('modalBenefits'))
        .hide();
      alert('Solicitação enviada com sucesso!');
      return;
    }

    // Build a nice message from DRF serializer errors
    let msg = 'Falha ao enviar. Tente novamente.';

    if (data) {
      if (typeof data === 'string') {
        // e.g. a simple string error
        msg = data;
      } else if (data.detail) {
        // DRF sometimes uses "detail"
        msg = data.detail;
      } else if (typeof data === 'object') {
        const lines = [];
        for (const [field, errors] of Object.entries(data)) {
          const label = field === 'non_field_errors' ? '' : `${field}: `;
          if (Array.isArray(errors)) {
            lines.push(label + errors.join(', '));
          } else {
            lines.push(label + String(errors));
          }
        }
        if (lines.length) {
          msg = lines.join('\n');
        }
      }
    }

    showError(msg);

  } catch (e) {
    // network / unexpected error
    showError('Erro de rede. Tente novamente.');
  } finally {
    btn.disabled = false;
    btn.textContent = old;
  }
}


document.getElementById('benefitsSubmitBtn').addEventListener('click', (e)=> submitBenefits(e.currentTarget));
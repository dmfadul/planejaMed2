const openBenefits = () => {
  document.getElementById('benefitsForm').reset();
  hideError();
  new bootstrap.Modal('#modalBenefits').show();
};
document.getElementById('benefitsSolicitar').addEventListener('click', e => { e.preventDefault(); openBenefits(); });

function showError(msg){ const el = document.getElementById('benefitsError'); el.textContent = msg; el.classList.remove('d-none'); }
function hideError(){ const el = document.getElementById('benefitsError'); el.textContent = ''; el.classList.add('d-none'); }

// (Optional) CSRF helper for Django
function getCookie(name){
  const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)'); return v ? v.pop() : '';
}

async function submitBenefits(btn){
  hideError();
  const type = document.getElementById('benefitType').value;
  const start = document.getElementById('startDate').value;
  const end   = document.getElementById('endDate').value;

  if (!type || !start || !end) return showError('Preencha todos os campos.');
  if (end < start) return showError('A data final não pode ser anterior à inicial.');

    // TODO: Have the modal display the serializer validation errors from the backend
  btn.disabled = true; const old = btn.textContent; btn.textContent = 'Enviando…';
  try {
    const res = await fetch('/api/vacation-requests/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
      body: JSON.stringify({ type, startDate: start, endDate: end })
    });
    if (!res.ok) throw new Error('Falha ao enviar. Tente novamente.');
    bootstrap.Modal.getInstance(document.getElementById('modalBenefits')).hide();
    // TODO: replace alert with your toast
    alert('Solicitação enviada com sucesso!');
  } catch (e) {
    showError(e.message);
  } finally {
    btn.disabled = false; btn.textContent = old;
  }
}

document.getElementById('benefitsSubmitBtn').addEventListener('click', (e)=> submitBenefits(e.currentTarget));
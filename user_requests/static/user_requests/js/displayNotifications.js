(function () {
  const LIST = "/api/user_requests/notifications/";
  const RESPOND = (id) => `/api/user_requests/notifications/${id}/respond/`; // POST {action:"accept"|"refuse"}
  const DELETE = (id) => `/api/user_requests/notifications/${id}/`;           // DELETE (archive for user)
  const MARK_READ = (id) => `/api/user_requests/notifications/${id}/read/`;   // PATCH {is_read:true}
  const csrftoken = (document.cookie.match('(^|;)\\s*csrftoken\\s*=\\s*([^;]+)')||[]).pop()||"";
  const listEl = document.getElementById("notifList");

  function card(n) {
    const isUnread = !n.is_read;
    const badge = isUnread ? '<span class="badge bg-primary">New</span>' : '';

    // Generate action buttons depending on notification kind
    const actions = (() => {
      console.log("kind", n.kind);
      switch (n.kind) {
        case "action":
          return `
            <div class="mt-3 d-flex gap-2">
              <button class="btn btn-sm btn-success" data-act="accept" data-id="${n.id}">Accept</button>
              <button class="btn btn-sm btn-outline-danger" data-act="refuse" data-id="${n.id}">Refuse</button>
            </div>`;

        case "cancel":
          return `
            <div class="mt-3 d-flex gap-2">
              <button class="btn btn-sm btn-warning" data-act="cancel" data-id="${n.id}">Cancel</button>
            </div>`;
      
        case "info":
        default:
          return `
            <div class="mt-3">
              <button class="btn btn-sm btn-outline-secondary" data-act="delete" data-id="${n.id}">Delete</button>
            </div>`;
      }
    })();

// Optional link wrapper
const link = n.url ? `<a href="${n.url}" class="stretched-link"></a>` : "";


    return `
      <div class="card ${isUnread ? 'border-primary' : ''} position-relative">
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-start">
            <h5 class="card-title mb-1">${n.title} ${badge}</h5>
            <small class="text-muted" title="${n.created_at}">${new Date(n.created_at).toLocaleString()}</small>
          </div>
          <p class="card-text mb-0">${n.body}</p>
          ${actions}
          ${link}
        </div>
      </div>
    `;
  }

  async function load() {
    const res = await fetch(LIST, { credentials: "same-origin" });
    const data = await res.json();
    if (!Array.isArray(data) || data.length === 0) {
      listEl.innerHTML = `<div class="text-muted">You’re all caught up.</div>`;
      return;
    }
    listEl.innerHTML = data.map(card).join("");
  }

  async function post(url, payload) {
    return fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRFToken": csrftoken },
      credentials: "same-origin",
      body: JSON.stringify(payload || {})
    });
  }
  async function patch(url, payload) {
    return fetch(url, {
      method: "PATCH",
      headers: { "Content-Type": "application/json", "X-CSRFToken": csrftoken },
      credentials: "same-origin",
      body: JSON.stringify(payload || {})
    });
  }
  async function del(url) {
    return fetch(url, {
      method: "DELETE",
      headers: { "X-CSRFToken": csrftoken },
      credentials: "same-origin"
    });
  }

  // Delegate actions
  document.addEventListener("click", async (e) => {
    const btn = e.target.closest("[data-act]");
    if (!btn) return;
    const id = btn.dataset.id;
    const act = btn.dataset.act;
    try {
      if (act === "accept" || act === "refuse" || act === "cancel") {
        await post(RESPOND(id), { action: act });
      } else if (act === "delete") {
        await del(DELETE(id));
      }
      // Optimistically mark read, better to move mark-read to the when the user opens the page
      await post(MARK_READ(id), { is_read: true }); // PATCH would be more correct but POST is easier to handle in DRF
    } finally {
      load();
    }
  });

  load();
})();
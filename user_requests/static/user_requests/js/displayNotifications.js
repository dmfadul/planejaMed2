(function () {
  const LIST = "/api/notifications/";
  const RESPOND = (id) => `/api/notifications/${id}/respond/`; // POST {action:"accept"|"refuse"}
  const DELETE = (id) => `/api/notifications/${id}/`;           // DELETE (archive for user)
  const MARK_READ = (id) => `/api/notifications/${id}/read/`;   // PATCH {is_read:true}
  const csrftoken = (document.cookie.match('(^|;)\\s*csrftoken\\s*=\\s*([^;]+)')||[]).pop()||"";
  const listEl = document.getElementById("notifList");

  function card(n) {
    const isUnread = !n.is_read;
    const badge = isUnread ? '<span class="badge bg-primary">New</span>' : '';

    const actions = (() => {
      switch (n.kind) {
        case "action":
          return `
            <div class="mt-3 d-flex gap-2">
              <button class="btn btn-sm btn-success" data-act="accept" data-id="${n.id}">Accept</button>
              <button class="btn btn-sm btn-outline-danger" data-act="refuse" data-id="${n.id}">Refuse</button>
            </div>`;
        case "mass_action":
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

    const link = n.url ? `<a href="${n.url}" class="stretched-link"></a>` : "";

    return `
      <div class="card ${isUnread ? 'border-primary' : ''} position-relative" data-notif-id="${n.id}">
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
      listEl.innerHTML = `<div class="text-muted">Nenhuma notificação.</div>`;
      return;
    }

    // Render first so "seen" means actually visible to the user
    listEl.innerHTML = data.map(card).join("");

    // Immediately mark unread as read (seen on page)
    const unreadIds = data.filter(n => !n.is_read).map(n => n.id);
    if (unreadIds.length) {
      await markSeen(unreadIds);
      // Optimistically update UI badges/borders without a full reload:
      unreadIds.forEach(id => {
        const el = listEl.querySelector(`[data-notif-id="${CSS.escape(String(id))}"]`);
        if (!el) return;
        el.classList.remove('border-primary');
        const badge = el.querySelector('.badge.bg-primary');
        if (badge) badge.remove();
      });
    }
  }

  async function post(url, payload = {}) {
  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrftoken,
      },
      credentials: "same-origin",
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      let errorMessage = "An unexpected error occurred.";

      try {
        // clone() prevents consuming the original response body
        const errorData = await response.clone().json();
        errorMessage = extractErrorMessage(errorData);
      } catch {
        // Backend did not return valid JSON
        const text = await response.clone().text();

        if (text) {
          errorMessage = text;
        }
      }

      showPageMessage(errorMessage, "error");
    }

    return response;
  } catch (error) {
    // Handles network failures, server unreachable, etc.
    showPageMessage(
      "Could not connect to the server. Please try again.",
      "danger"
    );

    throw error;
  }
}

function extractErrorMessage(errorData) {
  if (!errorData) {
    return "An unexpected error occurred.";
  }

  // Example: { "detail": "Permission denied." }
  if (typeof errorData.detail === "string") {
    return errorData.detail;
  }

  // Example: { "error": "Something went wrong." }
  if (typeof errorData.error === "string") {
    return errorData.error;
  }

  // Example: { "non_field_errors": ["This request already exists."] }
  if (Array.isArray(errorData.non_field_errors)) {
    return errorData.non_field_errors.join(" ");
  }

  // Example:
  // {
  //   "requestee": ["This user is unavailable."],
  //   "shift": ["This field is required."]
  // }
  if (typeof errorData === "object") {
    return Object.entries(errorData)
      .map(([field, messages]) => {
        const formattedField = field
          .replaceAll("_", " ")
          .replace(/^\w/, letter => letter.toUpperCase());

        const message = Array.isArray(messages)
          ? messages.join(" ")
          : String(messages);

        return `${formattedField}: ${message}`;
      })
      .join("\n");
  }

  return String(errorData);
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

  async function markSeen(ids) {
    // If your API supports bulk (e.g., /read_all/), use that here.
    // Otherwise, fan out PATCHes per-id:
    const tasks = ids.map(id => patch(MARK_READ(id), { is_read: true }));
    await Promise.allSettled(tasks);
  }

  // Delegate actions (no mark-read here anymore)
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
    } finally {
      load();
    }
  });

  // If the tab was opened in background, mark when it becomes visible
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible") load();
  });

  load();
})();

(function () {
  console.log("notifications.js loaded");
  
  // API endpoints
  const API_LIST = "/api/notifications/"; // GET list visible to current user
  const API_MARK_SEEN = "/api/notifications/mark-seen/"; // POST body: {ids: [..]}
  const notifDot = document.getElementById("notifDot");
  const notifSummary = document.getElementById("notifSummary");
  const notifMenuLink = document.getElementById("notifMenuLink");

  // Grab Django csrftoken for unsafe methods
  function getCookie(name) {
    const m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return m ? m.pop() : "";
  }
  const csrftoken = getCookie("csrftoken");

  async function fetchNotifications() {
    try {
      const res = await fetch(API_LIST, { credentials: "same-origin" });
      if (!res.ok) throw new Error("Fetch failed");
      const data = await res.json();
      console.log("Fetched notifications:", data);
      // Expected shape: [{id, kind: "action"|"info", title, body, created_at, is_read, url}]
      const unseen = data.filter(n => !n.is_read);
      // Toggle dot
      if (unseen.length > 0) {
        notifDot.classList.remove("d-none");
      } else {
        notifDot.classList.add("d-none");
      }
      // Summary line
      const count = data.length;
      notifSummary.textContent = count === 0
        ? "No notifications."
        : unseen.length > 0
          ? `${unseen.length} new • ${count} total`
          : `${count} notifications`;
      // Save ids to mark-seen on open
      notifMenuLink.dataset.latestIds = JSON.stringify(data.map(n => n.id).slice(0, 10)); // cap to avoid huge payloads
    } catch (e) {
      notifSummary.textContent = "Couldn’t load notifications.";
    }
  }

  // Mark recent notifications as seen when opening the dropdown
  async function markSeen(ids) {
    if (!ids || ids.length === 0) return;
    try {
      await fetch(API_MARK_SEEN, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrftoken },
        credentials: "same-origin",
        body: JSON.stringify({ ids })
      });
      // Immediately hide the dot; we’ll refetch soon anyway
      notifDot.classList.add("d-none");
    } catch (_) {}
  }

  // Event: dropdown shown -> mark recent as seen
  document.addEventListener("shown.bs.dropdown", (ev) => {
    if (ev.target.id === "notifMenuLink") {
      const ids = JSON.parse(notifMenuLink.dataset.latestIds || "[]");
      markSeen(ids);
    }
  });

  // Poll every 60s (tweak as you like)
  fetchNotifications();
  setInterval(fetchNotifications, 60000);
})();


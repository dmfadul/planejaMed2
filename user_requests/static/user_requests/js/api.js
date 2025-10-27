// api.js
// Network helpers: CSRF, error normalization, and the submitUserRequest endpoint

const API_ENDPOINT = '/api/user-requests/';

/** Standard Django CSRF cookie getter */
export function getCookie(name = 'csrftoken') {
  const cookieStr = document.cookie || '';
  const cookies = cookieStr.split(';').map(c => c.trim());
  for (const c of cookies) {
    if (c.startsWith(name + '=')) {
      return decodeURIComponent(c.slice(name.length + 1));
    }
  }
  return '';
}

/** DRF + Django-friendly error humanizer */
export function humanizeErrors(errors) {
  if (!errors) return "Unknown error.";
  if (typeof errors === "string") return errors;
  if (errors.detail) {
    return Array.isArray(errors.detail) ? errors.detail.join("\n") : String(errors.detail);
  }
  const out = [];
  if (errors.non_field_errors) {
    out.push([].concat(errors.non_field_errors).join("\n"));
  }
  for (const [field, msgs] of Object.entries(errors)) {
    if (field === "non_field_errors") continue;
    out.push(`${field}: ${Array.isArray(msgs) ? msgs.join(", ") : String(msgs)}`);
  }
  return out.join("\n");
}

/** Build payload. Tolerates null selectedHour. */
export function buildPayload({
                              action,
                              cardCRM,
                              selectedHour = null,
                              shiftCode = null,
                              center = null,
                              day = null,
                              startTime = null,
                              endTime = null,
                              meta = {}
                            }) {
  let shift, startHour, endHour;
  day = parseInt(day, 10) || null;
  
  if (selectedHour) {
    const [shiftStr, startHourStr, endHourStr] = selectedHour.split("|").map(s => s.trim());
    shift = parseInt(shiftStr, 10);
    startHour = parseInt(startHourStr.split(":")[0], 10);
    endHour   = parseInt(endHourStr.split(":")[0], 10);
  } else if (shiftCode && shiftCode !== "-") { // code selection used
    shift = shiftCode;
    startHour = null;
    endHour   = null;
  } else { // hours selection used
    shift = shiftCode; // custom shift
    startHour = parseInt(startTime.split(":")[0], 10);
    endHour   = parseInt(endTime.split(":")[0], 10);
  }
  return {
    action,
    cardCRM,
    ...(shift != null ? { shift, center, day, startHour, endHour } : {}),
    ...meta
  };
}

/** Fetch POST with CSRF, timeout, consistent JSON parse and error surface */
export async function post(body, { timeout = 10000, signal } = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);

  try {
    const resp = await fetch(API_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
      },
      credentials: 'same-origin',
      body: JSON.stringify(body),
      signal: signal ?? controller.signal,
    });

    const raw = await resp.text();
    let data = null;
    if (raw) {
      try { data = JSON.parse(raw); } catch { /* keep null */ }
    }

    if (!resp.ok) {
      const errors = data?.errors ?? data ?? { detail: resp.statusText };
      const err = new Error(humanizeErrors(errors));
      err.status = resp.status;
      err.data = errors;
      throw err;
    }
    return data;
  } finally {
    clearTimeout(timer);
  }
}

/** Convenience: build + post */
export async function submitUserRequest({
  action,
  cardCRM,
  selectedHour = null,
  shiftCode = null,
  center = null,
  day = null,
  startTime = null,
  endTime = null,
  meta = {},
  options = {}
}) {
  const payload = buildPayload({
    action,
    cardCRM,
    selectedHour,
    shiftCode,
    center,
    day,
    startTime,
    endTime,
    meta
  });
  return post(payload, options);
}

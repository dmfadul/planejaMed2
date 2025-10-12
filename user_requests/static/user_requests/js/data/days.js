export async function fetchDaySchedule({ center, year, monthNumber, day }) {
  const url = `/api/day_schedule/${center}/${year}/${monthNumber}/${day}/`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(res.statusText || 'Failed to fetch day schedule');
  return res.json(); // expected: { schedule: [{ cardLine, crm }, ...] }
}


export async function fetchNamesList() {
  const url = `/api/users/`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(res.statusText || 'Failed to fetch day schedule');
  return res.json(); // expected: array of { id, crm, name }
}
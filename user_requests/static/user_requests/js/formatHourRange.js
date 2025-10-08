function formatHourRange(shiftsArray) {
  // Helpers
  const pad2 = h => String(h % 24).padStart(2, '0');
  const fmt = (h) => `${pad2(h)}:00`;
  const normalizeEnd = (start, end) => (end <= start ? end + 24 : end);
  const overlap = (s1, e1, s2, e2) => {
    const a = Math.max(s1, s2);
    const b = Math.min(e1, e2);
    return b > a ? [a, b] : null;
  };

  // Segment definitions on an "unwrapped" 0..31 axis
  // Day: 07–19, Night: 19–07(next day)
  // Micros: m 07–13, t 13–19, c 19–01(next), v 01–07(next)
  const segments = {
    d:  [7, 19],
    n:  [19, 31],   // 31 == 7 next day
    m:  [7, 13],
    t:  [13, 19],
    c:  [19, 25],   // 25 == 1 next day
    v:  [1, 7],   // 31 == 7 next day
  };

  const order = ['dn', 'd', 'n', 'm', 't', 'c', 'v'];

  const formattedHours = [];
  const formattedIDs = [];

  for (const shift of shiftsArray) {
    const id = shift.id;
    const S0 = shift.start_time % 24;
    const E0 = shift.end_time % 24;
    const S = S0;
    const E = normalizeEnd(S0, E0);            // E in (S, S+24], with 24 meaning 24h if equal

    const isFullDay = (shift.start_time % 24) === (shift.end_time % 24); // equal hours => 24h
    const duration = isFullDay ? 24 : (E - S);

    // For each shift, we collect its own rows and push (keeping global order per shift)
    // 1) dn (only when full-day)
    if (isFullDay) {
      formattedHours.push(`dn: ${fmt(S)} - ${fmt(S)}`);
      formattedIDs.push(`${id}|${S0}|${E0}`);
    }

    // Helper to add a segment if there is overlap
    const addSegment = (label, segStart, segEnd) => {
      // The shift window is [S, S+duration]
      const windowStart = S;
      const windowEnd = S + duration;          // <= S+24

      // Segment can repeat every 24h; because window ≤ 24h, check the base and +24 copy
      const candidates = [
        [segStart, segEnd],
        [segStart + 24, segEnd + 24],
      ];

      for (const [a, b] of candidates) {
        const ov = overlap(windowStart, windowEnd, a, b);
        if (ov) {
          const [os, oe] = ov;
          // Display should wrap to 0..23 for hours
          const ds = os % 24;
          const de = oe % 24;
          formattedHours.push(`${label}: ${fmt(ds)} - ${fmt(de)}`);
          formattedIDs.push(`${id}|${ds}|${de}`);
          // Since these segments don't repeat within a 24h window more than once,
          // we can break after first overlap found for this label.
          break;
        }
      }
    };

    // 2) d, n, m, t, c, v in the requested order (but after dn)
    addSegment('d', ...segments.d);
    addSegment('n', ...segments.n);
    addSegment('m', ...segments.m);
    addSegment('t', ...segments.t);
    addSegment('c', ...segments.c);
    addSegment('v', ...segments.v);
  }

  // Now we need the overall order: dn, d, n, m, t, c, v.
  // We built in that order per shift already, but if multiple shifts exist,
  // we should sort by the label prefix across all rows.
  const labelRank = { dn: 0, d: 1, n: 2, m: 3, t: 4, c: 5, v: 6 };
  const zipped = formattedHours.map((h, idx) => [h, formattedIDs[idx]]);
  zipped.sort((a, b) => {
    const la = a[0].split(':')[0]; // 'dn', 'd', ...
    const lb = b[0].split(':')[0];
    return (labelRank[la] ?? 99) - (labelRank[lb] ?? 99);
  });

  const finalHours = zipped.map(z => z[0]);
  const finalIDs = zipped.map(z => z[1]);
  return [finalHours, finalIDs];
}

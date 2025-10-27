document.addEventListener("DOMContentLoaded", function () {
  const centerSelect = document.getElementById("centerSelect");
  const monthSelect  = document.getElementById("monthSelect");
  const yearSelect   = document.getElementById("yearSelect");
  const confirmBtn   = document.getElementById("submitMonthsBtn");
  const centerGroup  = centerSelect.closest(".mb-3");

  let currentMode = "monthtable"; // default

  // Track which mode opened the modal (controls whether center is required/visible)
  document.querySelectorAll(".open-month-modal").forEach(el => {
    el.addEventListener("click", function () {
      currentMode = this.getAttribute("data-mode");
      centerGroup.style.display = (currentMode === "sum-doctors") ? "none" : "";
    });
  });

  // Helper: populate a <select>
  const populateSelect = (selectElement, data, valueKey, textKey, currentKey = "current") => {
    selectElement.innerHTML = "";
    let anySelected = false;

    data.forEach(item => {
      const option = document.createElement("option");
      option.value = String(item[valueKey]);
      option.textContent = item[textKey];
      if (item[currentKey]) {
        option.selected = true;
        anySelected = true;
      }
      selectElement.appendChild(option);
    });

    if (!anySelected && selectElement.options.length > 0) {
      selectElement.options[0].selected = true;
    }
  };

  const selectOptionByValue = (selectEl, value) => {
    const v = String(value);
    for (const opt of selectEl.options) {
      opt.selected = (opt.value === v);
    }
  };

  // ---- Static defaults ----
  const now = new Date();
  const defaultMonth = now.getMonth() + 1; // 1-12
  const defaultYear  = now.getFullYear();

  const yearsData = Array.from({ length: (2031 - 2025 + 1) }, (_, i) => {
    const y = 2025 + i;
    return { year: y, current: y === defaultYear };
  });

  const monthNamesPt = [
    "janeiro","fevereiro","março","abril","maio","junho",
    "julho","agosto","setembro","outubro","novembro","dezembro"
  ];
  const monthsData = monthNamesPt.map((name, idx) => ({
    number: idx + 1,
    name,
    current: (idx + 1) === defaultMonth
  }));

  const defaultCenters = ["CCG", "CCO", "CCQ"].map((abbr, idx) => ({
    abbr,
    current: idx === 0
  }));

  // Populate with defaults first
  populateSelect(centerSelect, defaultCenters, "abbr", "abbr");
  populateSelect(monthSelect,   monthsData,    "number", "name");
  populateSelect(yearSelect,    yearsData,     "year",   "year");

  // ---- Try to override with backend data ----
  (async () => {
    // 1) centers
    try {
      const res = await fetch("/api/centers/");
      if (res.ok) {
        const centers = await res.json();
        if (Array.isArray(centers) && centers.length > 0) {
          // Accept both {abbr} or {name} shapes; default to abbr if present
          const normalized = centers.map((c, idx) => {
            const code = c.abbr ?? c.code ?? c.name ?? c.slug ?? "";
            return { abbr: String(code), current: idx === 0 };
          }).filter(c => c.abbr);
          if (normalized.length > 0) {
            populateSelect(centerSelect, normalized, "abbr", "abbr");
          }
        }
      }
    } catch (e) {
      console.warn("Centers fetch failed; keeping defaults.", e);
    }

    // 2) current month/year (from Month model serializer)
    try {
      const res = await fetch("/api/months/current");
      if (res.ok) {
        const cur = await res.json();
        console.log("Fetched current month:", cur);
        if (cur && typeof cur.number === "number" && typeof cur.year === "number") {
          // Ensure those values exist in the lists (they should)
          selectOptionByValue(monthSelect, cur.number);
          selectOptionByValue(yearSelect,  cur.year);
        }
      }
    } catch (e) {
      console.warn("Current month fetch failed; keeping defaults.", e);
    }
  })();

  // Confirm button → redirect based on mode
  confirmBtn.addEventListener("click", function () {
    const center = centerSelect.value;
    const month  = monthSelect.value;
    const year   = yearSelect.value;

    const centerOk = (currentMode === "sum-doctors") || !!center;
    if (month && year && centerOk) {
      let url;
      if (currentMode === "monthtable") {
        url = `${window.location.origin}/shifts/monthtable/${center}/${month}/${year}/`;
      } else if (currentMode === "sum-doctors") {
        url = `${window.location.origin}/shifts/sum-doctors/${month}/${year}/`;
      }
      window.location.href = url;
    } else {
      alert("Please select all fields.");
    }
  });
});
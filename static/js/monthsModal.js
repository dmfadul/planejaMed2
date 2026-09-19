document.addEventListener("DOMContentLoaded", function () {
  const centerSelect = document.getElementById("centerSelect");
  const monthSelect  = document.getElementById("monthSelect");
  const yearSelect   = document.getElementById("yearSelect");
  const confirmBtn   = document.getElementById("submitMonthsBtn");
  const centerGroup  = centerSelect.closest(".mb-3");

  const modesWithoutCenter = ["sum-doctors", "generalReport"];
  let currentMode = "monthtable";

// Create the "Excluir ECO" checkbox.
const excludeEcoGroup = document.createElement("div");
excludeEcoGroup.className = "form-check border rounded p-3 mb-3 bg-light";
excludeEcoGroup.style.display = "none";

excludeEcoGroup.innerHTML = `
  <input
    class="form-check-input border border-dark"
    type="checkbox"
    id="excludeEcoCheckbox"
    style="
      width: 1.25rem;
      height: 1.25rem;
      cursor: pointer;
      accent-color: #0d6efd;
    "
  >
  <label
    class="form-check-label fw-semibold ms-2"
    for="excludeEcoCheckbox"
    style="cursor: pointer;"
  >
    Excluir ECO
  </label>
`;

// Place it after the last selection field.
const yearGroup = yearSelect.closest(".mb-3");
yearGroup.insertAdjacentElement("afterend", excludeEcoGroup);

const excludeEcoCheckbox = document.getElementById(
  "excludeEcoCheckbox"
);

// Track which mode opened the modal.
 document.querySelectorAll(".open-month-modal").forEach(el => {
  el.addEventListener("click", function () {
    currentMode = this.getAttribute("data-mode");

    const needsCenter = !modesWithoutCenter.includes(currentMode);
    const isGeneralReport = currentMode === "generalReport";

    centerGroup.style.display = needsCenter ? "" : "none";
    excludeEcoGroup.style.display = isGeneralReport ? "" : "none";

    // Prevent a previous selection from remaining active.
    if (!isGeneralReport) {
      excludeEcoCheckbox.checked = false;
    }
  });
});

// Helper: populate a <select>.
const populateSelect = (
  selectElement,
  data,
  valueKey,
  textKey,
  currentKey = "current"
) => {
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
    const normalizedValue = String(value);

    for (const option of selectEl.options) {
      option.selected = option.value === normalizedValue;
    }
  };

  // Static defaults.
  const now = new Date();
  const defaultMonth = now.getMonth() + 1;
  const defaultYear  = now.getFullYear();

  const yearsData = Array.from(
    { length: 2031 - 2025 + 1 },
    (_, index) => {
      const year = 2025 + index;

      return {
        year,
        current: year === defaultYear
      };
    }
  );

  const monthNamesPt = [
    "janeiro",
    "fevereiro",
    "março",
    "abril",
    "maio",
    "junho",
    "julho",
    "agosto",
    "setembro",
    "outubro",
    "novembro",
    "dezembro"
  ];

  const monthsData = monthNamesPt.map((name, index) => ({
    number: index + 1,
    name,
    current: index + 1 === defaultMonth
  }));

  const defaultCenters = ["CCG", "CCO", "CCQ"].map((abbr, index) => ({
    abbr,
    current: index === 0
  }));

  // Populate with defaults first.
  populateSelect(centerSelect, defaultCenters, "abbr", "abbr");
  populateSelect(monthSelect, monthsData, "number", "name");
  populateSelect(yearSelect, yearsData, "year", "year");

  // Try to override defaults with backend data.
  (async () => {
    try {
      const response = await fetch("/api/centers/");

      if (response.ok) {
        const centers = await response.json();

        if (Array.isArray(centers) && centers.length > 0) {
          const normalized = centers
            .map((center, index) => {
              const code =
                center.abbr ??
                center.code ??
                center.name ??
                center.slug ??
                "";

              return {
                abbr: String(code),
                current: index === 0
              };
            })
            .filter(center => center.abbr);

          if (normalized.length > 0) {
            populateSelect(centerSelect, normalized, "abbr", "abbr");
          }
        }
      }
    } catch (error) {
      console.warn(
        "Centers fetch failed; keeping defaults.",
        error
      );
    }

    try {
      const response = await fetch("/api/months/current");

      if (response.ok) {
        const currentMonth = await response.json();

        if (
          currentMonth &&
          typeof currentMonth.number === "number" &&
          typeof currentMonth.year === "number"
        ) {
          selectOptionByValue(monthSelect, currentMonth.number);
          selectOptionByValue(yearSelect, currentMonth.year);
        }
      }
    } catch (error) {
      console.warn(
        "Current month fetch failed; keeping defaults.",
        error
      );
    }
  })();

  // Confirm button: redirect based on mode.
  confirmBtn.addEventListener("click", function () {
    const center = centerSelect.value;
    const month  = monthSelect.value;
    const year   = yearSelect.value;

    const needsCenter = !modesWithoutCenter.includes(currentMode);
    const centerOk = !needsCenter || Boolean(center);

    if (!month || !year || !centerOk) {
      alert("Please select all fields.");
      return;
    }

    let url;

    if (currentMode === "monthtable") {
      url = new URL(
        `/shifts/monthtable/${center}/${month}/${year}/`,
        window.location.origin
      );
    } else if (currentMode === "sum-doctors") {
      url = new URL(
        `/shifts/sum-doctors/${month}/${year}/`,
        window.location.origin
      );
    } else if (currentMode === "generalReport") {
      url = new URL(
        `/shifts/report/${month}/${year}/`,
        window.location.origin
      );

      url.searchParams.set(
        "exclude_eco",
        excludeEcoCheckbox.checked ? "1" : "0"
      );
    } else {
      console.log("Unknown mode:", currentMode);
      alert("Unknown mode.");
      return;
    }

    window.location.href = url.toString();
  });
});
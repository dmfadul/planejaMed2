document.addEventListener("DOMContentLoaded", async function () {
  const centerSelect = document.getElementById("centerSelect");
  const monthSelect = document.getElementById("monthSelect");
  const yearSelect = document.getElementById("yearSelect");
  const confirmBtn = document.getElementById("submitMonthsBtn");

  const populateSelect = (selectElement, data, valueKey, textKey) => {
    selectElement.innerHTML = '';
    data.forEach(item => {
      const option = document.createElement("option");
      option.value = item[valueKey];
      option.textContent = item[textKey];
      selectElement.appendChild(option);
    });
  };

  try {
    const [centersRes, monthsRes, yearsRes] = await Promise.all([
      fetch("/api/centers/"),
      fetch("/api/months/"),
      fetch("/api/years/")
    ]);

    const centersData = await centersRes.json();
    const monthsData = await monthsRes.json();
    const yearsData = await yearsRes.json();

    populateSelect(centerSelect, centersData, "abbr", "abbr");
    populateSelect(monthSelect, monthsData, "number", "name");
    populateSelect(yearSelect, yearsData, "year", "year");

  } catch (err) {
    console.error("Failed to load dropdown data:", err);
  }

  confirmBtn.addEventListener("click", function () {
    const center = centerSelect.value;
    const month = monthSelect.value;
    const year = yearSelect.value;

    if (center && month && year) {
      const url = `${window.location.origin}/shifts/monthtable/${center}/${month}/${year}/`;
      window.location.href = url;
    } else {
      alert("Please select all fields.");
    }
  });
});

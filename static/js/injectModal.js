document.addEventListener("DOMContentLoaded", async function () {
    console.log("Injecting modal script...");
  const centroSelect = document.getElementById("centroSelect");
  const mesSelect = document.getElementById("mesSelect");
  const anoSelect = document.getElementById("anoSelect");

  // Generic function to populate a <select> element
  const populateSelect = (selectElement, data, valueKey, textKey) => {
    selectElement.innerHTML = ''; // Clear previous options if needed
    data.forEach(item => {
      const option = document.createElement("option");
      option.value = item[valueKey];
      option.textContent = item[textKey];
      selectElement.appendChild(option);
    });
  };

  try {
    // Fetch and populate Centros
    const centrosResponse = await fetch("/api/centros/");
    const centrosData = await centrosResponse.json();
    populateSelect(centroSelect, centrosData, "id", "nome");

    // Fetch and populate Meses
    const mesesResponse = await fetch("/api/meses/");
    const mesesData = await mesesResponse.json();
    populateSelect(mesSelect, mesesData, "numero", "nome");

    // Fetch and populate Anos
    const anosResponse = await fetch("/api/anos/");
    const anosData = await anosResponse.json();
    anosData.forEach(ano => {
      const option = document.createElement("option");
      option.value = ano;
      option.textContent = ano;
      anoSelect.appendChild(option);
    });
  } catch (error) {
    console.error("Failed to load select options:", error);
    // Optionally, show a user-friendly alert or fallback UI
  }
});


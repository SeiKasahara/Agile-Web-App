document.addEventListener("DOMContentLoaded", () => {
  const openBtn = document.getElementById("open-upload-modal");
  const closeBtn = document.getElementById("close-upload-modal");
  const modal = document.getElementById("upload-modal");

  openBtn.addEventListener("click", () => {
    modal.classList.remove("hidden");
    modal.classList.add("flex");
  });
  closeBtn.addEventListener("click", () => {
    modal.classList.add("hidden");
    modal.classList.remove("flex");
  });

  modal.addEventListener("click", (e) => {
    if (e.target === modal) {
      modal.classList.add("hidden");
      modal.classList.remove("flex");
    }
  });
});

document.addEventListener("DOMContentLoaded", () => {
  const uploadForm = document.getElementById("upload-form");
  const previewSlot = document.createElement("div");
  previewSlot.id = "upload-preview";
  previewSlot.className = "pt-4 space-y-4";

  uploadForm.parentNode.insertBefore(previewSlot, uploadForm.nextSibling);

  uploadForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    previewSlot.innerHTML = "";
    const formData = new FormData(uploadForm);

    try {
      const resp = await fetch(uploadForm.action, {
        method: "POST",
        body: formData,
      });
      const data = await resp.json();

      if (!resp.ok) {
        previewSlot.innerHTML = `<p class="text-red-500">${
          data.error || data.message
        }</p>`;
        return;
      }

      const sample = data.sample || [];
      if (!sample.length) {
        previewSlot.innerHTML = `<p class="text-gray-500">No data to preview.</p>`;
        return;
      }

      if (Array.isArray(data.sample) && data.sample.length) {
        previewSlot.appendChild(renderTable(data.sample));
      }
      if (data.stats_html) {
        const statsDiv = document.createElement("div");
        statsDiv.innerHTML = `<h3 class="text-xl font-semibold">Statistics</h3>${data.stats_html}`;
        previewSlot.appendChild(statsDiv);
      }

      const msg = document.createElement("p");
      msg.className = "text-green-600";
      msg.textContent = data.message;
      previewSlot.insertBefore(msg, previewSlot.firstChild);
    } catch (err) {
      previewSlot.innerHTML = `<p class="text-red-500">Network error: ${err.message}</p>`;
    }
  });

  function renderTable(records) {
    const table = document.createElement("table");
    table.className = "min-w-full table-auto text-sm";

    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");
    Object.keys(records[0]).forEach((key) => {
      const th = document.createElement("th");
      th.className = "px-2 py-1 bg-gray-200 text-gray-700";
      th.textContent = key;
      headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    const tbody = document.createElement("tbody");
    records.forEach((row) => {
      const tr = document.createElement("tr");
      Object.values(row).forEach((val) => {
        const td = document.createElement("td");
        td.className = "border px-2 py-1";
        td.textContent = val;
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);

    return table;
  }
});

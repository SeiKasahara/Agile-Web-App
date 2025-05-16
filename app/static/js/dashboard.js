document.addEventListener("DOMContentLoaded", () => {
  const openBtn = document.getElementById("open-upload-modal");
  const openBtnMobile = document.getElementById("open-upload-modal-mobile");
  const closeBtn = document.getElementById("close-upload-modal");
  const modal = document.getElementById("upload-modal");

  openBtn.addEventListener("click", () => {
    modal.classList.remove("hidden");
    modal.classList.add("flex");
  });
  openBtnMobile.addEventListener("click", () => {
    modal.classList.remove("hidden");
    modal.classList.add("flex");
  });
  closeBtn.addEventListener("click", () => {
    modal.classList.add("hidden");
    modal.classList.remove("flex");
    window.location.reload();
  });

  modal.addEventListener("click", (e) => {
    if (e.target === modal) {
      modal.classList.add("hidden");
      modal.classList.remove("flex");
    }
  });
});

function disableButton(btn) {
  btn.classList.add(
    "cursor-not-allowed",
    "opacity-60",
    "pointer-events-none",
    "bg-gray-300",
    "text-gray-500"
  );
  btn.classList.remove("bg-black", "text-white", "hover:bg-gray-800");
}

function enableButton(btn) {
  btn.classList.remove(
    "cursor-not-allowed",
    "opacity-60",
    "pointer-events-none",
    "bg-gray-300",
    "text-gray-500"
  );
  btn.classList.add("bg-black", "text-white", "hover:bg-gray-800");
}

document.addEventListener("DOMContentLoaded", () => {
  const uploadForm = document.getElementById("upload-form");
  const previewSlot = document.createElement("div");
  const uploadBtn = document.getElementById("upload-btn");
  const uploading = document.getElementById("uploading");
  previewSlot.id = "upload-preview";
  previewSlot.className = "pt-4 space-y-4";

  uploadForm.parentNode.insertBefore(previewSlot, uploadForm.nextSibling);

  uploadForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    previewSlot.innerHTML = "";
    disableButton(uploadBtn);
    uploading.classList.remove("hidden");
    uploading.classList.add("flex");

    const formData = new FormData(uploadForm);

    try {
      const resp = await fetch(uploadForm.action, {
        method: "POST",
        body: formData,
      });
      const data = await resp.json();

      const handle = () => {
        if (!resp.ok) {
          previewSlot.innerHTML = `<p class="text-red-500">${data.error || data.message}</p>`;
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
      };
      handle();
    } catch (err) {
      previewSlot.innerHTML = `<p class="text-red-500">Internal Server Error: ${err.message}</p>`;
    } finally {
      enableButton(uploadBtn);
      uploading.classList.add("hidden");
      uploading.classList.remove("flex");
    }
  });

  function renderTable(records) {
    const table = document.createElement("table");
    table.className = "min-w-full table-auto text-sm";

    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");
    for (const key of Object.keys(records[0])) {
      const th = document.createElement("th");
      th.className = "px-2 py-1 bg-gray-200 text-gray-700";
      th.textContent = key;
      headerRow.appendChild(th);
    }
    thead.appendChild(headerRow);
    table.appendChild(thead);

    const tbody = document.createElement("tbody");
    for (const row of records) {
      const tr = document.createElement("tr");
      for (const val of Object.values(row)) {
        const td = document.createElement("td");
        td.className = "border px-2 py-1";
        td.textContent = val;
        tr.appendChild(td);
      }
      tbody.appendChild(tr);
    }
    table.appendChild(tbody);

    return table;
  }
});

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("filter-form");
  if (!form) return;
  for (const el of form.querySelectorAll(
    `input[name="date"], select[name="fuel_type"], select[name="location"]`
  )) {
    el.addEventListener("change", () => {
      form.submit();
    });
  }
});

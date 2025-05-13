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

      if (!resp.ok) {
        previewSlot.innerHTML = `<p class="text-red-500">${
          data.error || data.message
        }</p>`;
        enableButton(uploadBtn);
        uploading.classList.add("hidden");
        uploading.classList.remove("flex");
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
      enableButton(uploadBtn);
      uploading.classList.add("hidden");
      uploading.classList.remove("flex");
      previewSlot.insertBefore(msg, previewSlot.firstChild);
    } catch (err) {
      previewSlot.innerHTML = `<p class="text-red-500">Internal Server Error: ${err.message}</p>`;
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

document.addEventListener("DOMContentLoaded", function () {
  var form = document.getElementById("filter-form");
  if (!form) return;
  form
    .querySelectorAll(
      `input[name="date"], select[name="fuel_type"], select[name="location"]`
    )
    .forEach(function (el) {
      el.addEventListener("change", function () {
        form.submit();
      });
    });
});

document.addEventListener("DOMContentLoaded", () => {
  const shareBtn = document.getElementById("share-dashboard-btn");
  const modal = document.getElementById("share-modal");
  const closeBtn = document.getElementById("close-share-btn");
  const urlInput = document.getElementById("share-url-input");
  const copyBtn = document.getElementById("copy-share-btn");
  const twitterBtn = document.getElementById("twitter-share");
  const facebookBtn = document.getElementById("facebook-share");
  const linkedinBtn = document.getElementById("linkedin-share");

  function openModal(shareUrl) {
    urlInput.value = shareUrl;
    const encoded = encodeURIComponent(shareUrl);
    const text = encodeURIComponent("Check out my FuelPrice Dashboard!");
    twitterBtn.href = `https://twitter.com/intent/tweet?url=${encoded}&text=${text}`;
    facebookBtn.href = `https://www.facebook.com/sharer/sharer.php?u=${encoded}`;
    linkedinBtn.href = `https://www.linkedin.com/sharing/share-offsite/?url=${encoded}`;
    modal.classList.remove("hidden");
    modal.classList.add("flex");
  }

  closeBtn.addEventListener("click", () => {
    modal.classList.add("hidden");
    modal.classList.remove("flex");
  });
  modal.addEventListener("click", (e) => {
    if (e.target === modal) modal.classList.add("hidden");
  });

  copyBtn.addEventListener("click", () => {
    urlInput.select();
    document.execCommand("copy");
    copyBtn.textContent = "Copied!";
    setTimeout(() => (copyBtn.textContent = "Copy Link"), 2000);
  });

  shareBtn.addEventListener("click", async () => {
    const fuel = document.getElementById("fuel_type_select").value;
    const loc = document.getElementById("location_select").value;
    const date = document.getElementById("date_select").value;
    const forecastChart = Chart.getChart("forecastChart");
    const forecastConfig = JSON.parse(JSON.stringify(forecastChart.config));
    const params = new URLSearchParams({
      fuel_type: fuel,
      location: loc,
      date: date,
    });
    let url = `/dashboard/data?${params}`;
    const res = await fetch(url);
    const data = await res.json();
    console.log(data);

    const { points } = data;

    try {
      const res = await fetch("/share/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          fuel,
          loc,
          date,
          forecastConfig,
          heatmapPoints: points,
        }),
      });
      if (!res.ok) throw new Error(`Status ${res.status}`);
      const { url } = await res.json();
      openModal(url);
    } catch (err) {
      console.error(err);
      alert("Failed to generate share link. Please try again.");
    }
  });
});

// eslint-disable-next-line no-unused-vars
function previewAvatar(event) {
  const [file] = event.target.files;
  if (!file) return;

  const img = document.getElementById("avatar-preview");
  const initials = document.getElementById("avatar-initials");
  img.src = URL.createObjectURL(file);
  img.classList.remove("hidden");
  initials.classList.add("hidden");
}

document.addEventListener("DOMContentLoaded", () => {
  const avatarInput = document.getElementById("avatar-upload");
  const profileForm = document.getElementById("profile-form");
  const profileMsg = document.getElementById("profile-msg");
  //
  const verifyBtn = document.getElementById("verify-email-btn");
  const verifyMsg = document.getElementById("verify-msg");
  //
  const resetBtn = document.getElementById("reset-btn");
  const resetForm = document.getElementById("reset-form");
  const resetMsg = document.getElementById("reset-msg");
  //
  const codeSection = document.getElementById("code-section");
  const codeInput = document.getElementById("verify-code-input");
  //
  const confirmBtn = document.getElementById("confirm-code-btn");
  const confirmMsg = document.getElementById("confirm-msg");
  const verifiedBadge = document.getElementById("verified-badge");
  //
  const emailChangeBtn = document.getElementById("change-email-btn");
  const emailChangeForm = document.getElementById("change-email-form");
  const emailChangeMsg = document.getElementById("change-email-msg");
  const emailInput = emailChangeForm.querySelector("input[name='email']");

  function showMessage(el, message, isSuccess = true, size = "xs") {
    el.textContent = message;
    const colorClass = isSuccess ? "text-green-500" : "text-red-500";
    const sizeClass = size === "sm" ? "text-sm" : "text-xs";
    el.className = `${colorClass} ${sizeClass} text-center mt-2`;
  }

  window.previewAvatar = (event) => {
    const [file] = event.target.files;
    if (!file) return;
    const img = document.getElementById("avatar-preview");
    const initials = document.getElementById("avatar-initials");
    img.src = URL.createObjectURL(file);
    img.classList.remove("hidden");
    initials.classList.add("hidden");
  };

  if (profileForm) {
    profileForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      showMessage(profileMsg, "", true);
      const formData = new FormData(profileForm);

      if (avatarInput && avatarInput.files.length > 0) {
        formData.append("avatar", avatarInput.files[0]);
      }

      try {
        const resp = await fetch(profileForm.action, {
          method: "POST",
          body: formData,
        });
        const data = await resp.json();
        if (data.status === "success") {
          showMessage(profileMsg, data.message, true, "sm");
          if (data.avatar_url) {
            const img = document.getElementById("avatar-preview");
            img.src = data.avatar_url;
          }
        } else {
          throw new Error(data.message || "Failed to save settings");
        }
      } catch (err) {
        showMessage(profileMsg, err.message, false, "sm");
      }
    });
  }

  if (verifyBtn) {
    verifyBtn.addEventListener("click", async () => {
      showMessage(verifyMsg, "");
      verifyBtn.disabled = true;
      try {
        const resp = await fetch("/profile/verify-email", { method: "POST" });
        const data = await resp.json();
        if (data.status === "success") {
          showMessage(verifyMsg, "Code sent! Check your inbox.");
          codeSection.classList.remove("hidden");
        } else {
          throw new Error(data.message || "Send failed");
        }
      } catch (err) {
        showMessage(verifyMsg, err.message, false);
      } finally {
        setTimeout(() => {
          verifyBtn.disabled = false;
        }, 60000);
      }
    });
  }

  function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
  if (confirmBtn) {
    confirmBtn.addEventListener("click", async () => {
      const code = codeInput.value.trim();
      if (!/^\d{6}$/.test(code)) {
        showMessage(confirmMsg, "Please enter a 6-digit code.", false);
        return;
      }
      showMessage(confirmMsg, "");
      confirmBtn.disabled = true;
      const payload = {
        code,
        new_email: emailChangeForm.querySelector("input[name='email']").value,
      };
      try {
        const resp = await fetch("/profile/confirm-email", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        const data = await resp.json();
        if (data.status === "success") {
          showMessage(confirmMsg, "Your Email verified!", true);
          alert("Your Email verified!");
          await sleep(3000);
          codeSection.classList.add("hidden");
          verifyBtn?.classList.add("hidden");
          location.reload();
          if (verifiedBadge) verifiedBadge.textContent = "Verified";
        } else {
          throw new Error(data.message || "Invalid code");
        }
      } catch (err) {
        showMessage(confirmMsg, err.message, false);
      } finally {
        confirmBtn.disabled = false;
      }
    });
  }

  const showError = (input, message) => {
    const existing = input.parentNode.querySelector(".error-message");
    if (!existing) {
      const msg = document.createElement("p");
      msg.className = "error-message text-xs text-red-500 mt-1";
      msg.textContent = message;
      input.insertAdjacentElement("afterend", msg);
    }

    if (!input.classList.contains("border-red-500")) {
      input.classList.add("border-red-500");
      input.style.position = "relative";
      input.dataset.shaken = "true";
      anime({
        targets: input,
        boxShadow: [
          "0 0 0px rgba(255,0,0,0)",
          "0 0 4px rgba(255,0,0,0.8)",
          "0 0 8px rgba(255,0,0,1)",
          "0 0 0px rgba(255,0,0,0)",
        ],
        duration: 600,
        easing: "easeInOutQuad",
      });
    }
  };

  const clearError = (input) => {
    const existing = input.parentNode.querySelector(".error-message");
    if (existing) existing.remove();
    input.classList.remove("border-red-500");
    delete input.dataset.shaken;
  };

  const validateEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

  emailInput.addEventListener("input", () => {
    const email = emailInput.value.trim();
    if (!validateEmail(email)) {
      showError(emailInput, "Please enter a valid email address.");
      emailChangeBtn.disabled = true;
      emailChangeBtn.classList.add(
        "cursor-not-allowed",
        "opacity-60",
        "pointer-events-none",
        "bg-gray-300",
        "text-gray-500"
      );
      emailChangeBtn.classList.remove(
        "bg-black",
        "text-white",
        "hover:bg-gray-800"
      );
    } else {
      clearError(emailInput);
      emailChangeBtn.disabled = false;
      emailChangeBtn.classList.remove(
        "cursor-not-allowed",
        "opacity-60",
        "pointer-events-none",
        "bg-gray-300",
        "text-gray-500"
      );
      emailChangeBtn.classList.add(
        "bg-black",
        "text-white",
        "hover:bg-gray-800"
      );
    }
  });

  emailChangeBtn.addEventListener("click", (e) => {
    e.preventDefault();
    emailChangeBtn.disabled = true;
    document.getElementById("email-input").disabled = true;
    fetch(emailChangeForm.action, {
      method: "POST",
      body: new FormData(emailChangeForm),
    })
      .then((r) => r.json())
      .then((data) => {
        if (data.status === "success") {
          showMessage(emailChangeMsg, "Code sent! Check your inbox.");
          codeSection.classList.remove("hidden");
        } else {
          throw new Error(data.message || "Send failed");
        }
      })
      .catch((err) => {
        emailChangeMsg.textContent = err.message;
        emailChangeMsg.className = "text-red-500 text-xs mt-2 text-center";
      })
      .finally(() => {
        setTimeout(() => (emailChangeBtn.disabled = false), 60000);
      });
  });

  resetBtn.addEventListener("click", (e) => {
    e.preventDefault();
    resetMsg.textContent = "";
    resetBtn.disabled = true;

    fetch(resetForm.action, {
      method: "POST",
      body: new FormData(resetForm),
    })
      .then((r) => r.json())
      .then((data) => {
        if (data.status === "success") {
          resetMsg.textContent = "Reset link sent!";
          resetMsg.className = "text-green-500 text-xs mt-2 text-center";
        } else {
          throw new Error(data.message);
        }
      })
      .catch((err) => {
        resetMsg.textContent = err.message;
        resetMsg.className = "text-red-500 text-xs mt-2 text-center";
      })
      .finally(() => {
        setTimeout(() => (resetBtn.disabled = false), 60000);
      });
  });
});

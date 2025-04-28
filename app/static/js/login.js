function enableFormLeaveProtection(formId) {
  const form = document.getElementById(formId);
  if (!form) {
    console.warn(`Form with ID "${formId}" not found.`);
    return;
  }

  let isFormDirty = false;

  form.querySelectorAll("input, textarea, select").forEach((input) => {
    input.addEventListener("input", () => {
      isFormDirty = true;
    });
  });

  const beforeUnloadHandler = (e) => {
    if (isFormDirty) {
      e.preventDefault();
      e.returnValue = "";
    }
  };
  window.addEventListener("beforeunload", beforeUnloadHandler);

  form.addEventListener("submit", () => {
    window.removeEventListener("beforeunload", beforeUnloadHandler);
  });
}

function disableButton(btn) {
  btn.disabled = true;
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
  btn.disabled = false;
  btn.classList.remove(
    "cursor-not-allowed",
    "opacity-60",
    "pointer-events-none",
    "bg-gray-300",
    "text-gray-500"
  );
  btn.classList.add("bg-black", "text-white", "hover:bg-gray-800");
}

const validateEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("login-form");
  const emailInput = form.querySelector("input[name='email']");
  const passwordInput = form.querySelector("input[name='password']");
  const loginButton = document.getElementById("login-btn");
  enableFormLeaveProtection("login-form");

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

  const validateEmailInput = () => {
    const email = emailInput.value.trim();
    if (!validateEmail(email)) {
      showError(emailInput, "Please enter a valid email address.");
      return false;
    } else {
      clearError(emailInput);
      return true;
    }
  };

  const validatePasswordInput = () => {
    const password = passwordInput.value.trim();
    if (password.length === 0) {
      showError(passwordInput, "Please enter your password.");
      return false;
    } else {
      clearError(passwordInput);
      return true;
    }
  };

  const updateLoginButton = () => {
    const valid = validateEmailInput() && validatePasswordInput();
    loginButton.disabled = !valid;

    if (valid) {
      enableButton(loginButton);
    } else {
      disableButton(loginButton);
    }
  };

  emailInput.addEventListener("input", () => {
    validateEmailInput();
    updateLoginButton();
  });

  passwordInput.addEventListener("input", () => {
    validatePasswordInput();
    updateLoginButton();
  });

  form.addEventListener("submit", (e) => {
    e.preventDefault();

    const valid = validateEmailInput() && validatePasswordInput();
    if (!valid) return;

    disableButton(loginButton);

    const formData = new FormData(form);

    function showErrorMessage(message) {
      const msg = document.getElementById("login-msg");
      msg.textContent = message;
      msg.className = "text-red-500 text-center mt-2";
    }

    fetch("/login", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "success") {
          alert("Login Successful!", "Redirecting to dashboard...");
          setTimeout(() => {
            window.location.href = "/";
          }, 1500);
        } else {
          showErrorMessage(data.message);
          enableButton(loginButton);
        }
      })
      .catch(() => {
        showErrorMessage("Network error. Please try again.");
        enableButton(loginButton);
      });
  });
});

// eslint-disable-next-line no-unused-vars
function openForgotPasswordModal() {
  const modal = document.getElementById("forgot-password-modal");
  modal.classList.remove("hidden");
  modal.classList.add("flex");
}

// eslint-disable-next-line no-unused-vars
function closeForgotPasswordModal() {
  const modal = document.getElementById("forgot-password-modal");
  modal.classList.remove("flex");
  modal.classList.add("hidden");
}

// Optional: AJAX-like handling (can replace with real fetch later)
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("forgot-password-form");
  const emailInput = document.getElementById("reset-email");
  const emailBtn = document.getElementById("reset-btn");
  const msg = document.getElementById("reset-msg");
  const resendSection = document.getElementById("resend-section");
  const resendBtn = document.getElementById("resend-link-btn");
  const timerSpan = document.getElementById("resend-timer");

  let countdown = 0;
  let intervalId = null;

  const startCooldown = () => {
    countdown = 60;
    resendBtn.disabled = true;
    resendBtn.classList.add("cursor-not-allowed", "text-gray-400");
    timerSpan.textContent = `(${countdown}s)`;

    intervalId = setInterval(() => {
      countdown--;
      timerSpan.textContent = `(${countdown}s)`;
      if (countdown <= 0) {
        clearInterval(intervalId);
        resendBtn.disabled = false;
        resendBtn.classList.remove("cursor-not-allowed", "text-gray-400");
        timerSpan.textContent = "";
      }
    }, 1000);
  };

  form.addEventListener("submit", (e) => {
    e.preventDefault();

    const email = emailInput.value.trim();

    if (!validateEmail(email)) {
      msg.textContent = "Please enter a valid email address.";
      msg.classList.remove("text-green-500", "hidden");
      msg.classList.add("text-red-500");
      return;
    }

    const formData = new FormData();
    formData.append("email", email);

    fetch("/forgot-password", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "success") {
          msg.textContent = data.message;
          msg.classList.remove("text-red-500", "hidden");
          msg.classList.add("text-green-500");
          disableButton(emailBtn);
          resendSection.classList.remove("hidden");
          startCooldown();
        } else {
          msg.textContent = data.message || "Error occurred.";
          msg.classList.remove("text-green-500", "hidden");
          msg.classList.add("text-red-500");
          disableButton(emailBtn);
          resendSection.classList.remove("hidden");
          startCooldown();
        }
      })
      .catch(() => {
        msg.textContent = "Network error. Please try again.";
        msg.classList.remove("text-green-500", "hidden");
        msg.classList.add("text-red-500");
        disableButton(emailBtn);
        resendSection.classList.remove("hidden");
        startCooldown();
      });
  });

  resendBtn.addEventListener("click", () => {
    const formData = new FormData();
    const email = emailInput.value.trim();
    formData.append("email", email);
    fetch("/forgot-password", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "success") {
          msg.textContent = data.message;
          msg.classList.remove("text-red-500", "hidden");
          msg.classList.add("text-green-500");
        } else {
          msg.textContent = data.message || "Error occurred.";
          msg.classList.remove("text-green-500", "hidden");
          msg.classList.add("text-red-500");
        }
      })
      .catch(() => {
        msg.textContent = "Network error. Please try again.";
        msg.classList.remove("text-green-500", "hidden");
        msg.classList.add("text-red-500");
      });

    startCooldown();
  });
});

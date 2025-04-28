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

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("sign-up-form");
  const emailInput = form.querySelector("input[name='email']");
  const passwordInput = form.querySelector("input[name='password']");
  const confirmInput = form.querySelector("input[name='confirm_password']");
  const signUpButton = document.getElementById("sign-up-btn");
  const agreeCheckbox = document.getElementById("agree");
  enableFormLeaveProtection("sign-up-form");
  const backend_msg = document.getElementById("signup-msg");

  const validateEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

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

  function getPasswordStrength(password) {
    let score = 0;
    if (password.length >= 8) score++;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score++;
    if (/\d/.test(password)) score++;
    if (/[^A-Za-z0-9]/.test(password)) score++;
    return score;
  }

  function updatePasswordStrength(password) {
    const bar = document.getElementById("password-strength-bar");
    const text = document.getElementById("password-strength-text");

    const strength = getPasswordStrength(password);
    const strengthMap = {
      0: { width: "0%", color: "", label: "" },
      1: { width: "25%", color: "bg-red-500", label: "Weak" },
      2: { width: "50%", color: "bg-yellow-500", label: "Fair" },
      3: { width: "75%", color: "bg-blue-500", label: "Good" },
      4: { width: "100%", color: "bg-green-500", label: "Strong" },
    };

    const { width, color, label } = strengthMap[strength];
    bar.className = `h-full transition-all duration-300 ease-in-out ${color}`;
    bar.style.width = width;
    text.textContent = label;
    text.className = `text-xs mt-1 ${color.replace("bg-", "text-")}`;
  }

  emailInput.addEventListener("input", () => {
    const email = emailInput.value.trim();
    if (!validateEmail(email)) {
      showError(emailInput, "Please enter a valid email address.");
    } else {
      clearError(emailInput);
    }
    updateSubmitButton();
  });

  passwordInput.addEventListener("input", () => {
    const password = passwordInput.value.trim();
    updatePasswordStrength(password);

    if (password.length < 8) {
      showError(passwordInput, "Password must be at least 8 characters.");
    } else {
      clearError(passwordInput);
    }

    checkPasswordMatch();
    updateSubmitButton();
  });

  confirmInput.addEventListener("input", () => {
    checkPasswordMatch();
    updateSubmitButton();
  });

  function checkPasswordMatch() {
    const password = passwordInput.value.trim();
    const confirm = confirmInput.value.trim();
    if (confirm && password !== confirm) {
      showError(confirmInput, "Passwords do not match.");
    } else {
      clearError(confirmInput);
    }
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

  function updateSubmitButton() {
    const email = emailInput.value.trim();
    const password = passwordInput.value.trim();
    const confirm = confirmInput.value.trim();
    const agreed = agreeCheckbox.checked;

    const emailValid = validateEmail(email);
    const passwordValid = password.length >= 8;
    const passwordsMatch = !confirm || password === confirm;
    const allValid = emailValid && passwordValid && passwordsMatch && agreed;

    signUpButton.disabled = !allValid;

    if (!allValid) {
      disableButton(signUpButton);
    } else {
      enableButton(signUpButton);
    }
  }

  agreeCheckbox.addEventListener("change", updateSubmitButton);

  form.addEventListener("submit", (e) => {
    e.preventDefault();

    if (form.querySelector(".error-message")) return;

    disableButton(signUpButton);

    const formData = new FormData(form);

    fetch("/signup", {
      method: "POST",
      body: formData,
    })
      .then((response) => {
        if (response.status === 200) {
          alert("Account created successfully! Redirecting to login...");
          setTimeout(() => {
            window.location.href = "/login";
          }, 1500);
        } else if (response.status === 500) {
          backend_msg.textContent = "Server error. Please try again later.";
          backend_msg.className = "text-red-500 text-center mt-2";
          enableButton(signUpButton);
        } else {
          response.text().then((html) => {
            if (html.includes("Email already registered")) {
              backend_msg.textContent = "This email is already registered.";
              backend_msg.className = "text-red-500 text-center mt-2";
            } else {
              backend_msg.textContent = "Unknown error occurred.";
              backend_msg.className = "text-red-500 text-center mt-2";
            }
            enableButton(signUpButton);
          });
        }
      })
      .catch(() => {
        backend_msg.textContent =
          "Network error. Please check your connection.";
        backend_msg.className = "text-red-500 text-center mt-2";
        enableButton(signUpButton);
      });
  });
});

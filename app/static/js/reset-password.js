document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("form");
  const passwordInput = form.querySelector("input[name='new_password']");
  const confirmInput = form.querySelector("input[name='confirm_password']");
  const submitButton = form.querySelector("button[type='submit']");

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

  const getPasswordStrength = (password) => {
    let score = 0;
    if (password.length >= 8) score++;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score++;
    if (/\d/.test(password)) score++;
    if (/[^A-Za-z0-9]/.test(password)) score++;
    return score;
  };

  const updatePasswordStrength = (password) => {
    const strengthBar = document.getElementById("password-strength-bar");
    const strengthText = document.getElementById("password-strength-text");

    const strength = getPasswordStrength(password);
    const strengthMap = {
      0: { width: "0%", color: "", label: "" },
      1: { width: "25%", color: "bg-red-500", label: "Weak" },
      2: { width: "50%", color: "bg-yellow-500", label: "Fair" },
      3: { width: "75%", color: "bg-blue-500", label: "Good" },
      4: { width: "100%", color: "bg-green-500", label: "Strong" },
    };
    const { width, color, label } = strengthMap[strength];
    strengthBar.className = `h-full transition-all duration-300 ease-in-out ${color}`;
    strengthBar.style.width = width;
    strengthText.textContent = label;
    strengthText.className = `text-xs mt-1 ${color.replace("bg-", "text-")}`;
  };

  function checkPasswordLength() {
    const password = passwordInput.value.trim();
    updatePasswordStrength(password);

    if (password.length < 8) {
      showError(passwordInput, "Password must be at least 8 characters.");
      return false;
    } else {
      clearError(passwordInput);
      return true;
    }
  }

  passwordInput.addEventListener("input", () => {
    checkPasswordLength();
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
      return false;
    } else {
      clearError(confirmInput);
      return true;
    }
  }

  function updateSubmitButton() {
    const password = passwordInput.value.trim();
    const confirm = confirmInput.value.trim();

    const passwordValid = password.length >= 8;
    const passwordsMatch = !confirm || password === confirm;
    const allValid = passwordValid && passwordsMatch;

    submitButton.disabled = !allValid;

    if (!allValid) {
      submitButton.classList.add(
        "cursor-not-allowed",
        "opacity-60",
        "pointer-events-none",
        "bg-gray-300",
        "text-gray-500"
      );
      submitButton.classList.remove(
        "bg-black",
        "text-white",
        "hover:bg-gray-800"
      );
    } else {
      submitButton.classList.remove(
        "cursor-not-allowed",
        "opacity-60",
        "pointer-events-none",
        "bg-gray-300",
        "text-gray-500"
      );
      submitButton.classList.add("bg-black", "text-white", "hover:bg-gray-800");
    }
  }

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const valid = checkPasswordMatch() && checkPasswordLength();
    if (valid) {
      form.submit();
    }
  });
});

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("login-form");
  const emailInput = form.querySelector("input[name='email']");
  const passwordInput = form.querySelector("input[name='password']");
  const loginButton = document.getElementById("login-btn");

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
      loginButton.classList.remove(
        "cursor-not-allowed",
        "opacity-60",
        "pointer-events-none",
        "bg-gray-300",
        "text-gray-500"
      );
      loginButton.classList.add("bg-black", "text-white", "hover:bg-gray-800");
    } else {
      loginButton.classList.add(
        "cursor-not-allowed",
        "opacity-60",
        "pointer-events-none",
        "bg-gray-300",
        "text-gray-500"
      );
      loginButton.classList.remove(
        "bg-black",
        "text-white",
        "hover:bg-gray-800"
      );
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
    if (valid) {
      form.submit();
    }
  });
});

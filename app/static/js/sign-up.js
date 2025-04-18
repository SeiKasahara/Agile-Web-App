document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("sign-up-form");
  const emailInput = form.querySelector("input[name='email']");
  const passwordInput = form.querySelector("input[name='password']");
  const confirmInput = form.querySelector("input[name='confirm_password']");
  const signUpButton = document.getElementById("sign-up-btn");
  const agreeCheckbox = document.getElementById("agree");

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
        translateX: [-6, 6, -4, 4, -2, 2, 0],
        duration: 400,
        easing: "easeInOutSine",
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

  function updateSubmitButton() {
    const hasError = form.querySelectorAll(".error-message").length > 0;
    const agreed = agreeCheckbox.checked;
    signUpButton.disabled = hasError;

    if (hasError || !agreed) {
      signUpButton.classList.add(
        "cursor-not-allowed",
        "opacity-60",
        "pointer-events-none",
        "bg-gray-300",
        "text-gray-500"
      );
      signUpButton.classList.remove(
        "bg-black",
        "text-white",
        "hover:bg-gray-800"
      );
    } else {
      signUpButton.classList.remove(
        "cursor-not-allowed",
        "opacity-60",
        "pointer-events-none",
        "bg-gray-300",
        "text-gray-500"
      );
      signUpButton.classList.add("bg-black", "text-white", "hover:bg-gray-800");
    }
  }

  agreeCheckbox.addEventListener("change", updateSubmitButton);

  form.addEventListener("submit", (e) => {
    e.preventDefault();

    if (!form.querySelector(".error-message")) {
      form.submit();
    }
  });
});

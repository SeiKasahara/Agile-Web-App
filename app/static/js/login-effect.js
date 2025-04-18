document.addEventListener("DOMContentLoaded", () => {
  anime({
    targets: "#login-card",
    translateX: [-50, 0],
    opacity: [0, 1],
    duration: 600,
    easing: "easeOutExpo",
    delay: 100,
  });

  anime({
    targets: "#signup-cta",
    translateX: [50, 0],
    opacity: [0, 1],
    duration: 600,
    easing: "easeOutExpo",
    delay: 200,
  });

  anime({
    targets: "#bottom-brand",
    translateY: [20, 0],
    opacity: [0, 1],
    duration: 800,
    easing: "easeOutQuad",
    delay: 500,
  });
});

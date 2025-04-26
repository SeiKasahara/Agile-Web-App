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

const btn = document.querySelector(".animated-button");
if (btn) {
  btn.addEventListener("mouseenter", () => {
    anime({
      targets: btn,
      scale: 1.02,
      boxShadow: "0 0 8px rgba(0,0,0,0.2)",
      duration: 200,
      easing: "easeOutCubic",
    });
  });

  btn.addEventListener("mouseleave", () => {
    anime({
      targets: btn,
      scale: 1,
      boxShadow: "0 0 0 rgba(0,0,0,0)",
      duration: 200,
      easing: "easeOutCubic",
    });
  });
}

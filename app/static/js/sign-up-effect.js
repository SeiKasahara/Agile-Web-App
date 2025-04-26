document.addEventListener("DOMContentLoaded", () => {
  anime({
    targets: "#signup-form",
    translateX: [100, 0],
    opacity: [0, 1],
    duration: 1000,
    easing: "easeOutExpo",
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

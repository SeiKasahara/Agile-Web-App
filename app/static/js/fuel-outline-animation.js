document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("fuel-icon-container");

  fetch("/static/assets/fuel-icon.svg")
    .then((response) => response.text())
    .then((svgText) => {
      container.innerHTML = svgText;
      const fuelPath = container.querySelector("path");

      if (fuelPath) {
        const pathLength = fuelPath.getTotalLength();
        fuelPath.style.strokeDasharray = pathLength;
        fuelPath.style.strokeDashoffset = pathLength;

        anime({
          targets: fuelPath,
          strokeDashoffset: [pathLength, 0],
          easing: "easeInOutSine",
          duration: 2000,
          delay: 500,
        });
      }
    })
    .catch((error) => {
      console.error("Failed to load SVG:", error);
    });
});

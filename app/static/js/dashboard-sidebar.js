document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.getElementById("sidebar");
  const menuToggle = document.getElementById("menu-toggle");
  const overlay = document.getElementById("overlay");

  function openSidebar() {
    sidebar.classList.remove("-translate-x-full");
    sidebar.classList.add("translate-x-0");
    overlay.classList.remove("hidden");
  }

  function closeSidebar() {
    sidebar.classList.remove("translate-x-0");
    sidebar.classList.add("-translate-x-full");
    overlay.classList.add("hidden");
  }

  menuToggle.addEventListener("click", () => {
    if (sidebar.classList.contains("-translate-x-full")) {
      openSidebar();
    } else {
      closeSidebar();
    }
  });

  overlay.addEventListener("click", () => {
    closeSidebar();
  });
});

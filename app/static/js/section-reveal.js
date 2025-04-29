// eslint-disable-next-line no-unused-vars
gsap.registerPlugin(ScrollTrigger);

// eslint-disable-next-line no-unused-vars
gsap.to("#main-content", {
  scrollTrigger: {
    trigger: "#hero",
    start: "bottom top",
    toggleActions: "play none none reverse",
  },
  opacity: 1,
  duration: 1,
  ease: "power2.out",
});

// Animate section titles

// eslint-disable-next-line no-unused-vars
gsap.utils.toArray(".section-title").forEach((title) => {
  gsap.to(title, {
    opacity: 1,
    y: -20,
    duration: 1,
    ease: "power2.out",
    scrollTrigger: {
      trigger: title,
      start: "top 80%",
      toggleActions: "play none none reverse",
    },
  });
});

// Animate feature cards

// eslint-disable-next-line no-unused-vars
gsap.utils.toArray(".feature-card").forEach((card) => {
  gsap.to(card, {
    opacity: 1,
    y: -30,
    duration: 0.8,
    ease: "power2.out",
    scrollTrigger: {
      trigger: card,
      start: "top 85%",
      toggleActions: "play none none reverse",
    },
  });
});

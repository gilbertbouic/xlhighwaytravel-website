/**
 * XL Highway Travel — site interactions
 */
(function () {
  "use strict";

  const header = document.querySelector(".site-header");
  const toggle = document.querySelector(".nav-toggle");
  const nav = document.querySelector(".nav");

  // Sticky header shadow
  if (header) {
    const onScroll = () => {
      header.classList.toggle("is-scrolled", window.scrollY > 12);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  // Mobile nav
  if (toggle && nav) {
    toggle.addEventListener("click", () => {
      const open = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!open));
      nav.classList.toggle("is-open", !open);
      document.body.style.overflow = open ? "" : "hidden";
    });

    // Close on escape
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && nav.classList.contains("is-open")) {
        toggle.setAttribute("aria-expanded", "false");
        nav.classList.remove("is-open");
        document.body.style.overflow = "";
      }
    });

    // Close after link click (mobile)
    nav.querySelectorAll("a").forEach((a) => {
      a.addEventListener("click", () => {
        if (window.matchMedia("(max-width: 960px)").matches) {
          toggle.setAttribute("aria-expanded", "false");
          nav.classList.remove("is-open");
          document.body.style.overflow = "";
        }
      });
    });

    // Mobile dropdown parents
    nav.querySelectorAll(".nav-item > a").forEach((link) => {
      link.addEventListener("click", (e) => {
        if (!window.matchMedia("(max-width: 960px)").matches) return;
        const item = link.parentElement;
        if (item.querySelector(".dropdown")) {
          e.preventDefault();
          item.classList.toggle("is-open");
        }
      });
    });
  }

  // Reveal on scroll
  const reveals = document.querySelectorAll(".reveal");
  if (reveals.length && "IntersectionObserver" in window) {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
    );
    reveals.forEach((el) => io.observe(el));
  } else {
    reveals.forEach((el) => el.classList.add("is-visible"));
  }

  // Contact form → mailto (static GitHub hosting)
  const form = document.getElementById("quote-form");
  if (form) {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const data = new FormData(form);
      const name = (data.get("name") || "").toString().trim();
      const email = (data.get("email") || "").toString().trim();
      const phone = (data.get("phone") || "").toString().trim();
      const interest = (data.get("interest") || "").toString().trim();
      const dates = (data.get("dates") || "").toString().trim();
      const message = (data.get("message") || "").toString().trim();

      if (!name || !email || !message) {
        alert("Please fill in your name, email and message.");
        return;
      }

      const body = [
        `Name: ${name}`,
        `Email: ${email}`,
        `Phone: ${phone}`,
        `Interest: ${interest}`,
        `Travel dates: ${dates}`,
        "",
        message,
      ].join("\n");

      const subject = encodeURIComponent(
        `Travel enquiry from ${name}${interest ? " — " + interest : ""}`
      );
      const mailto = `mailto:bookings@xlhighwaytravel.co.za?subject=${subject}&body=${encodeURIComponent(body)}`;
      window.location.href = mailto;

      const note = document.getElementById("form-success");
      if (note) {
        note.hidden = false;
        note.focus();
      }
    });
  }

  // Current year in footer
  document.querySelectorAll("[data-year]").forEach((el) => {
    el.textContent = String(new Date().getFullYear());
  });
})();

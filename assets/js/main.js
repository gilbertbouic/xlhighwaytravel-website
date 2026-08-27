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

  // Contact / specials forms → mailto (static GitHub hosting)
  window.xlSubmitQuoteForm = function (form, successEl) {
    const data = new FormData(form);
    const name = (data.get("name") || "").toString().trim();
    const email = (data.get("email") || "").toString().trim();
    const phone = (data.get("phone") || "").toString().trim();
    const interest = (data.get("interest") || "").toString().trim();
    const dates = (data.get("dates") || "").toString().trim();
    const message = (data.get("message") || "").toString().trim();

    if (!name || !email || !message) {
      alert("Please fill in your name, email and message.");
      return false;
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
    window.location.href = `mailto:bookings@xlhighwaytravel.co.za?subject=${subject}&body=${encodeURIComponent(body)}`;

    if (successEl) {
      successEl.hidden = false;
      successEl.focus();
    }
    return true;
  };

  const form = document.getElementById("quote-form");
  if (form) {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      window.xlSubmitQuoteForm(form, document.getElementById("form-success"));
    });
  }

  // Client stories — horizontal scroller (arrows + slow auto-scroll)
  document.querySelectorAll(".testimonials-scroller").forEach((scroller) => {
    const viewport = scroller.querySelector(".testimonials-viewport");
    const track = scroller.querySelector(".testimonials");
    const prev = scroller.querySelector(".testimonials-nav--prev");
    const next = scroller.querySelector(".testimonials-nav--next");
    if (!viewport || !track) return;

    const originals = Array.from(track.children);
    originals.forEach((card) => {
      const clone = card.cloneNode(true);
      clone.setAttribute("aria-hidden", "true");
      clone.querySelectorAll("[aria-label]").forEach((el) => el.removeAttribute("aria-label"));
      track.appendChild(clone);
    });

    const gap = () => parseFloat(getComputedStyle(track).columnGap || getComputedStyle(track).gap) || 18;
    const cardStep = () => {
      const card = track.querySelector(".quote-card");
      return card ? card.getBoundingClientRect().width + gap() : viewport.clientWidth * 0.85;
    };
    const loopWidth = () =>
      originals.reduce((sum, el) => sum + el.getBoundingClientRect().width, 0) + gap() * originals.length;

    const reduced = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    let paused = false;
    let resumeTimer = 0;
    const pause = () => {
      paused = true;
      window.clearTimeout(resumeTimer);
    };
    const resumeSoon = () => {
      window.clearTimeout(resumeTimer);
      resumeTimer = window.setTimeout(() => { paused = false; }, 4000);
    };
    scroller.addEventListener("mouseenter", pause);
    scroller.addEventListener("mouseleave", () => { paused = false; });
    scroller.addEventListener("focusin", pause);
    scroller.addEventListener("focusout", resumeSoon);
    viewport.addEventListener("pointerdown", pause);
    viewport.addEventListener("pointerup", resumeSoon);
    viewport.addEventListener("wheel", pause, { passive: true });

    const wrap = () => {
      const w = loopWidth();
      if (w < 20) return;
      if (viewport.scrollLeft >= w) viewport.scrollLeft -= w;
      else if (viewport.scrollLeft < 0) viewport.scrollLeft += w;
    };

    const go = (dir) => {
      const w = loopWidth();
      const step = cardStep();
      if (dir < 0 && viewport.scrollLeft < 8) viewport.scrollLeft += w;
      if (dir > 0 && viewport.scrollLeft >= w - 8) viewport.scrollLeft -= w;
      viewport.scrollBy({ left: dir * step, behavior: reduced() ? "auto" : "smooth" });
    };
    prev && prev.addEventListener("click", () => go(-1));
    next && next.addEventListener("click", () => go(1));
    viewport.addEventListener("scroll", wrap, { passive: true });

    const tick = () => {
      if (!paused && !reduced()) {
        viewport.scrollLeft += 0.4;
        wrap();
      }
      requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  });

  document.querySelectorAll("[data-year]").forEach((el) => {
    el.textContent = String(new Date().getFullYear());
  });
})();

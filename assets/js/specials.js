/**
 * HQ campaign flyers on /specials.html — images + details + our form only.
 */
(function () {
  "use strict";

  const DATA_URL = "assets/data/specials.json";
  const WA = "27828261451";
  const section = document.getElementById("hq-flyers");
  if (!section) return;

  const grid = section.querySelector("[data-hq-grid]");
  const detail = section.querySelector("[data-hq-detail]");
  const emptyNote = section.querySelector("[data-hq-empty]");
  if (!grid || !detail) return;

  const lightbox = document.createElement("div");
  lightbox.className = "hq-lightbox";
  lightbox.hidden = true;
  lightbox.innerHTML =
    '<button type="button" class="hq-lightbox-close" aria-label="Close image">&times;</button>' +
    '<img alt="">';
  document.body.appendChild(lightbox);
  const lightboxImg = lightbox.querySelector("img");
  const lightboxClose = lightbox.querySelector(".hq-lightbox-close");

  function closeLightbox() {
    lightbox.hidden = true;
    document.body.style.overflow = "";
  }

  function openLightbox(src, alt) {
    lightboxImg.src = src;
    lightboxImg.alt = alt || "";
    lightbox.hidden = false;
    document.body.style.overflow = "hidden";
    lightboxClose.focus();
  }

  lightbox.addEventListener("click", (e) => {
    if (e.target === lightbox || e.target === lightboxClose) closeLightbox();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !lightbox.hidden) closeLightbox();
  });

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function waUrl(title) {
    const text = `Hi — please quote this special: ${title} (dates and travellers to follow)`;
    return `https://wa.me/${WA}?text=${encodeURIComponent(text)}`;
  }

  function renderGrid(campaigns) {
    grid.replaceChildren();
    campaigns.forEach((c) => {
      const cover = (c.images && c.images[0]) || "";
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "hq-card";
      btn.dataset.id = String(c.id);
      btn.setAttribute("aria-expanded", "false");
      btn.setAttribute("aria-controls", "hq-detail-panel");
      btn.innerHTML =
        `<span class="hq-card-media">${
          cover
            ? `<img src="${escapeHtml(cover)}" alt="${escapeHtml(c.title)}" width="800" height="800" loading="lazy">`
            : ""
        }</span>` +
        `<span class="hq-card-body">` +
        `<span class="hq-card-title">${escapeHtml(c.title)}</span>` +
        (c.ends_label
          ? `<span class="hq-card-end">Valid until ${escapeHtml(c.ends_label)}</span>`
          : `<span class="hq-card-end">While stocks last</span>`) +
        `</span>`;
      btn.addEventListener("click", () => selectCampaign(c, true));
      grid.appendChild(btn);
    });
  }

  function setExpanded(id) {
    grid.querySelectorAll(".hq-card").forEach((card) => {
      const on = card.dataset.id === String(id);
      card.classList.toggle("is-active", on);
      card.setAttribute("aria-expanded", on ? "true" : "false");
    });
  }

  function selectCampaign(c, updateHash) {
    if (detail.dataset.activeId === String(c.id) && !detail.hidden) {
      detail.hidden = true;
      detail.dataset.activeId = "";
      setExpanded("");
      if (updateHash) history.replaceState(null, "", "specials.html#hq-flyers");
      return;
    }

    const images = Array.isArray(c.images) ? c.images : [];
    const gallery = images
      .map((src, i) => {
        const alt = `${c.title} — flyer ${i + 1}`;
        return `<button type="button" class="hq-gallery-item" data-src="${escapeHtml(src)}" data-alt="${escapeHtml(alt)}">` +
          `<img src="${escapeHtml(src)}" alt="${escapeHtml(alt)}" width="900" height="900" loading="lazy">` +
          `</button>`;
      })
      .join("");

    const desc = (c.description_html || "").trim();
    const interest = c.title;
    const uid = `hq-${c.id}`;

    detail.hidden = false;
    detail.dataset.activeId = String(c.id);
    detail.innerHTML =
      `<div class="hq-detail-inner" id="campaign-${escapeHtml(c.id)}">` +
      `<div class="hq-detail-copy">` +
      `<span class="section-kicker">Book through XL Highway Travel</span>` +
      `<h3>${escapeHtml(c.title)}</h3>` +
      (c.ends_label
        ? `<p class="hq-detail-end">Valid until ${escapeHtml(c.ends_label)}</p>`
        : "") +
      (desc ? `<div class="hq-detail-desc">${desc}</div>` : "") +
      `<p class="hq-detail-note">Tap a flyer for a larger view. Tell us your dates and we will quote this campaign from South Africa — you stay with XL Highway Travel.</p>` +
      `</div>` +
      `<div class="hq-gallery" aria-label="${escapeHtml(c.title)} flyers">${gallery}</div>` +
      `<form class="form hq-form" id="${uid}-form" novalidate>` +
      `<h4>Enquire about this special</h4>` +
      `<input type="hidden" name="interest" value="${escapeHtml(interest)}">` +
      `<div class="form-row">` +
      `<div class="field"><label for="${uid}-name">Full name *</label>` +
      `<input id="${uid}-name" name="name" type="text" autocomplete="name" required></div>` +
      `<div class="field"><label for="${uid}-email">Email *</label>` +
      `<input id="${uid}-email" name="email" type="email" autocomplete="email" required></div>` +
      `</div>` +
      `<div class="form-row">` +
      `<div class="field"><label for="${uid}-phone">Phone / WhatsApp</label>` +
      `<input id="${uid}-phone" name="phone" type="tel" autocomplete="tel"></div>` +
      `<div class="field"><label for="${uid}-dates">Travel dates (approx.)</label>` +
      `<input id="${uid}-dates" name="dates" type="text" placeholder="e.g. 12–22 September 2026"></div>` +
      `</div>` +
      `<div class="field"><label for="${uid}-message">Message *</label>` +
      `<textarea id="${uid}-message" name="message" required placeholder="Travellers, must-haves, questions…">Please quote: ${escapeHtml(interest)}</textarea></div>` +
      `<div class="btn-row hq-form-actions">` +
      `<button class="btn btn-primary" type="submit">Send enquiry</button>` +
      `<a class="btn btn-whatsapp" href="${waUrl(c.title)}" rel="noopener">WhatsApp</a>` +
      `<a class="btn btn-outline" href="tel:+27317655845">Call</a>` +
      `</div>` +
      `<p class="form-note hq-form-success" hidden tabindex="-1">Your email app should open to bookings@xlhighwaytravel.co.za. If it doesn’t, write to us with this campaign name.</p>` +
      `</form>` +
      `</div>`;

    setExpanded(c.id);

    detail.querySelectorAll("a[href]").forEach((a) => {
      const href = (a.getAttribute("href") || "").toLowerCase();
      if (href.includes("xltravel") || href.includes("travelfind") || href.startsWith("http")) {
        a.replaceWith(...a.childNodes);
      }
    });

    detail.querySelectorAll(".hq-gallery-item").forEach((btn) => {
      btn.addEventListener("click", () => openLightbox(btn.dataset.src, btn.dataset.alt));
    });

    const form = detail.querySelector("form");
    const note = detail.querySelector(".hq-form-success");
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      if (typeof window.xlSubmitQuoteForm === "function") {
        window.xlSubmitQuoteForm(form, note);
      }
    });

    if (updateHash) {
      history.replaceState(null, "", `specials.html#campaign-${c.id}`);
    }
    detail.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function openFromHash(campaigns) {
    const hash = (location.hash || "").replace("#", "");
    if (!hash) return;
    const idMatch = hash.match(/^campaign-(\d+)$/);
    const found = idMatch
      ? campaigns.find((c) => String(c.id) === idMatch[1])
      : campaigns.find((c) => c.slug === hash);
    if (found) selectCampaign(found, false);
  }

  fetch(DATA_URL, { cache: "no-cache" })
    .then((res) => {
      if (!res.ok) throw new Error("specials.json missing");
      return res.json();
    })
    .then((data) => {
      const campaigns = Array.isArray(data.campaigns) ? data.campaigns.filter((c) => c && c.images && c.images.length) : [];
      if (!campaigns.length) {
        section.hidden = true;
        return;
      }
      if (emptyNote) emptyNote.hidden = true;
      renderGrid(campaigns);
      openFromHash(campaigns);
      window.addEventListener("hashchange", () => openFromHash(campaigns));
    })
    .catch(() => {
      section.hidden = true;
    });
})();

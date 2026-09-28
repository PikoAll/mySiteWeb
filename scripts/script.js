document.addEventListener("DOMContentLoaded", () => {
  console.log("DOM completamente caricato"); // Log iniziale per verifica

  const hamburger = document.getElementById("hamburger-menu");
  const navbar = document.getElementById("navbar");
  const overlay = document.getElementById("overlay");
  const scrollToTopButton = document.getElementById("scrollToTop");

  const header = document.getElementById("site-header");

  // Mobile menu. The hamburger is a <button>: Enter/Space already fire click.
  const setMenu = (open) => {
    if (open && header) {
      // the menu opens right under the header, whatever its current height
      navbar.style.setProperty(
        "--nav-top",
        Math.max(0, header.getBoundingClientRect().bottom) + "px",
      );
    }
    navbar.classList.toggle("active", open);
    overlay.classList.toggle("active", open);
    hamburger.setAttribute("aria-expanded", open ? "true" : "false");
    hamburger.setAttribute(
      "aria-label",
      open ? "Chiudi menu di navigazione" : "Apri menu di navigazione",
    );
  };

  hamburger.addEventListener("click", (event) => {
    event.stopPropagation();
    const open = !navbar.classList.contains("active");
    setMenu(open);
    if (open) history.replaceState({ menu: "opened" }, ""); // Modifica lo stato corrente
  });

  window.addEventListener("popstate", (event) => {
    if (event.state && event.state.menu === "opened") setMenu(false);
  });

  // Gestione click sull'overlay per chiudere il menu
  overlay.addEventListener("click", () => setMenu(false));

  // Gestione scroll per mostrare o nascondere il bottone "Torna su"
  window.addEventListener("scroll", () => {
    if (window.scrollY > 300) {
      scrollToTopButton.classList.add("show");
      console.log("EVENTO: Scorrimento, bottone 'Torna su' visibile");
    } else {
      scrollToTopButton.classList.remove("show");
      console.log("EVENTO: Scorrimento, bottone 'Torna su' nascosto");
    }
  });

  // Click sul bottone "Torna su"
  scrollToTopButton.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
    console.log("EVENTO: Click sul bottone 'Torna su'");
  });

  // Dropdown menus ("Servizi", "Dove lavoro", ...): handled by class, so any
  // number of <li class="dropdown"> works. The toggle is the <a> child, the
  // menu is the .dropdown-menu child. Open state = .active class on the menu
  // (never an inline style: it would disable the CSS :hover on desktop).
  const dropdowns = Array.from(document.querySelectorAll(".dropdown"))
    .map((root) => ({
      root,
      toggle: root.querySelector(":scope > a"),
      menu: root.querySelector(":scope > .dropdown-menu"),
    }))
    .filter((d) => d.toggle && d.menu);

  const setOpen = (d, open) => {
    d.menu.classList.toggle("active", open);
    d.toggle.setAttribute("aria-expanded", open ? "true" : "false");
  };
  const closeAll = (except) =>
    dropdowns.forEach((d) => d !== except && setOpen(d, false));

  dropdowns.forEach((d) => {
    d.toggle.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation(); // Evita conflitti con altri listener
      const open = !d.menu.classList.contains("active");
      closeAll(d);
      setOpen(d, open);
    });

    d.toggle.addEventListener("keydown", (event) => {
      if (event.key === " ") {
        event.preventDefault(); // evita lo scroll pagina sullo Spazio
        d.toggle.click();
      } else if (event.key === "ArrowDown") {
        event.preventDefault();
        closeAll(d);
        setOpen(d, true);
        const first = d.menu.querySelector("a");
        if (first) first.focus();
      }
    });

    // Tab fuori dalla tendina: si chiude. Solo da tastiera: un "focusout"
    // generico scatterebbe anche al tocco su un'altra voce, e nel menu mobile
    // (fisarmonica) la chiusura sposterebbe le voci prima che arrivi il click.
    d.root.addEventListener("keydown", (event) => {
      if (event.key !== "Tab") return;
      setTimeout(() => {
        if (!d.root.contains(document.activeElement)) setOpen(d, false);
      });
    });
  });

  // Esc chiude la tendina aperta e riporta il focus sul suo pulsante
  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    const open = dropdowns.find((d) => d.menu.classList.contains("active"));
    if (open) {
      setOpen(open, false);
      open.toggle.focus();
    } else if (navbar.classList.contains("active")) {
      setMenu(false);
      hamburger.focus();
    }
  });

  // Click al di fuori delle tendine: le chiude (e chiude il menu mobile)
  document.addEventListener("click", (event) => {
    if (dropdowns.some((d) => d.root.contains(event.target))) return;
    closeAll();
    if (navbar.classList.contains("active")) setMenu(false);
  });

  // Reset navbar e overlay all'avvio
  if (
    navbar.classList.contains("active") ||
    overlay.classList.contains("active")
  ) {
    navbar.classList.remove("active");
    overlay.classList.remove("active");
    console.log("INIZIALIZZAZIONE: Reset navbar e overlay all'avvio");
  }
});

// Reveal on scroll: only sections below the fold, only with JS (never the LCP).
(() => {
  if (
    !("IntersectionObserver" in window) ||
    window.matchMedia("(prefers-reduced-motion: reduce)").matches
  )
    return;
  const targets = Array.from(
    document.querySelectorAll("main > section:not(.intro)"),
  ).filter((el) => el.getBoundingClientRect().top > window.innerHeight);
  if (!targets.length) return;
  const io = new IntersectionObserver(
    (entries) =>
      entries.forEach((e) => {
        if (!e.isIntersecting) return;
        e.target.classList.add("is-visible");
        io.unobserve(e.target);
      }),
    // Root extended upwards: a section jumped over counts as seen.
    { rootMargin: "100000px 0px -8% 0px" },
  );
  targets.forEach((el) => {
    el.classList.add("reveal");
    io.observe(el);
  });
})();

// Page scene (scripts/fx/, declared with data-fx): lazy, fail-closed (else the
// static CSS background). Blog articles get the header strip from here, so
// the ones published by the weekly script get it too.
(() => {
  const intro = document.querySelector("main .intro-container");
  if (!document.querySelector("[data-fx]") && intro && /\/blog\//.test(location.pathname)) {
    const strip = document.createElement("div");
    strip.className = "fx-strip";
    strip.dataset.fx = "circuit";
    strip.dataset.fxMode = "strip";
    intro.prepend(strip);
  }
  const host = document.querySelector("[data-fx]");
  const scene = host && host.dataset.fx;
  let canvasOk = false;
  try {
    canvasOk = !!document.createElement("canvas").getContext("2d");
  } catch (e) {}
  if (
    !/^[a-z]+$/.test(scene || "") ||
    !canvasOk ||
    matchMedia("(prefers-reduced-motion: reduce)").matches ||
    !(navigator.hardwareConcurrency > 2) ||
    !("IntersectionObserver" in window && "ResizeObserver" in window)
  )
    return;
  // same ?v= as this file
  const base = document.querySelector('script[src*="scripts/script.js"]').src;
  const add = (name, next) => {
    const s = document.createElement("script");
    s.src = base.replace("script.js", "fx/" + name + ".js");
    s.onload = next;
    document.head.appendChild(s);
  };
  // fx.css before the canvas mounts
  const load = () => {
    const l = document.createElement("link");
    l.rel = "stylesheet";
    l.href = base.replace("scripts/script.js", "styles/fx.css");
    l.onload = () => add(scene, () => add("core"));
    document.head.appendChild(l);
  };
  const idle = () =>
    "requestIdleCallback" in window ? requestIdleCallback(load, { timeout: 3000 }) : setTimeout(load, 1500);
  if (document.readyState === "complete") idle();
  else addEventListener("load", idle, { once: true });
})();

// Mouse only: card spotlight and magnetic standalone CTAs.
(() => {
  if (!matchMedia("(hover: hover) and (pointer: fine)").matches) return;
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  let raf = 0;
  let ev = null;
  let pulled = null;
  const apply = () => {
    raf = 0;
    const t = ev.target instanceof Element ? ev.target : null;
    const card = t && t.closest(".card--link");
    if (card) {
      const r = card.getBoundingClientRect();
      card.style.setProperty("--mx", ev.clientX - r.left + "px");
      card.style.setProperty("--my", ev.clientY - r.top + "px");
    }
    const cta = t && t.closest(".intro-container > a.cta-link");
    if (pulled && pulled !== cta) pulled.style.transform = "";
    pulled = cta;
    if (cta) {
      const r = cta.getBoundingClientRect();
      const pull = (d, k) => Math.max(-6, Math.min(6, d * k)).toFixed(1) + "px";
      cta.style.transform = `translate(${pull(ev.clientX - r.left - r.width / 2, 0.15)}, ${pull(ev.clientY - r.top - r.height / 2, 0.3)})`;
    }
  };
  document.addEventListener(
    "pointermove",
    (e) => {
      ev = e;
      raf = raf || requestAnimationFrame(apply);
    },
    { passive: true },
  );
})();

// Sticky header: scroll progress --p (0..1) moves the wordmark into the strip
// left on screen (style.css, .brand). Transform only: no layout shift.
(() => {
  const header = document.getElementById("site-header");
  const band = header && header.querySelector(".brand-band");
  if (!band) return;
  let range = 0;
  let raf = 0;
  const measure = () => {
    const stuck = parseFloat(getComputedStyle(header).getPropertyValue("--band-stuck")) || 0;
    range = band.offsetHeight - stuck;
  };
  const update = () => {
    raf = 0;
    const p = range > 0 ? Math.min(1, Math.max(0, window.scrollY / range)) : 0;
    header.style.setProperty("--p", p.toFixed(3));
  };
  addEventListener("scroll", () => (raf = raf || requestAnimationFrame(update)), { passive: true });
  addEventListener("resize", () => (measure(), update()), { passive: true });
  measure();
  update();
})();

// Carousels (.carousel > .carousel-track): arrows added here, so without JS
// the track still scrolls (swipe, trackpad, keyboard). No autoplay.
(() => {
  document.querySelectorAll(".carousel").forEach((root, n) => {
    const track = root.querySelector(".carousel-track");
    if (!track) return;
    if (!track.id) track.id = "carousel-" + (n + 1);
    const sprite = (document.querySelector('script[src*="scripts/script.js"]').getAttribute("src").match(/^(?:\.\.\/)*/) || [""])[0] + "images/icons.svg";
    const button = (cls, label, icon) => {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "carousel-btn " + cls;
      b.setAttribute("aria-label", label);
      b.setAttribute("aria-controls", track.id);
      b.innerHTML = `<svg class="icon" aria-hidden="true"><use href="${sprite}#${icon}"/></svg>`;
      root.appendChild(b);
      return b;
    };
    const prev = button("prev", "Scorri indietro", "i-chevron-left");
    const next = button("next", "Scorri avanti", "i-chevron-right");
    const step = () => {
      const card = track.firstElementChild;
      const gap = parseFloat(getComputedStyle(track).columnGap) || 0;
      return card ? card.getBoundingClientRect().width + gap : track.clientWidth;
    };
    const go = (dir) => track.scrollBy({ left: dir * step(), behavior: "smooth" });
    prev.addEventListener("click", () => go(-1));
    next.addEventListener("click", () => go(1));
    track.addEventListener("keydown", (e) => {
      if (e.target !== track) return;
      if (e.key === "ArrowRight" || e.key === "ArrowLeft") {
        e.preventDefault();
        go(e.key === "ArrowRight" ? 1 : -1);
      }
    });
    let raf = 0;
    const sync = () => {
      raf = 0;
      const max = track.scrollWidth - track.clientWidth;
      root.classList.toggle("has-overflow", max > 2);
      prev.disabled = track.scrollLeft <= 2;
      next.disabled = track.scrollLeft >= max - 2;
    };
    track.addEventListener("scroll", () => (raf = raf || requestAnimationFrame(sync)), { passive: true });
    if ("ResizeObserver" in window) new ResizeObserver(sync).observe(track);
    sync();
  });
})();

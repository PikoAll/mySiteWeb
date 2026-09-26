document.addEventListener("DOMContentLoaded", () => {
  console.log("DOM completamente caricato"); // Log iniziale per verifica

  const hamburger = document.getElementById("hamburger-menu");
  const navbar = document.getElementById("navbar");
  const overlay = document.getElementById("overlay");
  const scrollToTopButton = document.getElementById("scrollToTop");

  // Gestione click sul pulsante hamburger
  hamburger.addEventListener("click", (event) => {
    event.stopPropagation();
    navbar.classList.toggle("active");
    overlay.classList.toggle("active");
    hamburger.setAttribute(
      "aria-expanded",
      navbar.classList.contains("active"),
    );
    console.log("EVENTO: Click sul pulsante hamburger");

    if (navbar.classList.contains("active")) {
      history.replaceState({ menu: "opened" }, ""); // Modifica lo stato corrente
      console.log("EVENTO: Stato aggiornato nella cronologia");
    }
  });

  // Gestione apertura/chiusura da tastiera (Invio/Spazio) sul div-bottone hamburger
  hamburger.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault(); // evita lo scroll pagina sullo Spazio
      hamburger.click();
      console.log("EVENTO: Tastiera sul pulsante hamburger");
    }
  });

  window.addEventListener("popstate", (event) => {
    if (event.state && event.state.menu === "opened") {
      console.log("EVENTO: popstate, chiudo menu");
      navbar.classList.remove("active");
      overlay.classList.remove("active");
      hamburger.setAttribute("aria-expanded", "false");
    } else {
      console.log("EVENTO: popstate, navigazione normale");
    }
  });

  // Gestione click sull'overlay per chiudere il menu
  overlay.addEventListener("click", () => {
    navbar.classList.remove("active");
    overlay.classList.remove("active");
    hamburger.setAttribute("aria-expanded", "false");
    console.log("EVENTO: Click sull'overlay");
  });

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
    }
  });

  // Click al di fuori delle tendine: le chiude (e chiude il menu mobile)
  document.addEventListener("click", (event) => {
    if (dropdowns.some((d) => d.root.contains(event.target))) return;
    closeAll();
    if (
      navbar.classList.contains("active") ||
      overlay.classList.contains("active")
    ) {
      console.log("EVENTO: Menu aperto, chiudo simulando clic sull'hamburger");
      hamburger.click();
    }
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

  /*DISPENSE FOTOPER PAGINA CREATIVE SERVICES*/
  const slide = document.querySelector(".carousel-slide");
  const images = document.querySelectorAll(".carousel-slide img");
  let currentIndex = 0;
  if (!slide || images.length === 0) return; // pagina senza carosello

  // Calcola la larghezza dell'immagine dinamicamente
  const updateWidth = () => images[0].clientWidth;

  // Funzione per scorrere automaticamente
  const autoScroll = () => {
    currentIndex++;
    if (currentIndex >= images.length) {
      currentIndex = 0; // Torna alla prima immagine
    }
    slide.style.transform = `translateX(${-updateWidth() * currentIndex}px)`;
  };

  // Scorrimento automatico ogni 3 secondi
  setInterval(autoScroll, 3000);

  // Aggiorna larghezza immagine su resize
  window.addEventListener("resize", () => {
    slide.style.transition = "none"; // Disabilita transizione durante il resize
    slide.style.transform = `translateX(${-updateWidth() * currentIndex}px)`;
    setTimeout(() => {
      slide.style.transition = "transform 0.5s ease-in-out"; // Riabilita la transizione
    });
  });

  /*FINE DISPENE FOTO PER PAGINA CREATIVE SERVICES*/
});

// Cookie consent for pikobit.it (Garante privacy, cookie guidelines of June 2021).
//
// Google Analytics 4 is NOT on the pages: this script loads gtag.js only after
// the visitor clicks "Accetta", so before the choice (and after "Rifiuta") the
// browser sends nothing to Google and no _ga cookie exists. Google Consent
// Mode v2 is set anyway (all four signals "denied" by default, only
// analytics_storage granted on "Accetta", ad_* never).
//
// The choice is a technical item in localStorage: {choice, version, ts}.
// The banner comes back when the policy VERSION changes or the choice is
// older than 6 months. Any element with data-cookie-prefs reopens it
// (footer "Preferenze cookie"); without JS that link opens privacy.html#cookie.
// Inserted on every page by scripts/site_chrome.py.
(function () {
  "use strict";

  var GA_ID = "G-TVGN1XBX7H";
  var VERSION = "2026-09-28"; // change it when the cookie policy changes
  var KEY = "pikobit-consent";
  var MAX_AGE_MS = 183 * 24 * 60 * 60 * 1000; // ~6 months
  var script = document.currentScript;
  var privacyUrl = new URL(
    "../privacy.html#cookie",
    script ? script.src : location.href,
  ).href;

  window.dataLayer = window.dataLayer || [];
  function gtag() {
    window.dataLayer.push(arguments);
  }
  gtag("consent", "default", {
    analytics_storage: "denied",
    ad_storage: "denied",
    ad_user_data: "denied",
    ad_personalization: "denied",
  });

  function read() {
    try {
      var saved = JSON.parse(localStorage.getItem(KEY));
      if (
        saved &&
        saved.version === VERSION &&
        Date.now() - saved.ts < MAX_AGE_MS &&
        (saved.choice === "granted" || saved.choice === "denied")
      ) {
        return saved;
      }
    } catch (e) {
      // no storage (private mode, blocked): ask again, never assume a yes
    }
    return null;
  }

  var memory = null; // the choice of this page view when storage fails

  function save(choice) {
    memory = { choice: choice, version: VERSION, ts: Date.now() };
    try {
      localStorage.setItem(KEY, JSON.stringify(memory));
    } catch (e) {
      // keep it for this page only
    }
  }

  var loaded = false;

  function startAnalytics() {
    window["ga-disable-" + GA_ID] = false;
    gtag("consent", "update", { analytics_storage: "granted" });
    if (loaded) return;
    loaded = true;
    gtag("js", new Date());
    gtag("config", GA_ID, {
      allow_google_signals: false,
      allow_ad_personalization_signals: false,
    });
    var s = document.createElement("script");
    s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + GA_ID;
    document.head.appendChild(s);
  }

  // _ga and _ga_<id> live on the widest domain GA could pick (.pikobit.it):
  // expire them on the host and on every parent domain.
  function deleteGaCookies() {
    var parts = location.hostname.split(".");
    var domains = [""];
    for (var i = 0; i < parts.length; i++) {
      domains.push("; domain=" + parts.slice(i).join("."));
      domains.push("; domain=." + parts.slice(i).join("."));
    }
    document.cookie.split(";").forEach(function (c) {
      var name = c.split("=")[0].trim();
      if (!/^_ga(_|$)/.test(name)) return;
      domains.forEach(function (d) {
        document.cookie =
          name + "=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/" + d;
      });
    });
  }

  function stopAnalytics() {
    window["ga-disable-" + GA_ID] = true;
    gtag("consent", "update", { analytics_storage: "denied" });
    deleteGaCookies();
  }

  var banner = null;
  var opener = null;

  function close() {
    if (!banner) return;
    banner.remove();
    banner = null;
    if (opener && document.contains(opener)) opener.focus();
    opener = null;
  }

  function decide(choice) {
    save(choice);
    if (choice === "granted") startAnalytics();
    else stopAnalytics();
    close();
  }

  function button(label, choice, cls) {
    var b = document.createElement("button");
    b.type = "button";
    b.className = cls;
    b.textContent = label;
    b.dataset.choice = choice;
    return b;
  }

  function open(from) {
    if (banner) {
      banner.focus();
      return;
    }
    banner = document.createElement("div");
    banner.className = "cookie-banner";
    banner.id = "cookie-banner";
    banner.setAttribute("role", "dialog");
    banner.setAttribute("aria-modal", "false");
    banner.setAttribute("aria-labelledby", "cookie-title");
    banner.setAttribute("aria-describedby", "cookie-text");
    banner.tabIndex = -1;

    var current = read() || memory;
    var state = current
      ? " Scelta attuale: statistiche " +
        (current.choice === "granted" ? "accettate." : "rifiutate.")
      : "";
    banner.innerHTML =
      '<p class="cookie-title" id="cookie-title">Cookie su questo sito</p>' +
      '<p class="cookie-text" id="cookie-text">Uso cookie tecnici, necessari al funzionamento del sito, ' +
      "e solo se accetti cookie di statistica di Google Analytics, per contare le visite in forma " +
      'aggregata. Puoi cambiare idea quando vuoi da "Preferenze cookie" in fondo alla pagina.' +
      state +
      ' <a href="' +
      privacyUrl +
      '">Informativa cookie</a></p>';

    var x = button("×", "denied", "cookie-close");
    x.setAttribute("aria-label", "Chiudi: rifiuta i cookie di statistica");
    banner.insertBefore(x, banner.firstChild);

    var actions = document.createElement("div");
    actions.className = "cookie-actions";
    actions.appendChild(button("Rifiuta", "denied", "cookie-btn"));
    actions.appendChild(button("Accetta", "granted", "cookie-btn"));
    banner.appendChild(actions);

    banner.addEventListener("click", function (e) {
      var b = e.target.closest("button[data-choice]");
      if (b) decide(b.dataset.choice);
    });
    banner.addEventListener("keydown", function (e) {
      if (e.key === "Escape") decide("denied"); // same as the X
    });

    // First in the tab order, shown at the bottom by CSS. Focus moves to it
    // only when the visitor asked for it (Preferenze cookie).
    document.body.insertBefore(banner, document.body.firstChild);
    if (from) {
      opener = from;
      banner.focus();
    }
  }

  document.addEventListener("click", function (e) {
    var link = e.target.closest("[data-cookie-prefs]");
    if (!link) return;
    e.preventDefault();
    open(link);
  });

  window.PikoConsent = { open: open, version: VERSION };

  var saved = read();
  if (saved && saved.choice === "granted") startAnalytics();
  else if (!saved) open(null);
})();

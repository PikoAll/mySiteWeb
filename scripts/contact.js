/*
 * contact.html: the site has no backend. The form checks the fields, then
 * "Invia su WhatsApp" opens wa.me and "Invia email" opens the mail app, both
 * with the message already written. Nothing is sent or stored by the site.
 */
(() => {
  "use strict";

  const PHONE = "393518891903";
  const EMAIL = "piko.bit.00@gmail.com";

  // Direct send with Web3Forms (https://web3forms.com), OFF. To turn it on:
  // put the access key here, set USE_WEB3FORMS = true, and add a sentence
  // about Web3Forms to privacy.html (the data would then pass through them).
  // const WEB3FORMS_KEY = "INSERISCI-QUI-LA-TUA-ACCESS-KEY";
  // const USE_WEB3FORMS = false;

  const form = document.getElementById("contact-form");
  if (!form) return;
  const status = document.getElementById("cf-status");
  const $ = (name) => form.elements[name];

  const value = (name) => ($(name).value || "").trim();

  // name -> check returning an error message, or "" when the field is fine
  const RULES = {
    nome: () => (value("nome").length < 2 ? "Scrivi il tuo nome." : ""),
    telefono: () => {
      const v = value("telefono");
      const digits = v.replace(/\D/g, "");
      return v &&
        (!/^[+\d\s().\/-]+$/.test(v) || digits.length < 6 || digits.length > 15)
        ? "Il numero di telefono non sembra valido (solo cifre, spazi e +)."
        : "";
    },
    email: () => {
      const v = value("email");
      return v && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v)
        ? "L'indirizzo email non sembra valido (esempio: nome@dominio.it)."
        : "";
    },
    messaggio: () =>
      value("messaggio").length < 10
        ? "Scrivi due righe sul tuo progetto (almeno 10 caratteri)."
        : "",
    privacy: () =>
      $("privacy").checked
        ? ""
        : "Per inviare devi accettare l'informativa privacy.",
  };

  const showError = (name, msg) => {
    const field = $(name);
    const box = document.getElementById("cf-" + name + "-err");
    field.setAttribute("aria-invalid", msg ? "true" : "false");
    if (box) box.textContent = msg;
  };

  const validate = () => {
    let first = null;
    for (const name in RULES) {
      const msg = RULES[name]();
      showError(name, msg);
      if (msg && !first) first = $(name);
    }
    return first;
  };

  // Plain text, one line per filled field, then the message.
  const compose = () => {
    const lines = ["Ciao Giuseppe, ti scrivo dal sito pikobit.it.", ""];
    const add = (label, name) =>
      value(name) && lines.push(label + ": " + value(name));
    add("Nome", "nome");
    add("Telefono", "telefono");
    add("Email", "email");
    add("Progetto", "tipo");
    add("Città", "citta");
    lines.push("", value("messaggio"));
    return lines.join("\n");
  };

  const subject = () =>
    "Richiesta dal sito" +
    (value("tipo") ? " - " + value("tipo") : "") +
    " - " +
    value("nome");

  const urls = {
    whatsapp: () =>
      "https://wa.me/" + PHONE + "?text=" + encodeURIComponent(compose()),
    email: () =>
      "mailto:" +
      EMAIL +
      "?subject=" +
      encodeURIComponent(subject()) +
      "&body=" +
      encodeURIComponent(compose()),
  };

  // Exposed so the e2e tests can catch the URL instead of leaving the page.
  const api = (window.PikoContact = {
    go(url, via) {
      if (via === "whatsapp") window.open(url, "_blank", "noopener");
      else window.location.href = url;
    },
  });

  // Errors clear as soon as the field is fixed.
  for (const name in RULES)
    $(name).addEventListener(name === "privacy" ? "change" : "input", () => {
      if ($(name).getAttribute("aria-invalid") === "true")
        showError(name, RULES[name]());
    });

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const via =
      event.submitter && event.submitter.value === "email"
        ? "email"
        : "whatsapp";
    const invalid = validate();
    if (invalid) {
      status.textContent = "Controlla i campi evidenziati.";
      invalid.focus();
      return;
    }
    // if (USE_WEB3FORMS) {
    //   const data = new FormData(form);
    //   data.append("access_key", WEB3FORMS_KEY);
    //   data.append("subject", subject());
    //   fetch("https://api.web3forms.com/submit", { method: "POST", body: data })
    //     .then((r) => r.json())
    //     .then((r) => (status.textContent = r.success ? "Messaggio inviato, grazie!" : "Invio non riuscito: usa WhatsApp o l'email."))
    //     .catch(() => (status.textContent = "Invio non riuscito: usa WhatsApp o l'email."));
    //   return;
    // }
    status.textContent =
      via === "whatsapp"
        ? "Apro WhatsApp con il messaggio pronto…"
        : "Apro la tua app di posta con il messaggio pronto…";
    api.go(urls[via](), via);
  });
})();

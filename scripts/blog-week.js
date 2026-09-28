/*
 * Blog (resources.html): show the articles of the last week, hide the older
 * ones behind "Mostra articoli precedenti". "Last week" = the 7 days ending
 * on the NEWEST article, not on today: a skipped Friday never empties the
 * page. The date comes from the card link (blog/YYYY-MM-DD-...), so the
 * weekly script keeps adding plain <div class="article-box"> cards anywhere
 * in the list and they are grouped right. Nothing is moved in the DOM; the
 * older cards only get [hidden], and only here: without JS all are visible.
 */
(function () {
  "use strict";

  var DAY = 86400000;
  var DATE_RE = /blog\/(\d{4})-(\d{2})-(\d{2})-/;

  // hrefs in page order -> array of booleans, true = recent (shown).
  // A card without a date in its link (old external links) counts as older;
  // if no card has a date, all are shown.
  function recentFlags(hrefs) {
    var times = hrefs.map(function (h) {
      var m = DATE_RE.exec(h || "");
      return m ? Date.UTC(+m[1], +m[2] - 1, +m[3]) : null;
    });
    var dated = times.filter(function (t) { return t !== null; });
    if (!dated.length) return hrefs.map(function () { return true; });
    var newest = Math.max.apply(null, dated);
    return times.map(function (t) { return t !== null && t > newest - 7 * DAY; });
  }

  if (typeof module === "object" && module.exports) module.exports = { recentFlags: recentFlags };
  if (typeof document === "undefined") return;

  function init() {
    var section = document.querySelector(".articles-section");
    if (!section) return;
    var cards = Array.prototype.slice.call(section.querySelectorAll(".article-box"));
    var flags = recentFlags(cards.map(function (c) {
      var a = c.querySelector("a[href]");
      return a ? a.getAttribute("href") : "";
    }));
    var older = cards.filter(function (c, i) { return !flags[i]; });
    if (!older.length) return;
    older.forEach(function (c) { c.hidden = true; });
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "show-older";
    btn.setAttribute("aria-expanded", "false");
    btn.textContent = "Mostra articoli precedenti (" + older.length + ")";
    btn.addEventListener("click", function () {
      older.forEach(function (c) { c.hidden = false; });
      btn.hidden = true;
      btn.setAttribute("aria-expanded", "true");
      var first = older[0].querySelector("a");
      if (first) first.focus();
    });
    section.insertAdjacentElement("afterend", btn);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();

/*
 * Pikobit FX engine: mounts the page scene (window.PikoFx[name], loaded first
 * by script.js) on [data-fx]. Owns canvas, DPR cap, resize, pause, 30 fps on
 * touch, pointer, tilt, dispose. Scene = (env) => ({ tilt, resize(), frame(dt, t) }).
 */
(() => {
  "use strict";

  const scenes = (window.PikoFx = window.PikoFx || {});
  const MAX_DPR = 1.5;
  const ACCENT = "0,191,255"; // --color-accent
  const ORANGE = "255,165,0"; // --color-cta

  const prng = (seed) => () => {
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };

  function layer(w, h, dpr) {
    const c = document.createElement("canvas");
    c.width = Math.max(1, Math.round(w * dpr));
    c.height = Math.max(1, Math.round(h * dpr));
    const g = c.getContext("2d");
    g.scale(dpr, dpr);
    return { c, g };
  }

  function glow(rgb, dpr) {
    const r = 14;
    const s = layer(r * 2, r * 2, dpr);
    const grad = s.g.createRadialGradient(r, r, 0, r, r, r);
    grad.addColorStop(0, `rgba(${rgb},.9)`);
    grad.addColorStop(0.25, `rgba(${rgb},.35)`);
    grad.addColorStop(1, `rgba(${rgb},0)`);
    s.g.fillStyle = grad;
    s.g.fillRect(0, 0, r * 2, r * 2);
    return s.c;
  }

  function mount(host) {
    const factory = scenes[host.dataset.fx];
    if (typeof factory !== "function") return null;
    const canvas = document.createElement("canvas");
    canvas.className = "fx-canvas";
    canvas.setAttribute("aria-hidden", "true");
    const ctx = canvas.getContext("2d");
    if (!ctx) return null;
    host.prepend(canvas);

    const dpr = Math.min(window.devicePixelRatio || 1, MAX_DPR);
    const touch = window.matchMedia("(pointer: coarse)").matches;
    const sprites = {};
    const env = {
      ctx,
      dpr,
      touch,
      w: 1,
      h: 1,
      mode: host.dataset.fxMode || "full",
      city: host.dataset.fxCity || "",
      // x/y: smoothed -1..1 (parallax); px/py: raw CSS px; on: mouse inside
      pointer: { x: 0, y: 0, tx: 0, ty: 0, px: -1e4, py: -1e4, on: false },
      rand: prng,
      layer: (w, h) => layer(w, h, dpr),
      a: (a) => `rgba(${ACCENT},${a})`,
      o: (a) => `rgba(${ORANGE},${a})`,
      glow: (orange) => {
        const k = orange ? "o" : "a";
        return sprites[k] || (sprites[k] = glow(orange ? ORANGE : ACCENT, dpr));
      },
      // Where the text is (measured on resize) and the free band above it,
      // beside the logo: scene objects go there, never behind the H1.
      text: [],
      band: { top: 0, bottom: 0 },
      slots() {
        const { w, h, band } = env;
        const bh = band.bottom - band.top;
        if (bh < 90) return [{ x: w / 2, y: h / 2, s: Math.min(w * 0.8, h * 0.6), dim: 0.45 }];
        const wide = w >= 820;
        const s = Math.min(bh * 0.92, w * (wide ? 0.2 : 0.24));
        const y = band.top + bh / 2;
        return [
          { x: w * (wide ? 0.2 : 0.15), y, s, dim: 1 },
          { x: w * (wide ? 0.8 : 0.85), y, s, dim: 1 },
        ];
      },
    };
    const scene = factory(env);
    const tilt = scene.tilt || 0;

    let raf = 0;
    let last = 0;
    let t = 0;
    let onScreen = true;
    const frameMs = touch ? 1000 / 30 : 0;
    const p = env.pointer;

    function resize() {
      const r = host.getBoundingClientRect();
      env.w = Math.max(1, Math.round(r.width));
      env.h = Math.max(1, Math.round(r.height));
      canvas.width = Math.round(env.w * dpr);
      canvas.height = Math.round(env.h * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      env.text = Array.from(host.querySelectorAll("h1,h2,h3,p,li,blockquote"))
        .flatMap((el) => Array.from(el.getClientRects()))
        .map((q) => [q.left - r.left - 8, q.top - r.top - 6, q.width + 16, q.height + 12]);
      env.band = { top: 12, bottom: Math.min(env.h, ...env.text.map((q) => q[1])) - 8 };
      scene.resize();
    }

    function frame(now) {
      raf = requestAnimationFrame(frame);
      if (frameMs && now - last < frameMs) return;
      const dt = Math.min(0.05, (now - (last || now)) / 1000);
      last = now;
      t += dt;
      if (touch) {
        // No gyroscope: slow automatic drift.
        p.tx = Math.sin(t * 0.25);
        p.ty = Math.sin(t * 0.18) * 0.6;
      }
      p.x += (p.tx - p.x) * 0.06;
      p.y += (p.ty - p.y) * 0.06;
      if (tilt)
        canvas.style.transform =
          `perspective(900px) rotateX(${(-p.y * tilt).toFixed(2)}deg) ` +
          `rotateY(${(p.x * tilt).toFixed(2)}deg) scale(1.08)`;
      ctx.clearRect(0, 0, env.w, env.h);
      scene.frame(dt, t);
      if (scene.textSafe) {
        // Safety net: whatever still falls behind a line of text fades out.
        ctx.globalCompositeOperation = "destination-out";
        ctx.fillStyle = "rgba(0,0,0,.85)";
        env.text.forEach((q) => ctx.fillRect(q[0], q[1], q[2], q[3]));
        ctx.globalCompositeOperation = "source-over";
      }
    }

    function start() {
      if (raf || document.hidden || !onScreen) return;
      last = 0;
      raf = requestAnimationFrame(frame);
    }
    function stop() {
      cancelAnimationFrame(raf);
      raf = 0;
    }

    const onMove = (e) => {
      const r = host.getBoundingClientRect();
      p.px = e.clientX - r.left;
      p.py = e.clientY - r.top;
      p.tx = (p.px / r.width) * 2 - 1;
      p.ty = (p.py / r.height) * 2 - 1;
      p.on = true;
    };
    const onLeave = () => {
      p.tx = p.ty = 0;
      p.px = p.py = -1e4;
      p.on = false;
    };
    const onVisibility = () => (document.hidden ? stop() : start());
    let timer = 0;
    const ro = new ResizeObserver(() => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        const r = host.getBoundingClientRect();
        if (Math.round(r.width) !== env.w || Math.round(r.height) !== env.h)
          resize();
      }, 150);
    });
    const io = new IntersectionObserver(([e]) => {
      onScreen = e.isIntersecting;
      onScreen ? start() : stop();
    });

    resize();
    if (!touch) {
      host.addEventListener("pointermove", onMove, { passive: true });
      host.addEventListener("pointerleave", onLeave, { passive: true });
    }
    document.addEventListener("visibilitychange", onVisibility);
    ro.observe(host);
    io.observe(host);
    start();
    requestAnimationFrame(() => host.classList.add("fx-on"));

    return function dispose() {
      stop();
      clearTimeout(timer);
      ro.disconnect();
      io.disconnect();
      host.removeEventListener("pointermove", onMove);
      host.removeEventListener("pointerleave", onLeave);
      document.removeEventListener("visibilitychange", onVisibility);
      host.classList.remove("fx-on");
      canvas.width = canvas.height = 0; // release the backing store now
      canvas.remove();
    };
  }

  let disposers = [];
  const mountAll = () => {
    disposers = Array.from(document.querySelectorAll("[data-fx]"))
      .map(mount)
      .filter(Boolean);
  };
  window.addEventListener("pagehide", () => {
    disposers.forEach((d) => d());
    disposers = [];
  });
  // Back/forward cache: the page comes back without a reload, remount.
  window.addEventListener(
    "pageshow",
    (e) => e.persisted && !disposers.length && mountAll(),
  );
  mountAll();
})();

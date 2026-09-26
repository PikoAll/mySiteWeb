/* Scene "puglia": dotted region (approximate hand-written outline), the 12
   cities, pulses from Monopoli; data-fx-city highlights one city. */
(window.PikoFx = window.PikoFx || {}).puglia = (env) => {
  // Clockwise from the Molise border: Gargano, Adriatic coast, Salento,
  // Ionian coast, then the inland border with Basilicata and Campania.
  const OUTLINE = [
    [15.13, 41.92],
    [15.35, 41.92],
    [15.88, 41.94],
    [16.02, 41.95],
    [16.18, 41.88],
    [16.05, 41.7],
    [15.92, 41.63],
    [16.15, 41.37],
    [16.42, 41.28],
    [16.6, 41.2],
    [16.87, 41.13],
    [17.09, 41.06],
    [17.3, 40.95],
    [17.58, 40.78],
    [17.95, 40.64],
    [18.3, 40.39],
    [18.49, 40.15],
    [18.36, 39.8],
    [17.99, 40.06],
    [17.89, 40.26],
    [17.4, 40.4],
    [17.24, 40.47],
    [16.87, 40.4],
    [16.75, 40.6],
    [16.42, 40.82],
    [16.09, 40.96],
    [15.85, 41.1],
    [15.46, 41.1],
    [15.25, 41.2],
    [15.16, 41.32],
    [15.05, 41.5],
    [15.1, 41.62],
    [15.2, 41.72],
  ];
  const CITIES = {
    monopoli: [17.3, 40.95],
    "polignano-a-mare": [17.22, 41.0],
    bari: [16.87, 41.12],
    brindisi: [17.94, 40.63],
    casamassima: [16.92, 40.95],
    "castellana-grotte": [17.17, 40.89],
    conversano: [17.11, 40.97],
    fasano: [17.36, 40.84],
    lecce: [18.17, 40.35],
    ostuni: [17.58, 40.73],
    putignano: [17.12, 40.85],
    taranto: [17.24, 40.47],
  };
  const K = Math.cos((41 * Math.PI) / 180); // equirectangular at 41°N
  const rnd = env.rand(Date.now() & 0xffff);
  const target = CITIES[env.city] ? env.city : "";
  let map = null;
  let pos = {};
  let pulses = [];
  let ring = {};

  const inside = (x, y, poly) => {
    let c = false;
    for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
      const [xi, yi] = poly[i];
      const [xj, yj] = poly[j];
      if (yi > y !== yj > y && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi)
        c = !c;
    }
    return c;
  };

  const spawn = () => {
    const others = Object.keys(CITIES).filter((c) => c !== "monopoli");
    const to =
      target && rnd() < 0.7
        ? target
        : others[Math.floor(rnd() * others.length)];
    return { to, f: 0, v: 0.35 + rnd() * 0.25 };
  };

  return {
    tilt: 4,
    resize() {
      const { w, h } = env;
      const lon = OUTLINE.map((p) => p[0]);
      const lat = OUTLINE.map((p) => p[1]);
      const minX = Math.min(...lon) * K;
      const maxY = Math.max(...lat);
      const mw = (Math.max(...lon) - Math.min(...lon)) * K;
      const mh = maxY - Math.min(...lat);
      const wide = w >= 820;
      // Wide: the map sits on the right, the text keeps the left and middle.
      const boxW = wide ? w * 0.34 : w * 0.95;
      const boxH = h * (wide ? 0.8 : 0.86);
      const s = Math.min(boxW / mw, boxH / mh);
      const ox = (wide ? w * 0.94 - mw * s : (w - mw * s) / 2) - minX * s;
      const oy = (h - mh * s) / 2 + maxY * s;
      const pr = ([lo, la]) => [ox + lo * K * s, oy - la * s];
      const poly = OUTLINE.map(pr);
      pos = {};
      for (const c in CITIES) pos[c] = pr(CITIES[c]);

      const L = env.layer(w, h);
      const g = L.g;
      const dim = wide ? 1 : 0.6;
      const step = Math.max(6, s * 0.06);
      const xs = poly.map((p) => p[0]);
      const ys = poly.map((p) => p[1]);
      g.fillStyle = env.a(0.26 * dim);
      for (let y = Math.min(...ys); y < Math.max(...ys); y += step)
        for (let x = Math.min(...xs); x < Math.max(...xs); x += step)
          if (inside(x, y, poly)) g.fillRect(x - 0.8, y - 0.8, 1.6, 1.6);
      g.fillStyle = env.a(0.65 * dim);
      for (let i = 0; i < poly.length; i++) {
        const [ax, ay] = poly[i];
        const [bx, by] = poly[(i + 1) % poly.length];
        const n = Math.ceil(Math.hypot(bx - ax, by - ay) / (step * 0.8));
        for (let k = 0; k < n; k++)
          g.fillRect(
            ax + ((bx - ax) * k) / n - 1,
            ay + ((by - ay) * k) / n - 1,
            2,
            2,
          );
      }
      map = L;
      pulses = Array.from({ length: 3 }, spawn);
      pulses.forEach((p) => (p.f = rnd()));
      ring = {};
    },
    frame(dt, t) {
      const { ctx, dpr, pointer: m } = env;
      const ox = -m.x * 8;
      const oy = -m.y * 6;
      ctx.save();
      ctx.translate(ox, oy);
      ctx.drawImage(map.c, 0, 0, map.c.width / dpr, map.c.height / dpr);
      ctx.globalCompositeOperation = "lighter";
      const sp = env.glow();
      const spo = env.glow(true);
      const [mx, my] = pos.monopoli;

      for (const p of pulses) {
        p.f += p.v * dt;
        const [tx, ty] = pos[p.to];
        const cx = (mx + tx) / 2;
        const cy = Math.min(my, ty) - Math.hypot(tx - mx, ty - my) * 0.35 - 10;
        const q = (f) => {
          const u = 1 - f;
          return [
            u * u * mx + 2 * u * f * cx + f * f * tx,
            u * u * my + 2 * u * f * cy + f * f * ty,
          ];
        };
        const hot = p.to === target;
        ctx.strokeStyle = hot ? env.o(0.45) : env.a(0.4);
        ctx.lineWidth = 1.4;
        ctx.beginPath();
        for (let i = 0; i <= 10; i++) {
          const [x, y] = q(
            Math.max(0, Math.min(1, p.f - 0.25 + (0.25 * i) / 10)),
          );
          i ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
        }
        ctx.stroke();
        const [hx, hy] = q(Math.min(1, p.f));
        ctx.drawImage(hot ? spo : sp, hx - 12, hy - 12, 24, 24);
        if (p.f >= 1) {
          ring[p.to] = 1;
          Object.assign(p, spawn());
        }
      }

      for (const c in pos) {
        const [x, y] = pos[c];
        const hot = c === target;
        const home = c === "monopoli";
        const breathe = 0.6 + 0.4 * Math.sin(t * 2 + x);
        ctx.drawImage(hot ? spo : sp, x - 10, y - 10, 20, 20);
        ctx.fillStyle = hot
          ? env.o(0.95)
          : env.a(home ? 0.95 : 0.6 * breathe + 0.3);
        ctx.beginPath();
        ctx.arc(x, y, hot || home ? 3.4 : 2.4, 0, 7);
        ctx.fill();
        const r = ring[c] || 0;
        if (hot || r > 0) {
          const k = hot ? (t * 0.8) % 1 : 1 - r;
          ctx.strokeStyle = hot ? env.o(0.7 * (1 - k)) : env.a(0.6 * r);
          ctx.lineWidth = 1.2;
          ctx.beginPath();
          ctx.arc(x, y, 4 + k * 16, 0, 7);
          ctx.stroke();
          if (r > 0) ring[c] = Math.max(0, r - dt * 1.5);
        }
      }
      ctx.restore();
    },
  };
};

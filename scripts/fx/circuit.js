/* Scene "circuit": PCB traces on two parallax layers + light pulses.
   Modes: full (home), lite (Monopoli), strip (blog header band). */
(window.PikoFx = window.PikoFx || {}).circuit = (env) => {
  const P = {
    full: { cell: 26, density: 1, pulses: 16, parallax: 14, tilt: 5, chips: 1 },
    lite: {
      cell: 30,
      density: 0.55,
      pulses: 7,
      parallax: 8,
      tilt: 3,
      chips: 1,
    },
    strip: {
      cell: 22,
      density: 0.7,
      pulses: 5,
      parallax: 6,
      tilt: 0,
      chips: 0,
    },
  }[env.mode] || {
    cell: 30,
    density: 0.55,
    pulses: 7,
    parallax: 8,
    tilt: 3,
    chips: 1,
  };
  const DIRS = [
    [1, 0],
    [0, 1],
    [-1, 0],
    [0, -1],
  ];
  const rnd = env.rand(Date.now() & 0xffff);
  let layers = [];
  let traces = [];
  let pulses = [];

  function buildTrace(rand, cols, rows, used) {
    let x = Math.floor(rand() * cols);
    let y = Math.floor(rand() * rows);
    if (used.has(x + "," + y)) return null;
    let d = Math.floor(rand() * 4);
    const cells = [[x, y]];
    used.add(x + "," + y);
    const len = 6 + Math.floor(rand() * 16);
    for (let i = 0, run = 0; i < len; i++, run++) {
      if (run > 2 && rand() < 0.28) {
        d = (d + (rand() < 0.5 ? 1 : 3)) % 4; // turn, never back
        run = 0;
      }
      const nx = x + DIRS[d][0];
      const ny = y + DIRS[d][1];
      if (
        nx < 0 ||
        ny < 0 ||
        nx >= cols ||
        ny >= rows ||
        used.has(nx + "," + ny)
      )
        break;
      x = nx;
      y = ny;
      used.add(x + "," + y);
      cells.push([x, y]);
    }
    return cells.length >= 5 ? cells : null;
  }

  // Grid cells -> pixel points, corners cut at 45° like real PCB routing.
  function toPoints(cells, cell) {
    const px = (c) => [cell / 2 + c[0] * cell, cell / 2 + c[1] * cell];
    const pts = [px(cells[0])];
    const k = cell * 0.45;
    for (let i = 1; i < cells.length - 1; i++) {
      const [a, b, c] = [cells[i - 1], cells[i], cells[i + 1]];
      if (b[0] - a[0] === c[0] - b[0] && b[1] - a[1] === c[1] - b[1]) continue;
      const [bx, by] = px(b);
      pts.push([bx - (b[0] - a[0]) * k, by - (b[1] - a[1]) * k]);
      pts.push([bx + (c[0] - b[0]) * k, by + (c[1] - b[1]) * k]);
    }
    pts.push(px(cells[cells.length - 1]));
    const lens = [0];
    for (let i = 1; i < pts.length; i++)
      lens.push(
        lens[i - 1] +
          Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]),
      );
    return { pts, lens, total: lens[lens.length - 1] };
  }

  function at(tr, s) {
    const { pts, lens } = tr;
    if (s <= 0) return pts[0];
    if (s >= tr.total) return pts[pts.length - 1];
    let i = 1;
    while (lens[i] < s) i++;
    const f = (s - lens[i - 1]) / (lens[i] - lens[i - 1]);
    return [
      pts[i - 1][0] + (pts[i][0] - pts[i - 1][0]) * f,
      pts[i - 1][1] + (pts[i][1] - pts[i - 1][1]) * f,
    ];
  }

  function chip(g, rand, x, y, cell, alpha) {
    const w = cell * (2 + Math.floor(rand() * 2));
    const h = cell * (1.5 + Math.floor(rand() * 2));
    g.fillStyle = "rgba(18,21,26,.9)";
    g.strokeStyle = env.a(alpha * 1.4);
    g.lineWidth = 1;
    g.fillRect(x, y, w, h);
    g.strokeRect(x + 0.5, y + 0.5, w - 1, h - 1);
    g.fillStyle = env.a(alpha * 1.6);
    for (let px = x + 6; px < x + w - 4; px += 7) {
      g.fillRect(px, y - 4, 3, 4);
      g.fillRect(px, y + h, 3, 4);
    }
  }

  const spawn = (p) => {
    p.tr = traces[Math.floor(rnd() * traces.length)];
    p.s = 0;
    p.v = 55 + rnd() * 90; // px/s
    p.tail = 40 + rnd() * 50;
    p.flash = 0;
    return p;
  };

  return {
    tilt: P.tilt,
    resize() {
      const rand = env.rand(0x9b1c); // same board on every visit
      const pad = P.parallax * 2; // layers bigger than the view, for parallax
      layers = [];
      traces = [];
      [
        { depth: 0.45, alpha: 0.09, width: 1, cell: P.cell * 0.8 },
        { depth: 1, alpha: 0.16, width: 1.6, cell: P.cell },
      ].forEach((spec, li) => {
        const lw = env.w + pad * 2;
        const lh = env.h + pad * 2;
        const L = env.layer(lw, lh);
        const g = L.g;
        const cols = Math.floor(lw / spec.cell);
        const rows = Math.floor(lh / spec.cell);
        const used = new Set();
        const want = Math.round(((cols * rows) / 14) * P.density);
        g.lineCap = g.lineJoin = "round";
        for (let tries = 0; tries < want * 4 && traces.length < 400; tries++) {
          const cells = buildTrace(rand, cols, rows, used);
          if (!cells) continue;
          const tr = toPoints(cells, spec.cell);
          g.strokeStyle = env.a(spec.alpha);
          g.lineWidth = spec.width;
          g.beginPath();
          tr.pts.forEach(([x, y], i) => (i ? g.lineTo(x, y) : g.moveTo(x, y)));
          g.stroke();
          g.fillStyle = env.a(spec.alpha * 1.5);
          [tr.pts[0], tr.pts[tr.pts.length - 1]].forEach(([x, y]) => {
            g.beginPath();
            g.arc(x, y, spec.width + 1.6, 0, 7);
            g.fill();
          });
          if (li) traces.push(tr);
        }
        if (li && P.chips) {
          const n = Math.max(1, Math.round((lw * lh) / 160000));
          for (let i = 0; i < n; i++)
            chip(
              g,
              rand,
              rand() * (lw - 120) + 20,
              rand() * (lh - 80) + 20,
              spec.cell,
              spec.alpha,
            );
        }
        layers.push({ c: L.c, depth: spec.depth, pad });
      });
      pulses = traces.length
        ? Array.from({ length: P.pulses }, () => spawn({}))
        : [];
      pulses.forEach((p) => (p.s = rnd() * p.tr.total)); // no synchronized start
    },
    frame(dt) {
      const { ctx, pointer: m, dpr } = env;
      let fx = 0;
      let fy = 0;
      for (const L of layers) {
        fx = -L.pad - m.x * P.parallax * L.depth;
        fy = -L.pad - m.y * P.parallax * L.depth;
        ctx.drawImage(L.c, fx, fy, L.c.width / dpr, L.c.height / dpr);
      }
      const sp = env.glow();
      ctx.save();
      ctx.translate(fx, fy); // pulses live on the front layer
      ctx.lineCap = "round";
      ctx.lineWidth = 2;
      ctx.globalCompositeOperation = "lighter";
      for (const p of pulses) {
        p.s += p.v * dt;
        if (p.s - p.tail > p.tr.total) {
          p.flash += dt;
          if (p.flash > 0.35) spawn(p);
          else {
            const [ex, ey] = p.tr.pts[p.tr.pts.length - 1];
            ctx.globalAlpha = 1 - p.flash / 0.35;
            ctx.drawImage(sp, ex - 20, ey - 20, 40, 40);
            ctx.globalAlpha = 1;
          }
          continue;
        }
        let prev = at(p.tr, p.s);
        for (let i = 1; i <= 6; i++) {
          const cur = at(p.tr, p.s - (p.tail * i) / 6);
          ctx.strokeStyle = env.a((0.85 * (1 - i / 6)).toFixed(3));
          ctx.beginPath();
          ctx.moveTo(prev[0], prev[1]);
          ctx.lineTo(cur[0], cur[1]);
          ctx.stroke();
          prev = cur;
        }
        if (p.s <= p.tr.total) {
          const [hx, hy] = at(p.tr, p.s);
          ctx.drawImage(sp, hx - 14, hy - 14, 28, 28);
        }
      }
      ctx.restore();
    },
  };
};

/* Scene "qr" (creative-services): business cards whose QR draws itself.
   Decorative pattern: it does not encode anything, on purpose. */
(window.PikoFx = window.PikoFx || {}).qr = (env) => {
  const rnd = env.rand(Date.now() & 0xffff);
  const N = 21; // modules per side, like a version-1 QR
  const CYCLE = 7;
  let cards = [];

  const finder = (i, j) => {
    for (const [fx, fy] of [[0, 0], [N - 7, 0], [0, N - 7]]) {
      const x = i - fx;
      const y = j - fy;
      if (x >= 0 && x < 7 && y >= 0 && y < 7)
        return x === 0 || y === 0 || x === 6 || y === 6 || (x > 1 && x < 5 && y > 1 && y < 5) ? 1 : -1;
      if (x >= -1 && x <= 7 && y >= -1 && y <= 7) return -1; // quiet ring
    }
    return 0;
  };
  const pattern = () => {
    const on = [];
    for (let j = 0; j < N; j++)
      for (let i = 0; i < N; i++) {
        const f = finder(i, j);
        if (f === 1 || (f === 0 && rnd() < 0.48)) on.push([i, j, f === 1 ? 0 : 0.15 + rnd() * 0.85]);
      }
    return on; // third value = when the module appears (finders first)
  };

  return {
    textSafe: true,
    tilt: 5,
    resize() {
      cards = env.slots().map((sl, i) => ({ ...sl, ph: i * 3, mods: pattern(), n: -1 }));
    },
    frame(dt, t) {
      const { ctx, pointer: m } = env;
      for (const c of cards) {
        const T = t + c.ph;
        const n = Math.floor(T / CYCLE);
        if (n !== c.n) {
          c.n = n;
          c.mods = pattern();
        }
        const k = (T % CYCLE) / CYCLE;
        const fade = k > 0.9 ? 1 - (k - 0.9) / 0.1 : 1;
        const a = c.dim * fade;
        const W = c.s * 1.1;
        const H = W * 0.58;
        const x = c.x - W / 2 - m.x * 6;
        const y = c.y - H / 2 - m.y * 5;
        ctx.lineWidth = 1.2;
        ctx.strokeStyle = env.a(0.45 * a);
        ctx.fillStyle = env.a(0.04 * a);
        ctx.beginPath();
        ctx.roundRect(x, y, W, H, 8);
        ctx.fill();
        ctx.stroke();
        ctx.fillStyle = env.a(0.35 * a);
        ctx.fillRect(x + 14, y + 16, W * 0.34, 6);
        ctx.fillRect(x + 14, y + 30, W * 0.24, 4);
        ctx.fillStyle = env.o(0.5 * a);
        ctx.fillRect(x + 14, y + H - 22, W * 0.2, 4);
        const q = H - 24;
        const cell = q / N;
        const qx = x + W - q - 12;
        const qy = y + 12;
        const draw = Math.min(1, k / 0.55); // modules appear in the first 55%
        ctx.fillStyle = env.a(0.38 * a);
        for (const [i, j, when] of c.mods)
          if (when <= draw) ctx.fillRect(qx + i * cell, qy + j * cell, cell * 0.9, cell * 0.9);
        if (draw < 1) {
          // scan line
          ctx.fillStyle = env.o(0.5 * a);
          ctx.fillRect(qx - 2, qy + q * draw, q + 4, 1.5);
        }
      }
    },
  };
};

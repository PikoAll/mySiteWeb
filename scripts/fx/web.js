/* Scene "web" (websites): browser wireframes building a page block by block. */
(window.PikoFx = window.PikoFx || {}).web = (env) => {
  const rnd = env.rand(Date.now() & 0xffff);
  const CYCLE = 6;
  let wins = [];

  // Page layout in 0..1 units of the content area; order = build order.
  const layout = () => {
    const img = rnd() < 0.5;
    const cols = 2 + Math.floor(rnd() * 2);
    const b = [[0, 0, 1, 0.1], img ? [0, 0.16, 0.48, 0.34] : [0.15, 0.16, 0.7, 0.08]];
    b.push(img ? [0.54, 0.18, 0.46, 0.06] : [0.25, 0.28, 0.5, 0.05]);
    b.push(img ? [0.54, 0.28, 0.36, 0.05] : [0.3, 0.37, 0.4, 0.05]);
    for (let i = 0; i < cols; i++) b.push([(i / cols) + 0.02, 0.58, 1 / cols - 0.04, 0.3]);
    b.push([img ? 0.54 : 0.4, img ? 0.4 : 0.46, 0.2, 0.07, 1]); // CTA, orange
    return b;
  };

  return {
    textSafe: true,
    tilt: 5,
    resize() {
      wins = env.slots().map((sl, i) => ({ ...sl, ph: i * 2.2, blocks: layout(), n: -1 }));
    },
    frame(dt, t) {
      const { ctx } = env;
      for (const wn of wins) {
        const T = t + wn.ph;
        const n = Math.floor(T / CYCLE);
        if (n !== wn.n) {
          wn.n = n;
          wn.blocks = layout();
        }
        const c = (T % CYCLE) / CYCLE;
        const fade = c > 0.9 ? 1 - (c - 0.9) / 0.1 : Math.min(1, c * 10);
        const W = wn.s;
        const H = wn.s * 0.72;
        const x = wn.x - W / 2 + env.pointer.x * -6;
        const y = wn.y - H / 2 + env.pointer.y * -5;
        const a = fade * wn.dim;
        ctx.lineWidth = 1.2;
        ctx.strokeStyle = env.a(0.45 * a);
        ctx.fillStyle = env.a(0.04 * a);
        ctx.beginPath();
        ctx.roundRect(x, y, W, H, 8);
        ctx.fill();
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(x, y + 18);
        ctx.lineTo(x + W, y + 18);
        ctx.stroke();
        ctx.fillStyle = env.a(0.5 * a);
        for (let i = 0; i < 3; i++) {
          ctx.beginPath();
          ctx.arc(x + 10 + i * 9, y + 9, 2.4, 0, 7);
          ctx.fill();
        }
        ctx.strokeRect(x + 42, y + 5, W * 0.5, 8);
        const cx = x + 12;
        const cy = y + 28;
        const cw = W - 24;
        const ch = H - 40;
        wn.blocks.forEach((b, i) => {
          // each block grows in during the first 60% of the cycle
          const k = Math.max(0, Math.min(1, (c / 0.6 - i / wn.blocks.length) * wn.blocks.length * 0.5));
          if (!k) return;
          const e = 1 - (1 - k) ** 3;
          ctx.strokeStyle = b[4] ? env.o(0.8 * a) : env.a(0.55 * a);
          ctx.fillStyle = b[4] ? env.o(0.18 * a) : env.a(0.08 * a);
          ctx.beginPath();
          ctx.roundRect(cx + b[0] * cw, cy + b[1] * ch, b[2] * cw * e, b[3] * ch, 3);
          ctx.fill();
          ctx.stroke();
        });
      }
    },
  };
};

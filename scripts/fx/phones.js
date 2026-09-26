/* Scene "phones" (modern-apps): floating phones with a scrolling app feed. */
(window.PikoFx = window.PikoFx || {}).phones = (env) => {
  const rnd = env.rand(Date.now() & 0xffff);
  let phones = [];

  return {
    textSafe: true,
    tilt: 5,
    resize() {
      phones = [];
      env.slots().forEach((sl, i) => {
        const n = env.w < 820 ? 1 : 2;
        for (let k = 0; k < n; k++)
          phones.push({
            x: sl.x + (k - (n - 1) / 2) * sl.s * 0.55,
            y: sl.y + (k ? sl.s * 0.08 : -sl.s * 0.04),
            s: sl.s * (k ? 0.78 : 0.9),
            dim: sl.dim * (k ? 0.7 : 1),
            v: 18 + rnd() * 16,
            off: rnd() * 100,
            ph: i * 2 + k,
            cards: Array.from({ length: 6 }, () => ({ h: 0.5 + rnd() * 0.6, o: rnd() < 0.2 })),
          });
      });
    },
    frame(dt, t) {
      const { ctx, pointer: m } = env;
      for (const p of phones) {
        const H = p.s;
        const W = H * 0.5;
        const x = p.x - W / 2 - m.x * 7;
        const y = p.y - H / 2 + Math.sin(t * 0.8 + p.ph) * 5 - m.y * 5;
        const a = p.dim;
        ctx.lineWidth = 1.4;
        ctx.strokeStyle = env.a(0.5 * a);
        ctx.fillStyle = "rgba(13,15,18,.7)";
        ctx.beginPath();
        ctx.roundRect(x, y, W, H, W * 0.14);
        ctx.fill();
        ctx.stroke();
        ctx.fillStyle = env.a(0.4 * a);
        ctx.fillRect(x + W * 0.38, y + 7, W * 0.24, 4);
        const sx = x + 7;
        const sy = y + 18;
        const sw = W - 14;
        const sh = H - 44;
        ctx.save();
        ctx.beginPath();
        ctx.rect(sx, sy, sw, sh);
        ctx.clip();
        const unit = sw * 0.62;
        const total = p.cards.reduce((s, c) => s + c.h * unit + 8, 0);
        p.off = (p.off + p.v * dt) % total;
        let cy = sy - p.off;
        for (let rep = 0; rep < 2; rep++)
          for (const c of p.cards) {
            const ch = c.h * unit;
            if (cy + ch > sy && cy < sy + sh) {
              ctx.fillStyle = env.a(0.07 * a);
              ctx.strokeStyle = c.o ? env.o(0.55 * a) : env.a(0.3 * a);
              ctx.lineWidth = 1;
              ctx.beginPath();
              ctx.roundRect(sx + 2, cy, sw - 4, ch, 5);
              ctx.fill();
              ctx.stroke();
              ctx.fillStyle = env.a(0.4 * a);
              ctx.beginPath();
              ctx.arc(sx + 12, cy + 11, 5, 0, 7);
              ctx.fill();
              ctx.fillRect(sx + 22, cy + 8, sw * 0.4, 3);
              ctx.fillRect(sx + 8, cy + ch - 10, sw * 0.6, 3);
            }
            cy += ch + 8;
          }
        ctx.restore();
        ctx.strokeStyle = env.a(0.3 * a);
        ctx.beginPath();
        ctx.moveTo(x + 7, y + H - 22);
        ctx.lineTo(x + W - 7, y + H - 22);
        ctx.stroke();
        for (let i = 0; i < 4; i++) {
          ctx.fillStyle = i === 1 ? env.o(0.6 * a) : env.a(0.4 * a);
          ctx.beginPath();
          ctx.arc(x + (W * (i + 0.5)) / 4, y + H - 11, 2.6, 0, 7);
          ctx.fill();
        }
      }
    },
  };
};

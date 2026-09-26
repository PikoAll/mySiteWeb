/* Scene "dashboard" (custom-software): live bars, line chart, scrolling rows. */
(window.PikoFx = window.PikoFx || {}).dashboard = (env) => {
  const rnd = env.rand(Date.now() & 0xffff);
  let panels = [];

  return {
    textSafe: true,
    tilt: 4,
    resize() {
      panels = env.slots().map((sl, i) => ({
        ...sl,
        kind: env.w < 820 ? 0 : i, // 0 = bars + line, 1 = table
        bars: Array.from({ length: 7 }, () => ({ v: rnd(), to: rnd() })),
        line: Array.from({ length: 30 }, () => 0.5),
        rows: Array.from({ length: 8 }, () => rnd()),
        off: 0,
        hot: -1,
        clock: 0,
      }));
    },
    frame(dt, t) {
      const { ctx, pointer: m } = env;
      for (const p of panels) {
        const W = p.s;
        const H = p.s * 0.78;
        const x = p.x - W / 2 - m.x * 6;
        const y = p.y - H / 2 - m.y * 5;
        const a = p.dim;
        p.clock += dt;
        ctx.lineWidth = 1.2;
        ctx.strokeStyle = env.a(0.4 * a);
        ctx.fillStyle = env.a(0.04 * a);
        ctx.beginPath();
        ctx.roundRect(x, y, W, H, 8);
        ctx.fill();
        ctx.stroke();
        ctx.fillStyle = env.a(0.35 * a);
        ctx.fillRect(x + 12, y + 12, W * 0.3, 6);
        if (p.kind === 0) {
          if (p.clock > 1.6) {
            p.clock = 0;
            p.bars.forEach((b) => (b.to = 0.15 + rnd() * 0.85));
          }
          const bw = (W - 24) / p.bars.length;
          const base = y + H * 0.58;
          p.bars.forEach((b, i) => {
            b.v += (b.to - b.v) * Math.min(1, dt * 4);
            const bh = b.v * H * 0.34;
            ctx.fillStyle = i === 4 ? env.o(0.55 * a) : env.a(0.35 * a);
            ctx.fillRect(x + 12 + i * bw + 3, base - bh, bw - 6, bh);
          });
          p.line.shift();
          p.line.push(Math.max(0.05, Math.min(0.95, p.line[p.line.length - 1] + (rnd() - 0.5) * 0.12)));
          ctx.strokeStyle = env.a(0.7 * a);
          ctx.beginPath();
          p.line.forEach((v, i) => {
            const lx = x + 12 + (i * (W - 24)) / (p.line.length - 1);
            const ly = y + H * 0.94 - v * H * 0.28;
            i ? ctx.lineTo(lx, ly) : ctx.moveTo(lx, ly);
          });
          ctx.stroke();
        } else {
          const rh = (H - 36) / 6;
          p.off += dt * 14;
          if (p.off >= rh) {
            p.off -= rh;
            p.rows.push(rnd());
            p.rows.shift();
            p.hot = 1;
          }
          p.hot = Math.max(0, p.hot - dt);
          ctx.save();
          ctx.beginPath();
          ctx.rect(x, y + 26, W, H - 30);
          ctx.clip();
          p.rows.forEach((r, i) => {
            const ry = y + 28 + i * rh - p.off;
            const fresh = i === p.rows.length - 2 && p.hot > 0;
            ctx.fillStyle = fresh ? env.o(0.25 * p.hot * a) : env.a(0.05 * a);
            ctx.fillRect(x + 8, ry, W - 16, rh - 4);
            ctx.fillStyle = env.a(0.35 * a);
            ctx.fillRect(x + 14, ry + rh / 2 - 4, W * 0.18, 4);
            ctx.fillRect(x + W * 0.4, ry + rh / 2 - 4, W * 0.3 * r, 4);
            ctx.fillStyle = r > 0.5 ? env.a(0.6 * a) : env.o(0.5 * a);
            ctx.beginPath();
            ctx.arc(x + W - 20, ry + rh / 2 - 2, 3, 0, 7);
            ctx.fill();
          });
          ctx.restore();
        }
      }
    },
  };
};

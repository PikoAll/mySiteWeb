/* Scene "neural": signals crossing a small network left to right; nodes
   fire when reached and glow near the mouse. */
(window.PikoFx = window.PikoFx || {}).neural = (env) => {
  const rnd = env.rand(Date.now() & 0xffff);
  let nodes = []; // [layer][i] = {x, y, heat}
  let sig = [];

  function fire(n, li) {
    n.heat = 1;
    const next = nodes[li + 1];
    if (!next) return;
    const k = rnd() < 0.55 ? 1 : 2;
    for (let j = 0; j < k && sig.length < 40; j++)
      sig.push({
        a: n,
        b: next[Math.floor(rnd() * next.length)],
        li: li + 1,
        f: 0,
        v: 0.9 + rnd() * 0.8,
        o: rnd() < 0.1,
      });
  }

  return {
    tilt: 3,
    resize() {
      const { w, h } = env;
      const narrow = w < 820;
      const counts = narrow ? [3, 5, 5, 3] : [4, 6, 6, 3];
      // Wide screens: two half-networks framing the text, joined in spirit.
      const x0 = narrow ? w * 0.08 : w * 0.04;
      const x1 = narrow ? w * 0.92 : w * 0.96;
      nodes = counts.map((n, li) => {
        const x = x0 + ((x1 - x0) * li) / (counts.length - 1);
        return Array.from({ length: n }, (_, i) => ({
          x: x + (rnd() - 0.5) * 18,
          y: h * 0.12 + (h * 0.76 * (i + 0.5)) / n + (rnd() - 0.5) * 14,
          heat: 0,
        }));
      });
      sig = [];
    },
    frame(dt) {
      const { ctx, pointer: m } = env;
      const ox = -m.x * 10;
      const oy = -m.y * 8;
      ctx.save();
      ctx.translate(ox, oy);
      ctx.lineWidth = 1;
      ctx.strokeStyle = env.a(0.08);
      ctx.beginPath();
      for (let li = 0; li < nodes.length - 1; li++)
        for (const a of nodes[li])
          for (const b of nodes[li + 1]) {
            ctx.moveTo(a.x, a.y);
            ctx.lineTo(b.x, b.y);
          }
      ctx.stroke();

      if (rnd() < dt * 1.6)
        fire(nodes[0][Math.floor(rnd() * nodes[0].length)], 0);

      const sp = env.glow();
      const spo = env.glow(true);
      ctx.globalCompositeOperation = "lighter";
      sig = sig.filter((s) => {
        s.f += s.v * dt;
        const f = Math.min(1, s.f);
        const x = s.a.x + (s.b.x - s.a.x) * f;
        const y = s.a.y + (s.b.y - s.a.y) * f;
        const tf = Math.max(0, f - 0.12);
        ctx.strokeStyle = s.o ? env.o(0.5) : env.a(0.5);
        ctx.lineWidth = 1.6;
        ctx.beginPath();
        ctx.moveTo(s.a.x + (s.b.x - s.a.x) * tf, s.a.y + (s.b.y - s.a.y) * tf);
        ctx.lineTo(x, y);
        ctx.stroke();
        ctx.drawImage(s.o ? spo : sp, x - 12, y - 12, 24, 24);
        if (s.f < 1) return true;
        if (rnd() < 0.8) fire(s.b, s.li);
        else s.b.heat = 1;
        return false;
      });

      for (const layer of nodes)
        for (const n of layer) {
          const d = Math.hypot(n.x + ox - m.px, n.y + oy - m.py);
          const near = m.on ? Math.max(0, 1 - d / 140) : 0;
          n.heat = Math.max(0, n.heat - dt * 1.4);
          const k = Math.max(n.heat, near);
          ctx.fillStyle = env.a(0.25 + 0.6 * k);
          ctx.beginPath();
          ctx.arc(n.x, n.y, 3 + 2.5 * k, 0, 7);
          ctx.fill();
          if (k > 0.05) {
            ctx.globalAlpha = k;
            ctx.drawImage(sp, n.x - 22, n.y - 22, 44, 44);
            ctx.globalAlpha = 1;
          }
        }
      ctx.restore();
    },
  };
};

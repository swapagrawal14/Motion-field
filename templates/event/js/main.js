/* Motion Field — event template. Every move checks reduced motion + fine pointer. */
(() => {
  const reduced = () => window.MotionPref?.reduced ?? matchMedia("(prefers-reduced-motion: reduce)").matches;
  const fine = matchMedia("(pointer: fine)").matches;

  /* ---- letter stagger ---- */
  const title = document.querySelector("[data-split]");
  if (title) {
    const label = title.textContent.trim();
    title.setAttribute("aria-label", label);
    title.textContent = "";
    let ci = 0;
    label.split(/\s+/).forEach((word, wi, arr) => {
      const w = document.createElement("span");
      w.className = "w"; w.setAttribute("aria-hidden", "true");
      [...word].forEach((ch) => {
        const s = document.createElement("span");
        s.className = "ch"; s.textContent = ch; s.style.setProperty("--i", ci++);
        w.appendChild(s);
      });
      title.appendChild(w);
      if (wi < arr.length - 1) title.appendChild(document.createTextNode(" "));
    });
  }

  /* ---- countdown ---- */
  const cells = { d: document.querySelector("[data-cd='d']"), h: document.querySelector("[data-cd='h']"), m: document.querySelector("[data-cd='m']") };
  const target = new Date("2027-02-14T18:00:00+05:30").getTime();
  const tick = () => {
    const diff = Math.max(0, target - Date.now());
    const d = Math.floor(diff / 86400000);
    const h = Math.floor(diff / 3600000) % 24;
    const m = Math.floor(diff / 60000) % 60;
    if (cells.d) cells.d.textContent = String(d).padStart(2, "0");
    if (cells.h) cells.h.textContent = String(h).padStart(2, "0");
    if (cells.m) cells.m.textContent = String(m).padStart(2, "0");
  };
  tick(); setInterval(tick, 30000);

  /* ---- nav scramble ---- */
  const GLYPHS = "!<>-_\\/[]{}—=+*^?#";
  document.querySelectorAll(".nav__links a, .nav__brand").forEach((el) => {
    if (reduced()) return;
    const text = el.textContent;
    const scramble = () => {
      const t0 = performance.now(), dur = 420;
      let raf = 0;
      const step = (now) => {
        const p = Math.min(1, (now - t0) / dur);
        const solved = Math.floor(p * text.length);
        let out = "";
        for (let i = 0; i < text.length; i++) out += text[i] === " " ? " " : i < solved ? text[i] : GLYPHS[(Math.random() * GLYPHS.length) | 0];
        el.textContent = out;
        if (p < 1) raf = requestAnimationFrame(step); else el.textContent = text;
      };
      cancelAnimationFrame(el._raf || 0);
      el._raf = requestAnimationFrame(step);
    };
    el.addEventListener("pointerenter", scramble);
    el.addEventListener("focus", scramble);
  });

  /* ---- drawn schedule path ---- */
  const pathWrap = document.querySelector("[data-path]");
  if (pathWrap) {
    const line = pathWrap.querySelector(".line");
    const nodes = [...pathWrap.querySelectorAll("[data-node]")];
    const steps = [...document.querySelectorAll("[data-step]")];
    const cut = [0.02, 0.34, 0.66, 0.99];
    let raf = 0, cur = 0;
    const targetP = () => {
      if (reduced()) return 1;
      const r = pathWrap.getBoundingClientRect(), vh = innerHeight;
      return Math.min(1, Math.max(0, (vh * 0.9 - r.top) / (r.height + vh * 0.55)));
    };
    const apply = (p) => {
      line.style.strokeDashoffset = String(1 - p);
      nodes.forEach((n, i) => n.classList.toggle("is-on", p >= cut[i] - 0.02));
      steps.forEach((s, i) => s.classList.toggle("is-on", p >= cut[i] - 0.02));
    };
    const loop = () => {
      raf = 0;
      const t = targetP();
      cur += (t - cur) * (reduced() ? 1 : 0.12);
      if (Math.abs(t - cur) < 0.001) cur = t;
      apply(cur);
      if (cur !== t) raf = requestAnimationFrame(loop);
    };
    const kick = () => { if (!raf) raf = requestAnimationFrame(loop); };
    addEventListener("scroll", kick, { passive: true });
    document.addEventListener("motionchange", kick);
    cur = targetP(); apply(cur);
  }

  /* ---- lineup tilt ---- */
  if (!reduced() && fine) {
    document.querySelectorAll("[data-tilt]").forEach((card) => {
      const inner = card.querySelector(".act__art");
      let raf = 0, rx = 0, ry = 0, tx = 0, ty = 0;
      const MAX = 8;
      const loop = () => {
        raf = 0;
        rx += (tx - rx) * 0.18; ry += (ty - ry) * 0.18;
        inner.style.transform = `perspective(800px) rotateX(${ry.toFixed(2)}deg) rotateY(${rx.toFixed(2)}deg) translateY(-4px)`;
        if (Math.abs(tx - rx) > 0.05 || Math.abs(ty - ry) > 0.05) raf = requestAnimationFrame(loop);
      };
      const kick = () => { if (!raf) raf = requestAnimationFrame(loop); };
      card.addEventListener("pointermove", (e) => {
        const r = card.getBoundingClientRect();
        tx = ((e.clientX - r.left) / r.width - 0.5) * MAX * 2;
        ty = (0.5 - (e.clientY - r.top) / r.height) * MAX * 2;
        kick();
      }, { passive: true });
      card.addEventListener("pointerleave", () => { tx = 0; ty = 0; kick(); });
      card.addEventListener("focus", () => { tx = 4; ty = -3; kick(); });
      card.addEventListener("blur", () => { tx = 0; ty = 0; kick(); });
    });
  }

  /* ---- magnetic ticket CTA ---- */
  const zone = document.querySelector("[data-mag-zone]");
  if (zone && !reduced() && fine) {
    const btn = zone.querySelector("[data-magnetic]");
    const label = btn?.querySelector(".btn__label");
    let raf = 0, x = 0, y = 0, tx = 0, ty = 0;
    const loop = () => {
      raf = 0;
      x += (tx - x) * 0.16; y += (ty - y) * 0.16;
      if (Math.abs(tx - x) <= 0.1 && Math.abs(ty - y) <= 0.1) { x = tx; y = ty; }
      btn.style.transform = `translate3d(${x.toFixed(2)}px, ${y.toFixed(2)}px, 0)`;
      if (label) label.style.transform = `translate3d(${(x * 0.45).toFixed(2)}px, ${(y * 0.45).toFixed(2)}px, 0)`;
      if (Math.abs(tx - x) > 0.1 || Math.abs(ty - y) > 0.1) raf = requestAnimationFrame(loop);
    };
    const kick = () => { if (!raf) raf = requestAnimationFrame(loop); };
    zone.addEventListener("pointermove", (e) => {
      const r = btn.getBoundingClientRect();
      const dx = e.clientX - (r.left + r.width / 2), dy = e.clientY - (r.top + r.height / 2);
      const inside = Math.hypot(dx, dy) < 200;
      tx = inside ? dx * 0.35 : 0; ty = inside ? dy * 0.35 : 0;
      kick();
    }, { passive: true });
    zone.addEventListener("pointerleave", () => { tx = 0; ty = 0; kick(); });
  }
})();

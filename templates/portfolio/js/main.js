/* Motion Field — portfolio template. Every move checks reduced motion + fine pointer. */
(() => {
  const reduced = () => window.MotionPref?.reduced ?? matchMedia("(prefers-reduced-motion: reduce)").matches;
  const fine = matchMedia("(pointer: fine)").matches;

  /* ---- letter stagger (hero) ---- */
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

  /* ---- horizontal work gallery ---- */
  const work = document.querySelector("[data-hscroll]");
  if (work) {
    const sticky = work.querySelector(".work__sticky");
    const track = work.querySelector(".work__track");
    let raf = 0, cur = 0;
    const desktop = () => innerWidth > 760 && !reduced();
    const measure = () => {
      if (!desktop()) { work.style.height = ""; track.style.transform = ""; return; }
      const extra = Math.max(0, track.scrollWidth - sticky.clientWidth);
      work.style.height = `calc(100vh + ${Math.round(extra)}px)`;
    };
    const target = () => {
      if (!desktop()) return 0;
      const extra = Math.max(1, track.scrollWidth - sticky.clientWidth);
      const r = work.getBoundingClientRect();
      return Math.min(1, Math.max(0, -r.top / extra));
    };
    const apply = (p) => {
      const extra = Math.max(0, track.scrollWidth - sticky.clientWidth);
      track.style.transform = `translate3d(${(-p * extra).toFixed(1)}px, 0, 0)`;
    };
    const loop = () => {
      raf = 0;
      const t = target();
      cur += (t - cur) * 0.14;
      if (Math.abs(t - cur) < 0.001) cur = t;
      apply(cur);
      if (cur !== t) raf = requestAnimationFrame(loop);
    };
    const kick = () => { if (!raf) raf = requestAnimationFrame(loop); };
    addEventListener("scroll", kick, { passive: true });
    addEventListener("resize", () => { measure(); kick(); }, { passive: true });
    document.addEventListener("motionchange", () => { measure(); kick(); });
    measure(); cur = target(); apply(cur);
  }

  /* ---- drawn process path ---- */
  const pathWrap = document.querySelector("[data-path]");
  if (pathWrap) {
    const line = pathWrap.querySelector(".line");
    const nodes = [...pathWrap.querySelectorAll("[data-node]")];
    const steps = [...document.querySelectorAll("[data-step]")];
    const cut = [0.02, 0.34, 0.66, 0.99];
    let raf = 0, cur = 0;
    const target = () => {
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
      const t = target();
      cur += (t - cur) * (reduced() ? 1 : 0.12);
      if (Math.abs(t - cur) < 0.001) cur = t;
      apply(cur);
      if (cur !== t) raf = requestAnimationFrame(loop);
    };
    const kick = () => { if (!raf) raf = requestAnimationFrame(loop); };
    addEventListener("scroll", kick, { passive: true });
    document.addEventListener("motionchange", kick);
    cur = target(); apply(cur);
  }

  /* ---- card tilt ---- */
  if (!reduced() && fine) {
    document.querySelectorAll("[data-tilt]").forEach((card) => {
      const inner = card.querySelector(".project__art");
      let raf = 0, rx = 0, ry = 0, tx = 0, ty = 0;
      const MAX = 6;
      const loop = () => {
        raf = 0;
        rx += (tx - rx) * 0.18; ry += (ty - ry) * 0.18;
        inner.style.transform = `perspective(900px) rotateX(${ry.toFixed(2)}deg) rotateY(${rx.toFixed(2)}deg) translateY(-4px)`;
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
    });
  }

  /* ---- magnetic CTA ---- */
  const zone = document.querySelector("[data-mag-zone]");
  if (zone && !reduced() && fine) {
    const btn = zone.querySelector("[data-magnetic]");
    const label = btn?.querySelector(".btn__label");
    let raf = 0, x = 0, y = 0, tx = 0, ty = 0;
    const loop = () => {
      raf = 0;
      x += (tx - x) * 0.16; y += (ty - y) * 0.16;
      if (Math.abs(tx - x) > 0.1 || Math.abs(ty - y) > 0.1) { /* keep going */ } else { x = tx; y = ty; }
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

  /* ---- count-up stats ---- */
  const stats = [...document.querySelectorAll("[data-count]")];
  if (stats.length) {
    const run = (el) => {
      const end = parseFloat(el.dataset.count) || 0;
      if (reduced()) { el.textContent = String(end); return; }
      const t0 = performance.now(), dur = 1200;
      const tick = (now) => {
        const p = Math.min(1, (now - t0) / dur);
        el.textContent = String(Math.round(end * (1 - Math.pow(1 - p, 3))));
        if (p < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    };
    const io = new IntersectionObserver((entries) => entries.forEach((e) => {
      if (e.isIntersecting) { run(e.target); io.unobserve(e.target); }
    }), { threshold: 0.6 });
    stats.forEach((s) => io.observe(s));
  }

  /* ---- journal image distortion ---- */
  const filter = document.getElementById("warp");
  const map = filter?.querySelector("feDisplacementMap");
  const turb = filter?.querySelector("feTurbulence");
  if (map && turb && !reduced()) {
    document.querySelectorAll("[data-distort]").forEach((fig) => {
      const img = fig.querySelector(".post__thumb");
      let raf = 0, cur = 0, target = 0;
      const tick = (now) => {
        raf = 0;
        cur += (target - cur) * 0.12;
        if (Math.abs(target - cur) < 0.15) cur = target;
        map.setAttribute("scale", cur.toFixed(2));
        if (target > 0) turb.setAttribute("baseFrequency", (0.012 + Math.sin(now / 380) * 0.004).toFixed(4) + " " + (0.02 + Math.cos(now / 430) * 0.006).toFixed(4));
        if (cur !== target || target > 0) raf = requestAnimationFrame(tick);
      };
      const kick = () => { if (!raf) raf = requestAnimationFrame(tick); };
      fig.addEventListener("pointerenter", () => { target = 20; kick(); });
      fig.addEventListener("pointerleave", () => { target = 0; kick(); });
      fig.addEventListener("focus", () => { target = 20; kick(); });
      fig.addEventListener("blur", () => { target = 0; kick(); });
    });
  }
})();

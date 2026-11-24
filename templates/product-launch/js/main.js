/* Motion Field — product-launch template.
   Every move checks reduced motion and pointer type. Loops stop themselves. */
(() => {
  const reduced = () => window.MotionPref?.reduced ?? matchMedia("(prefers-reduced-motion: reduce)").matches;
  const fine = matchMedia("(pointer: fine)").matches;

  /* ---------- split headline into letters (word-wrapped, no reflow) ---------- */
  document.querySelectorAll("[data-split]").forEach((el) => {
    const label = el.textContent.trim();
    el.setAttribute("aria-label", label);
    el.textContent = "";
    let ci = 0;
    label.split(/\s+/).forEach((word, wi, arr) => {
      const w = document.createElement("span");
      w.className = "w";
      w.setAttribute("aria-hidden", "true");
      [...word].forEach((ch) => {
        const s = document.createElement("span");
        s.className = "ch";
        s.textContent = ch;
        s.style.setProperty("--i", ci++);
        w.appendChild(s);
      });
      el.appendChild(w);
      if (wi < arr.length - 1) el.appendChild(document.createTextNode(" "));
    });
  });

  /* ---------- reveal on scroll ---------- */
  const revealEls = [...document.querySelectorAll("[data-reveal]")];
  if (revealEls.length) {
    if (reduced() || !("IntersectionObserver" in window)) {
      revealEls.forEach((el) => el.classList.add("is-in"));
    } else {
      const io = new IntersectionObserver((entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) { e.target.classList.add("is-in"); io.unobserve(e.target); }
        });
      }, { rootMargin: "0px 0px -12% 0px", threshold: 0.08 });
      revealEls.forEach((el, i) => { el.style.transitionDelay = `${Math.min(i % 4, 3) * 70}ms`; io.observe(el); });
    }
  }

  /* ---------- scroll progress + feature rail ---------- */
  const bar = document.querySelector("[data-progress]");
  const features = [...document.querySelectorAll("[data-feature]")];
  let raf = 0;
  const onScroll = () => {
    raf = 0;
    const doc = document.documentElement;
    const max = doc.scrollHeight - innerHeight;
    if (bar) bar.style.transform = `scaleX(${max > 0 ? Math.min(1, scrollY / max) : 0})`;
    const mid = innerHeight * 0.45;
    let active = 0;
    features.forEach((f, i) => { if (f.getBoundingClientRect().top <= mid) active = i; });
    features.forEach((f, i) => f.classList.toggle("is-active", i === active));
  };
  const kick = () => { if (!raf) raf = requestAnimationFrame(onScroll); };
  addEventListener("scroll", kick, { passive: true });
  addEventListener("resize", kick);
  onScroll();

  /* ---------- count-up ---------- */
  const counters = [...document.querySelectorAll("[data-count]")];
  if (counters.length) {
    const run = (el) => {
      const target = Number(el.dataset.count) || 0;
      if (reduced()) { el.textContent = String(target); return; }
      const t0 = performance.now(), dur = 1200;
      let raf2 = 0;
      const step = (now) => {
        const p = Math.min(1, (now - t0) / dur);
        el.textContent = String(Math.round(target * (1 - Math.pow(1 - p, 3))));
        if (p < 1) raf2 = requestAnimationFrame(step);
      };
      cancelAnimationFrame(el._raf || 0);
      el._raf = raf2 = requestAnimationFrame(step);
    };
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => { if (e.isIntersecting) { run(e.target); io.unobserve(e.target); } });
    }, { threshold: 0.6 });
    counters.forEach((c) => io.observe(c));
  }

  /* ---------- spec tabs ---------- */
  const tabs = [...document.querySelectorAll("[data-tab]")];
  const panes = [...document.querySelectorAll("[data-pane]")];
  const ink = document.querySelector(".tabs__ink");
  const syncInk = (tab) => {
    if (!ink) return;
    const w = tabs[0].offsetWidth;
    ink.style.width = `${w}px`;
    ink.style.transform = `translateX(${tab.offsetLeft - tabs[0].offsetLeft}px)`;
  };
  const select = (name, focus) => {
    tabs.forEach((t) => {
      const on = t.dataset.tab === name;
      t.setAttribute("aria-selected", String(on));
      t.tabIndex = on ? 0 : -1;
      if (on) { syncInk(t); if (focus) t.focus(); }
    });
    panes.forEach((p) => { p.hidden = p.dataset.pane !== name; });
  };
  tabs.forEach((t, i) => {
    t.addEventListener("click", () => select(t.dataset.tab));
    t.addEventListener("keydown", (e) => {
      if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
      e.preventDefault();
      const next = tabs[(i + (e.key === "ArrowRight" ? 1 : tabs.length - 1)) % tabs.length];
      select(next.dataset.tab, true);
    });
  });
  if (tabs[0]) { syncInk(tabs[0]); addEventListener("resize", () => syncInk(tabs.find((t) => t.getAttribute("aria-selected") === "true") || tabs[0])); }

  /* ---------- magnetic ---------- */
  const magnets = [...document.querySelectorAll("[data-magnetic]")];
  if (magnets.length && !reduced() && fine) {
    const items = magnets.map((el) => ({ el, x: 0, y: 0, tx: 0, ty: 0 }));
    let mr = 0;
    const loop = () => {
      mr = 0;
      let moving = false;
      items.forEach((it) => {
        it.x += (it.tx - it.x) * 0.16;
        it.y += (it.ty - it.y) * 0.16;
        if (Math.abs(it.tx - it.x) > 0.1 || Math.abs(it.ty - it.y) > 0.1) moving = true;
        else { it.x = it.tx; it.y = it.ty; }
        it.el.style.transform = `translate3d(${it.x.toFixed(2)}px, ${it.y.toFixed(2)}px, 0)`;
      });
      if (moving) mr = requestAnimationFrame(loop);
    };
    const kick2 = () => { if (!mr) mr = requestAnimationFrame(loop); };
    items.forEach((it) => {
      it.el.addEventListener("pointermove", (e) => {
        const r = it.el.getBoundingClientRect();
        it.tx = (e.clientX - (r.left + r.width / 2)) * 0.28;
        it.ty = (e.clientY - (r.top + r.height / 2)) * 0.34;
        kick2();
      }, { passive: true });
      it.el.addEventListener("pointerleave", () => { it.tx = 0; it.ty = 0; kick2(); }, { passive: true });
    });
  }

  /* ---------- waitlist (demo only — no network) ---------- */
  const form = document.querySelector("[data-wait]");
  const done = document.querySelector("[data-wait-done]");
  if (form && done) {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const input = form.querySelector("input");
      if (!input || !input.checkValidity()) { input && input.reportValidity(); return; }
      form.hidden = true;
      done.hidden = false;
    });
  }

  /* ---------- honour motion changes at runtime ---------- */
  document.addEventListener("motionchange", () => {
    if (reduced()) {
      document.querySelectorAll("[data-reveal]").forEach((el) => el.classList.add("is-in"));
      document.querySelectorAll("[data-magnetic]").forEach((el) => { el.style.transform = ""; });
    }
  });
})();

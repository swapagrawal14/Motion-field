/* Motion Field — gallery template.
   Cursor, mask reveal, masonry reveal + filters, six hover treatments, sticky hover preview,
   pinned horizontal strip, tilt, glare, magnetic, flip, toggle, scramble.
   Every loop stops itself; listeners are passive; reduced motion turns it all off. */
(() => {
  const reduced = () => window.MotionPref?.reduced ?? matchMedia("(prefers-reduced-motion: reduce)").matches;
  const fine = matchMedia("(pointer: fine)").matches;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];

  /* ---------- reveal on scroll ---------- */
  const revealables = $$("[data-reveal], .hero__title .line, .pin, .tile");
  if (revealables.length) {
    if (reduced() || !("IntersectionObserver" in window)) {
      revealables.forEach((el) => el.classList.add("is-in"));
    } else {
      const io = new IntersectionObserver((entries) => {
        entries.forEach((e) => { if (e.isIntersecting) { e.target.classList.add("is-in"); io.unobserve(e.target); } });
      }, { rootMargin: "0px 0px -10% 0px", threshold: 0.06 });
      revealables.forEach((el, i) => { el.style.transitionDelay = `${Math.min(i % 3, 2) * 60}ms`; io.observe(el); });
    }
  }

  /* ---------- scroll progress ---------- */
  const bar = $("[data-progress]");
  let raf = 0;
  const onScroll = () => {
    raf = 0;
    const max = document.documentElement.scrollHeight - innerHeight;
    if (bar) bar.style.transform = `scaleX(${max > 0 ? Math.min(1, scrollY / max) : 0})`;
    stripFrame();
  };
  const kick = () => { if (!raf) raf = requestAnimationFrame(onScroll); };
  addEventListener("scroll", kick, { passive: true });
  addEventListener("resize", kick);

  /* ---------- custom cursor ---------- */
  const cursor = $(".cursor");
  if (cursor && fine && !reduced()) {
    const ring = $(".cursor__ring", cursor), dot = $(".cursor__dot", cursor), label = $(".cursor__label", cursor);
    let x = innerWidth / 2, y = innerHeight / 2, rx = x, ry = y, cr = 0, seen = false, scale = 1, tscale = 1;
    const loop = () => {
      cr = 0;
      rx += (x - rx) * 0.18; ry += (y - ry) * 0.18; scale += (tscale - scale) * 0.2;
      ring.style.transform = `translate3d(${rx.toFixed(2)}px, ${ry.toFixed(2)}px, 0) scale(${scale.toFixed(3)})`;
      dot.style.transform = `translate3d(${x.toFixed(2)}px, ${y.toFixed(2)}px, 0)`;
      label.style.transform = `translate3d(${x.toFixed(2)}px, ${y.toFixed(2)}px, 0) translate(14px, 14px)`;
      if (Math.abs(x - rx) > 0.2 || Math.abs(y - ry) > 0.2 || Math.abs(tscale - scale) > 0.004) cr = requestAnimationFrame(loop);
    };
    const start = () => { if (!cr) cr = requestAnimationFrame(loop); };
    addEventListener("pointermove", (e) => {
      x = e.clientX; y = e.clientY;
      if (!seen) { seen = true; document.documentElement.classList.add("has-cursor"); rx = x; ry = y; }
      start();
    }, { passive: true });
    document.addEventListener("pointerover", (e) => {
      const t = e.target.closest("[data-cursor]");
      if (!t) return;
      label.textContent = t.dataset.cursor;
      cursor.classList.add("is-active"); tscale = 1.7; start();
    });
    document.addEventListener("pointerout", (e) => {
      const t = e.target.closest("[data-cursor]");
      if (t && !t.contains(e.relatedTarget)) { cursor.classList.remove("is-active"); tscale = 1; start(); }
    });
    document.addEventListener("mouseleave", () => { document.documentElement.classList.remove("has-cursor"); seen = false; });
    document.addEventListener("motionchange", () => {
      if (reduced()) { document.documentElement.classList.remove("has-cursor"); cursor.classList.remove("is-active"); }
    });
  }

  /* ---------- board filters ---------- */
  const pins = $$(".pin");
  $$(".chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      $$(".chip").forEach((c) => c.classList.toggle("is-on", c === chip));
      const f = chip.dataset.filter;
      pins.forEach((p, i) => {
        const show = f === "all" || p.dataset.cat === f;
        p.classList.toggle("is-hidden", !show);
        if (show) {
          p.classList.remove("is-in");
          p.style.transitionDelay = `${(i % 6) * 45}ms`;
          requestAnimationFrame(() => requestAnimationFrame(() => p.classList.add("is-in")));
        }
      });
    });
  });

  /* ---------- tilt cards ---------- */
  if (fine && !reduced()) {
    $$('.pin[data-fx="tilt"]').forEach((pin) => {
      const media = $(".pin__media", pin);
      if (!media) return;
      pin.addEventListener("pointermove", (e) => {
        const r = pin.getBoundingClientRect();
        const px = (e.clientX - r.left) / r.width - .5;
        const py = (e.clientY - r.top) / r.height - .5;
        media.style.setProperty("--rx", `${(-py * 10).toFixed(2)}deg`);
        media.style.setProperty("--ry", `${(px * 12).toFixed(2)}deg`);
      }, { passive: true });
      pin.addEventListener("pointerleave", () => {
        media.style.setProperty("--rx", "0deg");
        media.style.setProperty("--ry", "0deg");
      }, { passive: true });
    });
  }

  /* ---------- sticky hover preview ---------- */
  const float = $(".float");
  if (float && fine && !reduced()) {
    const img = $("[data-float-img]", float);
    let fx = innerWidth / 2, fy = innerHeight / 2, tx = fx, ty = fy, fr = 0;
    const floop = () => {
      fr = 0;
      fx += (tx - fx) * 0.14; fy += (ty - fy) * 0.14;
      float.style.transform = `translate3d(${fx.toFixed(2)}px, ${fy.toFixed(2)}px, 0) translate(-50%, -50%) scale(1) rotate(0deg)`;
      if (Math.abs(tx - fx) > 0.3 || Math.abs(ty - fy) > 0.3) fr = requestAnimationFrame(floop);
    };
    const fstart = () => { if (!fr) fr = requestAnimationFrame(floop); };
    $$(".typelist__row").forEach((row) => {
      row.addEventListener("pointerenter", () => {
        if (img) img.src = row.dataset.preview;
        tx = fx; ty = fy;
        float.classList.add("is-on"); fstart();
      });
      row.addEventListener("pointerleave", () => float.classList.remove("is-on"));
    });
    addEventListener("pointermove", (e) => { tx = e.clientX; ty = e.clientY; if (float.classList.contains("is-on")) fstart(); }, { passive: true });
  }

  /* ---------- pinned horizontal strip ---------- */
  const strip = $("[data-strip]");
  const stripSection = $(".strip");
  function stripFrame() {
    if (!strip || !stripSection || reduced()) return;
    const r = stripSection.getBoundingClientRect();
    const total = r.height - innerHeight;
    const p = Math.min(1, Math.max(0, -r.top / (total || 1)));
    // read the resolved px padding (getComputedStyle returns px, never the clamp() token)
    const padX = parseFloat(getComputedStyle(strip).paddingLeft) || 0;
    const max = Math.max(0, strip.scrollWidth - innerWidth + padX * 2);
    strip.style.transform = `translate3d(${(-p * max).toFixed(1)}px, 0, 0)`;
  }

  /* ---------- magnetic ---------- */
  const magnets = $$("[data-magnetic]");
  if (magnets.length && fine && !reduced()) {
    const items = magnets.map((el) => ({ el, x: 0, y: 0, tx: 0, ty: 0 }));
    let mr = 0;
    const mloop = () => {
      mr = 0;
      let moving = false;
      items.forEach((it) => {
        it.x += (it.tx - it.x) * 0.16; it.y += (it.ty - it.y) * 0.16;
        if (Math.abs(it.tx - it.x) > 0.1 || Math.abs(it.ty - it.y) > 0.1) moving = true;
        else { it.x = it.tx; it.y = it.ty; }
        it.el.style.transform = `translate3d(${it.x.toFixed(2)}px, ${it.y.toFixed(2)}px, 0)`;
      });
      if (moving) mr = requestAnimationFrame(mloop);
    };
    const mkick = () => { if (!mr) mr = requestAnimationFrame(mloop); };
    items.forEach((it) => {
      it.el.addEventListener("pointermove", (e) => {
        const r = it.el.getBoundingClientRect();
        it.tx = (e.clientX - (r.left + r.width / 2)) * 0.3;
        it.ty = (e.clientY - (r.top + r.height / 2)) * 0.36;
        mkick();
      }, { passive: true });
      it.el.addEventListener("pointerleave", () => { it.tx = 0; it.ty = 0; mkick(); }, { passive: true });
    });
  }

  /* ---------- flip card ---------- */
  $$("[data-flip]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const on = btn.getAttribute("aria-pressed") === "true";
      btn.setAttribute("aria-pressed", String(!on));
    });
  });

  /* ---------- elastic toggle ---------- */
  $$("[data-switch]").forEach((sw) => {
    sw.addEventListener("click", () => {
      sw.setAttribute("aria-checked", String(sw.getAttribute("aria-checked") !== "true"));
    });
  });

  /* ---------- glare border follows the pointer ---------- */
  $$("[data-glow]").forEach((btn) => {
    btn.addEventListener("pointermove", (e) => {
      const r = btn.getBoundingClientRect();
      const a = Math.atan2(e.clientY - (r.top + r.height / 2), e.clientX - (r.left + r.width / 2));
      btn.style.setProperty("--ga", `${(a * 180 / Math.PI + 90).toFixed(0)}deg`);
    }, { passive: true });
  });

  /* ---------- text scramble ---------- */
  const GLYPHS = "!<>-_\\/[]{}—=+*^?#";
  $$("[data-scramble-hover]").forEach((el) => {
    const text = el.textContent;
    if (reduced()) return;
    let raf2 = 0;
    const scramble = () => {
      const t0 = performance.now(), dur = 520;
      const step = (now) => {
        const p = Math.min(1, (now - t0) / dur);
        const solved = Math.floor(p * text.length);
        let out = "";
        for (let i = 0; i < text.length; i++) out += text[i] === " " ? " " : i < solved ? text[i] : GLYPHS[(Math.random() * GLYPHS.length) | 0];
        el.textContent = out;
        if (p < 1) raf2 = requestAnimationFrame(step); else el.textContent = text;
      };
      cancelAnimationFrame(raf2);
      raf2 = requestAnimationFrame(step);
    };
    el.addEventListener("pointerenter", scramble);
  });

  /* ---------- nav scramble ---------- */
  $$("[data-scramble]").forEach((el) => {
    const text = el.textContent;
    if (reduced()) return;
    let raf3 = 0;
    const go = () => {
      const t0 = performance.now(), dur = 380;
      const step = (now) => {
        const p = Math.min(1, (now - t0) / dur);
        const solved = Math.floor(p * text.length);
        let out = "";
        for (let i = 0; i < text.length; i++) out += i < solved ? text[i] : GLYPHS[(Math.random() * GLYPHS.length) | 0];
        el.textContent = out;
        if (p < 1) raf3 = requestAnimationFrame(step); else el.textContent = text;
      };
      cancelAnimationFrame(raf3);
      raf3 = requestAnimationFrame(step);
    };
    el.addEventListener("pointerenter", go);
    el.addEventListener("focus", go);
  });

  /* ---------- footer wordmark fills on scroll ---------- */
  const word = $(".foot__word");
  if (word) {
    if (reduced()) word.classList.add("is-in");
    else {
      const io2 = new IntersectionObserver((es) => {
        es.forEach((e) => { if (e.isIntersecting) word.classList.add("is-in"); });
      }, { threshold: 0.5 });
      io2.observe(word);
    }
  }

  /* ---------- honour motion changes at runtime ---------- */
  document.addEventListener("motionchange", () => {
    if (reduced()) {
      $$("[data-reveal], .hero__title .line, .pin, .tile").forEach((el) => el.classList.add("is-in"));
      $$("[data-magnetic]").forEach((el) => { el.style.transform = ""; });
      if (strip) strip.style.transform = "";
    }
  });

  onScroll();
})();

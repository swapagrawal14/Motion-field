/* =========================================================================
   Motion Field · Landing template · main.js
   Moves: smooth scroll (Lenis) · pinned hero shrink · word stagger ·
   staggered reveals · tide canvas · marquee · 3D card wall · progress rail ·
   magnetic CTA · pointer glow · footer wordmark parallax.
   Every move checks `reduced` and `finePointer`. No move is required for
   content to be readable: if a CDN fails, the page is static but complete.
   ========================================================================= */
(() => {
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const finePointer = matchMedia('(hover: hover) and (pointer: fine)').matches;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const hasGSAP = !!(window.gsap && window.ScrollTrigger);

  $$('[data-year]').forEach(el => (el.textContent = new Date().getFullYear()));

  /* ---------- marquee: clone track so translateX(-50%) loops seamlessly ---------- */
  $$('[data-marquee]').forEach(row => {
    const track = row.firstElementChild;
    if (!track || reduced) return;
    const clone = track.cloneNode(true);
    clone.setAttribute('aria-hidden', 'true');
    row.appendChild(clone);
  });

  /* ---------- word split for the hero title (keeps the text for screen readers) ---------- */
  $$('[data-split]').forEach(el => {
    const text = el.textContent.trim();
    el.setAttribute('aria-label', text);
    el.innerHTML = text.split(/\s+/).map(w => `<span class="w" aria-hidden="true"><span>${w}</span></span>`).join(' ');
  });

  /* ---------- tide canvas (procedural hero visual) ---------- */
  const tide = (() => {
    const cvs = $('[data-tide]');
    if (!cvs) return null;
    const ctx = cvs.getContext('2d');
    let w = 0, h = 0, dpr = 1, t = 0, raf = 0, running = false;
    const mouse = { x: 0.7, y: 0.5, tx: 0.7, ty: 0.5 };
    const resize = () => {
      dpr = Math.min(window.devicePixelRatio || 1, 1.75);
      const r = cvs.getBoundingClientRect();
      w = r.width; h = r.height;
      cvs.width = Math.round(w * dpr); cvs.height = Math.round(h * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      draw();
    };
    const draw = () => {
      ctx.clearRect(0, 0, w, h);
      mouse.x += (mouse.tx - mouse.x) * 0.05; mouse.y += (mouse.ty - mouse.y) * 0.05;
      const lines = w < 600 ? 22 : 34;
      const step = w < 600 ? 10 : 14;
      for (let i = 0; i < lines; i++) {
        const p = i / (lines - 1);
        const baseY = h * ((w < 600 ? 0.14 : 0.38) + p * (w < 600 ? 0.95 : 0.7));
        const amp = 18 + p * 46;
        const a = 0.05 + Math.pow(p, 1.4) * 0.5;
        ctx.beginPath();
        for (let x = -20; x <= w + 20; x += step) {
          const nx = x / w;
          const dx = nx - mouse.x, dy = (baseY / h) - mouse.y;
          const pull = Math.exp(-(dx * dx * 6 + dy * dy * 10)) * 60;
          const y = baseY
            + Math.sin(nx * 5.2 + t * 0.7 + p * 2.4) * amp * 0.6
            + Math.sin(nx * 11.0 - t * 0.45 + p * 5.0) * amp * 0.25
            - pull;
          x === -20 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
        }
        ctx.strokeStyle = i % 7 === 3 ? `rgba(45,226,255,${Math.min(1, a * 1.8)})` : `rgba(120,160,255,${a * 0.75})`;
        ctx.lineWidth = i % 7 === 3 ? 1.4 : 1;
        ctx.stroke();
      }
    };
    const loop = () => { t += 0.012; draw(); raf = requestAnimationFrame(loop); };
    const start = () => { if (running || reduced) return; running = true; raf = requestAnimationFrame(loop); };
    const stop = () => { running = false; cancelAnimationFrame(raf); };
    resize();
    addEventListener('resize', resize, { passive: true });
    if (finePointer && !reduced) {
      const device = $('[data-device]');
      addEventListener('pointermove', e => {
        mouse.tx = e.clientX / innerWidth; mouse.ty = e.clientY / innerHeight;
        if (device) { device.style.setProperty('--px', (mouse.tx - 0.5).toFixed(3)); device.style.setProperty('--py', (mouse.ty - 0.5).toFixed(3)); }
      }, { passive: true });
    }
    // pause when offscreen or tab hidden
    new IntersectionObserver(([e]) => (e.isIntersecting ? start() : stop())).observe(cvs);
    document.addEventListener('visibilitychange', () => (document.hidden ? stop() : start()));
    return { start, stop };
  })();

  /* ---------- pointer glow on feature cards ---------- */
  if (finePointer) {
    $$('[data-glow]').forEach(card => {
      card.addEventListener('pointermove', e => {
        const r = card.getBoundingClientRect();
        card.style.setProperty('--x', `${e.clientX - r.left}px`);
        card.style.setProperty('--y', `${e.clientY - r.top}px`);
      });
    });
  }

  /* ---------- nav hides on scroll down, shows on scroll up ---------- */
  const nav = $('[data-nav]');
  let lastY = scrollY;
  addEventListener('scroll', () => {
    const y = scrollY;
    if (nav) nav.classList.toggle('is-hidden', y > lastY && y > innerHeight * 0.6);
    lastY = y;
  }, { passive: true });

  if (!hasGSAP) { document.documentElement.classList.remove('motion'); return; }
  const { gsap, ScrollTrigger } = window;
  gsap.registerPlugin(ScrollTrigger);

  if (reduced) { // static page; only the progress rail shows its full state
    document.documentElement.classList.remove('motion');
    return;
  }

  /* ---------- smooth scroll ---------- */
  if (window.Lenis) {
    const lenis = new Lenis({ lerp: 0.1, smoothWheel: true });
    window.lenis = lenis; // tools/qa.py drives this
    lenis.on('scroll', ScrollTrigger.update);
    gsap.ticker.add(time => lenis.raf(time * 1000));
    gsap.ticker.lagSmoothing(0);
    $$('a[href^="#"]').forEach(a => a.addEventListener('click', e => {
      const id = a.getAttribute('href');
      const target = id.length > 1 ? $(id) : null;
      if (!target && id !== '#top') return;
      e.preventDefault();
      lenis.scrollTo(id === '#top' ? 0 : target, { offset: 0, duration: 1.4 });
    }));
  }

  const mm = gsap.matchMedia();

  /* ---------- hero entrance ---------- */
  // .motion (set in <head>) hides the words before first paint; hand that state to GSAP, then drop the gate.
  gsap.set('.hero__title .w > span', { y: 0, yPercent: 105 });
  gsap.set('[data-hero-fade]', { opacity: 0 });
  document.documentElement.classList.remove('motion');
  const intro = gsap.timeline({ defaults: { ease: 'expo.out' } });
  intro
    .to('.hero__title .w > span', { yPercent: 0, duration: 1.3, stagger: 0.07 }, 0.15)
    .to('[data-hero-fade]', { opacity: 1, duration: 1, stagger: 0.12 }, 0.6)
    .from('.eyebrow', { opacity: 0, y: 12, duration: 0.9 }, 0.1)
    .fromTo('.dev__chart path:last-child', { '--draw': 520 }, { '--draw': 0, duration: 2.2, ease: 'power3.inOut' }, 0.4)
    .from('[data-device]', { opacity: 0, duration: 1.6 }, 0.35)
    .from('[data-nav]', { opacity: 0, y: -20, duration: 1, clearProps: 'transform,opacity' }, 0.2);

  /* ---------- pinned hero: stage shrinks into a rounded card, copy drifts up ---------- */
  mm.add({ desktop: '(min-width: 761px)', mobile: '(max-width: 760px)' }, ctx => {
    const { desktop } = ctx.conditions;
    const tl = gsap.timeline({
      scrollTrigger: { trigger: '[data-hero]', start: 'top top', end: desktop ? '+=90%' : '+=45%', scrub: 0.6, pin: true, pinSpacing: true },
    });
    tl.to('[data-hero-stage]', { scale: desktop ? 0.86 : 0.92, borderRadius: desktop ? 36 : 24, ease: 'none' }, 0)
      .to('[data-hero-inner]', { yPercent: desktop ? -14 : -8, opacity: 0.25, ease: 'none' }, 0)
      .to('[data-hero-cue]', { opacity: 0, ease: 'none', duration: 0.3 }, 0)
      .to('[data-device]', { opacity: 0.35, ease: 'none' }, 0);
  });

  /* ---------- staggered reveals ---------- */
  $$('[data-reveal]').forEach(el => {
    gsap.from(el, {
      y: 36, opacity: 0, filter: 'blur(8px)', duration: 1.1, ease: 'expo.out',
      scrollTrigger: { trigger: el, start: 'top 88%', once: true },
    });
  });
  $$('[data-stagger]').forEach(group => {
    gsap.from(group.children, {
      y: 60, opacity: 0, duration: 1.2, ease: 'expo.out', stagger: 0.12,
      scrollTrigger: { trigger: group, start: 'top 82%', once: true },
    });
  });

  /* ---------- 3D card wall: plane un-tilts, columns drift in opposite directions ---------- */
  const wall = $('[data-wall]');
  if (wall) {
    gsap.fromTo('[data-wall-plane]', { '--rx': '48deg', '--rz': '-20deg' }, {
      '--rx': '22deg', '--rz': '-8deg', ease: 'none',
      scrollTrigger: { trigger: wall, start: 'top bottom', end: 'bottom top', scrub: 0.8 },
    });
    $$('[data-col]', wall).forEach(col => {
      const dir = Number(col.dataset.col);
      gsap.fromTo(col, { y: dir * -120 }, {
        y: dir * 120, ease: 'none',
        scrollTrigger: { trigger: wall, start: 'top bottom', end: 'bottom top', scrub: 0.8 },
      });
    });
    if (finePointer) { // gentle pointer tilt on top of the scroll tilt
      const plane = $('[data-wall-plane]');
      const tilt = deg => gsap.to(plane, { '--ry': `${deg}deg`, duration: 1.2, ease: 'power3.out', overwrite: 'auto' });
      wall.addEventListener('pointermove', e => {
        const r = wall.getBoundingClientRect();
        tilt(((e.clientX - r.left) / r.width - 0.5) * 8);
      });
      wall.addEventListener('pointerleave', () => tilt(0));
    }
  }

  /* ---------- process progress rail ---------- */
  const rail = $('[data-rail]');
  if (rail) {
    gsap.fromTo(rail, { '--p': 0 }, { '--p': 1, ease: 'none', scrollTrigger: { trigger: '[data-steps]', start: 'top 80%', end: 'bottom 55%', scrub: 0.5 } });
  }

  /* ---------- footer wordmark parallax ---------- */
  gsap.fromTo('[data-wordmark]', { yPercent: 30 }, { yPercent: 0, ease: 'none', scrollTrigger: { trigger: '.footer', start: 'top bottom', end: 'bottom bottom', scrub: true } });

  /* ---------- magnetic CTA ---------- */
  if (finePointer) {
    $$('[data-magnetic]').forEach(btn => {
      const label = $('[data-magnetic-label]', btn);
      const bx = gsap.quickTo(btn, 'x', { duration: 0.6, ease: 'power3.out' });
      const by = gsap.quickTo(btn, 'y', { duration: 0.6, ease: 'power3.out' });
      const lx = label && gsap.quickTo(label, 'x', { duration: 0.6, ease: 'power3.out' });
      const ly = label && gsap.quickTo(label, 'y', { duration: 0.6, ease: 'power3.out' });
      const zone = btn.parentElement; // padded wrapper = magnetic radius
      zone.addEventListener('pointermove', e => {
        const r = btn.getBoundingClientRect();
        const dx = e.clientX - (r.left + r.width / 2), dy = e.clientY - (r.top + r.height / 2);
        bx(dx * 0.35); by(dy * 0.35);
        if (lx) { lx(dx * 0.18); ly(dy * 0.18); }
      });
      zone.addEventListener('pointerleave', () => {
        gsap.to(btn, { x: 0, y: 0, duration: 1, ease: 'elastic.out(1, 0.4)' });
        if (label) gsap.to(label, { x: 0, y: 0, duration: 1, ease: 'elastic.out(1, 0.4)' });
      });
    });
  }

  addEventListener('load', () => ScrollTrigger.refresh());
})();

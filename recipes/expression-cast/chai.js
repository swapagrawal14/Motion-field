/* Chai Chalo — expression-cast runtime.
 * One neutral cutout per character + small face patches (blink / sing / surprised) laid over it at their
 * rect on the base canvas. Acting = swapping which patch is visible; the body never moves a pixel, so
 * it reads as a face changing, not a slideshow. Bob / hop / tilt live on separate wrapper layers.
 */
(() => {
  const ROOT = "../../assets/cast-expr/";
  const CAST = {};
  for (const [id, c] of Object.entries(window.MF_EXPR_CAST || {})) CAST[id] = { ...c, root: ROOT + c.dir + "/" };
  // Chotu Bhaiya, the chai-wala: an extra rigpop pack that lives with this recipe (no blink: his eyes are closed in a grin)
  CAST.chaiwala = { name: "Chotu Bhaiya, the chai-wala", w: 720, h: 720, base: "talk/base.webp", root: "art/chaiwala/",
    faces: { sing: { file: "talk/sing.webp", x: 277, y: 262, w: 126, h: 108 },
             surprised: { file: "talk/surprised.webp", x: 244, y: 139, w: 185, h: 208 } } };
  const LABEL = { kettle: "Kettle Kaka, a singing steel kettle", kulhad: "Kulhad, a clay chai cup", samosa: "Samosa Singh",
    jalebi: "Jalebi Rani", biscuit: "Biskut", chaiwala: "Chotu Bhaiya, the chai-wala" };

  const root = document.documentElement;
  const reduced = () => root.classList.contains("reduce-motion");
  const rigs = [];

  // ---------- mount ----------
  document.querySelectorAll(".rig[data-char]").forEach((el, n) => {
    const c = CAST[el.dataset.char];
    if (!c) return;
    el.style.setProperty("--ar", `${c.w} / ${c.h}`);
    const hero = !!el.closest(".hero");
    const lazy = hero ? "" : ' loading="lazy"';
    let faces = "";
    for (const [name, f] of Object.entries(c.faces)) {
      faces += `<img class="face f-${name}" src="${c.root}${f.file}" alt="" decoding="async"${lazy} style="left:${(f.x / c.w) * 100}%;top:${(f.y / c.h) * 100}%;width:${(f.w / c.w) * 100}%;height:${(f.h / c.h) * 100}%">`;
    }
    el.innerHTML = `<div class="bob"><div class="act"><img class="base" src="${c.root}${c.base}" alt="" width="${c.w}" height="${c.h}"${lazy}${hero && el.dataset.char === "kettle" ? ' fetchpriority="high"' : ""}>${faces}</div></div>`;
    el.setAttribute("role", "img");
    el.setAttribute("aria-label", LABEL[el.dataset.char] || c.name);
    if (el.classList.contains("poke")) el.tabIndex = 0;
    el.dataset.face = "neutral";
    rigs.push({ el, id: el.dataset.char, c, lock: 0, timer: 0, sec: el.closest(".sec, .foot") });
  });
  const R = new Map(rigs.map((r) => [r.el, r]));

  // ---------- faces with priority: chorus/cta (3) > react (2) > blink (1) ----------
  function face(r, name, ms = 0, prio = 2) {
    if (!r) return;
    if (r.lock > prio && name !== "neutral") return;
    if (name !== "neutral" && name !== "blink" && !r.c.faces[name]) name = r.c.faces.sing ? "sing" : "neutral";
    if (name === "blink" && !r.c.faces.blink) return;
    clearTimeout(r.timer);
    r.el.dataset.face = name;
    r.lock = name === "neutral" ? 0 : prio;
    if (ms) r.timer = setTimeout(() => { r.el.dataset.face = "neutral"; r.lock = 0; }, ms);
  }
  const replay = (el, cls) => { if (reduced()) return; el.classList.remove(cls); void el.offsetWidth; el.classList.add(cls);
    setTimeout(() => el.classList.remove(cls), 650); };

  // ---------- visibility: only act on what is on screen ----------
  const live = new Set();
  const io = new IntersectionObserver((ents) => {
    for (const e of ents) {
      e.target.classList.toggle("is-on", e.isIntersecting);
      if (e.isIntersecting) {
        live.add(e.target);
        if (!e.target.classList.contains("is-seen")) { e.target.classList.add("is-seen"); setTimeout(() => react(e.target), 350); }
      } else live.delete(e.target);
    }
  }, { threshold: 0.18 });
  document.querySelectorAll(".sec, .foot").forEach((s) => io.observe(s));
  const visible = (r) => !document.hidden && (!r.sec || live.has(r.sec));

  // random blinks, 2.5–6 s apart, per character
  function scheduleBlink(r) {
    setTimeout(() => {
      if (visible(r) && r.lock === 0) face(r, "blink", 140, 1);
      scheduleBlink(r);
    }, 2500 + Math.random() * 3500);
  }
  rigs.forEach(scheduleBlink);

  // a section scrolls in: its cast notices you, staggered
  function react(sec) {
    const list = rigs.filter((r) => r.sec === sec);
    if (sec.classList.contains("gang")) return talkAll(list);
    list.forEach((r, i) => setTimeout(() => {
      replay(r.el, "hop");
      face(r, "surprised", 520, 2);
      setTimeout(() => face(r, "sing", 420, 2), 560);
    }, i * 110));
  }
  // gang: everyone "talks" (sing/neutral flap) while their bubble pops
  function talkAll(list) {
    list.forEach((r, i) => setTimeout(() => {
      let k = 0;
      const flap = setInterval(() => {
        face(r, k % 2 ? "neutral" : "sing", 0, 2);
        if (++k > 9) { clearInterval(flap); face(r, "neutral"); }
      }, 150);
    }, 150 + i * 150));
  }

  // ---------- sound: ui-sound.js for UI blips, a WebAudio whistle for the kettle ----------
  let ac = null;
  const muted = () => !window.UIsound || window.UIsound.muted;
  function whistle() {
    if (muted()) return;
    try {
      ac = ac || new (window.AudioContext || window.webkitAudioContext)();
      const t = ac.currentTime, o = ac.createOscillator(), o2 = ac.createOscillator(), g = ac.createGain(), lfo = ac.createOscillator(), lg = ac.createGain();
      o.type = "sine"; o2.type = "sine";
      o.frequency.setValueAtTime(1500, t); o.frequency.exponentialRampToValueAtTime(2350, t + 0.35); o.frequency.setValueAtTime(2350, t + 1.0);
      o2.frequency.setValueAtTime(3000, t); o2.frequency.exponentialRampToValueAtTime(4700, t + 0.35);
      lfo.frequency.value = 9; lg.gain.value = 38; lfo.connect(lg).connect(o.frequency);
      g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(0.07, t + 0.12);
      g.gain.setValueAtTime(0.07, t + 0.9); g.gain.exponentialRampToValueAtTime(0.0001, t + 1.25);
      const g2 = ac.createGain(); g2.gain.value = 0.18; o2.connect(g2).connect(g);
      o.connect(g).connect(ac.destination);
      [o, o2, lfo].forEach((x) => { x.start(t); x.stop(t + 1.3); });
    } catch (e) { /* never break the page for a sound */ }
  }
  const sfx = (n) => window.UIsound && window.UIsound.play(n);

  // ---------- steam + notes ----------
  const STEAM = "art/steam.webp", NOTE = "art/note.webp", SPARK = "art/sparkle.webp";
  document.querySelectorAll(".rig[data-steam] .act").forEach((act) => {
    if (reduced()) return;
    const s = document.createElement("div"); s.className = "steam-src"; s.setAttribute("aria-hidden", "true"); act.appendChild(s);
    for (let i = 0; i < 3; i++) {
      const p = document.createElement("img");
      p.className = "steam"; p.src = STEAM; p.alt = ""; p.loading = "lazy";
      p.style.cssText = `--d:${i * 1.13};--dx:${-30 - i * 22}px;left:${-i * 14}px;top:0`;
      s.appendChild(p);
    }
  });
  function spawn(host, src, cls, n, opts = {}) {
    if (reduced() || !host) return;
    const box = host.getBoundingClientRect();
    for (let i = 0; i < n; i++) {
      const p = document.createElement("img");
      p.src = src; p.alt = ""; p.className = cls; p.setAttribute("aria-hidden", "true");
      const x = (opts.x ?? 0.5) * box.width + (Math.random() - 0.5) * (opts.spread ?? 60);
      const y = (opts.y ?? 0.2) * box.height;
      p.style.cssText = `left:${x}px;top:${y}px;--dx:${(Math.random() - 0.5) * 120 + (opts.dx || 0)}px;--dy:${-100 - Math.random() * 80}px;animation-delay:${i * 0.12}s;z-index:9`;
      host.appendChild(p);
      setTimeout(() => p.remove(), 1700 + i * 120);
    }
  }

  // ---------- chorus: whistle -> steam burst -> staggered sing wave ----------
  let singing = false;
  function chorus(scope) {
    if (singing) return;
    singing = true;
    const sec = scope || [...live].find((s) => s.matches(".chorus, .hero")) || document.querySelector(".chorus");
    const kettle = rigs.find((r) => r.sec === sec && r.id === "kettle") || rigs.find((r) => r.id === "kettle" && visible(r));
    whistle();
    if (kettle) {
      face(kettle, "surprised", 1100, 3); replay(kettle.el, "shake");
      spawn(kettle.el, STEAM, "burst", 4, { x: 0.08, y: 0.22, spread: 40, dx: -60 });
    }
    const cast = rigs.filter((r) => r.sec === sec && r !== kettle).sort((a, b) => a.el.getBoundingClientRect().left - b.el.getBoundingClientRect().left);
    const words = sec ? [...sec.querySelectorAll(".lyrics span")] : [];
    words.forEach((w, i) => setTimeout(() => w.classList.add("lit"), 350 + i * 210));
    cast.forEach((r, i) => setTimeout(() => {
      face(r, "sing", 900, 3); replay(r.el, "hop");
      spawn(r.el, NOTE, "note", 1, { x: 0.6, y: 0.05, spread: 30 });
      sfx("plip");
    }, 450 + i * 140));
    setTimeout(() => { if (kettle) face(kettle, "sing", 900, 3); }, 1150);
    setTimeout(() => { words.forEach((w) => w.classList.remove("lit")); singing = false; }, 2900);
  }
  document.querySelectorAll("[data-seeti]").forEach((b) => b.addEventListener("click", () => chorus(b.closest(".sec"))));
  // the chorus section whistles by itself every ~8 s while it is on screen
  setInterval(() => {
    const c = document.querySelector(".chorus");
    if (!document.hidden && live.has(c) && !reduced()) chorus(c);
  }, 8000);

  // ---------- poke: tap or Enter on any character ----------
  rigs.forEach((r) => {
    if (!r.el.classList.contains("poke")) return;
    const go = () => { replay(r.el, "hop"); face(r, Math.random() < 0.5 ? "surprised" : "sing", 650, 2); sfx("boing"); };
    r.el.addEventListener("click", go);
    r.el.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); go(); } });
  });

  // ---------- CTA: hover/focus = whole cast gasps; click = kettle pours, kulhad happy ----------
  let gasp = false;
  const gaspOn = () => { if (gasp) return; gasp = true; rigs.filter(visible).forEach((r, i) => setTimeout(() => face(r, "surprised", 0, 3), i * 40)); sfx("plip"); };
  const gaspOff = () => { if (!gasp) return; gasp = false; rigs.forEach((r) => { if (r.el.dataset.face === "surprised") face(r, "neutral"); }); };
  document.querySelectorAll("[data-cta]").forEach((b) => {
    b.addEventListener("pointerenter", gaspOn); b.addEventListener("focus", gaspOn);
    b.addEventListener("pointerleave", gaspOff); b.addEventListener("blur", gaspOff);
  });

  const okettle = R.get(document.querySelector(".o-kettle")), okulhad = R.get(document.querySelector(".o-kulhad"));
  const ochai = R.get(document.querySelector(".o-chaiwala"));
  const pourEl = document.querySelector(".pour"), toast = document.querySelector(".toast");
  let pouring = false;
  function pour() {
    if (pouring) return; pouring = true; gaspOff();
    okettle.el.classList.add("tilt"); face(okettle, "sing", 1500, 3); sfx("whoosh");
    pourEl.classList.add("on");
    face(okulhad, "surprised", 700, 3);
    setTimeout(() => { face(okulhad, "sing", 1600, 3); replay(okulhad.el, "hop"); spawn(okulhad.el, SPARK, "note", 4, { x: 0.5, y: 0, spread: 140 }); sfx("success"); }, 700);
    if (ochai) setTimeout(() => face(ochai, "sing", 1400, 3), 700);
    setTimeout(() => { pourEl.classList.remove("on"); okettle.el.classList.remove("tilt"); }, 1500);
    setTimeout(() => { pouring = false; }, 2300);
  }
  const form = document.getElementById("order-form");
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const nm = form.nm.value.trim() || "dost";
    const cup = form.cup.value === "kulhad" ? "kulhad" : "cutting glass";
    toast.textContent = `Order lag gaya, ${nm}! Ek ${cup}, cheeni ${form.sugar.value}. (Demo: no chai was harmed.)`;
    pour();
  });

  // ---------- hero: the shutter goes up ----------
  const hero = document.querySelector(".hero");
  const open = () => hero.classList.add("open");
  if (reduced()) open(); else setTimeout(open, 450);
  // hero greeting: once the cast is up, Kettle Kaka whistles and the counter sings
  setTimeout(() => { if (!reduced() && live.has(hero)) chorus(hero); }, 2600);

  // ---------- hidden tab: freeze ----------
  document.addEventListener("visibilitychange", () => root.classList.toggle("paused", document.hidden));

  window.Chai = { chorus, pour, gaspOn, gaspOff, face: (sel, f, ms, p) => face(R.get(document.querySelector(sel)), f, ms, p), rigs };
})();

/* Motion Field — UI sound kit (WebAudio, no audio files).
 *
 *   <script src="assets/ui-sound.js"></script>
 *   <button data-sfx-toggle>Sound off</button>
 *   <a data-sfx="pop" data-sfx-hover="tick">Open</a>
 *
 * Sound is MUTED by default: the first click on [data-sfx-toggle] creates the AudioContext and
 * enables playback. Nothing is fetched, nothing is stored, and the page is silent until the
 * visitor opts in. Reduced-motion users keep the same opt-in (sound is not motion, but silence
 * is the safe default).
 */
(() => {
  if (window.UIsound) return;
  let ctx = null;
  let muted = true;
  const toggles = () => [...document.querySelectorAll("[data-sfx-toggle]")];
  const statuses = () => [...document.querySelectorAll("[data-sfx-status]")];

  const ac = () => {
    if (!ctx) {
      const AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return null;
      ctx = new AC();
    }
    if (ctx.state === "suspended") ctx.resume();
    return ctx;
  };

  const env = (gain, t0, attack, decay, peak = 0.2) => {
    gain.gain.setValueAtTime(0.0001, t0);
    gain.gain.exponentialRampToValueAtTime(peak, t0 + attack);
    gain.gain.exponentialRampToValueAtTime(0.0001, t0 + attack + decay);
  };

  const tone = (freq, type, dur, peak, slideTo) => {
    const c = ac(); if (!c) return;
    const o = c.createOscillator(), g = c.createGain();
    o.type = type; o.frequency.setValueAtTime(freq, c.currentTime);
    if (slideTo) o.frequency.exponentialRampToValueAtTime(slideTo, c.currentTime + dur);
    env(g, c.currentTime, 0.004, dur, peak);
    o.connect(g).connect(c.destination);
    o.start(); o.stop(c.currentTime + dur + 0.02);
  };

  const noise = (dur, peak, filterFreq = 900, q = 0.8) => {
    const c = ac(); if (!c) return;
    const len = Math.floor(c.sampleRate * dur);
    const buf = c.createBuffer(1, len, c.sampleRate);
    const d = buf.getChannelData(0);
    for (let i = 0; i < len; i++) d[i] = (Math.random() * 2 - 1) * (1 - i / len);
    const src = c.createBufferSource(); src.buffer = buf;
    const f = c.createBiquadFilter(); f.type = "bandpass"; f.frequency.value = filterFreq; f.Q.value = q;
    const g = c.createGain(); env(g, c.currentTime, 0.01, dur, peak);
    src.connect(f).connect(g).connect(c.destination);
    src.start();
  };

  const FX = {
    pop: () => tone(520, "sine", 0.12, 0.18, 180),
    tick: () => tone(2500, "sine", 0.04, 0.07),
    whoosh: () => noise(0.45, 0.16, 700, 0.7),
    plip: () => tone(900, "sine", 0.15, 0.11, 2300),
    boing: () => { tone(220, "sine", 0.35, 0.16, 340); tone(440, "triangle", 0.2, 0.05, 220); },
    dab: () => noise(0.06, 0.05, 2400, 1.2),
    ring: () => { tone(1300, "sine", 0.5, 0.05); tone(1700, "sine", 0.45, 0.03); },
    success: () => { tone(523.25, "sine", 0.3, 0.11); setTimeout(() => tone(783.99, "sine", 0.32, 0.11), 90); },
    error: () => { tone(220, "sine", 0.28, 0.1); setTimeout(() => tone(174.61, "sine", 0.3, 0.1), 110); },
  };

  const sync = () => {
    toggles().forEach((b) => {
      b.setAttribute("aria-pressed", String(!muted));
      // only rewrite the label on a plain-text button — a toggle with a [data-sfx-status]
      // child keeps its markup (icon + label + state)
      if (!b.querySelector("[data-sfx-status]")) b.textContent = muted ? "Sound off" : "Sound on";
    });
    statuses().forEach((s) => (s.textContent = muted ? "muted" : "on"));
  };

  const play = (name) => {
    if (muted) return;
    const fn = FX[name] || FX.pop;
    try { fn(); } catch (e) { /* never break the page for a sound */ }
  };

  const enable = () => {
    muted = false;
    ac();
    sync();
    play("pop");
  };

  document.addEventListener("click", (e) => {
    const t = e.target.closest("[data-sfx-toggle]");
    if (t) { muted ? enable() : (muted = true, sync()); return; }
    const el = e.target.closest("[data-sfx]");
    if (el) play(el.dataset.sfx || "pop");
  });
  document.addEventListener("pointerover", (e) => {
    if (muted) return;
    const el = e.target.closest("[data-sfx-hover]");
    if (el && !el.contains(e.relatedTarget)) play(el.dataset.sfxHover || "tick");
  });
  document.addEventListener("keydown", (e) => {
    if (e.key !== "Enter" && e.key !== " ") return;
    const el = e.target.closest("[data-sfx]");
    if (el) play(el.dataset.sfx || "pop");
  });

  window.UIsound = {
    play,
    setMuted(v) { muted = !!v; if (!muted) ac(); sync(); },
    toggle() { muted ? enable() : (muted = true, sync()); },
    get muted() { return muted; },
    names: Object.keys(FX),
  };
  sync();
})();

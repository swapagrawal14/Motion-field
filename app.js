/* Motion Field: library, live previews, GPU shaders, scroll choreography. No build step. */
(() => {
"use strict";

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
const reduceMQ = window.matchMedia("(prefers-reduced-motion: reduce)");
let reducedMotion = reduceMQ.matches;
const finePointer = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

/* ------------------------------------------------------------------ */
/* Shader sources: one shared header, one body per look.               */
/* ------------------------------------------------------------------ */
const GLSL_HEAD = `precision highp float;
uniform vec2 u_res;
uniform float u_time;
uniform vec2 u_mouse;      // -1..1, follows the pointer
uniform vec3 u_c1, u_c2, u_c3;

float hash(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float noise(vec2 p){
  vec2 i = floor(p), f = fract(p);
  f = f * f * (3.0 - 2.0 * f);
  return mix(mix(hash(i), hash(i + vec2(1,0)), f.x),
             mix(hash(i + vec2(0,1)), hash(i + vec2(1,1)), f.x), f.y);
}
float fbm(vec2 p){
  float v = 0.0, a = 0.5;
  for (int i = 0; i < 5; i++){ v += a * noise(p); p *= 2.02; a *= 0.5; }
  return v;
}
vec3 palette(float x){
  x = clamp(x, 0.0, 1.0);
  return x < 0.5 ? mix(u_c1, u_c2, x * 2.0) : mix(u_c2, u_c3, x * 2.0 - 1.0);
}`;

const GLSL_BODIES = {
  mesh: `  // Mesh gradient: domain-warped noise mapped onto a three-stop palette
  vec2 q = vec2(fbm(p * 1.3 + u_time * 0.07), fbm(p * 1.3 + vec2(5.2, 1.3) - u_time * 0.06));
  float f = fbm(p * 1.1 + q * 1.8 + u_mouse * 0.25);
  col = palette(smoothstep(0.18, 0.82, f));`,
  swirl: `  // Swirl: polar coordinates twisted by time and noise
  float d = length(p);
  float a = atan(p.y, p.x) + d * 2.4 - u_time * 0.35 + u_mouse.x * 0.4;
  float s = sin(a * 3.0 + fbm(p * 2.0 + u_time * 0.1) * 3.5);
  col = palette(0.5 + 0.5 * s);
  col = mix(col, u_c1, smoothstep(0.45, 1.35, d));`,
  halftone: `  // Halftone tide: a dot grid whose radii ride a travelling wave
  float cell = u_res.y / 30.0;
  vec2 g = gl_FragCoord.xy / cell;
  vec2 id = floor(g), f = fract(g) - 0.5;
  float w = 0.5 + 0.5 * sin(id.x * 0.22 + id.y * 0.1 - u_time * 1.4 + fbm(id * 0.07 + u_time * 0.05) * 5.0);
  float r = 0.08 + 0.42 * w;
  float dotMask = smoothstep(r, r - 0.09, length(f));
  col = mix(u_c1, palette(0.35 + 0.65 * w), dotMask);`,
  aurora: `  // Aurora: soft bands bending over a night sky
  float b = sin(uv.x * 3.0 + u_time * 0.35 + fbm(uv * 3.0 + u_time * 0.08) * 3.0);
  float band = exp(-pow((uv.y - 0.58 - 0.16 * b) * 4.2, 2.0));
  float band2 = exp(-pow((uv.y - 0.36 + 0.12 * b) * 6.0, 2.0)) * 0.6;
  col = u_c1 + u_c2 * band * 0.95 + u_c3 * (band2 + band * band * 0.4);
  col += step(0.996, hash(floor(gl_FragCoord.xy / 2.0))) * 0.5 * (1.0 - band);`,
  flow: `  // Flow lines: contour lines over a drifting noise field
  float n = fbm(p * 1.4 + vec2(u_time * 0.05, -u_time * 0.03) + u_mouse * 0.2);
  float lines = sin((p.y + n * 1.6) * 26.0 - u_time * 1.6);
  col = mix(u_c1, palette(n * 1.2), smoothstep(0.1, 0.95, lines) * 0.85);`,
  ripple: `  // Ripple pool: rings radiating from the pointer
  vec2 c = u_mouse * vec2(0.6, 0.4);
  float d = length(p - c);
  float s = sin(d * 26.0 - u_time * 3.2) * exp(-d * 1.8);
  float n = fbm(p * 2.0 + u_time * 0.1);
  col = palette(0.45 + 0.4 * s + 0.25 * (n - 0.5));`
};
const SHADER_MODES = Object.keys(GLSL_BODIES);

function shaderSnippet(mode) {
  return `${GLSL_HEAD}

void main(){
  vec2 uv = gl_FragCoord.xy / u_res;
  vec2 p = (gl_FragCoord.xy - 0.5 * u_res) / min(u_res.x, u_res.y);
  vec3 col;
${GLSL_BODIES[mode]}
  col += (hash(gl_FragCoord.xy + u_time) - 0.5) * 0.04; // film grain
  gl_FragColor = vec4(col, 1.0);
}`;
}

/* ------------------------------------------------------------------ */
/* Data                                                                */
/* ------------------------------------------------------------------ */
const CATS = [
  { id: "all", label: "All" }, { id: "scroll", label: "Scroll" }, { id: "reveal", label: "Reveal" },
  { id: "type", label: "Type" }, { id: "3d", label: "3D & depth" }, { id: "shader", label: "Shader" }, { id: "micro", label: "Micro" }
];
const CAT_LABEL = Object.fromEntries(CATS.map((c) => [c.id, c.label]));

const library = [
  { id: "01", title: "The tide turn", category: "scroll", preview: { kind: "image", src: "assets/thumbs/study-tide.webp" }, desc: "A sideways tide that drifts as you move down the page. Best used when the story itself has a direction to travel.", tags: ["horizontal drift", "scroll-linked"], level: "Gentle", pop: 92, added: 1, badge: "Free",
    code: "const track = document.querySelector('.story-track');\nwindow.addEventListener('scroll', () => {\n  const progress = window.scrollY /\n    (document.body.scrollHeight - innerHeight);\n  track.style.transform =\n    `translateX(${progress * -24}vw)`;\n}, { passive: true });" },
  { id: "02", title: "Orbit, gently", category: "3d", preview: { kind: "image", src: "assets/thumbs/study-orbit.webp" }, desc: "A small constellation follows the reader. Slow, imperfect and just off-centre, like things are in real life.", tags: ["parallax", "pointer"], level: "Medium", pop: 88, added: 2, badge: "Free",
    code: "const scene = document.querySelector('.scene');\nscene.addEventListener('pointermove', (event) => {\n  const x = event.clientX / innerWidth - .5;\n  const y = event.clientY / innerHeight - .5;\n  scene.style.setProperty('--x', x.toFixed(2));\n  scene.style.setProperty('--y', y.toFixed(2));\n});" },
  { id: "03", title: "Soft-focus reveal", category: "reveal", preview: { kind: "image", src: "assets/thumbs/study-reveal.webp" }, desc: "Let a new chapter arrive in focus instead of all at once. A quiet reveal with a little depth and a lot of restraint.", tags: ["intersection", "blur to clear"], level: "Gentle", pop: 95, added: 3, badge: "Free",
    code: "const reveal = new IntersectionObserver((entries) => {\n  entries.forEach(({ target, isIntersecting }) => {\n    if (isIntersecting) target.classList.add('is-ready');\n  });\n}, { threshold: 0.22 });\n\ndocument.querySelectorAll('[data-reveal]')\n  .forEach((item) => reveal.observe(item));" },
  { id: "04", title: "Letters in the wind", category: "type", preview: { kind: "image", src: "assets/thumbs/study-type.webp" }, desc: "A headline gives the breeze a shape. Each letter eases into place with enough space to read, then enough time to stay.", tags: ["letter stagger", "headline"], level: "Medium", pop: 84, added: 4, badge: "Free",
    code: "const letters = document.querySelectorAll('.letter');\nletters.forEach((letter, index) => {\n  letter.style.setProperty('--delay', (index * 42) + 'ms');\n});\n\n/* Pair with a reduced-motion fallback. */" },
  { id: "05", title: "The long way round", category: "scroll", preview: { kind: "image", src: "assets/thumbs/study-path.webp" }, desc: "A hand-drawn path traces a small detour. Connect two ideas and make the transition part of the story.", tags: ["path draw", "scroll-linked"], level: "Medium", pop: 79, added: 5, badge: "Free",
    code: "const path = document.querySelector('.draw-path');\nconst length = path.getTotalLength();\npath.style.strokeDasharray = length;\npath.style.strokeDashoffset = length;\n\n// As progress moves from 0 to 1:\npath.style.strokeDashoffset = length * (1 - progress);" },
  { id: "06", title: "A page with a pulse", category: "micro", preview: { kind: "image", src: "assets/thumbs/study-pulse.webp" }, desc: "A small breath on hover and focus. A tactile signal for something you can actually interact with, never just decoration.", tags: ["micro-interaction", "hover + focus"], level: "Gentle", pop: 81, added: 6, badge: "Free",
    code: ".pulse-card {\n  transition: transform 360ms cubic-bezier(.2,.8,.2,1);\n}\n.pulse-card:hover,\n.pulse-card:focus-visible {\n  transform: translateY(-4px) rotate(-.4deg);\n}\n@media (prefers-reduced-motion: reduce) {\n  .pulse-card { transition: none; }\n}" },
  { id: "07", title: "Halftone tide", category: "shader", preview: { kind: "shader", mode: "halftone", palette: "#0a1330,#3d6bff,#d5ff3f" }, desc: "A grid of dots swells and settles like water over sand. Print texture, made to move.", tags: ["WebGL", "fragment shader"], level: "Bold", pop: 97, added: 12, badge: "Signature", code: shaderSnippet("halftone") },
  { id: "08", title: "Aurora veil", category: "shader", preview: { kind: "shader", mode: "aurora", palette: "#04060c,#21d4a2,#8a5cff" }, desc: "Soft bands of light bend across a night sky. A background that breathes without stealing the headline.", tags: ["WebGL", "noise"], level: "Medium", pop: 90, added: 13, badge: "Signature", code: shaderSnippet("aurora") },
  { id: "09", title: "Magnetic pull", category: "micro", preview: { kind: "css", html: `<div class="pv pv--magnet"><span class="c-magnet" data-comp="magnet"><span>Pull me</span></span></div>` }, desc: "A call to action that leans toward the cursor, then springs home. It tells the hand: yes, this one.", tags: ["pointer", "spring"], level: "Gentle", pop: 94, added: 9, badge: "Free",
    code: "btn.addEventListener('pointermove', (e) => {\n  const r = btn.getBoundingClientRect();\n  const x = (e.clientX - r.left - r.width / 2) * 0.35;\n  const y = (e.clientY - r.top - r.height / 2) * 0.35;\n  btn.style.transform = `translate(${x}px, ${y}px)`;\n});\nbtn.addEventListener('pointerleave', () => {\n  btn.style.transform = '';  // CSS transition springs it back\n});" },
  { id: "10", title: "Ink line draw", category: "scroll", preview: { kind: "css", html: `<div class="pv pv--ink"><svg viewBox="0 0 400 240" aria-hidden="true"><path class="pv-ink__path" d="M20 190 C 90 40, 150 40, 190 120 S 290 220, 380 50"/><circle class="pv-ink__dot" r="7" cx="380" cy="50"/></svg><span class="pv-ink__label">from here → to there</span></div>` }, desc: "One continuous line draws itself as the reader scrolls, tying two sections together like a thread.", tags: ["SVG", "stroke-dashoffset"], level: "Gentle", pop: 76, added: 10, badge: "Free",
    code: "const path = document.querySelector('.ink');\nconst len = path.getTotalLength();\npath.style.strokeDasharray = len;\nconst draw = () => {\n  const r = path.closest('section').getBoundingClientRect();\n  const p = Math.min(1, Math.max(0, 1 - r.bottom / (innerHeight + r.height)));\n  path.style.strokeDashoffset = len * (1 - p);\n};\naddEventListener('scroll', draw, { passive: true });" },
  { id: "11", title: "Kinetic headline", category: "type", preview: { kind: "css", html: `<div class="pv pv--kinetic"><div class="pv-k__row"><span>Move with meaning ✦ Move with meaning ✦ </span><span>Move with meaning ✦ Move with meaning ✦ </span></div><div class="pv-k__row pv-k__row--rev"><em>small moves big feeling ✦ small moves big feeling ✦ </em><em>small moves big feeling ✦ small moves big feeling ✦ </em></div><div class="pv-k__row"><span>Scroll ✦ Drift ✦ Reveal ✦ Scroll ✦ Drift ✦ Reveal ✦ </span><span>Scroll ✦ Drift ✦ Reveal ✦ Scroll ✦ Drift ✦ Reveal ✦ </span></div></div>` }, desc: "Oversized type in counter-moving rows. The page feels alive before anyone reads a word.", tags: ["marquee", "CSS keyframes"], level: "Bold", pop: 86, added: 11, badge: "Free",
    code: ".row { display: flex; width: max-content;\n  animation: slide 22s linear infinite; }\n.row--rev { animation-direction: reverse; }\n@keyframes slide { to { transform: translateX(-50%); } }\n@media (prefers-reduced-motion: reduce) {\n  .row { animation: none; }\n}" },
  { id: "12", title: "Depth stack", category: "3d", preview: { kind: "css", html: `<div class="pv pv--stack" data-comp="stack"><div class="pv-stack__scene"><i style="--z:0"></i><i style="--z:1"></i><i style="--z:2"></i><b>✦</b></div></div>` }, desc: "Three layers of glass pull apart in perspective as the pointer moves. Depth without a 3D engine.", tags: ["CSS 3D", "perspective"], level: "Medium", pop: 83, added: 14, badge: "Signature",
    code: ".scene { perspective: 900px; }\n.layer {\n  transform: rotateX(calc(var(--y) * 18deg))\n             rotateY(calc(var(--x) * -22deg))\n             translateZ(calc(var(--z) * 40px));\n  transition: transform .5s cubic-bezier(.2,.8,.2,1);\n}" },
  { id: "13", title: "Liquid swirl", category: "shader", preview: { kind: "shader", mode: "swirl", palette: "#06070a,#2b3cbf,#f2f0e7" }, desc: "Ink poured into water and stirred once. A slow polar twist that suits a calm, premium hero.", tags: ["WebGL", "polar coords"], level: "Medium", pop: 89, added: 15, badge: "Signature", code: shaderSnippet("swirl") },
  { id: "14", title: "Ripple pool", category: "shader", preview: { kind: "shader", mode: "ripple", palette: "#051822,#2fa6c9,#e9fbff" }, desc: "Rings spread from wherever the pointer rests. Touch the surface and it answers.", tags: ["WebGL", "pointer"], level: "Bold", pop: 80, added: 16, badge: "Signature", code: shaderSnippet("ripple") }
];
library.forEach((it, i) => { it.label = CAT_LABEL[it.category]; it.featured = i; });

const components = [
  { name: "Lodestar", cat: "Button", desc: "A pill that leans toward the cursor and springs home.", html: `<span class="c-magnet" data-comp="magnet" tabindex="0" role="button"><span>Hover me</span></span>`, tags: ["pointer", "spring"] },
  { name: "Halo", cat: "Loader", desc: "Three orbits at different speeds, a loader with a pulse.", html: `<span class="c-orbit" role="img" aria-label="Loading"><i></i><i></i><i></i><b></b></span>`, tags: ["CSS keyframes"] },
  { name: "Prism", cat: "Card", desc: "Tilts toward the pointer and catches a moving highlight.", html: `<div class="c-tilt" data-comp="tilt"><div class="c-tilt__card"><span class="mono">Field card</span><strong>Catch<br><em>the light.</em></strong><span class="c-tilt__glare"></span></div></div>`, tags: ["perspective", "pointer"] },
  { name: "Cipher", cat: "Text", desc: "Letters scramble, then settle into the word. Hover or focus to replay.", html: `<span class="c-scramble" data-comp="scramble" tabindex="0" data-text="Motion Field">Motion Field</span>`, tags: ["text", "requestAnimationFrame"] },
  { name: "Latch", cat: "Input", desc: "A switch with a squash-and-stretch knob.", html: `<button class="c-toggle" type="button" role="switch" aria-checked="false" aria-label="Demo switch" data-comp="toggle"><span></span></button>`, tags: ["spring", "accessible switch"] },
  { name: "Tidewave", cat: "Loader", desc: "Five bars breathing in a wave.", html: `<span class="c-bars" role="img" aria-label="Loading"><i></i><i></i><i></i><i></i><i></i></span>`, tags: ["stagger"] },
  { name: "Splash", cat: "Button", desc: "A ripple blooms from the exact spot you click.", html: `<button class="c-ripple" type="button" data-comp="ripple">Click anywhere</button>`, tags: ["click feedback"] },
  { name: "Lantern", cat: "Card", desc: "A soft spotlight follows the pointer around the border.", html: `<div class="c-spot" data-comp="spotlight"><span class="mono">Spotlight</span><strong>Hover to<br>light it up</strong></div>`, tags: ["radial-gradient", "pointer"] },
  { name: "Glide", cat: "Navigation", desc: "Tabs with an indicator that slides between choices.", html: `<div class="c-tabs" data-comp="tabs"><button type="button" class="is-on">Work</button><button type="button">Studio</button><button type="button">Notes</button><span class="c-tabs__ink"></span></div>`, tags: ["layout animation"] },
  { name: "Energy dial", cat: "Input", desc: "Turn it up and a tiny world wiggles harder. The best motion knows when to hush.", html: `<div class="c-dial" data-comp="dial"><div class="c-dial__stage"><i></i><i></i><i></i></div><label class="c-dial__label"><span class="mono">Energy</span><input type="range" min="0" max="100" value="45" aria-label="Motion energy"><output class="mono">45%</output></label></div>`, tags: ["range input", "CSS variables"] }
];
const compCode = {
  Lodestar: library[8].code,
  Halo: ".orbit i { position:absolute; inset:0; border-radius:50%;\n  border:2px solid transparent; border-top-color:currentColor;\n  animation: spin 1.2s linear infinite; }\n.orbit i:nth-child(2){ inset:10px; animation-duration:1.8s; animation-direction:reverse; }\n.orbit i:nth-child(3){ inset:20px; animation-duration:.9s; }\n@keyframes spin { to { transform: rotate(1turn); } }",
  Prism: "card.addEventListener('pointermove', (e) => {\n  const r = card.getBoundingClientRect();\n  const x = (e.clientX - r.left) / r.width - .5;\n  const y = (e.clientY - r.top) / r.height - .5;\n  card.style.transform = `rotateX(${-y * 12}deg) rotateY(${x * 14}deg)`;\n  card.style.setProperty('--gx', (x + .5) * 100 + '%');\n  card.style.setProperty('--gy', (y + .5) * 100 + '%');\n});",
  Cipher: "const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ✦*#';\nfunction scramble(el, text) {\n  let frame = 0;\n  const tick = () => {\n    el.textContent = [...text].map((c, i) =>\n      i < frame / 2 ? c : chars[Math.random() * chars.length | 0]).join('');\n    if (frame++ < text.length * 2) requestAnimationFrame(tick);\n  };\n  tick();\n}",
  Latch: ".switch span { transition: transform .45s cubic-bezier(.5,1.6,.4,1), width .2s; }\n.switch:active span { width: 34px; }\n.switch[aria-checked=true] span { transform: translateX(28px); }",
  Tidewave: ".bars i { animation: wave 1s ease-in-out infinite;\n  animation-delay: calc(var(--i) * 90ms); }\n@keyframes wave { 50% { transform: scaleY(.3); } }",
  Splash: "btn.addEventListener('pointerdown', (e) => {\n  const r = btn.getBoundingClientRect();\n  const dot = document.createElement('span');\n  dot.className = 'ripple';\n  dot.style.left = e.clientX - r.left + 'px';\n  dot.style.top = e.clientY - r.top + 'px';\n  btn.append(dot);\n  dot.addEventListener('animationend', () => dot.remove());\n});",
  Lantern: ".card { background:\n  radial-gradient(240px at var(--mx) var(--my), rgb(213 255 63 / .25), transparent 70%),\n  #121310; }\n/* update --mx / --my on pointermove */",
  Glide: "tabs.addEventListener('click', (e) => {\n  const b = e.target.closest('button'); if (!b) return;\n  ink.style.transform = `translateX(${b.offsetLeft}px)`;\n  ink.style.width = b.offsetWidth + 'px';\n});",
  "Energy dial": "range.addEventListener('input', () => {\n  stage.style.setProperty('--energy', range.value / 100);\n});\n/* .shape { animation: wiggle calc(2.4s - var(--energy) * 1.6s) ease-in-out infinite;\n   --amp: calc(var(--energy) * 18px); } */"
};
components.forEach((c) => { c.code = compCode[c.name]; c.category = c.cat; c.label = c.cat; c.title = c.name; });

const shaders = [
  ["Lime Mesh", "Gradient", "mesh", "#0b0c0a,#1f3d1a,#d5ff3f"],
  ["Ink Swirl", "Swirl", "swirl", "#06070a,#2b3cbf,#f2f0e7"],
  ["Halftone Tide", "Halftone", "halftone", "#0a1330,#3d6bff,#bfe3ff"],
  ["Aurora Field", "Aurora", "aurora", "#04060c,#21d4a2,#8a5cff"],
  ["Ember Flow", "Flow", "flow", "#120604,#f45d3e,#ffc46b"],
  ["Ripple Pool", "Ripple", "ripple", "#051822,#2fa6c9,#e9fbff"],
  ["Peach Mesh", "Gradient", "mesh", "#f6c9a3,#f45d3e,#5b2bd0"],
  ["Mono Halftone", "Halftone", "halftone", "#0b0c0a,#55554f,#f2f0e7"],
  ["Violet Swirl", "Swirl", "swirl", "#12051f,#8a5cff,#ffb3e6"],
  ["Ocean Flow", "Flow", "flow", "#020a14,#1c5bd6,#7ff0ff"],
  ["Citrus Swirl", "Swirl", "swirl", "#1a1500,#d5ff3f,#ff9f1c"],
  ["Midnight Aurora", "Aurora", "aurora", "#020306,#2b3cbf,#d5ff3f"]
].map(([title, cat, mode, palette]) => ({ title, cat, category: cat, label: cat, mode, palette, desc: `A live ${cat.toLowerCase()} background rendered on the GPU. Drop it behind a hero, a card or a closing call to action.`, tags: ["WebGL", "GLSL", cat.toLowerCase()], code: shaderSnippet(mode) }));

const sectionsData = [
  { title: "Glass Orbit", cat: "Hero", desc: "Full-bleed video hero that shrinks into a framed card as the page scrolls.", tags: ["sticky", "clip-path"], mock: "hero" },
  { title: "Tiers in Drift", cat: "Pricing", desc: "Three plans that rise in sequence, with the recommended one gently breathing.", tags: ["stagger", "hover lift"], mock: "pricing" },
  { title: "Field Bento", cat: "Features", desc: "A bento grid where every tile has its own small loop.", tags: ["grid", "micro-motion"], mock: "bento" },
  { title: "Kind Words", cat: "Testimonial", desc: "Two rows of quotes drifting in opposite directions, pausing on hover.", tags: ["marquee", "pause on hover"], mock: "quotes" },
  { title: "Halftone Sign-off", cat: "CTA", desc: "A closing call to action over a halftone shader, with an email field.", tags: ["WebGL", "form"], mock: "cta" },
  { title: "Wordmark Bleed", cat: "Footer", desc: "Oversized wordmark that parallaxes past the bottom edge of the page.", tags: ["parallax", "type"], mock: "footer" }
];
const screensData = [
  { title: "Motion Analytics", cat: "Dashboard", desc: "Bars that grow in on arrival and a number that counts up, nothing more.", tags: ["count-up", "stagger"], mock: "analytics" },
  { title: "Night Wallet", cat: "Finance", desc: "A card with a living shader surface and a balance that settles in.", tags: ["WebGL", "card"], mock: "wallet" },
  { title: "Field Radio", cat: "Media", desc: "A player whose waveform dances only while it plays.", tags: ["state-driven motion"], mock: "player" },
  { title: "Daily Rings", cat: "Health", desc: "Progress rings that close with an easing you can feel.", tags: ["SVG", "stroke"], mock: "rings" },
  { title: "Drift Board", cat: "Projects", desc: "A kanban board where cards glide between columns.", tags: ["FLIP", "layout"], mock: "kanban" }
];
[...sectionsData, ...screensData].forEach((s) => {
  s.category = s.cat; s.label = s.cat;
  s.code = `<!-- ${s.title} / ${s.cat} -->\n<section class="${s.mock}">\n  <!-- structure: see the prompt -->\n</section>\n\n/* Motion notes */\n/* ${s.tags.join(", ")} */\n/* Animate only transform and opacity; add a reduced-motion fallback. */`;
});

const COUNTS = { library: library.length, components: components.length, shaders: shaders.length, sections: sectionsData.length, screens: screensData.length, blueprints: sectionsData.length + screensData.length };

function buildPrompt(it) {
  return `Build a "${it.title}" ${String(it.label || it.cat).toLowerCase()} for a website.

The feeling: ${it.desc}

Requirements
- Plain HTML, CSS and vanilla JavaScript. No build step; a CDN library only if it clearly helps.
- Key techniques: ${(it.tags || []).join(", ")}.
- Smooth at 60fps: animate transform, opacity or a canvas/WebGL surface only; use requestAnimationFrame and passive listeners.
- Respect prefers-reduced-motion with a calm, static fallback.
- Keyboard and touch friendly, readable contrast, responsive from 360px to 1440px.
- Premium and restrained: no bouncy gimmicks, no stock AI look.

Start from this sketch and refine it:
${it.code}`;
}

/* ------------------------------------------------------------------ */
/* GPU shader engine: one WebGL context paints every visible tile.     */
/* ------------------------------------------------------------------ */
const ShaderEngine = (() => {
  const glc = $("#gl-canvas");
  let gl = null, prog = null, loc = {};
  const tiles = new Map(); // canvas -> state
  const visible = new Set();
  let running = false, last = 0;
  const t0 = performance.now();

  try {
    gl = glc.getContext("webgl", { preserveDrawingBuffer: true, antialias: false, alpha: false, powerPreference: "low-power" });
  } catch (e) { gl = null; }

  if (gl) {
    const frag = `${GLSL_HEAD}
uniform int u_mode;
void main(){
  vec2 uv = gl_FragCoord.xy / u_res;
  vec2 p = (gl_FragCoord.xy - 0.5 * u_res) / min(u_res.x, u_res.y);
  vec3 col = u_c1;
${SHADER_MODES.map((m, i) => `  ${i ? "else " : ""}if (u_mode == ${i}) {\n${GLSL_BODIES[m]}\n  }`).join("\n")}
  col += (hash(gl_FragCoord.xy + u_time) - 0.5) * 0.04;
  col *= 1.0 - 0.18 * length(uv - 0.5);
  gl_FragColor = vec4(col, 1.0);
}`;
    const vert = "attribute vec2 a; void main(){ gl_Position = vec4(a, 0.0, 1.0); }";
    const sh = (type, src) => { const s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s); if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) { console.warn(gl.getShaderInfoLog(s)); return null; } return s; };
    const vs = sh(gl.VERTEX_SHADER, vert), fs = sh(gl.FRAGMENT_SHADER, frag);
    if (vs && fs) {
      prog = gl.createProgram(); gl.attachShader(prog, vs); gl.attachShader(prog, fs); gl.linkProgram(prog);
      if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) { prog = null; }
    }
    if (prog) {
      gl.useProgram(prog);
      const buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buf);
      gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, 1]), gl.STATIC_DRAW);
      const a = gl.getAttribLocation(prog, "a"); gl.enableVertexAttribArray(a); gl.vertexAttribPointer(a, 2, gl.FLOAT, false, 0, 0);
      ["u_res", "u_time", "u_mouse", "u_c1", "u_c2", "u_c3", "u_mode"].forEach((n) => (loc[n] = gl.getUniformLocation(prog, n)));
    }
  }
  const ok = !!prog;
  const hex = (h) => { const n = parseInt(h.replace("#", ""), 16); return [(n >> 16 & 255) / 255, (n >> 8 & 255) / 255, (n & 255) / 255]; };

  const io = "IntersectionObserver" in window ? new IntersectionObserver((entries) => {
    entries.forEach((e) => { if (e.isIntersecting) visible.add(e.target); else visible.delete(e.target); });
    if (visible.size) start();
  }, { rootMargin: "120px" }) : null;

  function paint(canvas, time) {
    const st = tiles.get(canvas); if (!st) return;
    const cw = canvas.clientWidth, ch = canvas.clientHeight; if (!cw || !ch) return;
    const q = Math.min(window.devicePixelRatio || 1, 1.5) * 0.7;
    const scale = Math.min(q, 640 / cw, 640 / ch);
    const w = Math.max(2, Math.round(cw * scale)), h = Math.max(2, Math.round(ch * scale));
    if (canvas.width !== w || canvas.height !== h) { canvas.width = w; canvas.height = h; st.ctx = canvas.getContext("2d"); }
    st.mx += (st.tx - st.mx) * 0.08; st.my += (st.ty - st.my) * 0.08;
    gl.viewport(0, 0, w, h);
    gl.uniform2f(loc.u_res, w, h);
    gl.uniform1f(loc.u_time, time + st.seed);
    gl.uniform2f(loc.u_mouse, st.mx, st.my);
    gl.uniform3fv(loc.u_c1, st.c[0]); gl.uniform3fv(loc.u_c2, st.c[1]); gl.uniform3fv(loc.u_c3, st.c[2]);
    gl.uniform1i(loc.u_mode, st.mode);
    gl.drawArrays(gl.TRIANGLES, 0, 6);
    st.ctx.drawImage(glc, 0, glc.height - h, w, h, 0, 0, w, h);
    st.painted = true;
  }
  function frame(now) {
    if (!visible.size || document.hidden) { running = false; return; }
    if (now - last > 1000 / 40) {
      last = now;
      const time = (now - t0) / 1000;
      visible.forEach((c) => { if (!reducedMotion || !tiles.get(c).painted) paint(c, reducedMotion ? 4 : time); });
    }
    requestAnimationFrame(frame);
  }
  function start() { if (!ok || running) return; running = true; requestAnimationFrame(frame); }
  document.addEventListener("visibilitychange", () => { if (!document.hidden) start(); });

  function register(canvas) {
    if (tiles.has(canvas)) return;
    const mode = Math.max(0, SHADER_MODES.indexOf(canvas.dataset.shader));
    const pal = (canvas.dataset.palette || "#0b0c0a,#2b3cbf,#d5ff3f").split(",");
    if (!ok) { canvas.style.background = `radial-gradient(120% 90% at 30% 20%, ${pal[2]}, ${pal[1]} 45%, ${pal[0]})`; return; }
    tiles.set(canvas, { mode, c: pal.map(hex), ctx: canvas.getContext("2d"), seed: Math.random() * 40, mx: 0, my: 0, tx: 0, ty: 0, painted: false });
    const host = canvas.parentElement;
    host.addEventListener("pointermove", (e) => {
      const r = canvas.getBoundingClientRect(), st = tiles.get(canvas);
      st.tx = clamp(((e.clientX - r.left) / r.width) * 2 - 1, -1, 1); st.ty = clamp(-(((e.clientY - r.top) / r.height) * 2 - 1), -1, 1);
    }, { passive: true });
    host.addEventListener("pointerleave", () => { const st = tiles.get(canvas); st.tx = 0; st.ty = 0; });
    if (io) io.observe(canvas); else { visible.add(canvas); start(); }
  }
  function unregisterWithin(root) { $$("canvas.shader-canvas", root).forEach((c) => { tiles.delete(c); visible.delete(c); io && io.unobserve(c); }); }
  return { register, unregisterWithin, ok, start };
})();
const mountShaders = (root = document) => $$("canvas.shader-canvas", root).forEach((c) => ShaderEngine.register(c));

/* ------------------------------------------------------------------ */
/* Preview HTML                                                        */
/* ------------------------------------------------------------------ */
function previewHTML(pv, alt) {
  if (pv.kind === "image") return `<img src="${pv.src}" alt="${esc(alt)}" loading="lazy" decoding="async">`;
  if (pv.kind === "shader") return `<canvas class="shader-canvas" data-shader="${pv.mode}" data-palette="${pv.palette}" aria-hidden="true"></canvas>`;
  return pv.html;
}

const MOCKS = {
  hero: `<div class="mk mk--hero"><img src="assets/thumbs/study-orbit.webp" alt="" loading="lazy"><div class="mk-nav"><i></i><i></i><i></i><b></b></div><div class="mk-hero__copy"><b class="mk-l mk-l--xl"></b><b class="mk-l mk-l--lg"></b><span class="mk-btn"></span></div></div>`,
  pricing: `<div class="mk mk--pricing"><div class="mk-tier"><b class="mk-l"></b><b class="mk-price">$0</b><i></i><i></i><i></i></div><div class="mk-tier is-hot"><b class="mk-l"></b><b class="mk-price">$19</b><i></i><i></i><i></i></div><div class="mk-tier"><b class="mk-l"></b><b class="mk-price">$49</b><i></i><i></i><i></i></div></div>`,
  bento: `<div class="mk mk--bento"><div class="mk-b mk-b--a"><canvas class="shader-canvas" data-shader="mesh" data-palette="#0b0c0a,#2b3cbf,#d5ff3f"></canvas></div><div class="mk-b mk-b--b"><span class="c-bars"><i></i><i></i><i></i><i></i><i></i></span></div><div class="mk-b mk-b--c"><img src="assets/thumbs/study-pulse.webp" alt="" loading="lazy"></div><div class="mk-b mk-b--d"><b class="mk-big">98<small>%</small></b></div></div>`,
  quotes: `<div class="mk mk--quotes"><div class="mk-q"><div><span>“Finally, motion with manners.”</span><span>“Shipped it the same day.”</span><span>“Feels expensive.”</span><span>“Finally, motion with manners.”</span><span>“Shipped it the same day.”</span><span>“Feels expensive.”</span></div></div><div class="mk-q mk-q--rev"><div><span>“The reveal is so calm.”</span><span>“My clients noticed.”</span><span>“No build step!”</span><span>“The reveal is so calm.”</span><span>“My clients noticed.”</span><span>“No build step!”</span></div></div></div>`,
  cta: `<div class="mk mk--cta"><canvas class="shader-canvas" data-shader="halftone" data-palette="#0b0c0a,#3d6bff,#d5ff3f"></canvas><div class="mk-cta__copy"><b>Stay in the field.</b><span class="mk-input"><i></i><em></em></span></div></div>`,
  footer: `<div class="mk mk--footer"><div class="mk-cols"><span><b></b><i></i><i></i></span><span><b></b><i></i><i></i></span><span><b></b><i></i><i></i></span></div><strong>Motion<em>Field</em></strong></div>`,
  analytics: `<div class="mk mk--analytics"><div class="mk-head"><span class="mono">Scroll depth</span><b>74%</b></div><div class="mk-bars">${[42, 60, 38, 72, 55, 88, 64, 92, 70].map((h, i) => `<i style="--h:${h}%;--i:${i}"></i>`).join("")}</div></div>`,
  wallet: `<div class="mk mk--wallet"><div class="mk-card"><canvas class="shader-canvas" data-shader="swirl" data-palette="#12051f,#8a5cff,#ffb3e6"></canvas><span class="mono">Night wallet</span><b>₹ 48,250</b><small>•••• 1411</small></div><div class="mk-rows"><i></i><i></i><i></i></div></div>`,
  player: `<div class="mk mk--player"><img src="assets/thumbs/study-tide.webp" alt="" loading="lazy"><div class="mk-pl"><b>Tide, side B</b><span class="mono">Field radio</span><div class="mk-wave">${Array.from({ length: 24 }, (_, i) => `<i style="--i:${i}"></i>`).join("")}</div></div></div>`,
  rings: `<div class="mk mk--rings"><svg viewBox="0 0 120 120" aria-hidden="true"><circle class="r r1" cx="60" cy="60" r="50"/><circle class="r r2" cx="60" cy="60" r="38"/><circle class="r r3" cx="60" cy="60" r="26"/></svg><div class="mk-rings__k"><span><i style="background:#d5ff3f"></i>Move</span><span><i style="background:#f45d3e"></i>Focus</span><span><i style="background:#6d8bff"></i>Rest</span></div></div>`,
  kanban: `<div class="mk mk--kanban"><div class="mk-col"><span class="mono">To do</span><i></i><i></i></div><div class="mk-col"><span class="mono">Doing</span><i></i><i class="mk-move"></i></div><div class="mk-col"><span class="mono">Done</span><i></i></div></div>`
};

/* ------------------------------------------------------------------ */
/* Library grid                                                        */
/* ------------------------------------------------------------------ */
const grid = $("#library-grid"), search = $("#library-search"), empty = $("#library-empty");
let libFilter = "all", libTab = "featured";
const chipsHost = $("#library-chips");
chipsHost.innerHTML = CATS.map((c) => {
  const n = c.id === "all" ? library.length : library.filter((i) => i.category === c.id).length;
  return `<button type="button" class="chip${c.id === "all" ? " is-active" : ""}" data-filter="${c.id}" aria-pressed="${c.id === "all"}">${c.label} <span>${String(n).padStart(2, "0")}</span></button>`;
}).join("");

function setLibFilter(f) {
  libFilter = f;
  $$(".chip", chipsHost).forEach((b) => { const on = b.dataset.filter === f; b.classList.toggle("is-active", on); b.setAttribute("aria-pressed", on); });
  renderLibrary();
}
function cardHTML(it, i) {
  const isNew = it.added >= 12;
  return `<article class="card" style="--i:${i % 6}" data-reveal-card>
    <button class="card__media" type="button" data-open="library:${it.id}" aria-label="Preview ${esc(it.title)}">
      ${previewHTML(it.preview, `Artwork for ${it.title}`)}
      <span class="card__glare" aria-hidden="true"></span>
      <span class="card__preview" aria-hidden="true">Preview <i>→</i></span>
      ${isNew ? '<span class="card__new">New</span>' : ""}
    </button>
    <div class="card__info">
      <div><h3>${esc(it.title)}</h3><p>${it.label} · ${it.level}</p></div>
      <span class="badge${it.badge === "Signature" ? " badge--sig" : ""}">${it.badge}</span>
    </div>
  </article>`;
}
const studioCard = `<article class="card card--studio" data-reveal-card>
  <canvas class="shader-canvas" data-shader="flow" data-palette="#0b0c0a,#2b3cbf,#d5ff3f" aria-hidden="true"></canvas>
  <div class="card--studio__body">
    <span class="eyebrow eyebrow--light">The studio</span>
    <h3>Want a motion pass on <em>your own site?</em></h3>
    <p>Bespoke scroll stories and interactions, built to your brand and never published to the library.</p>
    <a class="pill pill--lime pill--sm" href="https://www.linkedin.com/in/swapnil-agrawal-109a3321b" target="_blank" rel="noopener"><span>Start a project</span> <i aria-hidden="true">→</i></a>
  </div>
</article>`;

function renderLibrary() {
  const q = search.value.trim().toLowerCase();
  let items = library.filter((it) => (libFilter === "all" || it.category === libFilter) && [it.title, it.label, it.desc, ...it.tags].join(" ").toLowerCase().includes(q));
  if (libTab === "popular") items = [...items].sort((a, b) => b.pop - a.pop);
  else if (libTab === "recent") items = [...items].sort((a, b) => b.added - a.added);
  ShaderEngine.unregisterWithin(grid);
  const html = items.map(cardHTML);
  if (items.length >= 4 && !q) html.splice(4, 0, studioCard);
  grid.innerHTML = html.join("");
  empty.hidden = items.length > 0;
  mountShaders(grid);
  initComponents(grid);
  observeCards(grid);
}
search.addEventListener("input", renderLibrary);
chipsHost.addEventListener("click", (e) => { const b = e.target.closest(".chip"); if (b) setLibFilter(b.dataset.filter); });
$("#library-clear").addEventListener("click", () => { search.value = ""; setLibFilter("all"); });
document.addEventListener("keydown", (e) => { if (e.key === "/" && !e.metaKey && !e.ctrlKey && !["INPUT", "TEXTAREA"].includes(document.activeElement.tagName) && !$("#modal").open) { e.preventDefault(); search.focus({ preventScroll: true }); smoothTo($("#library")); } });

const tabs = $$(".tabs .tab"), tabInk = $(".tabs__ink");
function moveInk() { const a = $(".tabs .tab.is-active"); if (!a) return; tabInk.style.width = a.offsetWidth + "px"; tabInk.style.transform = `translateX(${a.offsetLeft}px)`; }
tabs.forEach((t) => t.addEventListener("click", () => {
  libTab = t.dataset.tab;
  tabs.forEach((x) => { const on = x === t; x.classList.toggle("is-active", on); x.setAttribute("aria-selected", on); });
  moveInk(); renderLibrary();
}));
window.addEventListener("resize", moveInk);
document.fonts && document.fonts.ready.then(moveInk);

/* ------------------------------------------------------------------ */
/* Strips: components, shaders, sections, screens                      */
/* ------------------------------------------------------------------ */
const strips = {
  components: { data: components, cats: ["All", "Button", "Loader", "Card", "Text", "Input", "Navigation"], render: (c, i) => `
    <article class="tile tile--comp" data-cat="${c.cat}">
      <div class="tile__stage">${c.html}</div>
      <div class="tile__info">
        <div><h3>${c.name}</h3><p>${c.cat}</p></div>
        <div class="tile__actions"><button type="button" class="mini" data-open="components:${i}">Prompt <i aria-hidden="true">↗</i></button><button type="button" class="mini mini--icon" data-copy="components:${i}" aria-label="Copy ${c.name} prompt">⧉</button></div>
      </div>
    </article>` },
  shaders: { data: shaders, cats: ["All", "Gradient", "Swirl", "Halftone", "Aurora", "Flow", "Ripple"], render: (s, i) => `
    <article class="tile tile--shader" data-cat="${s.cat}">
      <button type="button" class="tile__shader" data-open="shaders:${i}" aria-label="Open ${s.title} shader">
        <canvas class="shader-canvas" data-shader="${s.mode}" data-palette="${s.palette}" aria-hidden="true"></canvas>
        <span class="tile__overlay"><span><b>${s.title}</b><small>${s.cat}</small></span><span class="tile__go">Preview <i aria-hidden="true">→</i></span></span>
      </button>
    </article>` },
  sections: { data: sectionsData, cats: ["All", "Hero", "Pricing", "Features", "Testimonial", "CTA", "Footer"], render: (s, i) => `
    <article class="tile tile--mock" data-cat="${s.cat}">
      <button type="button" class="tile__mock" data-open="sections:${i}" aria-label="Open ${s.title} blueprint">${MOCKS[s.mock]}<span class="tile__go tile__go--float">Preview <i aria-hidden="true">→</i></span></button>
      <div class="tile__info"><div><h3>${s.title}</h3><p>${s.cat}</p></div><button type="button" class="mini mini--icon" data-copy="sections:${i}" aria-label="Copy ${s.title} prompt">⧉</button></div>
    </article>` },
  screens: { data: screensData, cats: ["All", "Dashboard", "Finance", "Media", "Health", "Projects"], render: (s, i) => `
    <article class="tile tile--mock tile--screen" data-cat="${s.cat}">
      <button type="button" class="tile__mock" data-open="screens:${i}" aria-label="Open ${s.title} screen">${MOCKS[s.mock]}<span class="tile__go tile__go--float">Preview <i aria-hidden="true">→</i></span></button>
      <div class="tile__info"><div><h3>${s.title}</h3><p>${s.cat}</p></div><button type="button" class="mini mini--icon" data-copy="screens:${i}" aria-label="Copy ${s.title} prompt">⧉</button></div>
    </article>` }
};
Object.entries(strips).forEach(([key, cfg]) => {
  const strip = $(`#${key}-strip`);
  strip.innerHTML = `<div class="strip__track">${cfg.data.map(cfg.render).join("")}</div>`;
  const chips = $(`[data-chips-for="${key}"]`);
  chips.innerHTML = cfg.cats.map((c, i) => `<button type="button" class="chip${i ? "" : " is-active"}" data-cat="${c}" aria-pressed="${!i}">${c}</button>`).join("");
  chips.addEventListener("click", (e) => {
    const b = e.target.closest(".chip"); if (!b) return;
    $$(".chip", chips).forEach((x) => { const on = x === b; x.classList.toggle("is-active", on); x.setAttribute("aria-pressed", on); });
    $$(".tile", strip).forEach((t) => { const show = b.dataset.cat === "All" || t.dataset.cat === b.dataset.cat; t.hidden = !show; if (show) { t.classList.remove("is-pop"); void t.offsetWidth; t.classList.add("is-pop"); } });
    strip.scrollTo({ left: 0, behavior: reducedMotion ? "auto" : "smooth" });
  });
  mountShaders(strip);
  initComponents(strip);
  setupDragScroll(strip);
});
$$("[data-strip-prev],[data-strip-next]").forEach((b) => b.addEventListener("click", () => {
  const strip = $("#" + (b.dataset.stripPrev || b.dataset.stripNext));
  strip.scrollBy({ left: (b.dataset.stripPrev ? -1 : 1) * strip.clientWidth * 0.8, behavior: reducedMotion ? "auto" : "smooth" });
}));

function setupDragScroll(strip) {
  let down = false, sx = 0, sl = 0, moved = 0;
  strip.addEventListener("pointerdown", (e) => {
    if (e.pointerType !== "mouse" || e.button !== 0 || e.target.closest("input,.c-tabs,.c-toggle,.c-ripple,.c-magnet,.c-tilt,.c-spot")) return;
    down = true; moved = 0; sx = e.clientX; sl = strip.scrollLeft; strip.classList.add("is-dragging");
  });
  window.addEventListener("pointermove", (e) => { if (!down) return; const dx = e.clientX - sx; moved = Math.max(moved, Math.abs(dx)); strip.scrollLeft = sl - dx; });
  window.addEventListener("pointerup", () => { if (!down) return; down = false; strip.classList.remove("is-dragging"); });
  strip.addEventListener("click", (e) => { if (moved > 6) { e.preventDefault(); e.stopPropagation(); moved = 0; } }, true);
}

/* ------------------------------------------------------------------ */
/* Live component behaviours                                           */
/* ------------------------------------------------------------------ */
function initComponents(root) {
  $$("[data-comp]", root).forEach((el) => {
    if (el.dataset.ready) return; el.dataset.ready = "1";
    const kind = el.dataset.comp;
    if (kind === "magnet") {
      const host = el.closest(".tile__stage,.pv,.modal__preview") || el.parentElement;
      host.addEventListener("pointermove", (e) => {
        if (reducedMotion) return;
        const r = el.getBoundingClientRect();
        const x = e.clientX - (r.left + r.width / 2), y = e.clientY - (r.top + r.height / 2);
        const pull = Math.max(0, 1 - Math.hypot(x, y) / 220);
        el.style.transform = `translate(${x * 0.4 * pull}px, ${y * 0.4 * pull}px)`;
        el.firstElementChild.style.transform = `translate(${x * 0.15 * pull}px, ${y * 0.15 * pull}px)`;
        el.classList.toggle("is-near", pull > 0.55);
      }, { passive: true });
      host.addEventListener("pointerleave", () => { el.style.transform = ""; el.firstElementChild.style.transform = ""; el.classList.remove("is-near"); });
    }
    if (kind === "tilt" || kind === "stack") {
      const target = kind === "tilt" ? el.firstElementChild : el;
      el.addEventListener("pointermove", (e) => {
        if (reducedMotion) return;
        const r = el.getBoundingClientRect(), x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5;
        target.style.setProperty("--x", x.toFixed(3)); target.style.setProperty("--y", y.toFixed(3));
        target.style.setProperty("--gx", ((x + 0.5) * 100).toFixed(1) + "%"); target.style.setProperty("--gy", ((y + 0.5) * 100).toFixed(1) + "%");
        target.classList.add("is-active");
      }, { passive: true });
      el.addEventListener("pointerleave", () => { ["--x", "--y"].forEach((p) => target.style.setProperty(p, 0)); target.classList.remove("is-active"); });
    }
    if (kind === "scramble") {
      const text = el.dataset.text, chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ✦*#/";
      let raf = 0;
      const run = () => {
        if (reducedMotion) return;
        cancelAnimationFrame(raf); let f = 0;
        const tick = () => {
          el.textContent = [...text].map((c, i) => (c === " " || i < f / 2.2 ? c : chars[(Math.random() * chars.length) | 0])).join("");
          if (f++ < text.length * 2.2 + 2) raf = requestAnimationFrame(tick); else el.textContent = text;
        };
        tick();
      };
      el.addEventListener("pointerenter", run); el.addEventListener("focus", run);
      setTimeout(run, 900);
    }
    if (kind === "toggle") el.addEventListener("click", () => el.setAttribute("aria-checked", el.getAttribute("aria-checked") !== "true"));
    if (kind === "ripple") el.addEventListener("pointerdown", (e) => {
      const r = el.getBoundingClientRect(), dot = document.createElement("span");
      dot.className = "c-ripple__dot"; dot.style.left = e.clientX - r.left + "px"; dot.style.top = e.clientY - r.top + "px";
      el.append(dot); dot.addEventListener("animationend", () => dot.remove()); setTimeout(() => dot.remove(), 1200);
    });
    if (kind === "spotlight") el.addEventListener("pointermove", (e) => {
      const r = el.getBoundingClientRect(); el.style.setProperty("--mx", e.clientX - r.left + "px"); el.style.setProperty("--my", e.clientY - r.top + "px");
    }, { passive: true });
    if (kind === "tabs") {
      const ink = $(".c-tabs__ink", el);
      const place = (b) => { ink.style.width = b.offsetWidth + "px"; ink.style.transform = `translateX(${b.offsetLeft}px)`; };
      el.addEventListener("click", (e) => { const b = e.target.closest("button"); if (!b) return; $$("button", el).forEach((x) => x.classList.toggle("is-on", x === b)); place(b); });
      requestAnimationFrame(() => place($(".is-on", el)));
      window.addEventListener("resize", () => place($(".is-on", el)));
    }
    if (kind === "dial") {
      const input = $("input", el), out = $("output", el), stage = $(".c-dial__stage", el);
      const upd = () => { stage.style.setProperty("--energy", (input.value / 100).toFixed(2)); out.textContent = input.value + "%"; };
      input.addEventListener("input", upd); upd();
    }
  });
}

/* ------------------------------------------------------------------ */
/* Modal + copy                                                        */
/* ------------------------------------------------------------------ */
const modal = $("#modal"), mPreview = $("#modal-preview"), mCode = $("#modal-code"), mCopy = $("#modal-copy");
let mItem = null, mTab = "prompt";
const lookup = (ref) => {
  const [group, key] = ref.split(":");
  if (group === "library") return library.find((i) => i.id === key);
  return { components, shaders, sections: sectionsData, screens: screensData }[group][+key];
};
function setModalTab(tab) {
  mTab = tab;
  $$("[data-modal-tab]").forEach((b) => { const on = b.dataset.modalTab === tab; b.classList.toggle("is-active", on); b.setAttribute("aria-selected", on); });
  mCode.textContent = tab === "prompt" ? buildPrompt(mItem) : mItem.code;
  mCopy.firstElementChild.textContent = tab === "prompt" ? "Copy prompt" : "Copy code";
  mCode.parentElement.scrollTop = 0;
}
function openModal(ref) {
  const it = lookup(ref); if (!it) return;
  mItem = it;
  ShaderEngine.unregisterWithin(mPreview);
  let pv;
  if (it.preview) pv = previewHTML(it.preview.kind === "image" ? { kind: "image", src: it.preview.src.replace("thumbs/", "") } : it.preview, `Artwork for ${it.title}`);
  else if (it.mode) pv = `<canvas class="shader-canvas" data-shader="${it.mode}" data-palette="${it.palette}" aria-hidden="true"></canvas>`;
  else if (it.html) pv = `<div class="modal__stage">${it.html}</div>`;
  else pv = `<div class="modal__stage modal__stage--mock">${MOCKS[it.mock]}</div>`;
  mPreview.innerHTML = pv;
  $("#modal-kicker").textContent = `${it.label || it.cat}${it.id ? " · Study " + it.id : ""}`;
  $("#modal-title").textContent = it.title;
  $("#modal-desc").textContent = it.desc;
  $("#modal-tags").innerHTML = (it.tags || []).map((t) => `<span>${esc(t)}</span>`).join("") + (it.level ? `<span>${it.level} energy</span>` : "");
  const live = $("#modal-live");
  const liveId = it.id && +it.id <= 6 ? `#lab-${it.id}` : null;
  live.hidden = !liveId; if (liveId) live.setAttribute("href", liveId);
  setModalTab("prompt");
  modal.showModal();
  document.documentElement.classList.add("modal-open");
  lenis && lenis.stop();
  requestAnimationFrame(() => { mountShaders(mPreview); initComponents(mPreview); });
}
modal.addEventListener("close", () => { document.documentElement.classList.remove("modal-open"); lenis && lenis.start(); ShaderEngine.unregisterWithin(mPreview); });
$(".modal__close").addEventListener("click", () => modal.close());
modal.addEventListener("click", (e) => { if (e.target === modal) modal.close(); });
$$("[data-modal-tab]").forEach((b) => b.addEventListener("click", () => setModalTab(b.dataset.modalTab)));
mCopy.addEventListener("click", () => copyText(mTab === "prompt" ? buildPrompt(mItem) : mItem.code, mTab === "prompt" ? "Prompt copied. Paste it into your AI." : "Code copied. Make it yours."));

document.addEventListener("click", (e) => {
  const open = e.target.closest("[data-open]"); if (open) { e.preventDefault(); openModal(open.dataset.open); return; }
  const cp = e.target.closest("[data-copy]"); if (cp) { const it = lookup(cp.dataset.copy); copyText(buildPrompt(it), `${it.title} prompt copied.`); }
});

const toast = $("#toast"); let toastTimer;
function showToast(msg) { toast.textContent = msg; toast.classList.add("is-on"); clearTimeout(toastTimer); toastTimer = setTimeout(() => toast.classList.remove("is-on"), 2400); }
async function copyText(text, msg) {
  try { await navigator.clipboard.writeText(text); }
  catch { const ta = document.createElement("textarea"); ta.value = text; ta.style.cssText = "position:fixed;opacity:0"; (modal.open ? modal : document.body).append(ta); ta.select(); try { document.execCommand("copy"); } catch {} ta.remove(); }
  showToast(msg);
}

/* ------------------------------------------------------------------ */
/* Smooth scroll + scroll choreography                                 */
/* ------------------------------------------------------------------ */
let lenis = null;
function initLenis() {
  if (reducedMotion || !window.Lenis) return;
  lenis = new window.Lenis({ lerp: 0.09, smoothWheel: true, wheelMultiplier: 1 });
  const raf = (t) => { lenis.raf(t); requestAnimationFrame(raf); };
  requestAnimationFrame(raf);
  lenis.on("scroll", onScroll);
}
function smoothTo(el) {
  if (!el) return;
  if (lenis) lenis.scrollTo(el, { offset: -64, duration: 1.3 });
  else el.scrollIntoView({ behavior: reducedMotion ? "auto" : "smooth", block: "start" });
}
document.addEventListener("click", (e) => {
  const a = e.target.closest('a[href^="#"]'); if (!a) return;
  const id = a.getAttribute("href"); const el = id === "#main" || id === "#top" ? document.body : $(id);
  if (!el) return;
  e.preventDefault();
  if (a.dataset.jumpFilter) { search.value = ""; setLibFilter(a.dataset.jumpFilter); }
  if (modal.open) modal.close();
  closeMenu();
  if (el === document.body) { lenis ? lenis.scrollTo(0) : scrollTo({ top: 0, behavior: reducedMotion ? "auto" : "smooth" }); }
  else smoothTo(el);
});

const hero = $("#hero"), heroMedia = $("#hero-media"), heroContent = $("#hero-content"), heroStatement = $("#hero-statement"), heroAside = $("#hero-aside");
const nav = $(".nav"), bar = $("#progress-bar");
const workflow = $("#workflow"), steps = $$(".step"), wfFill = $("#workflow-fill"), wfLabel = $("#workflow-step");
const parallaxEls = $$("[data-speed]");
const driftEls = $$("[data-drift]");
const labPath = $("#lab-path-line"), labHead = $("#lab-path-head"), labPct = $("#lab-path-pct");
const pathLen = labPath ? labPath.getTotalLength() : 0;
if (labPath) { labPath.style.strokeDasharray = pathLen; labPath.style.strokeDashoffset = pathLen; }
let ticking = false;
function onScroll() { if (!ticking) { ticking = true; requestAnimationFrame(update); } }
function update() {
  ticking = false;
  const y = window.scrollY, vh = innerHeight;
  const max = document.documentElement.scrollHeight - vh;
  bar.style.transform = `scaleX(${max > 0 ? clamp(y / max) : 0})`;
  nav.classList.toggle("is-scrolled", y > 30);

  // Hero: pinned; video frame tucks into a card while copy lifts away
  const hr = hero.getBoundingClientRect();
  const span = Math.max(1, hr.height - vh);
  const p = reducedMotion ? 0 : clamp(-hr.top / span);
  hero.style.setProperty("--p", p.toFixed(4));
  heroContent.style.opacity = clamp(1 - p * 2.1).toFixed(3);
  hero.style.setProperty("--cy", (-p * 140).toFixed(1) + "px");
  heroAside.style.opacity = clamp(1 - p * 3).toFixed(3);
  const s = clamp((p - 0.42) / 0.38);
  heroStatement.style.opacity = s.toFixed(3);
  heroStatement.style.transform = `translate3d(-50%, calc(-50% + ${((1 - s) * 40).toFixed(1)}px), 0)`;

  // Workflow: rail fill + active step
  const wr = workflow.getBoundingClientRect();
  const wp = clamp((vh * 0.55 - wr.top) / (wr.height - vh * 0.3));
  wfFill.style.transform = `scaleY(${wp.toFixed(3)})`;
  let active = 0;
  steps.forEach((st, i) => { const r = st.getBoundingClientRect(); if (r.top < vh * 0.62) active = i; });
  steps.forEach((st, i) => st.classList.toggle("is-active", i === active && wr.top < vh * 0.7));
  wfLabel.textContent = `0${active + 1} / 03`;

  // Study 01: tide drift, scroll-linked horizontal movement
  driftEls.forEach((el) => {
    const r = el.parentElement.getBoundingClientRect();
    if (r.bottom < -100 || r.top > vh + 100) return;
    const prog = clamp((vh - r.top) / (vh + r.height));
    el.style.transform = `translate3d(${(reducedMotion ? 0 : (prog - 0.5) * parseFloat(el.dataset.drift)).toFixed(2)}vw, 0, 0)`;
  });

  // Study 05: path draws with scroll
  if (labPath) {
    const r = labPath.closest(".lab-path").getBoundingClientRect();
    const prog = reducedMotion ? 1 : clamp((vh * 0.92 - r.top) / (vh * 0.75));
    labPath.style.strokeDashoffset = (pathLen * (1 - prog)).toFixed(1);
    const pt = labPath.getPointAtLength(pathLen * prog);
    labHead.setAttribute("cx", pt.x.toFixed(1)); labHead.setAttribute("cy", pt.y.toFixed(1));
    labPct.textContent = Math.round(prog * 100) + "%";
    labPath.closest(".lab-path").classList.toggle("is-done", prog > 0.995);
  }

  // Parallax
  if (!reducedMotion) parallaxEls.forEach((el) => {
    const r = el.parentElement.getBoundingClientRect();
    if (r.bottom < -200 || r.top > vh + 200) return;
    el.style.transform = `translate3d(${((r.top - vh / 2) * parseFloat(el.dataset.speed)).toFixed(1)}px, 0, 0)`;
  });
}
window.addEventListener("scroll", () => { if (!lenis) onScroll(); }, { passive: true });
window.addEventListener("resize", onScroll);

/* Reveals */
const revealIO = "IntersectionObserver" in window && !reducedMotion ? new IntersectionObserver((entries) => {
  entries.forEach((e) => { if (e.isIntersecting) { e.target.classList.add("is-in"); revealIO.unobserve(e.target); } });
}, { threshold: 0.12, rootMargin: "0px 0px -6% 0px" }) : null;
function observeCards(root) {
  $$("[data-reveal-card]", root).forEach((el) => { if (revealIO) { el.classList.add("will-reveal"); revealIO.observe(el); } });
}
$$("[data-reveal]").forEach((el) => { if (revealIO) { el.classList.add("will-reveal"); revealIO.observe(el); } });
$$(".step,.lab-panel").forEach((el) => { if (revealIO) { el.classList.add("will-reveal"); revealIO.observe(el); } });
$$(".strip .tile").forEach((el, i) => { el.style.setProperty("--i", i % 6); if (revealIO) { el.classList.add("will-reveal"); revealIO.observe(el); } });

/* Counts + count-up */
$$("[data-count-of]").forEach((el) => (el.textContent = String(COUNTS[el.dataset.countOf]).padStart(2, "0")));
const countIO = "IntersectionObserver" in window ? new IntersectionObserver((entries) => {
  entries.forEach((e) => {
    if (!e.isIntersecting) return; countIO.unobserve(e.target);
    const el = e.target, to = COUNTS[el.dataset.countup];
    if (reducedMotion) { el.textContent = to; return; }
    const t0 = performance.now(), dur = 1500;
    const tick = (now) => { const k = clamp((now - t0) / dur), eased = 1 - Math.pow(1 - k, 4); el.textContent = Math.round(to * eased); if (k < 1) requestAnimationFrame(tick); };
    requestAnimationFrame(tick);
  });
}, { threshold: 0.6 }) : null;
$$("[data-countup]").forEach((el) => (countIO ? countIO.observe(el) : (el.textContent = COUNTS[el.dataset.countup])));

/* Magnetic CTAs */
if (finePointer) $$(".magnetic").forEach((el) => {
  el.addEventListener("pointermove", (e) => {
    if (reducedMotion) return;
    const r = el.getBoundingClientRect();
    el.style.setProperty("--mx", ((e.clientX - r.left - r.width / 2) * 0.22).toFixed(1) + "px");
    el.style.setProperty("--my", ((e.clientY - r.top - r.height / 2) * 0.3).toFixed(1) + "px");
  }, { passive: true });
  el.addEventListener("pointerleave", () => { el.style.setProperty("--mx", "0px"); el.style.setProperty("--my", "0px"); });
});

/* Card tilt + glare on library cards */
grid.addEventListener("pointermove", (e) => {
  if (!finePointer || reducedMotion) return;
  const m = e.target.closest(".card__media"); if (!m) return;
  const r = m.getBoundingClientRect(), x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5;
  m.style.setProperty("--rx", (-y * 5).toFixed(2) + "deg"); m.style.setProperty("--ry", (x * 6).toFixed(2) + "deg");
  m.style.setProperty("--gx", ((x + 0.5) * 100).toFixed(1) + "%"); m.style.setProperty("--gy", ((y + 0.5) * 100).toFixed(1) + "%");
}, { passive: true });
grid.addEventListener("pointerout", (e) => { const m = e.target.closest(".card__media"); if (m && !m.contains(e.relatedTarget)) { m.style.setProperty("--rx", "0deg"); m.style.setProperty("--ry", "0deg"); } });

/* Mobile menu */
const toggle = $(".nav__toggle"), links = $("#nav-links");
function closeMenu() { toggle.setAttribute("aria-expanded", "false"); toggle.setAttribute("aria-label", "Open menu"); links.classList.remove("is-open"); document.documentElement.classList.remove("menu-open"); }
toggle.addEventListener("click", () => {
  const open = toggle.getAttribute("aria-expanded") !== "true";
  toggle.setAttribute("aria-expanded", open); toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
  links.classList.toggle("is-open", open); document.documentElement.classList.toggle("menu-open", open);
});
document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeMenu(); });

/* Newsletter (front-end only) */
const form = $("#newsletter"), msg = $("#newsletter-msg"), email = $("#newsletter-email");
form.addEventListener("submit", (e) => {
  e.preventDefault();
  const v = email.value.trim();
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v)) { form.classList.add("is-error"); msg.textContent = "That email looks a little off. Mind checking it?"; email.focus(); return; }
  form.classList.remove("is-error"); form.classList.add("is-done");
  try { localStorage.setItem("motion-field-subscriber", v); } catch {}
  msg.innerHTML = `<b>✦ You're on the list.</b> The next issue will find you at ${esc(v)}.`;
  email.value = ""; email.blur();
});
email.addEventListener("input", () => form.classList.remove("is-error"));

/* Hero video: pause when offscreen, respect reduced motion */
const video = $(".hero__video");
if (reducedMotion) { video.removeAttribute("autoplay"); video.pause(); }
else if ("IntersectionObserver" in window) new IntersectionObserver(([e]) => { e.isIntersecting ? video.play().catch(() => {}) : video.pause(); }).observe(video);
reduceMQ.addEventListener && reduceMQ.addEventListener("change", (e) => { reducedMotion = e.matches; });


/* ------------------------------------------------------------------ */
/* Live lab: the six founding studies, running for real               */
/* ------------------------------------------------------------------ */
// Study 02: pointer-parallax orbit (idle drift on touch / no pointer)
$$("[data-orbit]").forEach((panel) => {
  const scene = $(".lab-orbit__scene", panel);
  let tx = 0, ty = 0, x = 0, y = 0, raf = 0, active = false, visible = false;
  const loop = (t) => {
    if (!active) { tx = Math.sin(t / 2400) * 0.35; ty = Math.cos(t / 3100) * 0.3; }
    x += (tx - x) * 0.07; y += (ty - y) * 0.07;
    scene.style.setProperty("--x", x.toFixed(3)); scene.style.setProperty("--y", y.toFixed(3));
    raf = visible && !reducedMotion ? requestAnimationFrame(loop) : 0;
  };
  panel.addEventListener("pointermove", (e) => {
    const r = panel.getBoundingClientRect(); active = true;
    tx = ((e.clientX - r.left) / r.width - 0.5) * 2; ty = ((e.clientY - r.top) / r.height - 0.5) * 2;
  }, { passive: true });
  panel.addEventListener("pointerleave", () => { active = false; });
  if ("IntersectionObserver" in window) new IntersectionObserver(([en]) => { visible = en.isIntersecting; if (visible && !raf && !reducedMotion) raf = requestAnimationFrame(loop); }).observe(panel);
});

// Study 03: blur-to-clear reveal
const blurStages = $$("[data-blur-reveal]");
const blurIO = "IntersectionObserver" in window ? new IntersectionObserver((entries) => entries.forEach((e) => { if (e.isIntersecting) e.target.classList.add("is-ready"); }), { threshold: 0.45 }) : null;
blurStages.forEach((el) => (blurIO && !reducedMotion ? blurIO.observe(el) : el.classList.add("is-ready")));

// Study 04: letter stagger
$$("[data-letters]").forEach((el) => {
  const text = el.textContent;
  el.innerHTML = text.split(" ").map((w) => `<span class="word" aria-hidden="true">${[...w].map((c) => `<span class="letter">${esc(c)}</span>`).join("")}</span>`).join(" ");
  $$(".letter", el).forEach((l, i) => l.style.setProperty("--delay", i * 42 + "ms"));
  const play = () => { el.classList.remove("is-in"); void el.offsetWidth; el.classList.add("is-in"); };
  if ("IntersectionObserver" in window && !reducedMotion) {
    const io = new IntersectionObserver(([en]) => { if (en.isIntersecting) { play(); io.disconnect(); } }, { threshold: 0.6 }); io.observe(el);
  } else el.classList.add("is-in");
  let last = 0;
  el.closest(".lab-panel").addEventListener("pointerenter", () => { const now = Date.now(); if (now - last > 1400 && !reducedMotion) { last = now; play(); } });
});

$$("[data-replay]").forEach((b) => b.addEventListener("click", () => {
  const st = b.closest(".lab-panel").querySelector("[data-blur-reveal]");
  st.classList.remove("is-ready"); void st.offsetWidth; setTimeout(() => st.classList.add("is-ready"), 350);
}));

// Playground: the wiggle-energy dial (from the original site)
const motionRange = $("#motion-range"), stage = $("#playground-stage"), motionValue = $("#motion-value"), motionLevel = $("#motion-level");
function updateMotion() {
  const amount = Number(motionRange.value);
  stage.style.setProperty("--energy", (amount / 100).toFixed(2));
  motionValue.textContent = `${amount}%`;
  motionLevel.textContent = amount < 28 ? "Barely a breath" : amount < 72 ? "A little wiggle" : "Full-body wiggle";
  motionRange.style.setProperty("--fill", amount + "%");
}
motionRange.addEventListener("input", updateMotion); updateMotion();
stage.addEventListener("pointermove", (e) => {
  const b = stage.getBoundingClientRect();
  stage.style.setProperty("--pointer-x", ((e.clientX - b.left) / b.width - 0.5).toFixed(2));
  stage.style.setProperty("--pointer-y", ((e.clientY - b.top) / b.height - 0.5).toFixed(2));
  stage.style.setProperty("--pointer-light-x", ((e.clientX - b.left) / b.width * 100).toFixed(1) + "%");
  stage.style.setProperty("--pointer-light-y", ((e.clientY - b.top) / b.height * 100).toFixed(1) + "%");
}, { passive: true });
stage.addEventListener("pointerleave", () => ["--pointer-x", "--pointer-y", "--pointer-light-x", "--pointer-light-y"].forEach((v) => stage.style.removeProperty(v)));

/* ------------------------------------------------------------------ */
/* Hero pointer depth: video, copy and light move at different depths  */
/* ------------------------------------------------------------------ */
(() => {
  const sticky = $(".hero__sticky");
  let tx = 0, ty = 0, x = 0, y = 0, raf = 0;
  const loop = () => {
    x += (tx - x) * 0.08; y += (ty - y) * 0.08;
    hero.style.setProperty("--hx", x.toFixed(3)); hero.style.setProperty("--hy", y.toFixed(3));
    raf = Math.abs(tx - x) + Math.abs(ty - y) > 0.002 ? requestAnimationFrame(loop) : 0;
  };
  const kick = () => { if (!raf) raf = requestAnimationFrame(loop); };
  sticky.addEventListener("pointermove", (e) => {
    if (reducedMotion || e.pointerType === "touch") return;
    const r = sticky.getBoundingClientRect();
    tx = ((e.clientX - r.left) / r.width - 0.5) * 2; ty = ((e.clientY - r.top) / r.height - 0.5) * 2;
    hero.style.setProperty("--lx", ((e.clientX - r.left) / r.width * 100).toFixed(1) + "%");
    hero.style.setProperty("--ly", ((e.clientY - r.top) / r.height * 100).toFixed(1) + "%");
    hero.classList.add("is-pointer"); kick();
  }, { passive: true });
  sticky.addEventListener("pointerleave", () => { tx = 0; ty = 0; hero.classList.remove("is-pointer"); kick(); });
})();

/* ------------------------------------------------------------------ */
/* Field-marker cursor: orbiting star + colour-seed trail (desktop)    */
/* ------------------------------------------------------------------ */
function setupFieldCursor() {
  if (!finePointer || reducedMotion) return;
  const cursor = document.createElement("div");
  cursor.className = "field-cursor"; cursor.setAttribute("aria-hidden", "true");
  cursor.innerHTML = '<span class="field-cursor__ring"><i></i><i></i><i></i></span><span class="field-cursor__core">✳</span><span class="field-cursor__label">FIELD MARK</span>';
  document.body.append(cursor);
  const trail = Array.from({ length: 4 }, (_, i) => { const d = document.createElement("span"); d.className = `field-cursor__trail field-cursor__trail--${i + 1}`; d.setAttribute("aria-hidden", "true"); document.body.append(d); return { node: d, x: 0, y: 0 }; });
  document.body.classList.add("has-field-cursor");
  const point = { x: -100, y: -100 }, labelEl = $(".field-cursor__label", cursor);
  let ready = false, frame = 0, lastSig = "";
  function classify(t) {
    if (!(t instanceof Element)) return { mode: "roam", label: "FIELD MARK" };
    if (t.closest("input[type=email],input[type=search],input[type=text],textarea,pre")) return { mode: "text", label: "TYPE HERE" };
    const card = t.closest(".card:not(.card--studio)");
    if (card) return { mode: "study", label: `PREVIEW / ${card.querySelector("h3")?.textContent.toUpperCase() || "STUDY"}` };
    if (t.closest(".play-stage")) return { mode: "play", label: "NUDGE THE ORBIT" };
    if (t.closest(".lab-panel,.lab-tide")) return { mode: "play", label: "TRY THE STUDY" };
    if (t.closest(".tile__stage")) return { mode: "play", label: "PLAY WITH IT" };
    if (t.closest(".tile__shader,.tile__mock")) return { mode: "study", label: "OPEN ↗" };
    if (t.closest("a,button,[role='button'],summary,input[type=range]")) return { mode: "action", label: "FOLLOW ↗" };
    if (t.closest(".hero__sticky")) return { mode: "hero", label: "FOLLOW THE LIGHT" };
    if (t.closest(".strip")) return { mode: "roam", label: "DRAG ↔" };
    return { mode: "roam", label: "FIELD MARK" };
  }
  function setContext(t) {
    const st = classify(t), sig = st.mode + st.label; if (sig === lastSig) return; lastSig = sig;
    cursor.dataset.mode = st.mode; labelEl.textContent = st.label;
    document.body.classList.toggle("is-text-entry", st.mode === "text");
  }
  function animate() {
    frame = 0; cursor.style.transform = `translate3d(${point.x}px, ${point.y}px, 0) translate(-50%, -50%)`;
    let moving = false;
    trail.forEach((d, i) => {
      const lead = i === 0 ? point : trail[i - 1], ease = i === 0 ? 0.42 : 0.32;
      d.x += (lead.x - d.x) * ease; d.y += (lead.y - d.y) * ease;
      d.node.style.transform = `translate3d(${d.x}px, ${d.y}px, 0) translate(-50%, -50%)`;
      if (Math.abs(lead.x - d.x) + Math.abs(lead.y - d.y) > 0.6) moving = true;
    });
    if (moving) frame = requestAnimationFrame(animate);
  }
  document.addEventListener("pointermove", (e) => {
    if (e.pointerType !== "mouse") return;
    point.x = e.clientX; point.y = e.clientY;
    setContext(document.elementFromPoint(point.x, point.y) || e.target);
    cursor.classList.add("is-visible"); trail.forEach((d) => d.node.classList.add("is-visible"));
    if (!ready) { trail.forEach((d) => { d.x = point.x; d.y = point.y; }); ready = true; }
    if (!frame) frame = requestAnimationFrame(animate);
  }, { passive: true });
  document.addEventListener("pointerdown", (e) => { if (e.pointerType === "mouse") cursor.classList.add("is-pressed"); });
  document.addEventListener("pointerup", () => cursor.classList.remove("is-pressed"));
  document.addEventListener("mouseleave", () => { cursor.classList.remove("is-visible"); trail.forEach((d) => d.node.classList.remove("is-visible")); });
  window.addEventListener("blur", () => { cursor.classList.remove("is-visible", "is-pressed"); trail.forEach((d) => d.node.classList.remove("is-visible")); });
  // keep the cursor above an open modal
  modal.addEventListener("close", () => document.body.append(cursor, ...trail.map((d) => d.node)));
  new MutationObserver(() => { if (modal.open) modal.append(cursor, ...trail.map((d) => d.node)); }).observe(modal, { attributes: true, attributeFilter: ["open"] });
}
setupFieldCursor();

/* Boot */
renderLibrary();
mountShaders(document);
requestAnimationFrame(() => document.documentElement.classList.add("is-loaded"));
if (document.readyState === "complete") initLenis(); else window.addEventListener("load", initLenis);
update(); moveInk();
})();

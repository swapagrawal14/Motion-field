const studies = [
  {
    id: "01", title: "The tide turn", category: "scroll", categoryLabel: "SCROLL CUE", image: "assets/preview-tide.png",
    description: "A sideways tide that drifts as you move down the page. Best used when the story itself has a direction to travel.",
    tags: ["horizontal drift", "scroll-linked"], level: "GENTLE",
    code: `const track = document.querySelector('.story-track');\nwindow.addEventListener('scroll', () => {\n  const progress = window.scrollY /\n    (document.body.scrollHeight - innerHeight);\n  track.style.transform =\n    \`translateX(\${progress * -24}vw)\`;\n}, { passive: true });`
  },
  {
    id: "02", title: "Orbit, gently", category: "3d", categoryLabel: "3D & DEPTH", image: "assets/preview-orbit.png",
    description: "A little constellation of objects follows the reader. Slow, imperfect, and just off-center — like things do in real life.",
    tags: ["parallax", "pointer"], level: "MEDIUM",
    code: `const scene = document.querySelector('.scene');\nscene.addEventListener('pointermove', (event) => {\n  const x = event.clientX / innerWidth - .5;\n  const y = event.clientY / innerHeight - .5;\n  scene.style.setProperty('--x', x.toFixed(2));\n  scene.style.setProperty('--y', y.toFixed(2));\n});`
  },
  {
    id: "03", title: "Soft-focus reveal", category: "reveal", categoryLabel: "REVEAL", image: "assets/preview-grid.png",
    description: "Let a new chapter arrive in focus instead of all at once. A quiet reveal with a little depth and a lot of restraint.",
    tags: ["intersection", "blur to clear"], level: "GENTLE",
    code: `const reveal = new IntersectionObserver((entries) => {\n  entries.forEach(({ target, isIntersecting }) => {\n    if (isIntersecting) target.classList.add('is-ready');\n  });\n}, { threshold: 0.22 });\n\ndocument.querySelectorAll('[data-reveal]')\n  .forEach((item) => reveal.observe(item));`
  },
  {
    id: "04", title: "Letters in the wind", category: "type", categoryLabel: "TYPE PLAY", image: "assets/preview-portal.png",
    description: "A headline gives the breeze a shape. Each letter eases into place with enough space to read, then enough time to stay.",
    tags: ["letter stagger", "headline"], level: "MEDIUM",
    code: `const letters = document.querySelectorAll('.letter');\nletters.forEach((letter, index) => {\n  letter.style.setProperty('--delay', \`\${index * 42}ms\`);\n});\n\n/* CSS: transition-delay: var(--delay); */\n/* Respect reduced motion with a media query. */`
  },
  {
    id: "05", title: "The long way round", category: "scroll", categoryLabel: "SCROLL CUE", image: "assets/preview-orbit.png",
    description: "A hand-drawn path that traces a small detour. Use it to connect ideas or make a transition feel like part of the story.",
    tags: ["path draw", "SVG stroke"], level: "MEDIUM",
    code: `const path = document.querySelector('.draw-path');\nconst length = path.getTotalLength();\npath.style.strokeDasharray = length;\npath.style.strokeDashoffset = length;\n\n// As progress moves from 0 to 1:\npath.style.strokeDashoffset = length * (1 - progress);`
  },
  {
    id: "06", title: "A page with a pulse", category: "reveal", categoryLabel: "REVEAL", image: "assets/preview-tide.png",
    description: "A small breath on hover and focus. A tactile signal for something you can actually interact with — never just decoration.",
    tags: ["micro-interaction", "hover + focus"], level: "GENTLE",
    code: `.pulse-card {\n  transition: transform 360ms cubic-bezier(.2,.8,.2,1);\n}\n.pulse-card:hover,\n.pulse-card:focus-visible {\n  transform: translateY(-4px) rotate(-.4deg);\n}\n@media (prefers-reduced-motion: reduce) {\n  .pulse-card { transition: none; }\n}`
  }
];

const grid = document.querySelector("#card-grid");
const searchInput = document.querySelector("#library-search");
const emptyState = document.querySelector("#empty-state");
const modal = document.querySelector("#detail-modal");
const toast = document.querySelector("#toast");
let activeFilter = "all";
let toastTimer;

function renderCards() {
  const query = searchInput.value.trim().toLowerCase();
  const filtered = studies.filter((study) => {
    const matchesFilter = activeFilter === "all" || study.category === activeFilter;
    const content = [study.title, study.categoryLabel, study.description, ...study.tags].join(" ").toLowerCase();
    return matchesFilter && content.includes(query);
  });
  grid.innerHTML = filtered.map((study, index) => `
    <article class="study-card" style="animation-delay:${index * 45}ms">
      <div class="card-visual" data-open-study="${study.id}" tabindex="0" role="button" aria-label="Open study: ${study.title}">
        <img src="${study.image}" alt="Abstract artwork for ${study.title}" loading="lazy">
        <span class="card-number">STUDY ${study.id}</span>
        <button class="card-open" type="button" data-open-study="${study.id}" aria-label="Open ${study.title}">↗</button>
      </div>
      <div class="card-info">
        <div class="card-meta"><span>${study.categoryLabel}</span><span>FIELD NOTES / ${study.id}</span></div>
        <h3>${study.title}</h3>
        <p>${study.description}</p>
        <div class="card-footer">${study.tags.map((tag) => `<span class="tag">${tag}</span>`).join("")}<span class="difficulty">${study.level}</span></div>
      </div>
    </article>
  `).join("");
  emptyState.hidden = filtered.length > 0;
}

function openStudy(id) {
  const study = studies.find((item) => item.id === id);
  if (!study) return;
  document.querySelector("#modal-image").src = study.image;
  document.querySelector("#modal-image").alt = `Abstract artwork for ${study.title}`;
  document.querySelector("#modal-number").textContent = `STUDY ${study.id} / MOTION FIELD`;
  document.querySelector("#modal-kicker").textContent = `${study.categoryLabel} · FIELD NOTES ${study.id}`;
  document.querySelector("#modal-title").textContent = study.title;
  document.querySelector("#modal-description").textContent = study.description;
  document.querySelector("#modal-meta").innerHTML = [...study.tags, study.level.toLowerCase() + " energy"].map((item) => `<span>${item}</span>`).join("");
  document.querySelector("#modal-code").textContent = study.code;
  modal.dataset.studyId = id;
  modal.showModal();
}

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("is-visible");
  window.clearTimeout(toastTimer);
  toastTimer = window.setTimeout(() => toast.classList.remove("is-visible"), 2200);
}

document.querySelectorAll(".filter-chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    activeFilter = chip.dataset.filter;
    document.querySelectorAll(".filter-chip").forEach((item) => {
      const active = item === chip;
      item.classList.toggle("is-active", active);
      item.setAttribute("aria-pressed", String(active));
    });
    renderCards();
  });
});

searchInput.addEventListener("input", renderCards);
grid.addEventListener("click", (event) => {
  const trigger = event.target.closest("[data-open-study]");
  if (trigger) openStudy(trigger.dataset.openStudy);
});
grid.addEventListener("keydown", (event) => {
  if ((event.key === "Enter" || event.key === " ") && event.target.matches(".card-visual")) {
    event.preventDefault();
    openStudy(event.target.dataset.openStudy);
  }
});
document.querySelector(".clear-search").addEventListener("click", () => {
  searchInput.value = "";
  activeFilter = "all";
  document.querySelectorAll(".filter-chip").forEach((item) => {
    const active = item.dataset.filter === "all";
    item.classList.toggle("is-active", active);
    item.setAttribute("aria-pressed", String(active));
  });
  renderCards();
});

document.querySelector(".modal-close").addEventListener("click", () => modal.close());
modal.addEventListener("click", (event) => {
  if (event.target === modal) modal.close();
});
document.querySelector("#copy-code").addEventListener("click", async () => {
  const study = studies.find((item) => item.id === modal.dataset.studyId);
  if (!study) return;
  try {
    await navigator.clipboard.writeText(study.code);
    showToast("Snippet copied — go make it yours.");
  } catch {
    const selection = document.createElement("textarea");
    selection.value = study.code;
    selection.style.position = "fixed";
    selection.style.opacity = "0";
    document.body.append(selection);
    selection.select();
    document.execCommand("copy");
    selection.remove();
    showToast("Snippet copied — go make it yours.");
  }
});

const motionRange = document.querySelector("#motion-range");
const stage = document.querySelector("#playground-stage");
const motionValue = document.querySelector("#motion-value");
const motionLevel = document.querySelector("#motion-level");
function updateMotion() {
  const amount = Number(motionRange.value);
  const normalized = amount / 100;
  stage.dataset.motion = String(amount);
  stage.style.setProperty("--motion", normalized.toFixed(2));
  const main = stage.querySelector(".sphere-main");
  const back = stage.querySelector(".sphere-back");
  const orbitA = stage.querySelector(".orbit-one");
  const orbitB = stage.querySelector(".orbit-two");
  main.style.transform = `translate(${(normalized - .5) * 36}px, ${(normalized - .5) * -24}px) scale(${.8 + normalized * .25})`;
  back.style.transform = `translate(${45 + normalized * 75}px, ${-35 - normalized * 70}px) scale(${.75 + normalized * .25})`;
  orbitA.style.transform = `rotateX(${56 + normalized * 23}deg) rotate(${-40 + amount * 1.25}deg) scale(${.72 + normalized * .4})`;
  orbitB.style.transform = `rotateX(${55 + normalized * 25}deg) rotate(${40 - amount * 1.2}deg) scale(${.78 + normalized * .32})`;
  motionValue.textContent = `${amount}%`;
  motionLevel.textContent = amount < 28 ? "BARELY A BREATH" : amount < 72 ? "A LITTLE WIGGLE" : "FULL-BODY WIGGLE";
}
motionRange.addEventListener("input", updateMotion);
updateMotion();

const menuToggle = document.querySelector(".menu-toggle");
const mainNav = document.querySelector("#main-nav");
menuToggle.addEventListener("click", () => {
  const isOpen = menuToggle.getAttribute("aria-expanded") === "true";
  menuToggle.setAttribute("aria-expanded", String(!isOpen));
  menuToggle.setAttribute("aria-label", isOpen ? "Open navigation" : "Close navigation");
  mainNav.classList.toggle("is-open", !isOpen);
});
mainNav.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => {
  mainNav.classList.remove("is-open");
  menuToggle.setAttribute("aria-expanded", "false");
  menuToggle.setAttribute("aria-label", "Open navigation");
}));

document.addEventListener("keydown", (event) => {
  if (event.key === "/" && !event.ctrlKey && !event.metaKey && !["INPUT", "TEXTAREA"].includes(document.activeElement.tagName)) {
    event.preventDefault();
    searchInput.focus();
  }
});

renderCards();

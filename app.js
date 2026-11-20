const studies = [
  {id:"01",title:"The tide turn",category:"scroll",categoryLabel:"SCROLL CUE",image:"assets/study-tide.webp",description:"A sideways tide that drifts as you move down the page. Best used when the story itself has a direction to travel.",tags:["horizontal drift","scroll-linked"],level:"GENTLE",code:`const track = document.querySelector('.story-track');\nwindow.addEventListener('scroll', () => {\n  const progress = window.scrollY /\n    (document.body.scrollHeight - innerHeight);\n  track.style.transform =\n    \`translateX(\${progress * -24}vw)\`;\n}, { passive: true });`},
  {id:"02",title:"Orbit, gently",category:"3d",categoryLabel:"3D & DEPTH",image:"assets/study-orbit.webp",description:"A small constellation follows the reader. Slow, imperfect and just off-center — like things do in real life.",tags:["parallax","pointer"],level:"MEDIUM",code:`const scene = document.querySelector('.scene');\nscene.addEventListener('pointermove', (event) => {\n  const x = event.clientX / innerWidth - .5;\n  const y = event.clientY / innerHeight - .5;\n  scene.style.setProperty('--x', x.toFixed(2));\n  scene.style.setProperty('--y', y.toFixed(2));\n});`},
  {id:"03",title:"Soft-focus reveal",category:"reveal",categoryLabel:"REVEAL",image:"assets/study-reveal.webp",description:"Let a new chapter arrive in focus instead of all at once. A quiet reveal with a little depth and a lot of restraint.",tags:["intersection","blur to clear"],level:"GENTLE",code:`const reveal = new IntersectionObserver((entries) => {\n  entries.forEach(({ target, isIntersecting }) => {\n    if (isIntersecting) target.classList.add('is-ready');\n  });\n}, { threshold: 0.22 });\n\ndocument.querySelectorAll('[data-reveal]')\n  .forEach((item) => reveal.observe(item));`},
  {id:"04",title:"Letters in the wind",category:"type",categoryLabel:"TYPE PLAY",image:"assets/study-type.webp",description:"A headline gives the breeze a shape. Each letter eases into place with enough space to read, then enough time to stay.",tags:["letter stagger","headline"],level:"MEDIUM",code:`const letters = document.querySelectorAll('.letter');\nletters.forEach((letter, index) => {\n  letter.style.setProperty('--delay', (index * 42) + 'ms');\n});\n\n/* Pair with a reduced-motion fallback. */`},
  {id:"05",title:"The long way round",category:"scroll",categoryLabel:"SCROLL CUE",image:"assets/study-path.webp",description:"A hand-drawn path traces a small detour. Connect two ideas and make the transition part of the story.",tags:["path draw","scroll-linked"],level:"MEDIUM",code:`const path = document.querySelector('.draw-path');\nconst length = path.getTotalLength();\npath.style.strokeDasharray = length;\npath.style.strokeDashoffset = length;\n\n// As progress moves from 0 to 1:\npath.style.strokeDashoffset = length * (1 - progress);`},
  {id:"06",title:"A page with a pulse",category:"reveal",categoryLabel:"REVEAL",image:"assets/study-pulse.webp",description:"A small breath on hover and focus. A tactile signal for something you can actually interact with — never just decoration.",tags:["micro-interaction","hover + focus"],level:"GENTLE",code:`.pulse-card {\n  transition: transform 360ms cubic-bezier(.2,.8,.2,1);\n}\n.pulse-card:hover,\n.pulse-card:focus-visible {\n  transform: translateY(-4px) rotate(-.4deg);\n}\n@media (prefers-reduced-motion: reduce) {\n  .pulse-card { transition: none; }\n}`}
];

const grid=document.querySelector("#card-grid");
const searchInput=document.querySelector("#library-search");
const emptyState=document.querySelector("#empty-state");
const modal=document.querySelector("#detail-modal");
const toast=document.querySelector("#toast");
let activeFilter="all",toastTimer;

function renderCards(){
  const query=searchInput.value.trim().toLowerCase();
  const filtered=studies.filter(study=>{
    const matchesFilter=activeFilter==="all"||study.category===activeFilter;
    const content=[study.title,study.categoryLabel,study.description,...study.tags].join(" ").toLowerCase();
    return matchesFilter&&content.includes(query);
  });
  grid.innerHTML=filtered.map((study,index)=>`
    <article class="study-card" style="animation-delay:${index*45}ms">
      <div class="card-visual" data-open-study="${study.id}" tabindex="0" role="button" aria-label="Open study: ${study.title}">
        <img src="${study.image}" alt="Abstract artwork for ${study.title}" loading="lazy">
        <span class="card-number">STUDY ${study.id}</span>
        <button class="card-open" type="button" data-open-study="${study.id}" aria-label="Open ${study.title}">↗</button>
      </div>
      <div class="card-info">
        <div class="card-meta"><span>${study.categoryLabel}</span><span>FIELD NOTES / ${study.id}</span></div>
        <h3>${study.title}</h3>
        <p>${study.description}</p>
        <div class="card-footer">${study.tags.map(tag=>`<span class="tag">${tag}</span>`).join("")}<span class="difficulty">${study.level}</span></div>
      </div>
    </article>`).join("");
  emptyState.hidden=filtered.length>0;
}
function openStudy(id){
  const study=studies.find(item=>item.id===id);if(!study)return;
  document.querySelector("#modal-image").src=study.image;
  document.querySelector("#modal-image").alt=`Abstract artwork for ${study.title}`;
  document.querySelector("#modal-number").textContent=`STUDY ${study.id} / MOTION FIELD`;
  document.querySelector("#modal-kicker").textContent=`${study.categoryLabel} · FIELD NOTES ${study.id}`;
  document.querySelector("#modal-title").textContent=study.title;
  document.querySelector("#modal-description").textContent=study.description;
  document.querySelector("#modal-meta").innerHTML=[...study.tags,study.level.toLowerCase()+" energy"].map(item=>`<span>${item}</span>`).join("");
  document.querySelector("#modal-code").textContent=study.code;
  modal.dataset.studyId=id;modal.showModal();
}
function showToast(message){toast.textContent=message;toast.classList.add("is-visible");clearTimeout(toastTimer);toastTimer=setTimeout(()=>toast.classList.remove("is-visible"),2200)}

document.querySelectorAll(".filter-chip").forEach(chip=>chip.addEventListener("click",()=>{
  activeFilter=chip.dataset.filter;
  document.querySelectorAll(".filter-chip").forEach(item=>{const active=item===chip;item.classList.toggle("is-active",active);item.setAttribute("aria-pressed",String(active))});
  renderCards();
}));
searchInput.addEventListener("input",renderCards);
grid.addEventListener("click",event=>{const trigger=event.target.closest("[data-open-study]");if(trigger)openStudy(trigger.dataset.openStudy)});
grid.addEventListener("keydown",event=>{if((event.key==="Enter"||event.key===" ")&&event.target.matches(".card-visual")){event.preventDefault();openStudy(event.target.dataset.openStudy)}});
document.querySelector(".clear-search").addEventListener("click",()=>{searchInput.value="";activeFilter="all";document.querySelectorAll(".filter-chip").forEach(item=>{const active=item.dataset.filter==="all";item.classList.toggle("is-active",active);item.setAttribute("aria-pressed",String(active))});renderCards()});
document.querySelector(".modal-close").addEventListener("click",()=>modal.close());
modal.addEventListener("click",event=>{if(event.target===modal)modal.close()});
document.querySelector("#copy-code").addEventListener("click",async()=>{
  const study=studies.find(item=>item.id===modal.dataset.studyId);if(!study)return;
  try{await navigator.clipboard.writeText(study.code)}catch{const selection=document.createElement("textarea");selection.value=study.code;selection.style.position="fixed";selection.style.opacity="0";document.body.append(selection);selection.select();document.execCommand("copy");selection.remove()}
  showToast("Snippet copied — go make it yours.");
});

const motionRange=document.querySelector("#motion-range"),stage=document.querySelector("#playground-stage"),motionValue=document.querySelector("#motion-value"),motionLevel=document.querySelector("#motion-level");
function updateMotion(){const amount=Number(motionRange.value),normalized=amount/100;stage.style.setProperty("--energy",normalized.toFixed(2));const labels=amount<28?"BARELY A BREATH":amount<72?"A LITTLE WIGGLE":"FULL-BODY WIGGLE";motionValue.textContent=`${amount}%`;motionLevel.textContent=labels;stage.dataset.motion=String(amount)}
motionRange.addEventListener("input",updateMotion);updateMotion();
stage.addEventListener("pointermove",event=>{const bounds=stage.getBoundingClientRect();stage.style.setProperty("--pointer-x",((event.clientX-bounds.left)/bounds.width-.5).toFixed(2));stage.style.setProperty("--pointer-y",((event.clientY-bounds.top)/bounds.height-.5).toFixed(2))});
stage.addEventListener("pointerleave",()=>{stage.style.setProperty("--pointer-x","0");stage.style.setProperty("--pointer-y","0")});

const menuToggle=document.querySelector(".menu-toggle"),mainNav=document.querySelector("#main-nav");
menuToggle.addEventListener("click",()=>{const isOpen=menuToggle.getAttribute("aria-expanded")==="true";menuToggle.setAttribute("aria-expanded",String(!isOpen));menuToggle.setAttribute("aria-label",isOpen?"Open navigation":"Close navigation");mainNav.classList.toggle("is-open",!isOpen)});
mainNav.querySelectorAll("a").forEach(link=>link.addEventListener("click",()=>{mainNav.classList.remove("is-open");menuToggle.setAttribute("aria-expanded","false");menuToggle.setAttribute("aria-label","Open navigation")}));
document.addEventListener("keydown",event=>{if(event.key==="/"&&!event.ctrlKey&&!event.metaKey&&!["INPUT","TEXTAREA"].includes(document.activeElement.tagName)){event.preventDefault();searchInput.focus()}});

const progressBar=document.querySelector("#reading-progress-bar");
function updateProgress(){const max=document.documentElement.scrollHeight-innerHeight;progressBar.style.width=`${max>0?Math.min(100,scrollY/max*100):0}%`}
window.addEventListener("scroll",updateProgress,{passive:true});window.addEventListener("resize",updateProgress);updateProgress();
const reducedMotion=window.matchMedia("(prefers-reduced-motion: reduce)").matches;
if(!reducedMotion&&"IntersectionObserver" in window){const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.add("is-visible");observer.unobserve(entry.target)}}),{threshold:.12});document.querySelectorAll(".library-heading,.library-controls,.card-grid,.playground-layout,.notes-intro,.notes-grid").forEach(el=>{el.classList.add("reveal");observer.observe(el)})}
renderCards();


/* An orbiting field marker gives each pointer region a different little job. */
function setupFieldCursor(){
  if(!window.matchMedia("(hover: hover) and (pointer: fine)").matches||window.matchMedia("(prefers-reduced-motion: reduce)").matches)return;
  const cursor=document.createElement("div");
  cursor.className="field-cursor";
  cursor.setAttribute("aria-hidden","true");
  cursor.innerHTML='<span class="field-cursor__ring"><i></i><i></i><i></i></span><span class="field-cursor__core">✳</span><span class="field-cursor__label">FIELD MARK</span>';
  document.body.append(cursor);
  const trail=Array.from({length:4},(_,index)=>{const dot=document.createElement("span");dot.className=`field-cursor__trail field-cursor__trail--${index+1}`;dot.setAttribute("aria-hidden","true");document.body.append(dot);return{node:dot,x:0,y:0}});
  document.body.classList.add("has-field-cursor");
  const point={x:-100,y:-100};
  let ready=false,frame=0,lastContext="";
  function classify(target){
    if(!(target instanceof Element))return{mode:"roam",label:"FIELD MARK"};
    const input=target.closest("input,textarea,select,[contenteditable='true']");
    if(input)return{mode:"text",label:"TYPE HERE"};
    const study=target.closest(".study-card");
    if(study){const number=study.querySelector(".card-number")?.textContent.replace(/[^0-9]/g,"")||"00";return{mode:"study",label:`UNFOLD / ${number}`}}
    if(target.closest(".hero-frame"))return{mode:"hero",label:"FOLLOW THE LIGHT"};
    if(target.closest(".play-stage"))return{mode:"play",label:"NUDGE THE ORBIT"};
    if(target.closest("a,button,[role='button']"))return{mode:"action",label:"FOLLOW ↗"};
    return{mode:"roam",label:"FIELD MARK"};
  }
  function setContext(target){
    const state=classify(target),signature=`${state.mode}:${state.label}`;
    if(signature===lastContext)return;
    lastContext=signature;cursor.dataset.mode=state.mode;cursor.querySelector(".field-cursor__label").textContent=state.label;
    document.body.classList.toggle("is-text-entry",state.mode==="text");
  }
  function animate(){
    frame=0;cursor.style.left=`${point.x}px`;cursor.style.top=`${point.y}px`;
    let moving=false;
    trail.forEach((dot,index)=>{
      const leader=index===0?point:trail[index-1],ease=index===0?.42:.32;
      dot.x+=(leader.x-dot.x)*ease;dot.y+=(leader.y-dot.y)*ease;
      dot.node.style.left=`${dot.x}px`;dot.node.style.top=`${dot.y}px`;
      if(Math.abs(leader.x-dot.x)+Math.abs(leader.y-dot.y)>.65)moving=true;
    });
    if(moving)frame=requestAnimationFrame(animate);
  }
  document.addEventListener("pointermove",event=>{
    if(event.pointerType!=="mouse")return;
    point.x=event.clientX;point.y=event.clientY;
    const target=document.elementFromPoint(point.x,point.y)||event.target;setContext(target);
    cursor.classList.add("is-visible");trail.forEach(dot=>dot.node.classList.add("is-visible"));
    if(!ready){trail.forEach(dot=>{dot.x=point.x;dot.y=point.y;dot.node.style.left=`${point.x}px`;dot.node.style.top=`${point.y}px`});ready=true}
    if(!frame)frame=requestAnimationFrame(animate);
  },{passive:true});
  document.addEventListener("pointerdown",event=>{if(event.pointerType==="mouse")cursor.classList.add("is-pressed")});
  document.addEventListener("pointerup",()=>cursor.classList.remove("is-pressed"));
  document.addEventListener("pointerover",event=>{if(event.pointerType==="mouse")setContext(event.target)});
  document.addEventListener("pointerout",event=>{if(event.pointerType==="mouse"&&event.relatedTarget)setContext(event.relatedTarget)});
  window.addEventListener("blur",()=>{cursor.classList.remove("is-visible","is-pressed");trail.forEach(dot=>dot.node.classList.remove("is-visible"));document.body.classList.remove("is-text-entry")});
  window.addEventListener("focus",()=>{ready=false});
}

function setCardPointer(visual,event){
  const bounds=visual.getBoundingClientRect();
  const x=Math.max(-1,Math.min(1,((event.clientX-bounds.left)/bounds.width-.5)*2));
  const y=Math.max(-1,Math.min(1,((event.clientY-bounds.top)/bounds.height-.5)*2));
  visual.style.setProperty("--card-light-x",`${((x+1)*50).toFixed(1)}%`);
  visual.style.setProperty("--card-light-y",`${((y+1)*50).toFixed(1)}%`);
  visual.style.setProperty("--card-rotate-x",`${(-y*6).toFixed(2)}deg`);
  visual.style.setProperty("--card-rotate-y",`${(x*7).toFixed(2)}deg`);
  visual.style.setProperty("--card-shift-x",`${(-x*10).toFixed(1)}px`);
  visual.style.setProperty("--card-shift-y",`${(-y*7).toFixed(1)}px`);
  visual.style.setProperty("--tag-shift-x",`${(x*5).toFixed(1)}px`);
  visual.style.setProperty("--tag-shift-y",`${(y*4).toFixed(1)}px`);
}
function resetCardPointer(visual){
  visual.classList.remove("is-pointer-active","is-touch-active");
  ["--card-light-x","--card-light-y"].forEach(name=>visual.style.removeProperty(name));
  ["--card-rotate-x","--card-rotate-y","--card-shift-x","--card-shift-y","--tag-shift-x","--tag-shift-y"].forEach(name=>visual.style.removeProperty(name));
}
function setupStudyInteractions(){
  const timers=new WeakMap();
  grid.addEventListener("pointermove",event=>{
    const visual=event.target.closest(".card-visual");if(!visual)return;
    if(event.pointerType==="mouse"||event.pointerType==="pen"){visual.classList.add("is-pointer-active");setCardPointer(visual,event)}
    else if(event.pointerType==="touch"&&visual.classList.contains("is-touch-active"))setCardPointer(visual,event);
  },{passive:true});
  grid.addEventListener("pointerout",event=>{
    const visual=event.target.closest(".card-visual");
    if(visual&&(event.pointerType==="mouse"||event.pointerType==="pen")&&!visual.contains(event.relatedTarget))resetCardPointer(visual);
  });
  grid.addEventListener("pointerdown",event=>{
    if(event.pointerType!=="touch")return;
    const visual=event.target.closest(".card-visual");if(!visual)return;
    clearTimeout(timers.get(visual));visual.classList.add("is-touch-active");setCardPointer(visual,event);
  });
  grid.addEventListener("pointerup",event=>{
    if(event.pointerType!=="touch")return;
    const visual=event.target.closest(".card-visual");if(!visual)return;
    timers.set(visual,setTimeout(()=>resetCardPointer(visual),360));
  });
  grid.addEventListener("pointercancel",event=>{const visual=event.target.closest(".card-visual");if(visual)resetCardPointer(visual)});
}

function setupHeroField(){
  const hero=document.querySelector("#hero-frame"),sticker=hero?.querySelector(".hero-sticker"),cta=hero?.querySelector(".button-lime");
  if(!hero)return;
  let touchTimer;
  function update(event){
    const bounds=hero.getBoundingClientRect(),x=Math.max(-1,Math.min(1,((event.clientX-bounds.left)/bounds.width-.5)*2)),y=Math.max(-1,Math.min(1,((event.clientY-bounds.top)/bounds.height-.5)*2));
    hero.style.setProperty("--hero-light-x",`${((x+1)*50).toFixed(1)}%`);hero.style.setProperty("--hero-light-y",`${((y+1)*50).toFixed(1)}%`);
    hero.style.setProperty("--hero-shift-x",`${(-x*14).toFixed(1)}px`);hero.style.setProperty("--hero-shift-y",`${(-y*10).toFixed(1)}px`);
    hero.style.setProperty("--shade-shift-x",`${(x*5).toFixed(1)}px`);hero.style.setProperty("--shade-shift-y",`${(y*4).toFixed(1)}px`);
    hero.style.setProperty("--copy-shift-x",`${(x*7).toFixed(1)}px`);hero.style.setProperty("--copy-shift-y",`${(y*5).toFixed(1)}px`);
    hero.style.setProperty("--sticker-shift-x",`${(-x*9).toFixed(1)}px`);hero.style.setProperty("--sticker-shift-y",`${(-y*8).toFixed(1)}px`);
    hero.style.setProperty("--sticker-rotate",`${(x*7).toFixed(1)}deg`);
  }
  function reset(){hero.classList.remove("is-pointer-active","is-touch-active");["--hero-light-x","--hero-light-y","--hero-shift-x","--hero-shift-y","--shade-shift-x","--shade-shift-y","--copy-shift-x","--copy-shift-y","--sticker-shift-x","--sticker-shift-y","--sticker-rotate"].forEach(name=>hero.style.removeProperty(name))}
  hero.addEventListener("pointermove",event=>{
    if(event.pointerType==="mouse"||event.pointerType==="pen"){hero.classList.add("is-pointer-active");update(event)}
    else if(event.pointerType==="touch"&&hero.classList.contains("is-touch-active"))update(event);
  },{passive:true});
  hero.addEventListener("pointerleave",reset);
  hero.addEventListener("pointerdown",event=>{if(event.pointerType==="touch"){clearTimeout(touchTimer);hero.classList.add("is-touch-active");update(event)}});
  hero.addEventListener("pointerup",event=>{if(event.pointerType==="touch")touchTimer=setTimeout(reset,440)});
  hero.addEventListener("pointercancel",reset);
  if(cta){cta.addEventListener("pointermove",event=>{if(event.pointerType!=="mouse")return;const bounds=cta.getBoundingClientRect();cta.style.setProperty("--magnet-x",`${(((event.clientX-bounds.left)/bounds.width-.5)*10).toFixed(1)}px`);cta.style.setProperty("--magnet-y",`${(((event.clientY-bounds.top)/bounds.height-.5)*10).toFixed(1)}px`)});cta.addEventListener("pointerleave",()=>{cta.style.removeProperty("--magnet-x");cta.style.removeProperty("--magnet-y")})}
}

function setupPlaygroundAura(){
  function nudge(event){const bounds=stage.getBoundingClientRect();stage.style.setProperty("--pointer-light-x",`${((event.clientX-bounds.left)/bounds.width*100).toFixed(1)}%`);stage.style.setProperty("--pointer-light-y",`${((event.clientY-bounds.top)/bounds.height*100).toFixed(1)}%`)}
  stage.addEventListener("pointermove",nudge,{passive:true});
  stage.addEventListener("pointerleave",()=>{stage.style.removeProperty("--pointer-light-x");stage.style.removeProperty("--pointer-light-y")});
}

setupFieldCursor();
setupStudyInteractions();
setupHeroField();
setupPlaygroundAura();

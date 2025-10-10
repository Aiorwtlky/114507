/* bg-icons V9 ─ 修正左側留白（容器左移半格）+ 全功能 */
console.log("bg-icons V9 loaded");

const ICONS = [
  "fa-car", "fa-car-side", "fa-car-burst", "fa-taxi",
  "fa-truck-front", "fa-bus", "fa-motorcycle", "fa-route",
  "fa-road", "fa-shield-halved", "fa-traffic-light", "fa-gauge-high",
  "fa-video", "fa-camera", "fa-microchip", "fa-bolt",
  "fa-charging-station", "fa-satellite-dish", "fa-solar-panel",
  "fa-tree", "fa-city", "fa-signs-post"
];

const PARALLAX = 0.4;   // 背景隨滾輪速度

function buildIcons() {
  const box = document.getElementById("bg-icons");
  box.innerHTML = "";          // 清舊
  box.style.transform = "";    // 先還原位移

  const vw = innerWidth;
  const vh = innerHeight;
  const docH = document.body.scrollHeight;

  /* === RWD 尺寸 === */
  let MAX, MIN, CELL;
  if (vw <= 480) { MAX=72;  MIN=36;  CELL=MAX*1.45; }
  else if (vw <= 768){ MAX=90;  MIN=44;  CELL=MAX*1.4; }
  else { MAX=120; MIN=54; CELL=MAX*1.35; }

  /* === 左移半格：讓左右都鋪滿 === */
  box.style.transform = `translateX(${-CELL/2}px)`;

  const cols = Math.ceil((vw + CELL) / CELL);        // +CELL 是因為左移後右邊也要補格
  const shiftMax = (docH - vh) * PARALLAX;
  const bufferRows = Math.ceil(shiftMax / CELL) + 1;
  const firstRow = -bufferRows;
  const rows = Math.ceil(docH / CELL) + bufferRows + 1;

  /* 鄰格去重表 */
  const gridType = Array.from({length: rows}, ()=>Array(cols).fill(null));

  let idx = 0;
  for (let r = 0; r < rows; r++){
    for (let c = 0; c < cols; c++){
      /* 抽 icon 且鄰格不同 */
      let icon, tries = 0;
      do{
        icon = ICONS[idx++ % ICONS.length];
      }while(
        ++tries < 12 &&
        (
          (r > 0 && gridType[r-1][c] === icon) ||
          (c > 0 && gridType[r][c-1] === icon)
        )
      );
      gridType[r][c] = icon;

      /* 元素 */
      const el = document.createElement("i");
      el.className = `bg-icon fas ${icon}`;
      const size = gsap.utils.random(MIN, MAX);
      el.style.fontSize = size + "px";

      const x = c*CELL + gsap.utils.random(size*.5, CELL - size*.5);
      const y = (firstRow + r)*CELL + gsap.utils.random(size*.5, CELL - size*.5);

      gsap.set(el,{x,y,rotate:gsap.utils.random(-40,40)});
      box.appendChild(el);

      /* 漂浮 */
      gsap.to(el,{
        x:`+=${gsap.utils.random(-40,40)}`,
        y:`+=${gsap.utils.random(-30,30)}`,
        rotate:gsap.utils.random(-45,45),
        duration:gsap.utils.random(8,12),
        ease:"sine.inOut",
        yoyo:true,
        repeat:-1
      });
    }
  }

  /* 視差 */
  ScrollTrigger.getById("bgParallax")?.kill();
  gsap.to("#bg-icons",{
    id:"bgParallax",
    y:()=> (document.body.scrollHeight - innerHeight) * PARALLAX,
    ease:"none",
    scrollTrigger:{
      trigger:document.body,
      start:"top top",
      end:"bottom bottom",
      scrub:true
    }
  });
}

/* 初載 & resize */
document.addEventListener("DOMContentLoaded", buildIcons);
let t; addEventListener("resize",()=>{ clearTimeout(t); t=setTimeout(buildIcons,200); });

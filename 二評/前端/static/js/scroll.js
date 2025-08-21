gsap.registerPlugin(ScrollTrigger);

const hero = document.getElementById("hero");      // 首頁才會存在
const features = document.querySelector(".features");
const cards = document.querySelectorAll(".card");

if (hero) {
  /* Hero 進場 */
  gsap.from(".mega-title", { y: -120, opacity: 0, duration: 1.2, ease: "power4.out" });
  gsap.from(".subtitle", { y: -90, opacity: 0, duration: 1, delay: .2 });
  gsap.from(".cta-group .btn", { y: 40, opacity: 0, duration: .9, delay: .4, stagger: .15, ease: "power2.out" });

  /* Features Cards */
  if (features) {
    gsap.from(features, { scrollTrigger: { trigger: features, start: "top 80%" }, opacity: 0, y: 120, duration: 1, ease: "power2.out" });
    cards.forEach(c => gsap.from(c, { scrollTrigger: { trigger: c, start: "top 85%" }, y: 60, scale: .9, opacity: 0, duration: 1, ease: "expo.out" }));
  }

  /* 向下箭頭 */
  // const arrow=document.createElement("div");
  // arrow.className="scroll-indicator";
  // arrow.textContent="▼";
  // document.body.appendChild(arrow);

  // arrow.addEventListener("click",()=>{
  //   const heroTop=hero.getBoundingClientRect().top;
  //   (Math.abs(heroTop)<40?document.getElementById("features"):hero)
  //     .scrollIntoView({behavior:"smooth"});
  // });

  // window.addEventListener("scroll",()=>{
  //   const heroBottom=hero.getBoundingClientRect().bottom;
  //   arrow.style.opacity=heroBottom<window.innerHeight*0.25?"0":"1";
  // });

  window.onload = () => {
    const hero = document.querySelector(".hero");
    const features = document.getElementById("features");
    if (!hero || !features) return;
  
    const arrow = document.createElement("div");
    arrow.className = "scroll-indicator";
    arrow.textContent = "▼";
    document.body.appendChild(arrow);
  
    let atHero = true; // 初始在 hero 區域
  
    arrow.addEventListener("click", () => {
      const target = atHero ? features : hero;
      const yOffset = -47.5; // ← 這裡調整你想要上移的像素
      const yPosition = target.getBoundingClientRect().top + window.scrollY + yOffset;
  
      window.scrollTo({
        top: yPosition,
        behavior: "smooth"
      });
  
      atHero = !atHero;
    });
  
    window.addEventListener("scroll", () => {
      const heroBottom = hero.getBoundingClientRect().bottom;
      arrow.style.opacity = heroBottom < window.innerHeight * 0.25 ? "0" : "1";
    });
    }
  };
  
/* 時鐘 */
function updateClock(){
    const now = new Date();
    const pad = n => n.toString().padStart(2,'0');
    const str = `${now.getFullYear()}-${pad(now.getMonth()+1)}-${pad(now.getDate())} `
              + `${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;
    document.getElementById('clock').textContent = str;
  }
  setInterval(updateClock, 1000);
  updateClock();
  
  /* 控制邏輯 */
  const statusBar = document.getElementById('statusBar');
  const btns = document.querySelectorAll('.ctrlBtn');
  let active = '';   // 當前模式: left | right | rear | ''
  
  btns.forEach(btn=>{
    btn.addEventListener('click',()=>{
      const mode = btn.dataset.mode;
      if(active === mode){         // 取消
        document.body.className = '';
        active = '';
        btns.forEach(b=>b.classList.remove('active'));
        statusBar.textContent = '　';
      }else{
        active = mode;
        document.body.className = `${mode}-active`;
        btns.forEach(b=>b.classList.toggle('active', b===btn));
        statusBar.textContent = 
          mode==='left' ? '車輛左轉彎' :
          mode==='right'? '車輛右轉彎' :
          '車輛倒車中';
      }
    });
  });
  
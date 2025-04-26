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

document.addEventListener('DOMContentLoaded', function () {
  const deviceInfoBtn = document.getElementById('deviceInfoBtn');
  const deviceInfoModal = document.getElementById('deviceInfoModal');
  const deviceInfoText = document.getElementById('deviceInfoText');
  const closeModalBtn = document.getElementById('closeModalBtn');
  const resetDeviceBtn = document.getElementById('resetDeviceBtn');

  deviceInfoBtn.addEventListener('click', function () {
      fetch('/device_info')
          .then(response => response.json())
          .then(data => {
              deviceInfoText.innerHTML = `
                  <p>製造商名：${data.manufacturer}</p>
                  <p>製造商地址：${data.manufacturer_address}</p>
                  <p>設備序號：${data.device_serial}</p>
                  <p>軟體版本：${data.software_version}</p>
                  <hr>
                  <p>車輛廠牌：${data.car_brand || '-'}</p>
                  <p>車牌號碼：${data.car_plate || '-'}</p>
                  <p>車種：${data.vehicle_type || '-'}</p>
                  <p>駕駛座方向：${data.driver_position || '-'}</p>
              `;
              deviceInfoModal.style.display = 'block';
          })
          .catch(error => {
              alert("讀取設備資料失敗！");
              console.error(error);
          });
  });

  closeModalBtn.addEventListener('click', function () {
      deviceInfoModal.style.display = 'none';
  });

  resetDeviceBtn.addEventListener('click', function () {
    if (confirm("確定要重設車輛資訊嗎？")) {
        fetch('/reset_device_info', {
            method: 'POST'
        })
        .then(response => {
            if (response.ok) {
                // 成功後，前端自己跳到 /reset_success 頁面
                window.location.href = '/reset_success';
            } else {
                alert("重設失敗！");
            }
        })
        .catch(error => {
            alert("重設失敗！");
            console.error(error);
        });
    }
});
});

  
/* 時鐘 */
function updateClock() {
  const now = new Date();
  const pad = n => n.toString().padStart(2, '0');
  const str = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} `
      + `${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;
  document.getElementById('clock').textContent = str;
}
setInterval(updateClock, 1000);
updateClock();

/* 全域變數 */
const statusBar = document.getElementById('statusBar');
const btns = document.querySelectorAll('.ctrlBtn');
const deviceInfoBtn = document.getElementById('deviceInfoBtn');
const deviceInfoModal = document.getElementById('deviceInfoModal');
const deviceInfoText = document.getElementById('deviceInfoText');
const closeModalBtn = document.getElementById('closeModalBtn');
const resetDeviceBtn = document.getElementById('resetDeviceBtn');

let active = '';
let previousMode = '';
let currentAudio = null;

/* 播放音效 */
function playSound(mode) {
  if (currentAudio) {
      currentAudio.pause();
      currentAudio.currentTime = 0;
  }

  let audioSrc = '';
  if (mode === 'left') {
      audioSrc = '/static/sounds/left_turn.mp3';
  } else if (mode === 'right') {
      audioSrc = '/static/sounds/right_turn.mp3';
  } else if (mode === 'rear') {
      audioSrc = '/static/sounds/reverse.mp3';
  }

  if (audioSrc) {
      currentAudio = new Audio(audioSrc);
      currentAudio.loop = true;
      currentAudio.play();
  } else {
      currentAudio = null;
  }
}

/* 更新畫面和音效 */
function updateMode(mode) {
  if (mode !== previousMode) {
      if (mode !== '') {
          playSound(mode);
      } else if (currentAudio) {
          currentAudio.pause();
          currentAudio.currentTime = 0;
          currentAudio = null;
      }
      previousMode = mode;
  }

  if (mode !== '') {
      document.body.className = `${mode}-active`;
      active = mode;
      btns.forEach(b => b.classList.toggle('active', b.dataset.mode === mode));
      statusBar.textContent =
          mode === 'left' ? '車輛左轉彎' :
              mode === 'right' ? '車輛右轉彎' :
                  '車輛倒車中';
  } else {
      document.body.className = '';
      active = '';
      btns.forEach(b => b.classList.remove('active'));
      statusBar.textContent = '　';
  }
}

/* 檢查 GPIO */
function checkGPIOStatus() {
  fetch('/gpio_status')
      .then(response => response.json())
      .then(data => {
          let modeFromGPIO = '';

          if (data.rear) {
              modeFromGPIO = 'rear';
          } else if (data.left) {
              modeFromGPIO = 'left';
          } else if (data.right) {
              modeFromGPIO = 'right';
          }

          updateMode(modeFromGPIO);
      })
      .catch(error => {
          console.error('GPIO檢查失敗', error);
      });
}

/* 每 200ms 檢查一次 */
setInterval(checkGPIOStatus, 200);

/* 手動按按鈕（模擬GPIO） */
btns.forEach(btn => {
  btn.addEventListener('click', () => {
      const mode = btn.dataset.mode;
      if (active === mode) {
          updateMode('');
      } else {
          updateMode(mode);
      }
  });
});

/* 裝置資訊Modal */
document.addEventListener('DOMContentLoaded', function () {
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
              .then(response => response.text())
              .then(html => {
                  document.open();
                  document.write(html);
                  document.close();
              })
              .catch(error => {
                  alert("重設失敗！");
                  console.error(error);
              });
      }
  });
});
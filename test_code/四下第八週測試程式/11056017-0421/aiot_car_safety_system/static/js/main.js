function checkStatus() {
  $.get('/status', function (data) {
    const { status, danger, object, objects } = data;

    const statusText = document.getElementById('statusText');
    const statusBox = document.getElementById('statusBox');
    const objectList = document.getElementById('objectList');
    const alertSound = document.getElementById('alertSound');

    if (danger) {
      statusText.textContent = `⚠️ 警告：偵測到 ${object}`;
      statusBox.className = 'p-5 rounded border border-3 border-danger bg-danger-subtle';
      alertSound.play();
    } else {
      statusText.textContent = '✅ 安全狀態';
      statusBox.className = 'p-5 rounded border border-3 border-success bg-success-subtle';
    }

    if (objects && objects.length > 0) {
      objectList.textContent = `🚧 偵測到物件：${objects.join(', ')}`;
    } else {
      objectList.textContent = '🔍 目前畫面中沒有明顯物件';
    }
  });
}

setInterval(checkStatus, 2000);

document.getElementById('toggleBtn').addEventListener('click', function () {
  const videoDiv = document.getElementById('videoContainer');
  const video = document.getElementById('videoStream');

  if (videoDiv.style.display === 'none') {
    video.src = '/video_feed';
    videoDiv.style.display = 'block';
    this.textContent = '⏹️ 隱藏即時影像';
  } else {
    video.src = '';
    videoDiv.style.display = 'none';
    this.textContent = '▶️ 顯示即時影像';
  }
});

document.getElementById('cameraSelect').addEventListener('change', function () {
  const selectedIndex = this.value;
  const video = document.getElementById('videoStream');
  video.src = '';

  fetch(`/switch_camera/${selectedIndex}`)
    .then(res => res.json())
    .then(data => {
      console.log(data.message);
      setTimeout(() => {
        video.src = '/video_feed';
      }, 500);
    });
});

document.addEventListener('DOMContentLoaded', function () {
    let countdown = 900; // 15分鐘
    let timer = null;
    const countdownSpan = document.getElementById('countdown');
    const qrImage = document.getElementById('qrImage');

    const serverUrl = "http://172.20.10.2:307";  // ⚠️你的S端IP
    const deviceSerial = "mdgcs001";              // ⚠️你的device序號

    function startCountdown() {
        timer = setInterval(() => {
            countdown--;
            countdownSpan.textContent = countdown;

            if (countdown <= 0) {
                clearInterval(timer);
                alert("⚠️ Reset QR已過期，系統將重新產生新的QR");
                refreshResetQRCode();
            }
        }, 1000);
    }

    function refreshResetQRCode() {
        fetch(`${serverUrl}/generate_reset_token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ device_serial: deviceSerial })
        })
        .then(response => response.json())
        .then(data => {
            qrImage.src = "data:image/png;base64," + data.qr_base64;
            clearInterval(timer);
            countdown = 900;
            startCountdown();
        })
        .catch(error => {
            alert("⚠️ 重新取得QR失敗，請稍後重試");
            console.error(error);
        });
    }

    function startSyncCheck() {
        setInterval(() => {
            fetch(`${serverUrl}/sync_device`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ device_serial: deviceSerial })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === "pending") {
                    console.log("✅ 伺服器回應：設備已重設，顯示成功頁");
                    window.location.href = '/reset_success';
                }
            })            
            .catch(error => {
                console.error("同步檢查失敗：", error);
            });
        }, 5000); // 每5秒檢查一次
    }

    startCountdown();
    startSyncCheck(); // 🔥 同步偵測開啟
});
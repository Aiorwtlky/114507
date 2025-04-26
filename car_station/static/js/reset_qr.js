document.addEventListener('DOMContentLoaded', function () {
    let countdown = 900; // 15分鐘
    let timer = null;    // 🔥 timer變全域
    const countdownSpan = document.getElementById('countdown');
    const qrImage = document.getElementById('qrImage');

    const serverUrl = "http://192.168.0.48:307";
    const deviceSerial = "mdgcs001";             

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
            clearInterval(timer);  // 🔥 先清掉舊的 timer
            countdown = 900;       // 重置倒數
            startCountdown();      // 重新啟動新的倒數
        })
        .catch(error => {
            alert("⚠️ 重新取得QR失敗，請稍後重試");
            console.error(error);
        });
    }

    startCountdown();
});

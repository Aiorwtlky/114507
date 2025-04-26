document.addEventListener('DOMContentLoaded', function () {
    let countdown = 900; // 15分鐘
    const countdownSpan = document.getElementById('countdown');
    const refreshBtn = document.getElementById('refreshBtn');
    const qrImage = document.getElementById('qrImage');

    const serverUrl = "http://localhost:307"; // ⚠️改你的S端IP
    const deviceSerial = "mdgcs001";             // ⚠️改你的C端device_serial

    function startCountdown() {
        const timer = setInterval(() => {
            countdown--;
            countdownSpan.textContent = countdown;

            if (countdown <= 0) {
                clearInterval(timer);
                alert("⚠️ QR Code 已過期，請重新產生！");
            }
        }, 1000);
    }

    function refreshQRCode() {
        fetch(`${serverUrl}/register_device`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ device_serial: deviceSerial })
        })
        .then(response => response.json())
        .then(data => {
            qrImage.src = "data:image/png;base64," + data.qr_base64;
            countdown = 900; // 重設倒數
        })
        .catch(error => {
            alert("⚠️ 重新取得 QR 失敗");
            console.error(error);
        });
    }

    function syncDeviceStatus() {
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
                if (data.status === "bound") {
                    saveDeviceInfoLocally(data);
                }
            })
            .catch(error => {
                console.error("同步失敗：", error);
            });
        }, 5000); // 每5秒查一次
    }

    function saveDeviceInfoLocally(data) {
        fetch('/save_device_info', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                car_brand: data.car_brand,
                car_plate: data.car_plate,
                vehicle_type: data.vehicle_type,
                driver_position: data.driver_position
            })
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                window.location.href = '/install_success'; // 綁定成功，跳回首頁
            }
        })
        .catch(error => {
            console.error("本地儲存失敗：", error);
        });
    }

    refreshBtn.addEventListener('click', refreshQRCode);

    startCountdown();
    syncDeviceStatus();
});

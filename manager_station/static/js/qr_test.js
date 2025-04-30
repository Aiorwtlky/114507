document.addEventListener('DOMContentLoaded', function () {
    const generateBtn = document.getElementById('generateBtn');
    const input = document.getElementById('deviceSerialInput');
    const encryptedText = document.getElementById('encryptedText');
    const qrImage = document.getElementById('qrImage');

    generateBtn.addEventListener('click', function () {
        const serial = input.value.trim();
        if (!serial) {
            alert('請輸入 device serial');
            return;
        }

        fetch('/generate_token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ device_serial: serial })
        })
        .then(response => response.json())
        .then(data => {
            encryptedText.textContent = "加密結果：" + data.token;
            qrImage.src = "data:image/png;base64," + data.qr_base64;
            qrImage.style.display = 'block';
        })
        .catch(error => {
            alert('發生錯誤');
            console.error(error);
        });
    });
});

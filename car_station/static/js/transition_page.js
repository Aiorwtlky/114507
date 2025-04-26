document.addEventListener('DOMContentLoaded', function () {
    let countdownElement = document.getElementById('countdown');
    if (countdownElement) {
        let count = parseInt(countdownElement.innerText);

        let timer = setInterval(function () {
            count--;
            if (count <= 0) {
                clearInterval(timer);
            }
            countdownElement.innerText = count;
        }, 1000);
    }
});

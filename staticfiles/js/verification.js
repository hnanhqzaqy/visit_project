document.addEventListener('DOMContentLoaded', function () {
    const countdownElement = document.getElementById('countdown');
    const resendText = document.getElementById('resend-text');
    const resendLink = document.getElementById('resend-link');

    if (!countdownElement || !resendText || !resendLink) {
        return;
    }

    let remainingSeconds = 120;

    const timer = setInterval(function () {
        remainingSeconds -= 1;

        countdownElement.textContent = remainingSeconds;

        if (remainingSeconds <= 0) {
            clearInterval(timer);

            resendText.style.display = 'none';
            resendLink.style.display = 'inline-block';
        }
    }, 1000);
});
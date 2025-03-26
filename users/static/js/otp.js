// otp.js
document.addEventListener('DOMContentLoaded', function () {
    const otpBoxes = document.querySelectorAll('.otp-box');

    otpBoxes.forEach((box, index) => {
        box.addEventListener('input', (e) => {
            if (e.target.value.length === 1 && index < otpBoxes.length - 1) {
                otpBoxes[index + 1].focus(); // Move to the next input
            }
        });

        box.addEventListener('keydown', (e) => {
            if (e.key === 'Backspace' && index > 0 && e.target.value === '') {
                otpBoxes[index - 1].focus(); // Move to the previous input
            }
        });
    });
});

setTimeout(function() {
    var successMessage = document.querySelector('.success-message');
    if (successMessage) {
        successMessage.style.display = 'none';
    }
}, 10000);  // 10 seconds
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('verify-form');
    const submitBtn = document.getElementById('submit-btn');
    const btnText = submitBtn.querySelector('span');
    const spinner = document.getElementById('btn-spinner');

    if (form) {
        form.addEventListener('submit', () => {
            // Show loading state
            btnText.textContent = 'Verifying...';
            spinner.classList.remove('default-hidden');
            submitBtn.style.opacity = '0.8';
            submitBtn.style.cursor = 'not-allowed';
        });
    }
});

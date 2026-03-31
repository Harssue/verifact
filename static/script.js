document.addEventListener('DOMContentLoaded', () => {
    // Grab form and UI controls once the page DOM is ready.
    const form = document.getElementById('verify-form');
    const submitBtn = document.getElementById('submit-btn');
    // Safely resolve nested span only if submit button exists.
    const btnText = submitBtn ? submitBtn.querySelector('span') : null;
    const spinner = document.getElementById('btn-spinner');

    // Bind submit loading state only when all required elements are present.
    if (form && submitBtn && btnText && spinner) {
        form.addEventListener('submit', () => {
            // Show loading state
            btnText.textContent = 'Verifying...';
            spinner.classList.remove('default-hidden');
            submitBtn.style.opacity = '0.8';
            submitBtn.style.cursor = 'not-allowed';
            // Prevent accidental double submit while backend is processing.
            submitBtn.disabled = true;
        });
    }
});

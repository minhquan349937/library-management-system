document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const passwordInput = document.querySelector('input[name="password"]');

    form.addEventListener('submit', function(e) {
        if (passwordInput.value.length < 8) {
            e.preventDefault();
            alert('Password must be at least 8 characters long');
        }
    });

    passwordInput.addEventListener('input', function() {
        // Simple password strength check
        const strength = this.value.length < 8 ? 'Weak' : 
                        this.value.length < 12 ? 'Medium' : 'Strong';
        
        // Update strength indicator if it exists
        const strengthEl = document.querySelector('.password-strength');
        if (strengthEl) {
            strengthEl.textContent = `Password strength: ${strength}`;
        }
    });
});
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const submitBtn = document.getElementById('submitBtn');
    const passwordToggle = document.getElementById('passwordToggle');
    const passwordInput = document.getElementById('password');
    const loginField = document.getElementById('login_field');
    
    // Password toggle functionality
    if (passwordToggle && passwordInput) {
        passwordToggle.addEventListener('click', function() {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            
            // Update icon
            const icon = passwordToggle.querySelector('svg');
            if (type === 'text') {
                icon.innerHTML = `
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                    <line x1="1" y1="1" x2="23" y2="23"/>
                `;
            } else {
                icon.innerHTML = `
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                `;
            }
        });
    }
    
    // Real-time validation
    function validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    function validateUsername(username) {
        return username.length >= 3 && /^[a-zA-Z0-9_]+$/.test(username);
    }
    
    function showFieldError(fieldId, message) {
        const errorElement = document.getElementById(fieldId + '_error');
        const inputElement = document.getElementById(fieldId);
        
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.classList.add('show');
        }
        
        if (inputElement) {
            inputElement.style.borderColor = '#ef4444';
        }
    }
    
    function hideFieldError(fieldId) {
        const errorElement = document.getElementById(fieldId + '_error');
        const inputElement = document.getElementById(fieldId);
        
        if (errorElement) {
            errorElement.classList.remove('show');
        }
        
        if (inputElement) {
            inputElement.style.borderColor = '#e5e7eb';
        }
    }
    
    // Login field validation
    if (loginField) {
        loginField.addEventListener('blur', function() {
            const value = this.value.trim();
            
            if (!value) {
                showFieldError('login_field', 'Email or username is required');
                return;
            }
            
            // Check if it's an email or username
            if (value.includes('@')) {
                if (!validateEmail(value)) {
                    showFieldError('login_field', 'Please enter a valid email address');
                    return;
                }
            } else {
                if (!validateUsername(value)) {
                    showFieldError('login_field', 'Username must be at least 3 characters and contain only letters, numbers, and underscores');
                    return;
                }
            }
            
            hideFieldError('login_field');
        });
        
        loginField.addEventListener('input', function() {
            if (this.value.trim()) {
                hideFieldError('login_field');
            }
        });
    }
    
    // Password validation
    if (passwordInput) {
        passwordInput.addEventListener('blur', function() {
            const value = this.value;
            
            if (!value) {
                showFieldError('password', 'Password is required');
                return;
            }
            
            if (value.length < 6) {
                showFieldError('password', 'Password must be at least 6 characters long');
                return;
            }
            
            hideFieldError('password');
        });
        
        passwordInput.addEventListener('input', function() {
            if (this.value) {
                hideFieldError('password');
            }
        });
    }
    
    // Form submission with loading state
    if (loginForm && submitBtn) {
        loginForm.addEventListener('submit', function(e) {
            // Validate all fields before submission
            let isValid = true;
            
            if (loginField) {
                const loginValue = loginField.value.trim();
                if (!loginValue) {
                    showFieldError('login_field', 'Email or username is required');
                    isValid = false;
                } else if (loginValue.includes('@') && !validateEmail(loginValue)) {
                    showFieldError('login_field', 'Please enter a valid email address');
                    isValid = false;
                } else if (!loginValue.includes('@') && !validateUsername(loginValue)) {
                    showFieldError('login_field', 'Invalid username format');
                    isValid = false;
                }
            }
            
            if (passwordInput) {
                const passwordValue = passwordInput.value;
                if (!passwordValue) {
                    showFieldError('password', 'Password is required');
                    isValid = false;
                } else if (passwordValue.length < 6) {
                    showFieldError('password', 'Password must be at least 6 characters long');
                    isValid = false;
                }
            }
            
            if (!isValid) {
                e.preventDefault();
                return;
            }
            
            // Show loading state
            submitBtn.classList.add('loading');
            submitBtn.disabled = true;
            
            // Remove loading state after a delay if form submission fails
            setTimeout(() => {
                submitBtn.classList.remove('loading');
                submitBtn.disabled = false;
            }, 5000);
        });
    }
    
    // Social login handlers (placeholder for future implementation)
    const googleBtn = document.querySelector('.google-btn');
    const githubBtn = document.querySelector('.github-btn');
    
    if (googleBtn) {
        googleBtn.addEventListener('click', function() {
            // Placeholder for Google OAuth implementation
            alert('Google login will be implemented soon!');
        });
    }
    
    if (githubBtn) {
        githubBtn.addEventListener('click', function() {
            // Placeholder for GitHub OAuth implementation
            alert('GitHub login will be implemented soon!');
        });
    }
    
    // Auto-fill demo credentials
    const demoCredentials = document.querySelector('.demo-credentials');
    if (demoCredentials) {
        demoCredentials.addEventListener('click', function() {
            if (loginField) {
                loginField.value = 'admin';
                loginField.dispatchEvent(new Event('input'));
            }
            if (passwordInput) {
                passwordInput.value = 'admin123';
                passwordInput.dispatchEvent(new Event('input'));
            }
        });
        
        // Add cursor pointer style
        demoCredentials.style.cursor = 'pointer';
        demoCredentials.title = 'Click to auto-fill demo credentials';
    }
    
    // Smooth focus transitions
    const formInputs = document.querySelectorAll('.form-input');
    formInputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
        });
    });
    
    // Remember me functionality
    const rememberCheckbox = document.getElementById('remember_me');
    if (rememberCheckbox) {
        // Load saved credentials if remember me was checked
        const savedUsername = localStorage.getItem('rememberedUsername');
        if (savedUsername && loginField) {
            loginField.value = savedUsername;
            rememberCheckbox.checked = true;
        }
        
        // Save credentials when form is submitted with remember me checked
        if (loginForm) {
            loginForm.addEventListener('submit', function() {
                if (rememberCheckbox.checked && loginField) {
                    localStorage.setItem('rememberedUsername', loginField.value);
                } else {
                    localStorage.removeItem('rememberedUsername');
                }
            });
        }
    }
    
    // Enhanced keyboard navigation
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && e.target.classList.contains('form-input')) {
            const inputs = Array.from(document.querySelectorAll('.form-input'));
            const currentIndex = inputs.indexOf(e.target);
            
            if (currentIndex < inputs.length - 1) {
                e.preventDefault();
                inputs[currentIndex + 1].focus();
            }
        }
    });
    
    // Add ripple effect to buttons
    function createRipple(event) {
        const button = event.currentTarget;
        const circle = document.createElement('span');
        const diameter = Math.max(button.clientWidth, button.clientHeight);
        const radius = diameter / 2;
        
        circle.style.width = circle.style.height = `${diameter}px`;
        circle.style.left = `${event.clientX - button.offsetLeft - radius}px`;
        circle.style.top = `${event.clientY - button.offsetTop - radius}px`;
        circle.classList.add('ripple');
        
        const ripple = button.getElementsByClassName('ripple')[0];
        if (ripple) {
            ripple.remove();
        }
        
        button.appendChild(circle);
    }
    
    // Add ripple effect styles
    const style = document.createElement('style');
    style.textContent = `
        .submit-btn {
            position: relative;
            overflow: hidden;
        }
        
        .ripple {
            position: absolute;
            border-radius: 50%;
            background-color: rgba(255, 255, 255, 0.3);
            transform: scale(0);
            animation: ripple 600ms linear;
            pointer-events: none;
        }
        
        @keyframes ripple {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
    
    if (submitBtn) {
        submitBtn.addEventListener('click', createRipple);
    }
});

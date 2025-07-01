// Main JavaScript for Hydration Calculator

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Add smooth scrolling to all links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Add form validation
    initializeFormValidation();

    // Add interactive elements
    initializeInteractiveElements();

    // Check for saved theme preference
    initializeTheme();
}

function initializeFormValidation() {
    // Bootstrap form validation
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Custom validation for specific fields
    const weightInput = document.getElementById('id_weight');
    if (weightInput) {
        weightInput.addEventListener('input', function() {
            validateWeight(this);
        });
    }

    const ageInput = document.getElementById('id_age');
    if (ageInput) {
        ageInput.addEventListener('input', function() {
            validateAge(this);
        });
    }

    const customGoalInput = document.getElementById('id_custom_daily_goal');
    if (customGoalInput) {
        customGoalInput.addEventListener('input', function() {
            validateCustomGoal(this);
        });
    }
}

function validateWeight(input) {
    const value = parseFloat(input.value);
    const feedback = input.parentNode.querySelector('.invalid-feedback') || createFeedbackElement(input);
    
    if (value < 30 || value > 300) {
        input.setCustomValidity('Weight must be between 30 and 300 kg');
        feedback.textContent = 'Weight must be between 30 and 300 kg';
        input.classList.add('is-invalid');
    } else {
        input.setCustomValidity('');
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
    }
}

function validateAge(input) {
    const value = parseInt(input.value);
    const feedback = input.parentNode.querySelector('.invalid-feedback') || createFeedbackElement(input);
    
    if (value < 1 || value > 120) {
        input.setCustomValidity('Age must be between 1 and 120 years');
        feedback.textContent = 'Age must be between 1 and 120 years';
        input.classList.add('is-invalid');
    } else {
        input.setCustomValidity('');
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
    }
}

function validateCustomGoal(input) {
    const value = parseInt(input.value);
    const feedback = input.parentNode.querySelector('.invalid-feedback') || createFeedbackElement(input);
    
    if (input.value && (value < 500 || value > 5000)) {
        input.setCustomValidity('Custom goal must be between 500 and 5000 ml');
        feedback.textContent = 'Custom goal must be between 500 and 5000 ml';
        input.classList.add('is-invalid');
    } else {
        input.setCustomValidity('');
        input.classList.remove('is-invalid');
        if (input.value) {
            input.classList.add('is-valid');
        }
    }
}

function createFeedbackElement(input) {
    const feedback = document.createElement('div');
    feedback.className = 'invalid-feedback';
    input.parentNode.appendChild(feedback);
    return feedback;
}

function initializeInteractiveElements() {
    // Add water drop animation to buttons
    const waterButtons = document.querySelectorAll('.btn-primary');
    waterButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            createWaterDropAnimation(e);
        });
    });

    // Add progress bar animation
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(bar => {
        animateProgressBar(bar);
    });

    // Add counter animation for stats
    const statNumbers = document.querySelectorAll('.card-title');
    statNumbers.forEach(number => {
        if (isNumeric(number.textContent)) {
            animateCounter(number);
        }
    });
}

function createWaterDropAnimation(event) {
    const button = event.currentTarget;
    const rect = button.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    const drop = document.createElement('span');
    drop.className = 'water-drop';
    drop.style.position = 'absolute';
    drop.style.left = x + 'px';
    drop.style.top = y + 'px';
    drop.style.color = '#1e90ff';
    drop.innerHTML = '💧';
    drop.style.pointerEvents = 'none';
    drop.style.fontSize = '1.5rem';

    button.style.position = 'relative';
    button.appendChild(drop);

    setTimeout(() => {
        if (drop.parentNode) {
            drop.parentNode.removeChild(drop);
        }
    }, 2000);
}

function animateProgressBar(bar) {
    const targetWidth = bar.style.width;
    bar.style.width = '0%';
    setTimeout(() => {
        bar.style.width = targetWidth;
    }, 300);
}

function animateCounter(element) {
    const target = parseInt(element.textContent.replace(/[^\d]/g, ''));
    if (isNaN(target)) return;

    let current = 0;
    const increment = target / 50;
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        element.textContent = Math.floor(current);
    }, 50);
}

function isNumeric(str) {
    return /^\d+$/.test(str.replace(/[^\d]/g, ''));
}

function initializeTheme() {
    // Check for saved theme preference or default to light mode
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);

    // Add theme toggle functionality if toggle exists
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
}

// Utility Functions
function showToast(type, message, duration = 3000) {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    toast.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    document.body.appendChild(toast);
    
    // Auto remove after specified duration
    setTimeout(() => {
        if (toast.parentNode) {
            toast.classList.remove('show');
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 150);
        }
    }, duration);
}

function formatNumber(num) {
    return new Intl.NumberFormat().format(num);
}

function formatDate(date) {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    }).format(new Date(date));
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Dashboard specific functions
function updateWaterBottle(percentage) {
    const waterFill = document.querySelector('.water-fill');
    const progressText = document.querySelector('.progress-text');
    
    if (waterFill) {
        waterFill.style.height = percentage + '%';
    }
    
    if (progressText) {
        progressText.textContent = percentage + '%';
    }
}

function updateProgressBar(elementId, percentage) {
    const progressBar = document.getElementById(elementId);
    if (progressBar) {
        progressBar.style.width = percentage + '%';
        progressBar.textContent = percentage + '%';
        
        // Update color based on progress
        progressBar.className = progressBar.className.replace(/bg-\w+/, '');
        if (percentage >= 100) {
            progressBar.classList.add('bg-success');
        } else if (percentage >= 75) {
            progressBar.classList.add('bg-info');
        } else if (percentage >= 50) {
            progressBar.classList.add('bg-warning');
        } else {
            progressBar.classList.add('bg-primary');
        }
    }
}

// Chart utilities
function createGradient(ctx, color1, color2) {
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, color1);
    gradient.addColorStop(1, color2);
    return gradient;
}

// Local storage utilities
function saveToLocalStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
    } catch (e) {
        console.warn('Local storage not available');
    }
}

function getFromLocalStorage(key, defaultValue = null) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : defaultValue;
    } catch (e) {
        console.warn('Local storage not available');
        return defaultValue;
    }
}

// Performance monitoring
function measurePerformance(label, fn) {
    const start = performance.now();
    const result = fn();
    const end = performance.now();
    console.log(`${label} took ${end - start} milliseconds`);
    return result;
}

// Export functions for use in other scripts
window.HydrationApp = {
    showToast,
    updateWaterBottle,
    updateProgressBar,
    formatNumber,
    formatDate,
    saveToLocalStorage,
    getFromLocalStorage,
    debounce
};

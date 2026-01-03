/**
 * ULTRA-INTENSE LOGIN ANIMATION INITIALIZER
 * Maximum power and dominance for high-security system entry
 */

(function() {
    'use strict';

    /**
     * Initialize the ultra-intense login animation
     * @param {string} containerSelector - CSS selector for the container element
     */
    function initUltraIntenseLogin(containerSelector = 'body') {
        const container = document.querySelector(containerSelector);
        if (!container) {
            console.error('Container element not found:', containerSelector);
            return;
        }

        // Create main animation container
        const animationContainer = document.createElement('div');
        animationContainer.className = 'ultra-intense-login-container';
        
        // Create ultra-bright screen flash
        const screenFlash = document.createElement('div');
        screenFlash.className = 'ultra-screen-flash';
        animationContainer.appendChild(screenFlash);

        // Create mega explosion
        const megaExplosion = document.createElement('div');
        megaExplosion.className = 'mega-explosion';
        animationContainer.appendChild(megaExplosion);

        // Create camera shake wrapper
        const cameraShake = document.createElement('div');
        cameraShake.className = 'camera-shake';
        animationContainer.appendChild(cameraShake);

        // Create shockwave container
        const shockwaveContainer = document.createElement('div');
        shockwaveContainer.className = 'shockwave-container';
        for (let i = 1; i <= 5; i++) {
            const shockwave = document.createElement('div');
            shockwave.className = `shockwave shockwave-${i}`;
            shockwaveContainer.appendChild(shockwave);
        }
        cameraShake.appendChild(shockwaveContainer);

        // Create fracture container
        const fractureContainer = document.createElement('div');
        fractureContainer.className = 'fracture-container';
        for (let i = 1; i <= 10; i++) {
            const fracture = document.createElement('div');
            fracture.className = `fracture fracture-${i}`;
            fractureContainer.appendChild(fracture);
        }
        cameraShake.appendChild(fractureContainer);

        // Create power surge container
        const powerSurgeContainer = document.createElement('div');
        powerSurgeContainer.className = 'power-surge-container';
        for (let i = 1; i <= 6; i++) {
            const surge = document.createElement('div');
            surge.className = `power-surge power-surge-${i}`;
            powerSurgeContainer.appendChild(surge);
        }
        cameraShake.appendChild(powerSurgeContainer);

        // Create scan lines container
        const scanLinesContainer = document.createElement('div');
        scanLinesContainer.className = 'scan-lines-container';
        for (let i = 1; i <= 3; i++) {
            const scanLine = document.createElement('div');
            scanLine.className = `scan-line scan-line-${i}`;
            scanLinesContainer.appendChild(scanLine);
        }
        cameraShake.appendChild(scanLinesContainer);

        // Create energy pulse container
        const energyPulseContainer = document.createElement('div');
        energyPulseContainer.className = 'energy-pulse-container';
        for (let i = 1; i <= 3; i++) {
            const pulse = document.createElement('div');
            pulse.className = `energy-pulse energy-pulse-${i}`;
            energyPulseContainer.appendChild(pulse);
        }
        cameraShake.appendChild(energyPulseContainer);

        // Create extreme glitch overlay
        const extremeGlitch = document.createElement('div');
        extremeGlitch.className = 'extreme-glitch';
        cameraShake.appendChild(extremeGlitch);

        // Create system unlock effect
        const systemUnlock = document.createElement('div');
        systemUnlock.className = 'system-unlock-effect';
        animationContainer.appendChild(systemUnlock);

        // Create unlock particles
        const unlockParticles = document.createElement('div');
        unlockParticles.className = 'unlock-particles';
        for (let i = 1; i <= 8; i++) {
            const particle = document.createElement('div');
            particle.className = `unlock-particle unlock-particle-${i}`;
            unlockParticles.appendChild(particle);
        }
        animationContainer.appendChild(unlockParticles);

        // Append to container
        container.appendChild(animationContainer);

        // Remove screen flash after animation completes (FASTER than registration)
        setTimeout(() => {
            if (screenFlash.parentNode) {
                screenFlash.remove();
            }
        }, 400);

        // Restart mega explosion periodically for continuous impact (FASTER than registration)
        setInterval(() => {
            const newExplosion = document.createElement('div');
            newExplosion.className = 'mega-explosion';
            animationContainer.appendChild(newExplosion);
            
            setTimeout(() => {
                if (newExplosion.parentNode) {
                    newExplosion.remove();
                }
            }, 300);
        }, 3000);

        // Restart system unlock effect periodically
        setInterval(() => {
            const newUnlock = document.createElement('div');
            newUnlock.className = 'system-unlock-effect';
            animationContainer.appendChild(newUnlock);
            
            // Create new unlock particles
            const newParticles = document.createElement('div');
            newParticles.className = 'unlock-particles';
            for (let i = 1; i <= 8; i++) {
                const particle = document.createElement('div');
                particle.className = `unlock-particle unlock-particle-${i}`;
                newParticles.appendChild(particle);
            }
            animationContainer.appendChild(newParticles);
            
            setTimeout(() => {
                if (newUnlock.parentNode) {
                    newUnlock.remove();
                }
                if (newParticles.parentNode) {
                    newParticles.remove();
                }
            }, 1500);
        }, 5000);

        return animationContainer;
    }

    /**
     * Destroy the animation (cleanup)
     * @param {HTMLElement} animationContainer - The animation container element
     */
    function destroyUltraIntenseLogin(animationContainer) {
        if (animationContainer && animationContainer.parentNode) {
            animationContainer.remove();
        }
    }

    // Auto-initialize on DOM ready if data attribute is present
    document.addEventListener('DOMContentLoaded', function() {
        const autoInitElements = document.querySelectorAll('[data-ultra-intense-login]');
        autoInitElements.forEach(element => {
            const container = element.getAttribute('data-ultra-intense-login') || 'body';
            initUltraIntenseLogin(container);
        });
    });

    // Export functions to global scope
    window.UltraIntenseLogin = {
        init: initUltraIntenseLogin,
        destroy: destroyUltraIntenseLogin
    };

})();


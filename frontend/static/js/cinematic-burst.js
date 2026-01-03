/**
 * CINEMATIC BURST ANIMATION INITIALIZER
 * Dynamically creates and manages the high-impact background animation
 */

(function () {
    'use strict';

    /**
     * Initialize the cinematic burst animation
     * @param {string} containerSelector - CSS selector for the container element
     */
    function initCinematicBurst(containerSelector = 'body') {
        const container = document.querySelector(containerSelector);
        if (!container) {
            console.error('Container element not found:', containerSelector);
            return;
        }

        // Create main animation container
        const animationContainer = document.createElement('div');
        animationContainer.className = 'cinematic-burst-container';

        // Create screen flash effect
        const screenFlash = document.createElement('div');
        screenFlash.className = 'screen-flash';
        animationContainer.appendChild(screenFlash);

        // Create initial burst explosion
        const burstExplosion = document.createElement('div');
        burstExplosion.className = 'burst-explosion';
        animationContainer.appendChild(burstExplosion);

        // Create shard container
        const shardContainer = document.createElement('div');
        shardContainer.className = 'shard-container';

        // Generate shards (Reduced count for performance)
        for (let i = 1; i <= 4; i++) {
            const shard = document.createElement('div');
            shard.className = `shard shard-${i}`;
            shardContainer.appendChild(shard);
        }
        animationContainer.appendChild(shardContainer);

        // Create lines container
        const linesContainer = document.createElement('div');
        linesContainer.className = 'lines-container';

        // Generate horizontal lines (Reduced)
        for (let i = 1; i <= 3; i++) {
            const line = document.createElement('div');
            line.className = `line line-${i}`;
            linesContainer.appendChild(line);
        }

        // Generate vertical lines (Reduced)
        for (let i = 1; i <= 2; i++) {
            const line = document.createElement('div');
            line.className = `line-vertical line-v${i}`;
            linesContainer.appendChild(line);
        }
        animationContainer.appendChild(linesContainer);

        // Create particles container
        const particlesContainer = document.createElement('div');
        particlesContainer.className = 'particles-container';

        // Generate particles (Reduced)
        for (let i = 1; i <= 5; i++) {
            const particle = document.createElement('div');
            particle.className = `particle particle-${i}`;
            particlesContainer.appendChild(particle);
        }
        animationContainer.appendChild(particlesContainer);

        // Create energy waves
        for (let i = 1; i <= 3; i++) {
            const wave = document.createElement('div');
            wave.className = `energy-wave energy-wave-${i}`;
            animationContainer.appendChild(wave);
        }

        // Create glitch overlay
        const glitchOverlay = document.createElement('div');
        glitchOverlay.className = 'glitch-overlay';
        animationContainer.appendChild(glitchOverlay);

        // Append to container
        container.appendChild(animationContainer);

        // Remove screen flash after animation completes
        setTimeout(() => {
            if (screenFlash.parentNode) {
                screenFlash.remove();
            }
        }, 500);

        // Restart burst explosion periodically for continuous impact
        setInterval(() => {
            const newBurst = document.createElement('div');
            newBurst.className = 'burst-explosion';
            animationContainer.appendChild(newBurst);

            setTimeout(() => {
                if (newBurst.parentNode) {
                    newBurst.remove();
                }
            }, 800);
        }, 5000);

        return animationContainer;
    }

    /**
     * Destroy the animation (cleanup)
     * @param {HTMLElement} animationContainer - The animation container element
     */
    function destroyCinematicBurst(animationContainer) {
        if (animationContainer && animationContainer.parentNode) {
            animationContainer.remove();
        }
    }

    // Auto-initialize on DOM ready if data attribute is present
    document.addEventListener('DOMContentLoaded', function () {
        const autoInitElements = document.querySelectorAll('[data-cinematic-burst]');
        autoInitElements.forEach(element => {
            const container = element.getAttribute('data-cinematic-burst') || 'body';
            initCinematicBurst(container);
        });
    });

    // Export functions to global scope
    window.CinematicBurst = {
        init: initCinematicBurst,
        destroy: destroyCinematicBurst
    };

})();


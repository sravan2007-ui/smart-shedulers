/**
 * ANTI-GRAVITY LOGIN ANIMATION
 * Physics-driven, cursor-reactive force field system
 * Heavy motion, zero-gravity control system feel
 */

(function () {
    'use strict';

    let mouseX = 0;
    let mouseY = 0;
    let forceFieldZone = null;
    let particles = [];
    let shards = [];
    let fragments = [];
    let animationFrame = null;
    let isMouseActive = false;

    /**
     * Initialize anti-gravity animation
     * @param {string} containerSelector - CSS selector for container
     */
    function initAntiGravity(containerSelector = 'body') {
        const container = document.querySelector(containerSelector);
        if (!container) {
            console.error('Container not found:', containerSelector);
            return;
        }

        // Create main container
        const animationContainer = document.createElement('div');
        animationContainer.className = 'anti-gravity-container';

        // Create force field grid
        const grid = document.createElement('div');
        grid.className = 'force-field-grid';
        animationContainer.appendChild(grid);

        // Create entry burst
        const entryBurst = document.createElement('div');
        entryBurst.className = 'anti-gravity-entry';
        animationContainer.appendChild(entryBurst);

        // Create force field zone (cursor reactive)
        forceFieldZone = document.createElement('div');
        forceFieldZone.className = 'force-field-zone';
        animationContainer.appendChild(forceFieldZone);

        // Create gravity wells
        createGravityWells(animationContainer);

        // Create energy streams
        createEnergyStreams(animationContainer);

        // Create floating particles
        createParticles(animationContainer, 6);

        // Create floating shards
        createShards(animationContainer, 5);

        // Create UI fragments
        createFragments(animationContainer, 4);

        // Append to container
        container.appendChild(animationContainer);

        // Create Flashlight/Spotlight Pointer
        const pointer = document.createElement('div');
        pointer.className = 'gravity-pointer';
        animationContainer.appendChild(pointer);

        // Setup cursor tracking
        setupCursorTracking(container, pointer);

        // Start physics simulation
        startPhysicsSimulation();

        // Remove entry burst after animation
        setTimeout(() => {
            if (entryBurst.parentNode) {
                entryBurst.remove();
            }
        }, 1500);

        return animationContainer;
    }

    /**
     * Create floating particles
     */
    function createParticles(container, count) {
        const sizes = ['large', 'medium', 'small'];
        const animations = ['floatHeavy', 'floatHeavyReverse'];

        for (let i = 0; i < count; i++) {
            const particle = document.createElement('div');
            const size = sizes[Math.floor(Math.random() * sizes.length)];
            const animation = animations[Math.floor(Math.random() * animations.length)];
            const depth = Math.floor(Math.random() * 4) + 1;

            particle.className = `anti-gravity-particle particle-${size} cursor-reactive depth-layer-${depth}`;
            // Optimization: Set initial position to 0 and track logic coordinate for transform
            particle.style.left = '0';
            particle.style.top = '0';
            // Use logical coordinates for state
            const initialX = Math.random() * 100;
            const initialY = Math.random() * 100;

            particle.style.transform = `translate3d(${initialX}vw, ${initialY}vh, 0)`;
            // We use standard CCS animation for "float", but JS will override transform.
            // We need to decide: JS physics OR CSS float. 
            // User wants "Antigravity" which implies physics. We will disable CSS animation if JS runs.
            particle.style.animation = 'none';
            particle.style.willChange = 'transform';

            container.appendChild(particle);
            particles.push({
                element: particle,
                x: initialX,
                y: initialY,
                vx: (Math.random() - 0.5) * 0.5,
                vy: (Math.random() - 0.5) * 0.5,
                mass: size === 'large' ? 3 : size === 'medium' ? 2 : 1
            });
        }
    }

    /**
     * Create floating shards
     */
    function createShards(container, count) {
        const sizes = ['large', 'medium', 'small'];
        const colors = [
            'rgba(255, 255, 255, 0.2)',
            'rgba(255, 255, 255, 0.15)',
            'rgba(255, 255, 255, 0.1)'
        ];

        for (let i = 0; i < count; i++) {
            const shard = document.createElement('div');
            const size = sizes[Math.floor(Math.random() * sizes.length)];
            const color = colors[Math.floor(Math.random() * colors.length)];
            const depth = Math.floor(Math.random() * 4) + 1;
            const direction = Math.random() > 0.5 ? 1 : -1;

            shard.className = `anti-gravity-shard shard-${size} cursor-reactive depth-layer-${depth}`;
            shard.style.left = '0';
            shard.style.top = '0';
            const initialX = Math.random() * 100;
            const initialY = Math.random() * 100;

            shard.style.transform = `translate3d(${initialX}vw, ${initialY}vh, 0)`;
            shard.style.borderColor = `transparent transparent ${color} transparent`;
            shard.style.animation = 'none'; // Physics controlled
            shard.style.willChange = 'transform';

            container.appendChild(shard);
            shards.push({
                element: shard,
                x: initialX,
                y: initialY,
                vx: (Math.random() - 0.5) * 0.3,
                vy: (Math.random() - 0.5) * 0.3,
                mass: size === 'large' ? 2.5 : size === 'medium' ? 1.5 : 1
            });
        }
    }

    /**
     * Create UI fragments
     */
    function createFragments(container, count) {
        const types = ['square', 'rectangle', 'circle', 'triangle'];

        for (let i = 0; i < count; i++) {
            const fragment = document.createElement('div');
            const type = types[Math.floor(Math.random() * types.length)];
            const depth = Math.floor(Math.random() * 4) + 1;

            fragment.className = `ui-fragment fragment-${type} cursor-reactive depth-layer-${depth}`;
            fragment.style.left = '0';
            fragment.style.top = '0';
            const initialX = Math.random() * 100;
            const initialY = Math.random() * 100;
            fragment.style.transform = `translate3d(${initialX}vw, ${initialY}vh, 0)`;
            fragment.style.willChange = 'transform';

            container.appendChild(fragment);
            fragments.push({
                element: fragment,
                x: initialX,
                y: initialY,
                vx: (Math.random() - 0.5) * 0.4,
                vy: (Math.random() - 0.5) * 0.4,
                mass: 1.5
            });
        }
    }

    /**
     * Create gravity wells
     */
    function createGravityWells(container) {
        const wellCount = 3;
        for (let i = 0; i < wellCount; i++) {
            const well = document.createElement('div');
            const type = Math.random() > 0.5 ? 'attractive' : 'repulsive';
            well.className = `gravity-well ${type}`;
            well.style.left = Math.random() * 100 + '%';
            well.style.top = Math.random() * 100 + '%';
            well.style.animationDelay = Math.random() * 2 + 's';
            container.appendChild(well);
        }
    }

    /**
     * Create energy streams
     */
    function createEnergyStreams(container) {
        const streamCount = 5;
        for (let i = 0; i < streamCount; i++) {
            const stream = document.createElement('div');
            stream.className = 'energy-stream';
            stream.style.left = Math.random() * 100 + '%';
            stream.style.top = '-200px';
            stream.style.animationDelay = Math.random() * 2 + 's';
            container.appendChild(stream);
        }
    }

    /**
     * Setup cursor tracking and force field
     */
    function setupCursorTracking(container, pointer) {
        container.addEventListener('mousemove', (e) => {
            const rect = container.getBoundingClientRect();
            mouseX = ((e.clientX - rect.left) / rect.width) * 100; // in %
            mouseY = ((e.clientY - rect.top) / rect.height) * 100; // in %
            isMouseActive = true;

            // Update force field position
            if (forceFieldZone) {
                // Use transform instead of left/top for performance
                forceFieldZone.style.transform = `translate3d(${e.clientX}px, ${e.clientY}px, 0)`;
                forceFieldZone.classList.add('active');
            }

            // Update pointer (Flashlight)
            if (pointer) {
                pointer.style.transform = `translate3d(${e.clientX}px, ${e.clientY}px, 0)`;
                pointer.style.opacity = '1';
            }
        });

        container.addEventListener('mouseleave', () => {
            isMouseActive = false;
            if (forceFieldZone) {
                forceFieldZone.classList.remove('active');
            }
            if (pointer) {
                pointer.style.opacity = '0';
            }
        });
    }

    /**
     * Physics simulation - repulsion and attraction
     */
    function startPhysicsSimulation() {
        function simulate() {
            // Apply forces to particles
            // Batch DOM reads/writes if possible, but mostly just transform updates here
            for (let i = 0, len = particles.length; i < len; i++) updateEntityPhysics(particles[i]);
            for (let i = 0, len = shards.length; i < len; i++) updateEntityPhysics(shards[i]);
            for (let i = 0, len = fragments.length; i < len; i++) updateEntityPhysics(fragments[i]);

            animationFrame = requestAnimationFrame(simulate);
        }

        function updateEntityPhysics(entity) {
            // Mouse Repulsion
            if (isMouseActive) {
                const dx = entity.x - mouseX;
                const aspect = window.innerHeight / window.innerWidth;
                const dy = (entity.y - mouseY) * aspect;

                const distanceSq = dx * dx + dy * dy;
                const limitSq = 225; // 15^2

                if (distanceSq < limitSq && distanceSq > 0.01) {
                    const distance = Math.sqrt(distanceSq);
                    const force = 0.8 / (distance * 0.5); // increased force
                    const angle = Math.atan2(dy, dx);

                    entity.vx += Math.cos(angle) * force * 0.08;
                    entity.vy += Math.sin(angle) * force * 0.08;
                }
            }

            // Apply damping
            entity.vx *= 0.95;
            entity.vy *= 0.95;

            // Ambient drift
            entity.vx += (Math.random() - 0.5) * 0.005;
            entity.vy += (Math.random() - 0.5) * 0.005;

            // Update position
            entity.x += entity.vx;
            entity.y += entity.vy;

            // Boundary wrapping
            if (entity.x < -10) entity.x = 110;
            if (entity.x > 110) entity.x = -10;
            if (entity.y < -10) entity.y = 110;
            if (entity.y > 110) entity.y = -10;

            // Use transform for performant movement
            // entity.element.style.left/top cause reflows. We used left/top for initialization,
            // but for animation we should use transform.
            // However, to switch to pure transform we need to track base position or
            // just update the transform relative to 0,0 if we set left/top to 0.
            // Let's assume we keep the initial left/top % as "base" (which we aren't, we are changing x/y).
            // So we must update left/top OR use transform from a clear origin.
            // Updating left/top is the lag source.
            // FIX: Set left:0, top:0 on creation (or in CSS) and only translate here.

            // For now, to avoid rewriting creation logic partially, we will assume elements are absolute.
            // BUT: changing left/top % on every frame IS high cost.
            // We'll update the style to use translate3d(vw, vh, 0).

            entity.element.style.transform = `translate3d(${entity.x}vw, ${entity.y}vh, 0)`;
        }

        simulate();
    }

    /**
     * Destroy animation
     */
    function destroyAntiGravity(animationContainer) {
        if (animationFrame) {
            cancelAnimationFrame(animationFrame);
        }
        if (animationContainer && animationContainer.parentNode) {
            animationContainer.remove();
        }
        particles = [];
        shards = [];
        fragments = [];
    }

    // Auto-initialize
    document.addEventListener('DOMContentLoaded', function () {
        const autoInitElements = document.querySelectorAll('[data-anti-gravity]');
        autoInitElements.forEach(element => {
            const container = element.getAttribute('data-anti-gravity') || 'body';
            // If the target is the container itself, we append TO it, logic handles specific container
            // The logic in initAntiGravity appends to document.querySelector(selector)
            initAntiGravity(container);
        });
    });

    // Export
    window.AntiGravity = {
        init: initAntiGravity,
        destroy: destroyAntiGravity
    };

})();

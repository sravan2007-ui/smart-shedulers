/**
 * ANTI-GRAVITY LOGIN ANIMATION
 * Physics-driven, cursor-reactive force field system
 * Heavy motion, zero-gravity control system feel
 */

(function() {
    'use strict';

    let mouseX = 0;
    let mouseY = 0;
    let forceFieldZone = null;
    let particles = [];
    let shards = [];
    let fragments = [];
    let animationFrame = null;

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
        createParticles(animationContainer, 15);

        // Create floating shards
        createShards(animationContainer, 12);

        // Create UI fragments
        createFragments(animationContainer, 10);

        // Append to container
        container.appendChild(animationContainer);

        // Setup cursor tracking
        setupCursorTracking(animationContainer);

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
            particle.style.left = Math.random() * 100 + '%';
            particle.style.top = Math.random() * 100 + '%';
            particle.style.animation = `${animation} ${8 + Math.random() * 4}s ease-in-out infinite`;
            particle.style.animationDelay = Math.random() * 2 + 's';
            
            container.appendChild(particle);
            particles.push({
                element: particle,
                x: parseFloat(particle.style.left),
                y: parseFloat(particle.style.top),
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
            shard.style.left = Math.random() * 100 + '%';
            shard.style.top = Math.random() * 100 + '%';
            shard.style.borderColor = `transparent transparent ${color} transparent`;
            shard.style.animation = `shardFloat${direction} ${10 + Math.random() * 5}s ease-in-out infinite`;
            shard.style.animationDelay = Math.random() * 3 + 's';
            
            container.appendChild(shard);
            shards.push({
                element: shard,
                x: parseFloat(shard.style.left),
                y: parseFloat(shard.style.top),
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
        const animations = ['fragmentFloat1', 'fragmentFloat2'];

        for (let i = 0; i < count; i++) {
            const fragment = document.createElement('div');
            const type = types[Math.floor(Math.random() * types.length)];
            const animation = animations[Math.floor(Math.random() * animations.length)];
            const depth = Math.floor(Math.random() * 4) + 1;
            
            fragment.className = `ui-fragment fragment-${type} cursor-reactive depth-layer-${depth}`;
            fragment.style.left = Math.random() * 100 + '%';
            fragment.style.top = Math.random() * 100 + '%';
            fragment.style.animation = `${animation} ${12 + Math.random() * 6}s ease-in-out infinite`;
            fragment.style.animationDelay = Math.random() * 4 + 's';
            
            container.appendChild(fragment);
            fragments.push({
                element: fragment,
                x: parseFloat(fragment.style.left),
                y: parseFloat(fragment.style.top),
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
    function setupCursorTracking(container) {
        container.addEventListener('mousemove', (e) => {
            const rect = container.getBoundingClientRect();
            mouseX = ((e.clientX - rect.left) / rect.width) * 100;
            mouseY = ((e.clientY - rect.top) / rect.height) * 100;
            
            // Update force field position
            if (forceFieldZone) {
                forceFieldZone.style.left = mouseX + '%';
                forceFieldZone.style.top = mouseY + '%';
                forceFieldZone.classList.add('active');
            }
        });

        container.addEventListener('mouseleave', () => {
            if (forceFieldZone) {
                forceFieldZone.classList.remove('active');
            }
        });
    }

    /**
     * Physics simulation - repulsion and attraction
     */
    function startPhysicsSimulation() {
        function simulate() {
            const forceFieldRadius = 150; // pixels equivalent
            const repulsionForce = 200;
            const attractionForce = 100;

            // Apply forces to particles
            particles.forEach(particle => {
                const rect = particle.element.getBoundingClientRect();
                const px = rect.left + rect.width / 2;
                const py = rect.top + rect.height / 2;
                
                if (forceFieldZone && forceFieldZone.classList.contains('active')) {
                    const fRect = forceFieldZone.getBoundingClientRect();
                    const fx = fRect.left + fRect.width / 2;
                    const fy = fRect.top + fRect.height / 2;
                    
                    const dx = px - fx;
                    const dy = py - fy;
                    const distance = Math.sqrt(dx * dx + dy * dy);
                    
                    if (distance < forceFieldRadius && distance > 0) {
                        const force = repulsionForce / (distance * distance);
                        const angle = Math.atan2(dy, dx);
                        
                        particle.vx += Math.cos(angle) * force * 0.01;
                        particle.vy += Math.sin(angle) * force * 0.01;
                        
                        particle.element.classList.add('repulsion-effect');
                    } else {
                        particle.element.classList.remove('repulsion-effect');
                    }
                }
                
                // Apply velocity with damping
                particle.vx *= 0.95;
                particle.vy *= 0.95;
                
                // Update position
                const currentLeft = parseFloat(particle.element.style.left) || particle.x;
                const currentTop = parseFloat(particle.element.style.top) || particle.y;
                
                const newX = currentLeft + particle.vx;
                const newY = currentTop + particle.vy;
                
                // Boundary wrapping
                particle.x = newX < 0 ? 100 : newX > 100 ? 0 : newX;
                particle.y = newY < 0 ? 100 : newY > 100 ? 0 : newY;
                
                particle.element.style.left = particle.x + '%';
                particle.element.style.top = particle.y + '%';
            });

            // Apply forces to shards
            shards.forEach(shard => {
                const rect = shard.element.getBoundingClientRect();
                const sx = rect.left + rect.width / 2;
                const sy = rect.top + rect.height / 2;
                
                if (forceFieldZone && forceFieldZone.classList.contains('active')) {
                    const fRect = forceFieldZone.getBoundingClientRect();
                    const fx = fRect.left + fRect.width / 2;
                    const fy = fRect.top + fRect.height / 2;
                    
                    const dx = sx - fx;
                    const dy = sy - fy;
                    const distance = Math.sqrt(dx * dx + dy * dy);
                    
                    if (distance < forceFieldRadius && distance > 0) {
                        const force = repulsionForce / (distance * distance);
                        const angle = Math.atan2(dy, dx);
                        
                        shard.vx += Math.cos(angle) * force * 0.008;
                        shard.vy += Math.sin(angle) * force * 0.008;
                        
                        shard.element.classList.add('repulsion-effect');
                    } else {
                        shard.element.classList.remove('repulsion-effect');
                    }
                }
                
                shard.vx *= 0.96;
                shard.vy *= 0.96;
                
                const currentLeft = parseFloat(shard.element.style.left) || shard.x;
                const currentTop = parseFloat(shard.element.style.top) || shard.y;
                
                const newX = currentLeft + shard.vx;
                const newY = currentTop + shard.vy;
                
                shard.x = newX < 0 ? 100 : newX > 100 ? 0 : newX;
                shard.y = newY < 0 ? 100 : newY > 100 ? 0 : newY;
                
                shard.element.style.left = shard.x + '%';
                shard.element.style.top = shard.y + '%';
            });

            // Apply forces to fragments
            fragments.forEach(fragment => {
                const rect = fragment.element.getBoundingClientRect();
                const fx = rect.left + rect.width / 2;
                const fy = rect.top + rect.height / 2;
                
                if (forceFieldZone && forceFieldZone.classList.contains('active')) {
                    const fRect = forceFieldZone.getBoundingClientRect();
                    const fcx = fRect.left + fRect.width / 2;
                    const fcy = fRect.top + fRect.height / 2;
                    
                    const dx = fx - fcx;
                    const dy = fy - fcy;
                    const distance = Math.sqrt(dx * dx + dy * dy);
                    
                    if (distance < forceFieldRadius && distance > 0) {
                        const force = repulsionForce / (distance * distance);
                        const angle = Math.atan2(dy, dx);
                        
                        fragment.vx += Math.cos(angle) * force * 0.009;
                        fragment.vy += Math.sin(angle) * force * 0.009;
                        
                        fragment.element.classList.add('repulsion-effect');
                    } else {
                        fragment.element.classList.remove('repulsion-effect');
                    }
                }
                
                fragment.vx *= 0.95;
                fragment.vy *= 0.95;
                
                const currentLeft = parseFloat(fragment.element.style.left) || fragment.x;
                const currentTop = parseFloat(fragment.element.style.top) || fragment.y;
                
                const newX = currentLeft + fragment.vx;
                const newY = currentTop + fragment.vy;
                
                fragment.x = newX < 0 ? 100 : newX > 100 ? 0 : newX;
                fragment.y = newY < 0 ? 100 : newY > 100 ? 0 : newY;
                
                fragment.element.style.left = fragment.x + '%';
                fragment.element.style.top = fragment.y + '%';
            });

            animationFrame = requestAnimationFrame(simulate);
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
    document.addEventListener('DOMContentLoaded', function() {
        const autoInitElements = document.querySelectorAll('[data-anti-gravity]');
        autoInitElements.forEach(element => {
            const container = element.getAttribute('data-anti-gravity') || 'body';
            initAntiGravity(container);
        });
    });

    // Export
    window.AntiGravity = {
        init: initAntiGravity,
        destroy: destroyAntiGravity
    };

})();


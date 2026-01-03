/**
 * ZERO-GRAVITY UI ENGINE
 * A lightweight, custom physics engine for floating UI elements.
 * Features: AABB/Circle collisions, mouse repulsion, throw physics, and wall bouncing.
 */

(function () {
    'use strict';

    const CONFIG = {
        gravity: { x: 0, y: 0 }, // Zero gravity
        friction: 0.98, // Air resistance
        restitution: 0.8, // Bounciness
        mouseRepulsionRadius: 150,
        mouseRepulsionForce: 2,
        maxVelocity: 15
    };

    let bodies = [];
    let animationFrame;
    let width = window.innerWidth;
    let height = window.innerHeight;
    let mouse = { x: -1000, y: -1000, vx: 0, vy: 0 };
    let lastMouse = { x: -1000, y: -1000 };

    class Body {
        constructor(element, type = 'box') {
            this.element = element;
            this.type = type; // 'box' or 'circle'

            // Random initial position if not set
            const rect = element.getBoundingClientRect();
            this.width = rect.width;
            this.height = rect.height;
            this.radius = Math.max(this.width, this.height) / 2;

            // Central position
            this.x = Math.random() * (width - this.width);
            this.y = Math.random() * (height - this.height);

            // Random velocity
            this.vx = (Math.random() - 0.5) * 4;
            this.vy = (Math.random() - 0.5) * 4;

            this.rotation = Math.random() * 360;
            this.vRotation = (Math.random() - 0.5) * 2;

            this.isDragging = false;

            // Initialize element style
            this.element.style.position = 'absolute';
            this.element.style.willChange = 'transform';
            this.element.style.userSelect = 'none';
            this.updateVisual();

            // Drag Events
            this.element.addEventListener('mousedown', (e) => this.startDrag(e));
            this.element.addEventListener('touchstart', (e) => this.startDrag(e));
        }

        startDrag(e) {
            e.preventDefault();
            this.isDragging = true;
            this.element.style.cursor = 'grabbing';
            this.element.style.zIndex = 1000;
        }

        update() {
            if (this.isDragging) {
                // Follow mouse/touch tightly
                this.x = mouse.x - this.width / 2;
                this.y = mouse.y - this.height / 2;
                this.vx = mouse.vx * 1.5; // Add "throw" momentum
                this.vy = mouse.vy * 1.5;
                this.vx = Math.min(Math.max(this.vx, -CONFIG.maxVelocity), CONFIG.maxVelocity);
                this.vy = Math.min(Math.max(this.vy, -CONFIG.maxVelocity), CONFIG.maxVelocity);
            } else {
                // Apply Physics
                this.x += this.vx;
                this.y += this.vy;
                this.rotation += this.vRotation;

                // Wall Collisions
                if (this.x < 0) { this.x = 0; this.vx *= -CONFIG.restitution; }
                if (this.x + this.width > width) { this.x = width - this.width; this.vx *= -CONFIG.restitution; }
                if (this.y < 0) { this.y = 0; this.vy *= -CONFIG.restitution; }
                if (this.y + this.height > height) { this.y = height - this.height; this.vy *= -CONFIG.restitution; }

                // Friction
                this.vx *= CONFIG.friction;
                this.vy *= CONFIG.friction;

                // Mouse Repulsion (if collision enabled)
                const dx = (this.x + this.width / 2) - mouse.x;
                const dy = (this.y + this.height / 2) - mouse.y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < CONFIG.mouseRepulsionRadius && !this.isDragging) {
                    const force = (1 - dist / CONFIG.mouseRepulsionRadius) * CONFIG.mouseRepulsionForce;
                    this.vx += (dx / dist) * force;
                    this.vy += (dy / dist) * force;
                }
            }

            this.updateVisual();
        }

        updateVisual() {
            this.element.style.transform = `translate3d(${this.x}px, ${this.y}px, 0) rotate(${this.rotation}deg)`;
        }
    }

    function init() {
        const container = document.querySelector('[data-zero-g]');
        if (!container) return;

        // Force container to relative/absolute to contain physics
        container.style.position = 'relative';
        container.style.width = '100vw';
        container.style.height = '100vh';
        container.style.overflow = 'hidden';

        // Gather all elements tagged for physics
        const elements = document.querySelectorAll('.zero-g-element');
        elements.forEach(el => {
            bodies.push(new Body(el));
        });

        // Event Listeners
        window.addEventListener('resize', () => {
            width = window.innerWidth;
            height = window.innerHeight;
        });

        window.addEventListener('mousemove', (e) => {
            lastMouse.x = mouse.x;
            lastMouse.y = mouse.y;
            mouse.x = e.clientX;
            mouse.y = e.clientY;
            mouse.vx = mouse.x - lastMouse.x;
            mouse.vy = mouse.y - lastMouse.y;
        });

        window.addEventListener('mouseup', () => {
            bodies.forEach(b => {
                if (b.isDragging) {
                    b.isDragging = false;
                    b.element.style.cursor = 'grab';
                    b.element.style.zIndex = '';
                }
            });
        });

        animate();
    }

    function animate() {
        bodies.forEach(b => b.update());

        // Simple O(N^2) Collision Resolution for preventing overlap
        for (let i = 0; i < bodies.length; i++) {
            for (let j = i + 1; j < bodies.length; j++) {
                resolveCollision(bodies[i], bodies[j]);
            }
        }

        animationFrame = requestAnimationFrame(animate);
    }

    function resolveCollision(b1, b2) {
        if (b1.isDragging || b2.isDragging) return;

        const dx = (b1.x + b1.width / 2) - (b2.x + b2.width / 2);
        const dy = (b1.y + b1.height / 2) - (b2.y + b2.height / 2);
        const dist = Math.sqrt(dx * dx + dy * dy);
        const minDist = (b1.width + b2.width) / 2 * 0.8; // Approximate radius

        if (dist < minDist) {
            const angle = Math.atan2(dy, dx);
            const targetX = (b2.x + b2.width / 2) + Math.cos(angle) * minDist;
            const targetY = (b2.y + b2.height / 2) + Math.sin(angle) * minDist;

            // Push apart
            const ax = (targetX - (b1.x + b1.width / 2)) * 0.05;
            const ay = (targetY - (b1.y + b1.height / 2)) * 0.05;

            b1.vx += ax;
            b1.vy += ay;
            b2.vx -= ax;
            b2.vy -= ay;
        }
    }

    document.addEventListener('DOMContentLoaded', init);

})();

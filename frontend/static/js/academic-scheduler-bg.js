/**
 * INTELLIGENT CLASSROOM SCHEDULER BACKGROUND
 * Professional 3D animated background nodes, floating classroom blocks, and grid systems.
 * Aligned with NEP 2020: Structure, Planning, Intelligence.
 */

(function () {
    'use strict';

    /**
     * Configuration for the academic simulation
     */
    const CONFIG = {
        nodeCount: 40,
        connectionDistance: 150,
        floatSpeed: 0.2, // Slow, controlled movement
        colors: {
            background: '#0f172a', // Deep Slate
            nodes: 'rgba(148, 163, 184, 0.5)', // Slate-400
            lines: 'rgba(148, 163, 184, 0.15)', // Very subtle lines
            blockBase: 'rgba(56, 189, 248, 0.1)', // Light Blue transparent
            blockBorder: 'rgba(56, 189, 248, 0.3)' // Light Blue border
        }
    };

    let canvas, ctx;
    let width, height;
    let nodes = [];
    let animationFrame;
    let blocksContainer;

    /**
     * Initialize the Academic Background
     * @param {string} containerSelector 
     */
    function initAcademicBackground(containerSelector = 'body') {
        const container = document.querySelector(containerSelector);
        if (!container) return;

        // Container setup
        const bgContainer = document.createElement('div');
        bgContainer.className = 'academic-bg-container';
        bgContainer.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 0;
            overflow: hidden;
            background: radial-gradient(circle at 50% 50%, #1e293b 0%, #0f172a 100%);
        `;

        // 1. Create Grid Plane (Perspective Floor)
        const gridPlane = document.createElement('div');
        gridPlane.className = 'academic-grid-plane';
        gridPlane.style.cssText = `
            position: absolute;
            width: 200%;
            height: 200%;
            top: -50%;
            left: -50%;
            background-image: 
                linear-gradient(rgba(56, 189, 248, 0.1) 1px, transparent 1px),
                linear-gradient(90deg, rgba(56, 189, 248, 0.1) 1px, transparent 1px);
            background-size: 60px 60px;
            transform-origin: 50% 100%;
            transform: perspective(1000px) rotateX(60deg);
            animation: gridMove 20s linear infinite;
        `;
        bgContainer.appendChild(gridPlane);

        // 2. Create Canvas for Nodes (Neural Network / Faculty Connection)
        canvas = document.createElement('canvas');
        canvas.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 1;
            pointer-events: none;
        `;
        bgContainer.appendChild(canvas);
        ctx = canvas.getContext('2d');

        // 3. Create Floating Classroom Blocks
        blocksContainer = document.createElement('div');
        blocksContainer.className = 'floating-blocks-container';
        blocksContainer.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 2;
            pointer-events: none;
            perspective: 1000px;
        `;
        bgContainer.appendChild(blocksContainer);

        createFloatingBlocks(blocksContainer, 6); // 6 major floating elements

        container.appendChild(bgContainer);

        // Handle resize
        window.addEventListener('resize', onResize);
        onResize();

        // Initialize Nodes
        createNodes();

        // Start Loop
        animate();

        // Add CSS Animation for Grid
        if (!document.getElementById('academic-bg-styles')) {
            const style = document.createElement('style');
            style.id = 'academic-bg-styles';
            style.innerHTML = `
                @keyframes gridMove {
                    0% { transform: perspective(1000px) rotateX(60deg) translateY(0); }
                    100% { transform: perspective(1000px) rotateX(60deg) translateY(50px); }
                }
                @keyframes floatBlock {
                    0% { transform: translateY(0); }
                    100% { transform: translateY(-30px); }
                }
                @keyframes rotateCube {
                    0% { transform: rotateX(0deg) rotateY(0deg); }
                    100% { transform: rotateX(360deg) rotateY(360deg); }
                }
            `;
            document.head.appendChild(style);
        }
    }

    function onResize() {
        if (canvas) {
            width = canvas.width = window.innerWidth;
            height = canvas.height = window.innerHeight;
        }
    }

    /**
     * Create connection nodes
     */
    function createNodes() {
        nodes = [];
        for (let i = 0; i < CONFIG.nodeCount; i++) {
            nodes.push({
                x: Math.random() * width,
                y: Math.random() * height,
                vx: (Math.random() - 0.5) * CONFIG.floatSpeed,
                vy: (Math.random() - 0.5) * CONFIG.floatSpeed,
                size: Math.random() * 2 + 1
            });
        }
    }

    /**
     * Create HTML/CSS 3D Blocks
     */
    function createFloatingBlocks(container, count) {
        for (let i = 0; i < count; i++) {
            const cube = document.createElement('div');
            const size = Math.random() * 40 + 30; // 30-70px
            const left = Math.random() * 80 + 10;
            const top = Math.random() * 80 + 10;
            const delay = Math.random() * 5;
            const duration = Math.random() * 10 + 15; // Slower rotation
            const floatDur = Math.random() * 4 + 4;

            // Container for the cube to handle position + float
            const wrapper = document.createElement('div');
            wrapper.className = 'cube-wrapper';
            wrapper.style.cssText = `
                position: absolute;
                left: ${left}%;
                top: ${top}%;
                width: ${size}px;
                height: ${size}px;
                perspective: 1000px;
                animation: floatBlock ${floatDur}s ease-in-out infinite alternate;
                animation-delay: -${delay}s;
            `;

            // The 3D Cube itself
            cube.className = 'academic-cube';
            cube.style.cssText = `
                width: 100%;
                height: 100%;
                position: relative;
                transform-style: preserve-3d;
                animation: rotateCube ${duration}s linear infinite;
            `;

            // Create 6 faces
            const faces = ['front', 'back', 'right', 'left', 'top', 'bottom'];
            faces.forEach(face => {
                const el = document.createElement('div');
                el.className = `cube-face face-${face}`;
                el.style.cssText = `
                    position: absolute;
                    width: ${size}px;
                    height: ${size}px;
                    background: rgba(56, 189, 248, 0.05); /* very light blue fill */
                    border: 1px solid rgba(56, 189, 248, 0.3);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 10px;
                    color: rgba(56, 189, 248, 0.5);
                    box-shadow: inset 0 0 10px rgba(56, 189, 248, 0.1);
                    backface-visibility: visible;
                `;

                // Transforms for cube structure
                const translate = size / 2;
                switch (face) {
                    case 'front': el.style.transform = `rotateY(0deg) translateZ(${translate}px)`; break;
                    case 'back': el.style.transform = `rotateY(180deg) translateZ(${translate}px)`; break;
                    case 'right': el.style.transform = `rotateY(90deg) translateZ(${translate}px)`; break;
                    case 'left': el.style.transform = `rotateY(-90deg) translateZ(${translate}px)`; break;
                    case 'top': el.style.transform = `rotateX(90deg) translateZ(${translate}px)`; break;
                    case 'bottom': el.style.transform = `rotateX(-90deg) translateZ(${translate}px)`; break;
                }

                // Add some academic "data" texture
                if (Math.random() > 0.5) {
                    el.innerHTML = '+';
                }

                cube.appendChild(el);
            });

            wrapper.appendChild(cube);
            container.appendChild(wrapper);
        }
    }

    /**
     * Animation Loop
     */
    function animate() {
        ctx.clearRect(0, 0, width, height);

        // Update and Draw Nodes
        ctx.fillStyle = CONFIG.colors.nodes;
        ctx.strokeStyle = CONFIG.colors.lines;

        // Update positions
        nodes.forEach(node => {
            node.x += node.vx;
            node.y += node.vy;

            // Bounce off walls
            if (node.x < 0 || node.x > width) node.vx *= -1;
            if (node.y < 0 || node.y > height) node.vy *= -1;

            // Draw Node
            ctx.beginPath();
            ctx.arc(node.x, node.y, node.size, 0, Math.PI * 2);
            ctx.fill();
        });

        // Draw Connections
        for (let i = 0; i < nodes.length; i++) {
            for (let j = i + 1; j < nodes.length; j++) {
                const dx = nodes[i].x - nodes[j].x;
                const dy = nodes[i].y - nodes[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < CONFIG.connectionDistance) {
                    ctx.globalAlpha = 1 - (dist / CONFIG.connectionDistance);
                    ctx.beginPath();
                    ctx.moveTo(nodes[i].x, nodes[i].y);
                    ctx.lineTo(nodes[j].x, nodes[j].y);
                    ctx.stroke();
                }
            }
        }
        ctx.globalAlpha = 1;

        animationFrame = requestAnimationFrame(animate);
    }

    // Initialize on load
    document.addEventListener('DOMContentLoaded', () => {
        const targets = document.querySelectorAll('[data-academic-bg]');
        targets.forEach(el => {
            const selector = el.getAttribute('data-academic-bg');
            if (selector) initAcademicBackground(selector);
        });
    });

})();

class CinematicBackground {
    constructor() {
        this.canvas = document.createElement('canvas');
        this.ctx = this.canvas.getContext('2d');
        this.shards = [];
        this.width = window.innerWidth;
        this.height = window.innerHeight;
        this.centerX = this.width / 2;
        this.centerY = this.height / 2;
        this.frameCount = 0;
        this.colors = ['#FFFFFF', '#FF0055', '#00FFFF', '#FFFF00']; // High contrast colors

        this.init();
    }

    init() {
        this.canvas.id = 'cinematic-bg';
        this.canvas.style.position = 'fixed';
        this.canvas.style.top = '0';
        this.canvas.style.left = '0';
        this.canvas.style.width = '100%';
        this.canvas.style.height = '100%';
        this.canvas.style.zIndex = '-1';
        this.canvas.style.background = '#000000'; // Deep black background
        document.body.appendChild(this.canvas);

        window.addEventListener('resize', () => this.resize());
        this.resize();
        this.createBurst();
        this.animate();
    }

    resize() {
        this.width = window.innerWidth;
        this.height = window.innerHeight;
        this.canvas.width = this.width;
        this.canvas.height = this.height;
        this.centerX = this.width / 2;
        this.centerY = this.height / 2;
    }

    createBurst() {
        // Initial explosive burst of shards
        const shardCount = 150;
        for (let i = 0; i < shardCount; i++) {
            this.shards.push(new Shard(this.centerX, this.centerY, this.colors));
        }
    }

    animate() {
        // Glitch effect: Randomly clear canvas with slight opacity or color shift
        if (Math.random() > 0.98) {
            this.ctx.fillStyle = `rgba(0, 255, 255, 0.1)`;
            this.ctx.fillRect(0, 0, this.width, this.height);
        } else {
            this.ctx.fillStyle = 'rgba(0, 0, 0, 0.2)'; // Trails effect
            this.ctx.fillRect(0, 0, this.width, this.height);
        }

        // Glitch displace
        if (Math.random() > 0.99) {
            const temp = this.ctx.getImageData(0, 0, this.width, this.height);
            this.ctx.putImageData(temp, Math.random() * 10 - 5, Math.random() * 10 - 5);
        }

        this.shards.forEach((shard, index) => {
            shard.update();
            shard.draw(this.ctx);

            // Remove off-screen shards and replace them to keep the energy up
            if (shard.isOffScreen(this.width, this.height) || shard.life <= 0) {
                this.shards.splice(index, 1);
                // Continually add new shards from edges or random points for chaos
                if (this.shards.length < 100) {
                    this.shards.push(new Shard(
                        Math.random() * this.width,
                        Math.random() * this.height,
                        this.colors,
                        true // isRefill
                    ));
                }
            }
        });

        // Occasional secondary bursts
        if (Math.random() > 0.995) {
            const x = Math.random() * this.width;
            const y = Math.random() * this.height;
            for (let i = 0; i < 20; i++) {
                this.shards.push(new Shard(x, y, this.colors));
            }
        }

        this.frameCount++;
        requestAnimationFrame(() => this.animate());
    }
}

class Shard {
    constructor(x, y, colors, isRefill = false) {
        this.x = x;
        this.y = y;
        this.colors = colors;

        const angle = Math.random() * Math.PI * 2;
        // Explosive speed
        const speed = isRefill ? Math.random() * 10 + 2 : Math.random() * 30 + 10;

        this.vx = Math.cos(angle) * speed;
        this.vy = Math.sin(angle) * speed;

        this.size = Math.random() * 40 + 5;
        this.color = colors[Math.floor(Math.random() * colors.length)];
        this.rotation = Math.random() * Math.PI * 2;
        this.rotationSpeed = (Math.random() - 0.5) * 0.5;
        this.type = Math.floor(Math.random() * 3); // 0: tri, 1: rect, 2: line
        this.life = 100;
        this.decay = Math.random() * 2 + 0.5;
    }

    update() {
        this.x += this.vx;
        this.y += this.vy;
        this.rotation += this.rotationSpeed;
        this.life -= this.decay;

        // Friction? No, we want high energy. Maybe slight acceleration?
        // this.vx *= 0.99;
        // this.vy *= 0.99;
    }

    draw(ctx) {
        ctx.save();
        ctx.translate(this.x, this.y);
        ctx.rotate(this.rotation);

        ctx.fillStyle = this.color;
        ctx.strokeStyle = this.color;
        ctx.lineWidth = 2;
        ctx.globalAlpha = this.life / 100;

        // Glitchy stroke
        if (Math.random() > 0.9) {
            ctx.lineWidth = Math.random() * 10;
        }

        ctx.beginPath();
        if (this.type === 0) {
            // Sharp Triangle
            ctx.moveTo(0, -this.size);
            ctx.lineTo(this.size * 0.5, this.size);
            ctx.lineTo(-this.size * 0.5, this.size);
            ctx.closePath();
            ctx.fill();
        } else if (this.type === 1) {
            // Jagged Rect
            ctx.fillRect(-this.size / 2, -this.size / 2, this.size, this.size * 0.2); // Thin shard
        } else {
            // Line / Laser
            ctx.moveTo(-this.size, 0);
            ctx.lineTo(this.size, 0);
            ctx.stroke();
        }

        ctx.restore();
    }

    isOffScreen(width, height) {
        return (this.x < -100 || this.x > width + 100 || this.y < -100 || this.y > height + 100);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new CinematicBackground();
});

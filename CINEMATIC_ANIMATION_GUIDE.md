# Cinematic Burst Animation - Integration Guide

## Overview
A high-impact, cinematic background animation designed for maximum visual shock and instant attention. Features explosive burst effects, fast-moving abstract shards, sharp lines, glitch transitions, and intense motion patterns.

## Features
- **Dynamic Burst Effect**: Explosive radial burst animation on load
- **Fast-Moving Shards**: 8 triangular shards with high-speed rotation and movement
- **Sharp Lines**: Horizontal and vertical lines moving across the screen
- **Glitch Effects**: Screen flicker and color shift animations
- **Energy Particles**: Small fast-moving particles with glow effects
- **Energy Waves**: Expanding circular waves from center
- **Screen Flash**: Initial white flash for maximum impact

## Quick Start

### Method 1: Auto-initialize with data attribute
Add the data attribute to any element:

```html
<div data-cinematic-burst="body"></div>
```

### Method 2: Manual initialization
```html
<script>
    // Initialize on page load
    window.addEventListener('DOMContentLoaded', function() {
        CinematicBurst.init('body');
    });
</script>
```

### Method 3: Initialize on specific container
```html
<div id="my-container">
    <!-- Your content -->
</div>

<script>
    CinematicBurst.init('#my-container');
</script>
```

## Full Integration Example

### 1. Include CSS in your template
```html
<link href="{{ url_for('static', filename='css/cinematic-burst-animation.css') }}" rel="stylesheet">
```

### 2. Include JavaScript
```html
<script src="{{ url_for('static', filename='js/cinematic-burst.js') }}"></script>
```

### 3. Add to your page
```html
<body>
    <!-- Animation container -->
    <div data-cinematic-burst="body"></div>
    
    <!-- Your content with z-index above animation -->
    <div style="position: relative; z-index: 10;">
        <!-- Your page content -->
    </div>
</body>
```

## Styling Your Content

Since the animation uses `z-index: -1`, your content should have a higher z-index:

```css
.your-content {
    position: relative;
    z-index: 10;
    /* Your styles */
}
```

## Customization

### Adjust Animation Speed
Edit the animation durations in `cinematic-burst-animation.css`:

```css
/* Make shards move faster */
.shard-1 {
    animation: shardMove1 1.5s infinite; /* Changed from 2.5s */
}
```

### Change Colors
Modify the color values in the CSS:

```css
.shard-1 {
    border-bottom: 30px solid #your-color;
}
```

### Disable Specific Effects
Comment out unwanted elements in the JavaScript:

```javascript
// Don't create energy waves
// for (let i = 1; i <= 3; i++) {
//     const wave = document.createElement('div');
//     wave.className = `energy-wave energy-wave-${i}`;
//     animationContainer.appendChild(wave);
// }
```

## Performance Notes

- Uses `will-change` and `transform: translateZ(0)` for GPU acceleration
- All animations use `transform` for optimal performance
- Consider reducing particle count on mobile devices

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Requires CSS3 animations support
- Hardware acceleration recommended for smooth performance

## Cleanup

To remove the animation:

```javascript
const container = document.querySelector('.cinematic-burst-container');
if (container) {
    CinematicBurst.destroy(container);
}
```

## Example Usage in Flask Template

```html
{% extends "base.html" %}

{% block content %}
    <!-- Include animation CSS -->
    <link href="{{ url_for('static', filename='css/cinematic-burst-animation.css') }}" rel="stylesheet">
    
    <!-- Initialize animation -->
    <div data-cinematic-burst="body"></div>
    
    <!-- Your page content -->
    <div class="content-wrapper" style="position: relative; z-index: 10;">
        <h1>Your Content Here</h1>
    </div>
    
    <!-- Include animation JS -->
    <script src="{{ url_for('static', filename='js/cinematic-burst.js') }}"></script>
{% endblock %}
```

## Tips

1. **Use on landing pages** for maximum impact
2. **Combine with glassmorphism** for modern UI
3. **Ensure text contrast** - use white or bright text
4. **Test performance** on target devices
5. **Consider user preferences** - some users may prefer reduced motion

## Troubleshooting

**Animation not appearing?**
- Check browser console for errors
- Verify CSS and JS files are loaded
- Ensure container element exists

**Performance issues?**
- Reduce number of shards/particles
- Disable glitch effects
- Use `transform` instead of `left/top` animations

**Animation too intense?**
- Increase animation durations
- Reduce opacity values
- Disable screen flash effect


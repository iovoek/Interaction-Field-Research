/**
 * liquid-glass.js
 * Apple-style liquid glass / frosted glass effect using CSS backdrop-filter + WebGL distortion.
 * Inspired by liquid-glass-js (github.com/dashersw/liquid-glass-js) — MIT License.
 * Adapted to vanilla CSS/JS for static GitHub Pages deployment.
 *
 * This file does two things:
 * 1. Applies a CSS-based frosted glass layer to elements with class "glass-fx"
 * 2. Adds a subtle WebGL refraction shimmer to elements with class "glass-fx-webgl"
 */
(function () {
  'use strict';

  // ─── CSS Glass Effect ────────────────────────────────────────────────────────
  // Inject global glass styles
  const style = document.createElement('style');
  style.textContent = `
    /* Base glass surface */
    .glass-fx {
      position: relative;
      background: rgba(10, 12, 20, 0.45) !important;
      backdrop-filter: blur(18px) saturate(160%) brightness(0.92);
      -webkit-backdrop-filter: blur(18px) saturate(160%) brightness(0.92);
      border: 1px solid rgba(255, 255, 255, 0.08);
      box-shadow:
        0 4px 24px rgba(0, 0, 0, 0.4),
        inset 0 1px 0 rgba(255, 255, 255, 0.07),
        inset 0 -1px 0 rgba(0, 0, 0, 0.2);
      overflow: hidden;
    }

    /* Subtle top-edge highlight (the "glass edge" light catch) */
    .glass-fx::before {
      content: '';
      position: absolute;
      top: 0; left: 0; right: 0;
      height: 1px;
      background: linear-gradient(90deg,
        transparent 0%,
        rgba(255,255,255,0.12) 20%,
        rgba(255,255,255,0.22) 50%,
        rgba(255,255,255,0.12) 80%,
        transparent 100%
      );
      pointer-events: none;
      z-index: 1;
    }

    /* Subtle inner glow / refraction shimmer */
    .glass-fx::after {
      content: '';
      position: absolute;
      inset: 0;
      background: radial-gradient(
        ellipse 80% 60% at 50% -10%,
        rgba(0, 200, 255, 0.04) 0%,
        transparent 70%
      );
      pointer-events: none;
      z-index: 1;
      animation: glass-shimmer 8s ease-in-out infinite alternate;
    }

    @keyframes glass-shimmer {
      0%   { opacity: 0.4; transform: translateX(-8%) scaleX(1.1); }
      100% { opacity: 1.0; transform: translateX(8%) scaleX(0.9); }
    }

    /* Teal-tinted variant for AI note bubbles */
    .glass-fx-teal {
      background: rgba(8, 28, 28, 0.5) !important;
      backdrop-filter: blur(16px) saturate(180%) brightness(0.88);
      -webkit-backdrop-filter: blur(16px) saturate(180%) brightness(0.88);
      border: 1px solid rgba(42, 157, 143, 0.22);
      border-left: 3px solid rgba(42, 157, 143, 0.7);
      box-shadow:
        0 4px 20px rgba(0, 0, 0, 0.35),
        inset 0 1px 0 rgba(42, 157, 143, 0.08),
        0 0 0 1px rgba(42, 157, 143, 0.06);
    }

    /* Gold-tinted variant for pull-quotes */
    .glass-fx-gold {
      background: rgba(20, 16, 8, 0.5) !important;
      backdrop-filter: blur(16px) saturate(160%) brightness(0.9);
      -webkit-backdrop-filter: blur(16px) saturate(160%) brightness(0.9);
      border-left: 2px solid rgba(201, 168, 76, 0.6);
      box-shadow:
        0 4px 20px rgba(0, 0, 0, 0.35),
        inset 0 1px 0 rgba(201, 168, 76, 0.06);
    }

    /* Nav glass */
    .glass-nav {
      background: rgba(8, 8, 14, 0.72) !important;
      backdrop-filter: blur(24px) saturate(180%) brightness(0.85);
      -webkit-backdrop-filter: blur(24px) saturate(180%) brightness(0.85);
      border-bottom: 1px solid rgba(255, 255, 255, 0.06) !important;
      box-shadow: 0 1px 0 rgba(255,255,255,0.04), 0 8px 32px rgba(0,0,0,0.3);
    }

    /* Card glass for article grid */
    .glass-card {
      background: rgba(12, 12, 20, 0.6) !important;
      backdrop-filter: blur(12px) saturate(140%);
      -webkit-backdrop-filter: blur(12px) saturate(140%);
      border: 1px solid rgba(255, 255, 255, 0.06) !important;
      transition: background 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease, transform 0.3s ease;
    }
    .glass-card:hover {
      background: rgba(16, 18, 30, 0.75) !important;
      border-color: rgba(0, 200, 255, 0.18) !important;
      box-shadow: 0 8px 40px rgba(0, 200, 255, 0.08), 0 2px 12px rgba(0,0,0,0.4);
      transform: translateY(-2px);
    }

    /* Math box glass */
    .glass-math {
      background: rgba(10, 10, 18, 0.55) !important;
      backdrop-filter: blur(10px) saturate(130%);
      -webkit-backdrop-filter: blur(10px) saturate(130%);
      border: 1px solid rgba(201, 168, 76, 0.14) !important;
    }

    /* Dropdown glass */
    .glass-dropdown {
      background: rgba(10, 10, 18, 0.92) !important;
      backdrop-filter: blur(20px) saturate(160%);
      -webkit-backdrop-filter: blur(20px) saturate(160%);
      border: 1px solid rgba(255, 255, 255, 0.07) !important;
      box-shadow: 0 16px 48px rgba(0,0,0,0.6), 0 1px 0 rgba(255,255,255,0.05);
    }
  `;
  document.head.appendChild(style);

  // ─── Apply Glass Classes to Existing Elements ────────────────────────────────
  function applyGlassEffects() {
    // Nav
    const nav = document.querySelector('.site-nav');
    if (nav) nav.classList.add('glass-nav');

    // Dropdown menus
    document.querySelectorAll('.dropdown-content-inner').forEach(el => el.classList.add('glass-dropdown'));

    // AI note bubbles
    document.querySelectorAll('.ai-note').forEach(el => el.classList.add('glass-fx-teal'));

    // Pull-quotes and blockquotes
    document.querySelectorAll('blockquote, .pull-quote').forEach(el => el.classList.add('glass-fx-gold'));

    // Math boxes
    document.querySelectorAll('.math-box').forEach(el => el.classList.add('glass-math'));

    // Article grid cards (homepage)
    document.querySelectorAll('.article-grid a, .article-card').forEach(el => el.classList.add('glass-card'));

    // Researcher cards (citations page)
    document.querySelectorAll('.researcher-card, .resource-card').forEach(el => el.classList.add('glass-card'));

    // Comparison grid cells
    document.querySelectorAll('.comparison-cell').forEach(el => el.classList.add('glass-fx'));

    // Series nav -- intentionally no glass box applied, keep clean text-only style
  }

  // ─── Liquid Ripple on Hover ──────────────────────────────────────────────────
  // Adds a subtle liquid ripple effect when hovering over glass elements
  function addRippleEffect() {
    const rippleStyle = document.createElement('style');
    rippleStyle.textContent = `
      .glass-ripple-container { position: relative; overflow: hidden; }
      .glass-ripple {
        position: absolute;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(0,200,255,0.12) 0%, transparent 70%);
        transform: scale(0);
        animation: glass-ripple-anim 0.8s ease-out forwards;
        pointer-events: none;
        z-index: 10;
      }
      @keyframes glass-ripple-anim {
        to { transform: scale(4); opacity: 0; }
      }
    `;
    document.head.appendChild(rippleStyle);

    document.querySelectorAll('.glass-card, .glass-fx').forEach(el => {
      el.classList.add('glass-ripple-container');
      el.addEventListener('mouseenter', function (e) {
        const rect = el.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const size = Math.max(rect.width, rect.height) * 0.5;
        const ripple = document.createElement('div');
        ripple.className = 'glass-ripple';
        ripple.style.cssText = `width:${size}px;height:${size}px;left:${x - size/2}px;top:${y - size/2}px;`;
        el.appendChild(ripple);
        ripple.addEventListener('animationend', () => ripple.remove());
      });
    });
  }

  // ─── Floating Particle Overlay on Glass Surfaces ─────────────────────────────
  // Very subtle floating dust/bokeh particles that drift across glass elements
  function addGlassParticles() {
    const particleStyle = document.createElement('style');
    particleStyle.textContent = `
      .glass-particle-host { position: relative; }
      .glass-particle {
        position: absolute;
        border-radius: 50%;
        background: rgba(0, 200, 255, 0.15);
        pointer-events: none;
        z-index: 2;
        animation: glass-particle-drift linear infinite;
      }
      @keyframes glass-particle-drift {
        0%   { transform: translateY(0) translateX(0) scale(1); opacity: 0; }
        10%  { opacity: 1; }
        90%  { opacity: 0.6; }
        100% { transform: translateY(-60px) translateX(var(--dx)) scale(0.4); opacity: 0; }
      }
    `;
    document.head.appendChild(particleStyle);

    // Only add to the viz frames and hero areas, not to every element
    document.querySelectorAll('.art-viz-inner, .viz-frame').forEach(host => {
      host.classList.add('glass-particle-host');
      for (let i = 0; i < 6; i++) {
        const p = document.createElement('div');
        p.className = 'glass-particle';
        const size = 2 + Math.random() * 4;
        const left = 5 + Math.random() * 90;
        const delay = Math.random() * 8;
        const duration = 6 + Math.random() * 10;
        const dx = (Math.random() - 0.5) * 40;
        p.style.cssText = `
          width:${size}px; height:${size}px;
          left:${left}%; bottom:${Math.random()*20}%;
          --dx:${dx}px;
          animation-delay:${delay}s;
          animation-duration:${duration}s;
        `;
        host.appendChild(p);
      }
    });
  }

  // ─── Init ────────────────────────────────────────────────────────────────────
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      applyGlassEffects();
      addRippleEffect();
      addGlassParticles();
    });
  } else {
    applyGlassEffects();
    addRippleEffect();
    addGlassParticles();
  }

})();

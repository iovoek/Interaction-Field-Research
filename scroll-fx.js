/**
 * scroll-fx.js — Apple-style scroll reveal system
 * Shared across all pages of Exchange Is the Equation
 *
 * Animations:
 *  .reveal        — fade + translateY (paragraphs, general content)
 *  .reveal-left   — fade + translateX from left (section headers)
 *  .reveal-scale  — fade + scale (pull-quotes, callouts)
 *  .reveal-stagger — children stagger in sequence (article grids, lists)
 *  .parallax-hero  — subtle parallax on hero backgrounds
 */

(function () {
  'use strict';

  // ─── CSS injection ────────────────────────────────────────────────────────
  const style = document.createElement('style');
  style.textContent = `
    /* Base reveal state */
    .reveal,
    .reveal-left,
    .reveal-scale {
      opacity: 0;
      will-change: opacity, transform;
      transition-timing-function: cubic-bezier(0.25, 0.46, 0.45, 0.94);
    }

    .reveal {
      transform: translateY(28px);
      transition: opacity 0.75s, transform 0.75s;
    }

    .reveal-left {
      transform: translateX(-32px);
      transition: opacity 0.7s, transform 0.7s;
    }

    .reveal-scale {
      transform: scale(0.96);
      transition: opacity 0.8s, transform 0.8s;
    }

    /* Stagger children */
    .reveal-stagger > * {
      opacity: 0;
      transform: translateY(22px);
      will-change: opacity, transform;
      transition: opacity 0.65s cubic-bezier(0.25, 0.46, 0.45, 0.94),
                  transform 0.65s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    }

    /* Visible state */
    .reveal.is-visible,
    .reveal-left.is-visible,
    .reveal-scale.is-visible {
      opacity: 1;
      transform: none;
    }

    .reveal-stagger.is-visible > * {
      opacity: 1;
      transform: none;
    }

    /* Stagger delays for children */
    .reveal-stagger.is-visible > *:nth-child(1)  { transition-delay: 0s; }
    .reveal-stagger.is-visible > *:nth-child(2)  { transition-delay: 0.08s; }
    .reveal-stagger.is-visible > *:nth-child(3)  { transition-delay: 0.16s; }
    .reveal-stagger.is-visible > *:nth-child(4)  { transition-delay: 0.24s; }
    .reveal-stagger.is-visible > *:nth-child(5)  { transition-delay: 0.32s; }
    .reveal-stagger.is-visible > *:nth-child(6)  { transition-delay: 0.40s; }
    .reveal-stagger.is-visible > *:nth-child(7)  { transition-delay: 0.48s; }
    .reveal-stagger.is-visible > *:nth-child(8)  { transition-delay: 0.56s; }
    .reveal-stagger.is-visible > *:nth-child(n+9){ transition-delay: 0.64s; }

    /* Progress bar */
    #read-progress {
      position: fixed;
      top: 0; left: 0;
      height: 2px;
      width: 0%;
      background: linear-gradient(90deg, #2a9d8f, #c9a84c);
      z-index: 9999;
      transition: width 0.1s linear;
      pointer-events: none;
    }

    /* Section divider glow pulse */
    .rule-glow {
      height: 1px;
      background: linear-gradient(90deg, transparent, rgba(201,168,76,0.4), transparent);
      margin: 2.5rem 0;
      animation: rule-pulse 4s ease-in-out infinite;
    }
    @keyframes rule-pulse {
      0%, 100% { opacity: 0.4; }
      50% { opacity: 1; }
    }

    /* Floating equation overlay enhancement */
    .eq-overlay {
      position: absolute;
      top: 1.2rem; right: 1.4rem;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.62rem;
      color: rgba(201,168,76,0.22);
      letter-spacing: 0.04em;
      pointer-events: none;
      user-select: none;
      animation: eq-drift 12s ease-in-out infinite;
    }
    @keyframes eq-drift {
      0%, 100% { transform: translateY(0px); opacity: 0.22; }
      50% { transform: translateY(-6px); opacity: 0.38; }
    }

    /* Cursor glow (subtle) */
    #cursor-glow {
      position: fixed;
      width: 320px; height: 320px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(42,157,143,0.04) 0%, transparent 70%);
      pointer-events: none;
      z-index: 0;
      transform: translate(-50%, -50%);
      transition: left 0.15s ease-out, top 0.15s ease-out;
    }
  `;
  document.head.appendChild(style);

  // ─── Reading progress bar ─────────────────────────────────────────────────
  const progressBar = document.createElement('div');
  progressBar.id = 'read-progress';
  document.body.insertBefore(progressBar, document.body.firstChild);

  function updateProgress() {
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const pct = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
    progressBar.style.width = pct + '%';
  }
  window.addEventListener('scroll', updateProgress, { passive: true });

  // ─── Cursor glow ──────────────────────────────────────────────────────────
  const cursorGlow = document.createElement('div');
  cursorGlow.id = 'cursor-glow';
  document.body.appendChild(cursorGlow);

  document.addEventListener('mousemove', function (e) {
    cursorGlow.style.left = e.clientX + 'px';
    cursorGlow.style.top = e.clientY + 'px';
  }, { passive: true });

  // ─── IntersectionObserver for reveals ────────────────────────────────────
  const revealOpts = {
    threshold: 0.12,
    rootMargin: '0px 0px -40px 0px'
  };

  const revealObserver = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        revealObserver.unobserve(entry.target);
      }
    });
  }, revealOpts);

  function attachReveal() {
    // Paragraphs inside main
    const main = document.querySelector('main');
    if (!main) return;

    // Tag h2 headings with reveal-left
    main.querySelectorAll('h2').forEach(function (el) {
      if (!el.classList.contains('reveal-left')) {
        el.classList.add('reveal-left');
        revealObserver.observe(el);
      }
    });

    // Tag h3 headings with reveal
    main.querySelectorAll('h3').forEach(function (el) {
      if (!el.classList.contains('reveal')) {
        el.classList.add('reveal');
        revealObserver.observe(el);
      }
    });

    // Paragraphs
    main.querySelectorAll('p').forEach(function (el) {
      if (!el.classList.contains('reveal') && !el.classList.contains('subtitle')) {
        el.classList.add('reveal');
        revealObserver.observe(el);
      }
    });

    // Pull-quotes / blockquotes
    main.querySelectorAll('blockquote, .pull-quote, .callout, .stat-block, .domain-card, .article-card').forEach(function (el) {
      if (!el.classList.contains('reveal-scale')) {
        el.classList.add('reveal-scale');
        revealObserver.observe(el);
      }
    });

    // Grids — stagger children (only grids without overflow:hidden)
    main.querySelectorAll('.domain-grid, .researcher-grid, .series-grid, .resources-grid').forEach(function (el) {
      if (!el.classList.contains('reveal-stagger')) {
        el.classList.add('reveal-stagger');
        revealObserver.observe(el);
      }
    });

    // Article cards — individual reveal with delay (article-grid has overflow:hidden)
    main.querySelectorAll('.article-card').forEach(function (el, i) {
      if (!el.classList.contains('reveal')) {
        el.classList.add('reveal');
        el.style.transitionDelay = (i * 0.04) + 's';
        revealObserver.observe(el);
      }
    });

    // Viz frames (canvas containers)
    main.querySelectorAll('.viz-frame, .canvas-wrap, .art-viz-frame').forEach(function (el) {
      if (!el.classList.contains('reveal-scale')) {
        el.classList.add('reveal-scale');
        revealObserver.observe(el);
      }
    });
  }

  // ─── Parallax hero ────────────────────────────────────────────────────────
  function setupParallax() {
    const hero = document.querySelector('.hero, .page-hero');
    if (!hero) return;
    window.addEventListener('scroll', function () {
      const y = window.scrollY;
      hero.style.transform = 'translateY(' + (y * 0.18) + 'px)';
    }, { passive: true });
  }

  // ─── Smooth nav highlight on scroll ──────────────────────────────────────
  function setupNavHighlight() {
    const sections = document.querySelectorAll('main h2[id], main h3[id]');
    if (sections.length === 0) return;
    const navLinks = document.querySelectorAll('.site-nav a, .toc a');

    const sectionObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          navLinks.forEach(function (link) {
            link.classList.remove('nav-active');
            if (link.getAttribute('href') === '#' + entry.target.id) {
              link.classList.add('nav-active');
            }
          });
        }
      });
    }, { threshold: 0.5 });

    sections.forEach(function (s) { sectionObserver.observe(s); });
  }

  // ─── Replace .rule dividers with glowing ones ────────────────────────────
  function upgradeRules() {
    document.querySelectorAll('.rule').forEach(function (el) {
      el.classList.add('rule-glow');
    });
  }

  // ─── Init ─────────────────────────────────────────────────────────────────
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      attachReveal();
      setupParallax();
      setupNavHighlight();
      upgradeRules();
    });
  } else {
    attachReveal();
    setupParallax();
    setupNavHighlight();
    upgradeRules();
  }

})();

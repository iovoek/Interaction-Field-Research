/**
 * particle-field.js
 * Mouse-reactive ambient particle field background using Three.js.
 * Inspired by react-three-fiber demos (github.com/pmndrs/react-three-fiber).
 * Adapted to vanilla Three.js r128 for static GitHub Pages deployment.
 *
 * Creates a full-viewport canvas behind all page content with:
 * - 2000 particles in a 3D field
 * - Mouse parallax: particles shift subtly toward the cursor
 * - Scroll parallax: field drifts as you scroll
 * - Color: teal/cyan particles on dark background
 * - Performance: uses instanced mesh + requestAnimationFrame
 */
(function () {
  'use strict';

  // Only run if Three.js is available
  function init() {
    if (typeof THREE === 'undefined') return;

    // Create the background canvas
    const canvas = document.createElement('canvas');
    canvas.id = 'pf-canvas';
    canvas.style.cssText = `
      position: fixed;
      top: 0; left: 0;
      width: 100%; height: 100%;
      pointer-events: none;
      z-index: 0;
      opacity: 0.55;
    `;
    document.body.insertBefore(canvas, document.body.firstChild);

    // Make sure page content is above the canvas
    const pageStyle = document.createElement('style');
    pageStyle.textContent = `
      .site-nav, main, header, footer, .mobile-menu {
        position: relative;
        z-index: 1;
      }
    `;
    document.head.appendChild(pageStyle);

    const renderer = new THREE.WebGLRenderer({ canvas, antialias: false, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
    renderer.setClearColor(0x000000, 0);

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(60, 1, 0.1, 200);
    camera.position.z = 30;

    function resize() {
      const w = window.innerWidth, h = window.innerHeight;
      renderer.setSize(w, h);
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
    }
    resize();
    window.addEventListener('resize', resize);

    // ── Particle field ──────────────────────────────────────────────────────────
    const COUNT = 1800;
    const positions = new Float32Array(COUNT * 3);
    const colors = new Float32Array(COUNT * 3);
    const sizes = new Float32Array(COUNT);

    for (let i = 0; i < COUNT; i++) {
      // Spread in a wide flat disk-ish volume
      const theta = Math.random() * Math.PI * 2;
      const r = 5 + Math.random() * 40;
      positions[i * 3]     = Math.cos(theta) * r;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 30;
      positions[i * 3 + 2] = Math.sin(theta) * r * 0.4 + (Math.random() - 0.5) * 20;

      // Color: mix between deep teal and faint cyan
      const t = Math.random();
      colors[i * 3]     = 0.0 + t * 0.05;
      colors[i * 3 + 1] = 0.25 + t * 0.55;
      colors[i * 3 + 2] = 0.35 + t * 0.55;

      sizes[i] = 0.5 + Math.random() * 1.5;
    }

    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    geo.setAttribute('size', new THREE.BufferAttribute(sizes, 1));

    const mat = new THREE.PointsMaterial({
      size: 0.18,
      vertexColors: true,
      transparent: true,
      opacity: 0.7,
      sizeAttenuation: true,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    });

    const points = new THREE.Points(geo, mat);
    scene.add(points);

    // ── Connection lines between nearby particles ───────────────────────────────
    // We draw a sparse set of lines between close particles for the "network" look
    const linePositions = [];
    const lineColors = [];
    const threshold = 8;
    const maxLines = 300;
    let lineCount = 0;

    for (let i = 0; i < COUNT && lineCount < maxLines; i++) {
      for (let j = i + 1; j < COUNT && lineCount < maxLines; j++) {
        const dx = positions[i*3] - positions[j*3];
        const dy = positions[i*3+1] - positions[j*3+1];
        const dz = positions[i*3+2] - positions[j*3+2];
        const dist = Math.sqrt(dx*dx + dy*dy + dz*dz);
        if (dist < threshold) {
          linePositions.push(
            positions[i*3], positions[i*3+1], positions[i*3+2],
            positions[j*3], positions[j*3+1], positions[j*3+2]
          );
          const alpha = 1 - dist / threshold;
          lineColors.push(0, 0.3 * alpha, 0.4 * alpha, 0, 0.3 * alpha, 0.4 * alpha);
          lineCount++;
        }
      }
    }

    if (linePositions.length > 0) {
      const lineGeo = new THREE.BufferGeometry();
      lineGeo.setAttribute('position', new THREE.Float32BufferAttribute(linePositions, 3));
      lineGeo.setAttribute('color', new THREE.Float32BufferAttribute(lineColors, 3));
      const lineMat = new THREE.LineBasicMaterial({
        vertexColors: true,
        transparent: true,
        opacity: 0.25,
        blending: THREE.AdditiveBlending,
        depthWrite: false
      });
      scene.add(new THREE.LineSegments(lineGeo, lineMat));
    }

    // ── Mouse parallax ──────────────────────────────────────────────────────────
    let mouseX = 0, mouseY = 0;
    let targetX = 0, targetY = 0;

    window.addEventListener('mousemove', function (e) {
      mouseX = (e.clientX / window.innerWidth - 0.5) * 2;
      mouseY = -(e.clientY / window.innerHeight - 0.5) * 2;
    });

    // ── Scroll parallax ─────────────────────────────────────────────────────────
    let scrollY = 0;
    window.addEventListener('scroll', function () {
      scrollY = window.scrollY;
    });

    // ── Animation loop ──────────────────────────────────────────────────────────
    let startTime = null;

    function animate(ts) {
      if (!startTime) startTime = ts;
      const t = (ts - startTime) / 1000;

      // Smooth mouse follow
      targetX += (mouseX - targetX) * 0.03;
      targetY += (mouseY - targetY) * 0.03;

      // Slow rotation of the whole field
      points.rotation.y = t * 0.018 + targetX * 0.15;
      points.rotation.x = targetY * 0.08;

      // Scroll drift: field moves up as user scrolls down
      points.position.y = -scrollY * 0.004;

      // Camera subtle drift
      camera.position.x = targetX * 2;
      camera.position.y = targetY * 1.5;
      camera.lookAt(0, 0, 0);

      renderer.render(scene, camera);
      requestAnimationFrame(animate);
    }

    requestAnimationFrame(animate);
  }

  // Wait for Three.js to be available
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      // Small delay to ensure Three.js script has executed
      setTimeout(init, 100);
    });
  } else {
    setTimeout(init, 100);
  }

})();

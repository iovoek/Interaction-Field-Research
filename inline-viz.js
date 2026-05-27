/**
 * inline-viz.js
 * Floating transparent Three.js inline visualizations for article pages.
 * Usage: <div class="inline-viz" data-scene="SCENE_NAME"></div>
 *
 * Scenes available:
 *   error-growth       -- sqrt(k) error accumulation spiral
 *   field-lines        -- interaction field flow vectors
 *   orientation-flip   -- arrow field flipping inward->outward
 *   transaction-density -- node exchange density heatmap
 *   torus-equation     -- torus knot (the equation)
 *   fibonacci-coherence -- golden ratio spiral building up
 *   bifurcation-tree   -- branching decision paths
 *   wave-interference  -- two waves interfering (exchange field)
 *   lattice-propagation -- error wave through a node lattice
 */

(function() {
  if (typeof THREE === 'undefined') {
    // Defer until Three.js loads
    window.addEventListener('load', init);
    return;
  }
  init();

  function init() {
    const containers = document.querySelectorAll('.inline-viz[data-scene]');
    if (!containers.length) return;

    containers.forEach(function(container) {
      const sceneName = container.getAttribute('data-scene');
      const eq = container.getAttribute('data-eq') || null;
      setupScene(container, sceneName, eq);
    });
  }

  function setupScene(container, sceneName, eqText) {
    // Create canvas
    const canvas = document.createElement('canvas');
    canvas.style.cssText = 'display:block;width:100%;height:100%;';
    container.appendChild(canvas);

    // Equation overlay
    if (eqText) {
      const eqEl = document.createElement('div');
      eqEl.className = 'inline-viz-eq';
      eqEl.textContent = eqText;
      container.appendChild(eqEl);
    }

    // Three.js renderer -- transparent background
    const renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setClearColor(0x000000, 0); // fully transparent

    const scene = new THREE.Scene();
    const w = container.clientWidth || 600;
    const h = container.clientHeight || 220;
    const camera = new THREE.PerspectiveCamera(50, w / h, 0.1, 1000);
    camera.position.set(0, 0, 14);

    function resize() {
      const cw = container.clientWidth || 600;
      const ch = container.clientHeight || 220;
      renderer.setSize(cw, ch);
      camera.aspect = cw / ch;
      camera.updateProjectionMatrix();
    }
    resize();
    window.addEventListener('resize', resize);

    // Color palette
    const CYAN    = new THREE.Color(0x00e5ff);
    const MAGENTA = new THREE.Color(0xff00cc);
    const TEAL    = new THREE.Color(0x2a9d8f);
    const GOLD    = new THREE.Color(0xc9a84c);
    const RED     = new THREE.Color(0xff2244);
    const WHITE   = new THREE.Color(0xffffff);
    const GREEN   = new THREE.Color(0x00ff88);

    let updateFn = null;

    // ---- SCENE BUILDERS ----

    if (sceneName === 'error-growth') {
      // Two spirals: error grows as sqrt(k) in red, bounded correction in cyan
      // Equation: sigma_k = sigma_0 * sqrt(k)
      const steps = 100;
      const errPts = [], corrPts = [];
      for (let i = 0; i < steps; i++) {
        const t = i / steps;
        const angle = t * Math.PI * 5;
        const rErr  = 0.5 + t * 5;
        const rCorr = 0.5 + t * 0.4;
        errPts.push(new THREE.Vector3(Math.cos(angle) * rErr, t * 7 - 3.5, Math.sin(angle) * rErr));
        corrPts.push(new THREE.Vector3(Math.cos(angle) * rCorr, t * 7 - 3.5, Math.sin(angle) * rCorr));
      }
      const errLine  = new THREE.Line(new THREE.BufferGeometry().setFromPoints(errPts),  new THREE.LineBasicMaterial({ color: RED,  transparent: true, opacity: 0.85 }));
      const corrLine = new THREE.Line(new THREE.BufferGeometry().setFromPoints(corrPts), new THREE.LineBasicMaterial({ color: CYAN, transparent: true, opacity: 0.85 }));
      scene.add(errLine, corrLine);

      // Axis
      scene.add(new THREE.Line(
        new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0,-3.5,0), new THREE.Vector3(0,3.5,0)]),
        new THREE.LineBasicMaterial({ color: 0x334455, transparent: true, opacity: 0.4 })
      ));

      // Tracers
      const tGeo = new THREE.SphereGeometry(0.18, 8, 8);
      const errT  = new THREE.Mesh(tGeo, new THREE.MeshBasicMaterial({ color: RED }));
      const corrT = new THREE.Mesh(tGeo.clone(), new THREE.MeshBasicMaterial({ color: CYAN }));
      scene.add(errT, corrT);

      updateFn = function(t) {
        scene.rotation.y = t * 0.18;
        const prog = (t * 0.12) % 1;
        const idx = Math.floor(prog * (steps - 1));
        errT.position.copy(errPts[idx]);
        corrT.position.copy(corrPts[idx]);
        const pulse = 1 + Math.sin(t * 4) * 0.3;
        errT.scale.setScalar(pulse);
        corrT.scale.setScalar(pulse);
      };
    }

    else if (sceneName === 'field-lines') {
      // Interaction field: flowing vectors from a source node outward
      // Equation: F(x) = sum_i w_ij * delta(x_i, x_j)
      const N = 12;
      const arrows = [];
      for (let i = 0; i < N; i++) {
        const angle = (i / N) * Math.PI * 2;
        const r = 3 + Math.random() * 2;
        const origin = new THREE.Vector3(Math.cos(angle) * r, Math.sin(angle) * r * 0.6, (Math.random()-0.5)*2);
        const dir = origin.clone().normalize();

        const shaft = new THREE.Mesh(
          new THREE.CylinderGeometry(0.04, 0.04, 1.2, 6),
          new THREE.MeshBasicMaterial({ color: TEAL, transparent: true, opacity: 0.7 })
        );
        const head = new THREE.Mesh(
          new THREE.ConeGeometry(0.14, 0.4, 6),
          new THREE.MeshBasicMaterial({ color: CYAN, transparent: true, opacity: 0.9 })
        );
        head.position.y = 0.8;

        const group = new THREE.Group();
        group.add(shaft, head);
        group.position.copy(origin);
        group.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0), dir);
        scene.add(group);
        arrows.push({ group, origin, dir, phase: i / N });
      }

      // Center source node
      const src = new THREE.Mesh(
        new THREE.SphereGeometry(0.4, 12, 12),
        new THREE.MeshBasicMaterial({ color: CYAN, transparent: true, opacity: 0.9 })
      );
      scene.add(src);

      updateFn = function(t) {
        scene.rotation.y = t * 0.12;
        const pulse = 1 + Math.sin(t * 2) * 0.15;
        src.scale.setScalar(pulse);
        arrows.forEach(function(a) {
          const wave = Math.sin(t * 2 + a.phase * Math.PI * 2) * 0.5 + 0.5;
          a.group.children[0].material.opacity = 0.3 + wave * 0.5;
          a.group.children[1].material.opacity = 0.5 + wave * 0.4;
          // Pulse along direction
          const dist = 3 + wave * 1.5;
          a.group.position.copy(a.dir.clone().multiplyScalar(dist));
        });
      };
    }

    else if (sceneName === 'orientation-flip') {
      // Arrow field: all arrows start pointing inward (red), flip outward (cyan) in a wave
      // Equation: Orientation O in {-1, +1}, error E(O) = E_0 * exp(-lambda * O)
      const N = 4;
      const arrowData = [];
      for (let x = -N; x <= N; x += 2) {
        for (let y = -N; y <= N; y += 2) {
          const origin = new THREE.Vector3(x * 0.9, y * 0.9, 0);
          const dir = origin.clone().normalize();
          if (dir.length() < 0.01) continue;

          const mat1 = new THREE.MeshBasicMaterial({ color: RED, transparent: true, opacity: 0.8 });
          const mat2 = new THREE.MeshBasicMaterial({ color: RED, transparent: true, opacity: 0.8 });
          const shaft = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 0.7, 6), mat1);
          const head  = new THREE.Mesh(new THREE.ConeGeometry(0.12, 0.28, 6), mat2);
          head.position.y = 0.49;

          const group = new THREE.Group();
          group.add(shaft, head);
          group.position.copy(origin);
          group.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0), dir.clone().negate());
          scene.add(group);
          arrowData.push({ group, dir, mat1, mat2, dist: origin.length() });
        }
      }
      const maxDist = Math.sqrt(2) * N * 0.9;

      updateFn = function(t) {
        scene.rotation.y = t * 0.13;
        const prog = (Math.sin(t * 0.4) * 0.5 + 0.5); // oscillate 0..1
        arrowData.forEach(function(a) {
          const normDist = a.dist / maxDist;
          const flip = Math.max(0, Math.min(1, (prog - normDist * 0.4) / 0.3));
          a.group.quaternion.setFromUnitVectors(
            new THREE.Vector3(0,1,0),
            a.dir.clone().lerp(a.dir.clone().negate(), flip).normalize()
          );
          const col = new THREE.Color().lerpColors(RED, CYAN, flip);
          a.mat1.color.copy(col);
          a.mat2.color.copy(col);
        });
      };
    }

    else if (sceneName === 'transaction-density') {
      // Nodes with exchange density: bright nodes = high transaction density
      // Equation: rho(x) = sum_ij delta(x - x_ij) * w_ij
      const nodes = [];
      const N = 18;
      for (let i = 0; i < N; i++) {
        const angle = (i / N) * Math.PI * 2;
        const r = 2 + Math.random() * 3;
        const pos = new THREE.Vector3(
          Math.cos(angle) * r,
          (Math.random() - 0.5) * 4,
          Math.sin(angle) * r * 0.5
        );
        const density = Math.random();
        const col = new THREE.Color().lerpColors(TEAL, CYAN, density);
        const mesh = new THREE.Mesh(
          new THREE.SphereGeometry(0.1 + density * 0.25, 8, 8),
          new THREE.MeshBasicMaterial({ color: col, transparent: true, opacity: 0.6 + density * 0.4 })
        );
        mesh.position.copy(pos);
        scene.add(mesh);
        nodes.push({ mesh, density, pos, phase: Math.random() * Math.PI * 2 });
      }

      // Connection lines between nearby nodes
      for (let i = 0; i < N; i++) {
        for (let j = i + 1; j < N; j++) {
          const d = nodes[i].pos.distanceTo(nodes[j].pos);
          if (d < 3.5) {
            const strength = (nodes[i].density + nodes[j].density) / 2;
            scene.add(new THREE.Line(
              new THREE.BufferGeometry().setFromPoints([nodes[i].pos, nodes[j].pos]),
              new THREE.LineBasicMaterial({ color: TEAL, transparent: true, opacity: strength * 0.4 })
            ));
          }
        }
      }

      updateFn = function(t) {
        scene.rotation.y = t * 0.1;
        nodes.forEach(function(n) {
          const pulse = 1 + Math.sin(t * 1.5 + n.phase) * 0.2 * n.density;
          n.mesh.scale.setScalar(pulse);
          n.mesh.material.opacity = 0.5 + Math.sin(t * 1.5 + n.phase) * 0.3 * n.density;
        });
      };
    }

    else if (sceneName === 'torus-equation') {
      // Torus knot -- the mathematical structure of interwoven fields
      // Equation: r(t) = (R + r*cos(qt)) * [cos(pt), sin(pt), sin(qt)/R]
      const knotGeo = new THREE.TorusKnotGeometry(4, 0.3, 200, 16, 3, 5);
      const knotMat = new THREE.MeshBasicMaterial({ color: CYAN, wireframe: true, transparent: true, opacity: 0.7 });
      const knot = new THREE.Mesh(knotGeo, knotMat);
      scene.add(knot);

      const innerGeo = new THREE.TorusKnotGeometry(2.5, 0.12, 150, 12, 2, 3);
      scene.add(new THREE.Mesh(innerGeo, new THREE.MeshBasicMaterial({ color: MAGENTA, wireframe: true, transparent: true, opacity: 0.45 })));

      // Particles along knot path
      const pts = [];
      for (let i = 0; i < 300; i++) {
        const t = (i / 300) * Math.PI * 2;
        const r = 4 + Math.cos(5 * t) * 0.3;
        pts.push(new THREE.Vector3(r * Math.cos(3 * t), r * Math.sin(3 * t), -Math.sin(5 * t) * 0.3));
      }
      const particles = [];
      for (let i = 0; i < 10; i++) {
        const m = new THREE.Mesh(
          new THREE.SphereGeometry(0.12, 6, 6),
          new THREE.MeshBasicMaterial({ color: i % 2 === 0 ? CYAN : MAGENTA })
        );
        scene.add(m);
        particles.push({ m, offset: i / 10 });
      }

      updateFn = function(t) {
        knot.rotation.y = t * 0.22;
        knot.rotation.x = t * 0.11;
        scene.rotation.z = t * 0.05;
        particles.forEach(function(p) {
          const idx = Math.floor(((t * 0.07 + p.offset) % 1) * pts.length);
          p.m.position.copy(pts[idx]);
          p.m.scale.setScalar(1 + Math.sin(t * 4 + p.offset * 6) * 0.3);
        });
      };
    }

    else if (sceneName === 'fibonacci-coherence') {
      // Golden ratio / Fibonacci spiral building up
      // Equation: theta_n = n * 2*pi/phi^2, r_n = sqrt(n)
      const N = 180;
      const phi = (1 + Math.sqrt(5)) / 2;
      const goldenAngle = Math.PI * 2 / (phi * phi);
      const pts = [];
      for (let i = 0; i < N; i++) {
        const angle = i * goldenAngle;
        const r = Math.sqrt(i) * 0.38;
        const z = (i / N - 0.5) * 8;
        pts.push(new THREE.Vector3(Math.cos(angle) * r, z, Math.sin(angle) * r));
      }

      const positions = new Float32Array(N * 3);
      pts.forEach(function(p, i) { positions[i*3]=p.x; positions[i*3+1]=p.y; positions[i*3+2]=p.z; });
      const ptGeo = new THREE.BufferGeometry();
      ptGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
      const ptCloud = new THREE.Points(ptGeo, new THREE.PointsMaterial({ color: CYAN, size: 0.14, transparent: true, opacity: 0.9 }));
      scene.add(ptCloud);

      const linePts = [];
      for (let i = 1; i < N; i++) linePts.push(pts[i-1], pts[i]);
      scene.add(new THREE.LineSegments(
        new THREE.BufferGeometry().setFromPoints(linePts),
        new THREE.LineBasicMaterial({ color: TEAL, transparent: true, opacity: 0.35 })
      ));

      const tracer = new THREE.Mesh(new THREE.SphereGeometry(0.2, 8, 8), new THREE.MeshBasicMaterial({ color: WHITE }));
      scene.add(tracer);

      updateFn = function(t) {
        scene.rotation.y = t * 0.2;
        const prog = (t * 0.08) % 1;
        const idx = Math.min(Math.floor(prog * N), N - 1);
        tracer.position.copy(pts[idx]);
        tracer.scale.setScalar(1 + Math.sin(t * 5) * 0.3);
      };
    }

    else if (sceneName === 'bifurcation-tree') {
      // Branching paths at a decision point
      // Equation: x_{n+1} = r * x_n * (1 - x_n)  [logistic map]
      const steps = 80;

      // Pre-split path
      const prePts = [];
      for (let i = 0; i < 25; i++) {
        const t = i / 25;
        prePts.push(new THREE.Vector3(-6 + t * 6, Math.sin(t * Math.PI * 2) * 0.4, 0));
      }
      scene.add(new THREE.Line(
        new THREE.BufferGeometry().setFromPoints(prePts),
        new THREE.LineBasicMaterial({ color: WHITE, transparent: true, opacity: 0.6 })
      ));

      // Branch A: ordered
      const brA = [];
      for (let i = 0; i < steps; i++) {
        const t = i / steps;
        const angle = t * Math.PI * 7;
        const r = 0.4 + t * 3;
        brA.push(new THREE.Vector3(t * 7, Math.cos(angle) * r, Math.sin(angle) * r));
      }
      scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(brA), new THREE.LineBasicMaterial({ color: CYAN, transparent: true, opacity: 0.9 })));

      // Branch B: chaotic
      const brB = [];
      for (let i = 0; i < steps; i++) {
        const t = i / steps;
        const angle = t * Math.PI * 11;
        const r = 2.5 * (1 - t * 0.85);
        const noise = (Math.sin(i * 7.3) + Math.cos(i * 3.1)) * t * 0.7;
        brB.push(new THREE.Vector3(t * 7, -Math.cos(angle) * r + noise, Math.sin(angle) * r * 0.5 + noise));
      }
      scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(brB), new THREE.LineBasicMaterial({ color: RED, transparent: true, opacity: 0.85 })));

      // Split node
      const split = new THREE.Mesh(new THREE.SphereGeometry(0.22, 10, 10), new THREE.MeshBasicMaterial({ color: WHITE }));
      scene.add(split);

      // Particles
      const pA = [], pB = [];
      for (let i = 0; i < 4; i++) {
        const mA = new THREE.Mesh(new THREE.SphereGeometry(0.11, 6, 6), new THREE.MeshBasicMaterial({ color: CYAN }));
        const mB = new THREE.Mesh(new THREE.SphereGeometry(0.09, 6, 6), new THREE.MeshBasicMaterial({ color: RED }));
        scene.add(mA, mB);
        pA.push(mA); pB.push(mB);
      }

      updateFn = function(t) {
        scene.rotation.y = Math.sin(t * 0.09) * 0.4;
        split.scale.setScalar(1 + Math.sin(t * 3) * 0.25);
        pA.forEach(function(p, i) {
          const idx = Math.floor(((t * 0.14 + i * 0.25) % 1) * (steps - 1));
          p.position.copy(brA[idx]);
        });
        pB.forEach(function(p, i) {
          const idx = Math.floor(((t * 0.11 + i * 0.25) % 1) * (steps - 1));
          p.position.copy(brB[idx]);
        });
      };
    }

    else if (sceneName === 'wave-interference') {
      // Two waves interfering -- exchange field interference pattern
      // Equation: psi(x,t) = A*sin(kx - wt) + B*sin(kx + wt)
      const N = 80;
      const waveA = [], waveB = [], combined = [];
      for (let i = 0; i < N; i++) {
        const x = (i / N - 0.5) * 14;
        waveA.push(new THREE.Vector3(x, 0, 0));
        waveB.push(new THREE.Vector3(x, 0, 0));
        combined.push(new THREE.Vector3(x, 0, 0));
      }

      const posA = new Float32Array(N * 3);
      const posB = new Float32Array(N * 3);
      const posC = new Float32Array(N * 3);

      const geoA = new THREE.BufferGeometry(); geoA.setAttribute('position', new THREE.BufferAttribute(posA, 3));
      const geoB = new THREE.BufferGeometry(); geoB.setAttribute('position', new THREE.BufferAttribute(posB, 3));
      const geoC = new THREE.BufferGeometry(); geoC.setAttribute('position', new THREE.BufferAttribute(posC, 3));

      scene.add(new THREE.Line(geoA, new THREE.LineBasicMaterial({ color: CYAN,    transparent: true, opacity: 0.55 })));
      scene.add(new THREE.Line(geoB, new THREE.LineBasicMaterial({ color: MAGENTA, transparent: true, opacity: 0.55 })));
      scene.add(new THREE.Line(geoC, new THREE.LineBasicMaterial({ color: WHITE,   transparent: true, opacity: 0.9  })));

      updateFn = function(t) {
        scene.rotation.y = Math.sin(t * 0.07) * 0.2;
        for (let i = 0; i < N; i++) {
          const x = (i / N - 0.5) * 14;
          const yA = Math.sin(x * 0.8 - t * 1.5) * 1.8;
          const yB = Math.sin(x * 0.8 + t * 1.5) * 1.8;
          posA[i*3]=x; posA[i*3+1]=yA-3; posA[i*3+2]=0;
          posB[i*3]=x; posB[i*3+1]=yB;   posB[i*3+2]=0;
          posC[i*3]=x; posC[i*3+1]=(yA+yB)*0.5+3; posC[i*3+2]=0;
        }
        geoA.attributes.position.needsUpdate = true;
        geoB.attributes.position.needsUpdate = true;
        geoC.attributes.position.needsUpdate = true;
      };
    }

    else if (sceneName === 'lattice-propagation') {
      // Error wave propagating through a node lattice
      // Equation: E_ij(t) = E_0 * exp(-d_ij / lambda) * sin(omega*t - k*d_ij)
      const cols = 9, rows = 6;
      const sp = 1.8;
      const nodes = [];
      for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
          const x = (c - (cols-1)/2) * sp;
          const y = (r - (rows-1)/2) * sp;
          const geo = new THREE.SphereGeometry(0.1, 7, 7);
          const mat = new THREE.MeshBasicMaterial({ color: 0x112233 });
          const mesh = new THREE.Mesh(geo, mat);
          mesh.position.set(x, y, 0);
          scene.add(mesh);
          nodes.push({ x, y, r, c, mesh });
        }
      }

      updateFn = function(t) {
        scene.rotation.y = Math.sin(t * 0.08) * 0.3;
        const waveFront = (t * 1.2) % (cols * sp);
        nodes.forEach(function(n) {
          const d = n.x + (cols-1)/2 * sp; // distance from left edge
          const phase = d - waveFront;
          const activation = Math.exp(-Math.abs(phase) * 0.5) * Math.max(0, Math.sin(t * 2 - d * 0.5));
          const col = new THREE.Color().lerpColors(
            new THREE.Color(0x0a1a2a),
            new THREE.Color(0xff2244),
            Math.max(0, activation)
          );
          n.mesh.material.color.copy(col);
          n.mesh.scale.setScalar(1 + activation * 1.2);
        });
      };
    }

    // Fallback: simple rotating torus
    else {
      const torus = new THREE.Mesh(
        new THREE.TorusGeometry(3, 0.8, 16, 60),
        new THREE.MeshBasicMaterial({ color: TEAL, wireframe: true, transparent: true, opacity: 0.6 })
      );
      scene.add(torus);
      updateFn = function(t) { torus.rotation.x = t * 0.5; torus.rotation.y = t * 0.3; };
    }

    // Animation loop
    let startTime = null;
    function animate(ts) {
      if (!startTime) startTime = ts;
      const elapsed = (ts - startTime) / 1000;
      if (updateFn) updateFn(elapsed);
      renderer.render(scene, camera);
      requestAnimationFrame(animate);
    }
    requestAnimationFrame(animate);
  }

})();

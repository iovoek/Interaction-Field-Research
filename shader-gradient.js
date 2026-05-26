/**
 * shader-gradient.js
 * Animated mesh gradient background using WebGL2 + Perlin noise vertex displacement.
 * Derived from ShaderGradient (github.com/ruucm/shadergradient) — MIT License.
 * Adapted to vanilla WebGL2 for static GitHub Pages deployment.
 *
 * Usage: Add <canvas id="sg-canvas"></canvas> to your page and include this script.
 * The canvas will fill its parent container and animate continuously.
 */
(function () {
  'use strict';

  const VERT = `#version 300 es
precision highp float;

// Classic 3D Perlin noise (inlined from glsl-noise)
vec3 mod289v3(vec3 x){ return x - floor(x*(1./289.))*289.; }
vec4 mod289v4(vec4 x){ return x - floor(x*(1./289.))*289.; }
vec4 permute(vec4 x){ return mod289v4(((x*34.)+1.)*x); }
vec4 taylorInvSqrt(vec4 r){ return 1.79284291400159 - 0.85373472095314*r; }
vec3 fade3(vec3 t){ return t*t*t*(t*(t*6.-15.)+10.); }

float cnoise(vec3 P){
  vec3 Pi0=floor(P), Pi1=Pi0+1.;
  Pi0=mod289v3(Pi0); Pi1=mod289v3(Pi1);
  vec3 Pf0=fract(P), Pf1=Pf0-1.;
  vec4 ix=vec4(Pi0.x,Pi1.x,Pi0.x,Pi1.x);
  vec4 iy=vec4(Pi0.yy,Pi1.yy);
  vec4 iz0=Pi0.zzzz, iz1=Pi1.zzzz;
  vec4 ixy=permute(permute(ix)+iy);
  vec4 ixy0=permute(ixy+iz0), ixy1=permute(ixy+iz1);
  vec4 gx0=ixy0*(1./7.), gy0=fract(floor(gx0)*(1./7.))-.5;
  gx0=fract(gx0);
  vec4 gz0=vec4(.5)-abs(gx0)-abs(gy0);
  vec4 sz0=step(gz0,vec4(0.));
  gx0-=sz0*(step(0.,gx0)-.5); gy0-=sz0*(step(0.,gy0)-.5);
  vec4 gx1=ixy1*(1./7.), gy1=fract(floor(gx1)*(1./7.))-.5;
  gx1=fract(gx1);
  vec4 gz1=vec4(.5)-abs(gx1)-abs(gy1);
  vec4 sz1=step(gz1,vec4(0.));
  gx1-=sz1*(step(0.,gx1)-.5); gy1-=sz1*(step(0.,gy1)-.5);
  vec3 g000=vec3(gx0.x,gy0.x,gz0.x), g100=vec3(gx0.y,gy0.y,gz0.y);
  vec3 g010=vec3(gx0.z,gy0.z,gz0.z), g110=vec3(gx0.w,gy0.w,gz0.w);
  vec3 g001=vec3(gx1.x,gy1.x,gz1.x), g101=vec3(gx1.y,gy1.y,gz1.y);
  vec3 g011=vec3(gx1.z,gy1.z,gz1.z), g111=vec3(gx1.w,gy1.w,gz1.w);
  vec4 norm0=taylorInvSqrt(vec4(dot(g000,g000),dot(g010,g010),dot(g100,g100),dot(g110,g110)));
  g000*=norm0.x; g010*=norm0.y; g100*=norm0.z; g110*=norm0.w;
  vec4 norm1=taylorInvSqrt(vec4(dot(g001,g001),dot(g011,g011),dot(g101,g101),dot(g111,g111)));
  g001*=norm1.x; g011*=norm1.y; g101*=norm1.z; g111*=norm1.w;
  float n000=dot(g000,Pf0), n100=dot(g100,vec3(Pf1.x,Pf0.yz));
  float n010=dot(g010,vec3(Pf0.x,Pf1.y,Pf0.z)), n110=dot(g110,vec3(Pf1.xy,Pf0.z));
  float n001=dot(g001,vec3(Pf0.xy,Pf1.z)), n101=dot(g101,vec3(Pf1.x,Pf0.y,Pf1.z));
  float n011=dot(g011,vec3(Pf0.x,Pf1.yz)), n111=dot(g111,Pf1);
  vec3 fade_xyz=fade3(Pf0);
  vec4 n_z=mix(vec4(n000,n100,n010,n110),vec4(n001,n101,n011,n111),fade_xyz.z);
  vec2 n_yz=mix(n_z.xy,n_z.zw,fade_xyz.y);
  return 2.2*mix(n_yz.x,n_yz.y,fade_xyz.x);
}

in vec3 position;
in vec2 uv;

uniform float uTime;
uniform float uNoiseDensity;
uniform float uNoiseStrength;
uniform float uSpeed;

out vec3 vPos;
out float vDistort;

void main(){
  vec3 pos = position;
  float t = uTime * uSpeed;
  float distort = cnoise(vec3(pos.xy * uNoiseDensity, t)) * uNoiseStrength;
  pos.z += distort;
  vPos = pos;
  vDistort = distort;
  gl_Position = vec4(pos.xy, 0., 1.);
}
`;

  const FRAG = `#version 300 es
precision highp float;

in vec3 vPos;
in float vDistort;

uniform vec3 uC1;
uniform vec3 uC2;
uniform vec3 uC3;
uniform float uTime;

out vec4 fragColor;

void main(){
  // Three-color gradient across x and z axes, modulated by displacement
  float t = smoothstep(-1.5, 1.5, vPos.x + vDistort * 0.4);
  float s = smoothstep(-0.8, 0.8, vPos.y + vDistort * 0.2);
  vec3 col = mix(mix(uC1, uC2, t), uC3, s);
  // Subtle vignette
  float dist = length(vPos.xy * 0.35);
  col *= 1. - smoothstep(0.6, 1.4, dist) * 0.5;
  fragColor = vec4(col, 1.);
}
`;

  function buildGrid(cols, rows) {
    const positions = [];
    const uvs = [];
    const indices = [];
    for (let r = 0; r <= rows; r++) {
      for (let c = 0; c <= cols; c++) {
        const x = (c / cols) * 2 - 1;
        const y = (r / rows) * 2 - 1;
        positions.push(x, y, 0);
        uvs.push(c / cols, r / rows);
      }
    }
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const a = r * (cols + 1) + c;
        const b = a + 1;
        const d = a + (cols + 1);
        const e = d + 1;
        indices.push(a, b, d, b, e, d);
      }
    }
    return { positions: new Float32Array(positions), uvs: new Float32Array(uvs), indices: new Uint32Array(indices) };
  }

  function compileShader(gl, type, src) {
    const s = gl.createShader(type);
    gl.shaderSource(s, src);
    gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {
      console.warn('[shader-gradient] Shader compile error:', gl.getShaderInfoLog(s));
      gl.deleteShader(s);
      return null;
    }
    return s;
  }

  function createProgram(gl, vsrc, fsrc) {
    const vs = compileShader(gl, gl.VERTEX_SHADER, vsrc);
    const fs = compileShader(gl, gl.FRAGMENT_SHADER, fsrc);
    if (!vs || !fs) return null;
    const prog = gl.createProgram();
    gl.attachShader(prog, vs);
    gl.attachShader(prog, fs);
    gl.linkProgram(prog);
    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) {
      console.warn('[shader-gradient] Program link error:', gl.getProgramInfoLog(prog));
      return null;
    }
    return prog;
  }

  function hexToRgb(hex) {
    const r = parseInt(hex.slice(1, 3), 16) / 255;
    const g = parseInt(hex.slice(3, 5), 16) / 255;
    const b = parseInt(hex.slice(5, 7), 16) / 255;
    return [r, g, b];
  }

  /**
   * initShaderGradient(canvas, options)
   * options: {
   *   c1: '#0a0a1a',  // color 1
   *   c2: '#0d2a2a',  // color 2 (teal hint)
   *   c3: '#0a0a0f',  // color 3
   *   speed: 0.12,
   *   noiseDensity: 1.2,
   *   noiseStrength: 0.18,
   *   cols: 80,
   *   rows: 50
   * }
   */
  window.initShaderGradient = function (canvas, opts) {
    opts = Object.assign({
      c1: '#0a0a1a',
      c2: '#0d2a28',
      c3: '#03030a',
      speed: 0.10,
      noiseDensity: 1.1,
      noiseStrength: 0.22,
      cols: 80,
      rows: 50
    }, opts || {});

    const gl = canvas.getContext('webgl2', { antialias: false, alpha: false });
    if (!gl) { console.warn('[shader-gradient] WebGL2 not supported'); return; }

    const prog = createProgram(gl, VERT, FRAG);
    if (!prog) return;

    const { positions, uvs, indices } = buildGrid(opts.cols, opts.rows);

    const vao = gl.createVertexArray();
    gl.bindVertexArray(vao);

    // position buffer
    const posBuf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, posBuf);
    gl.bufferData(gl.ARRAY_BUFFER, positions, gl.STATIC_DRAW);
    const posLoc = gl.getAttribLocation(prog, 'position');
    gl.enableVertexAttribArray(posLoc);
    gl.vertexAttribPointer(posLoc, 3, gl.FLOAT, false, 0, 0);

    // uv buffer
    const uvBuf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, uvBuf);
    gl.bufferData(gl.ARRAY_BUFFER, uvs, gl.STATIC_DRAW);
    const uvLoc = gl.getAttribLocation(prog, 'uv');
    if (uvLoc >= 0) {
      gl.enableVertexAttribArray(uvLoc);
      gl.vertexAttribPointer(uvLoc, 2, gl.FLOAT, false, 0, 0);
    }

    // index buffer
    const idxBuf = gl.createBuffer();
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, idxBuf);
    gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, indices, gl.STATIC_DRAW);

    gl.bindVertexArray(null);

    // uniforms
    const uTime = gl.getUniformLocation(prog, 'uTime');
    const uSpeed = gl.getUniformLocation(prog, 'uSpeed');
    const uND = gl.getUniformLocation(prog, 'uNoiseDensity');
    const uNS = gl.getUniformLocation(prog, 'uNoiseStrength');
    const uC1 = gl.getUniformLocation(prog, 'uC1');
    const uC2 = gl.getUniformLocation(prog, 'uC2');
    const uC3 = gl.getUniformLocation(prog, 'uC3');

    const c1 = hexToRgb(opts.c1);
    const c2 = hexToRgb(opts.c2);
    const c3 = hexToRgb(opts.c3);

    function resize() {
      const w = canvas.parentElement ? canvas.parentElement.clientWidth : window.innerWidth;
      const h = canvas.parentElement ? canvas.parentElement.clientHeight : window.innerHeight;
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.round(w * dpr);
      canvas.height = Math.round(h * dpr);
      canvas.style.width = w + 'px';
      canvas.style.height = h + 'px';
      gl.viewport(0, 0, canvas.width, canvas.height);
    }
    resize();
    window.addEventListener('resize', resize);

    let start = null;
    function loop(ts) {
      if (!start) start = ts;
      const t = (ts - start) / 1000;
      gl.useProgram(prog);
      gl.uniform1f(uTime, t);
      gl.uniform1f(uSpeed, opts.speed);
      gl.uniform1f(uND, opts.noiseDensity);
      gl.uniform1f(uNS, opts.noiseStrength);
      gl.uniform3fv(uC1, c1);
      gl.uniform3fv(uC2, c2);
      gl.uniform3fv(uC3, c3);
      gl.bindVertexArray(vao);
      gl.drawElements(gl.TRIANGLES, indices.length, gl.UNSIGNED_INT, 0);
      gl.bindVertexArray(null);
      requestAnimationFrame(loop);
    }
    requestAnimationFrame(loop);
  };

  // Auto-init any canvas with data-shader-gradient attribute
  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('canvas[data-shader-gradient]').forEach(function (canvas) {
      const c1 = canvas.dataset.c1 || undefined;
      const c2 = canvas.dataset.c2 || undefined;
      const c3 = canvas.dataset.c3 || undefined;
      const speed = canvas.dataset.speed ? parseFloat(canvas.dataset.speed) : undefined;
      window.initShaderGradient(canvas, { c1, c2, c3, speed });
    });
  });

})();

// core.js - the shared engine of a code-drawn film.
// THE CONTRACT: every frame is a pure function of t (seconds). No Math.random(), no state carried
// between frames, no counters, no physics integrated frame by frame. Frames render in parallel and
// out of order, so anything else flickers or desyncs.
// Randomness comes from hash/rng seeded by a stable KEY per object, re-seeded 12 times a second by
// boil(), which is what makes the ink "boil" like hand-drawn animation (2 frames per seed at 24 fps).
/* eslint-disable no-unused-vars */
(function (G) {
  const W = 1920, H = 1080, TAU = Math.PI * 2;
  const BOIL_HZ = 12;

  // ---------- math ----------
  const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
  const lerp = (a, b, u) => a + (b - a) * u;
  const inv = (a, b, x) => b === a ? (x >= a ? 1 : 0) : clamp((x - a) / (b - a));   // inverse lerp, clamped (zero-length safe)
  const smooth = u => { u = clamp(u); return u * u * (3 - 2 * u); };
  const smoother = u => { u = clamp(u); return u * u * u * (u * (u * 6 - 15) + 10); };
  const easeIn = u => { u = clamp(u); return u * u * u; };
  const easeOut = u => { u = clamp(u); return 1 - Math.pow(1 - u, 3); };
  const easeInOut = u => { u = clamp(u); return u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2; };
  const backOut = (u, s = 1.70158) => { u = clamp(u) - 1; return u * u * ((s + 1) * u + s) + 1; };
  // eased progress of t through [t0, t1]
  const seg = (t, t0, t1, e = smoother) => e(inv(t0, t1, t));
  // a damped spring response to a step at t0 (analytic, so still a pure function of t)
  const spring = (t, t0, freq = 2.2, damp = 4.5) => {
    if (t <= t0) return 0; const x = t - t0;
    return 1 - Math.exp(-damp * x) * Math.cos(TAU * freq * x);
  };
  // piecewise keys: keys = [[t, value], ...] sorted by t; eased between
  const keys = (t, ks, e = smoother) => {
    if (t <= ks[0][0]) return ks[0][1];
    for (let i = 1; i < ks.length; i++) {
      if (t <= ks[i][0]) {
        const [t0, v0] = ks[i - 1], [t1, v1] = ks[i];
        const u = e(inv(t0, t1, t));
        return Array.isArray(v0) ? v0.map((v, j) => lerp(v, v1[j], u)) : lerp(v0, v1, u);
      }
    }
    return ks[ks.length - 1][1];
  };

  // ---------- deterministic randomness ----------
  function hashStr(s) {                    // FNV-1a -> uint32
    s = String(s); let h = 2166136261 >>> 0;
    for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619) >>> 0; }
    return h >>> 0;
  }
  function mulberry32(a) {
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      let r = Math.imul(a ^ (a >>> 15), 1 | a);
      r = (r + Math.imul(r ^ (r >>> 7), 61 | r)) ^ r;
      return ((r ^ (r >>> 14)) >>> 0) / 4294967296;
    };
  }
  const rng = (key, salt = 0) => mulberry32((hashStr(key) ^ Math.imul(salt | 0, 2654435761)) >>> 0);
  const hash01 = (key, salt = 0) => rng(key, salt)();                 // one stable float per key
  const boilStep = t => Math.floor(t * BOIL_HZ + 1e-6);
  // a fresh stream per object per boil step: a moving object never shifts anyone else's stream
  const boil = (key, t) => rng(key, boilStep(t) + 7);
  // smooth 1-D value noise, deterministic
  function noise1(x, key = 'n') {
    const i = Math.floor(x), f = x - i, s = smooth(f);
    return lerp(hash01(key, i), hash01(key, i + 1), s) * 2 - 1;
  }

  // ---------- colour ----------
  function hexRgb(h) {
    h = h.replace('#', ''); if (h.length === 3) h = h.split('').map(c => c + c).join('');
    const n = parseInt(h, 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
  }
  const rgba = (hex, a = 1) => { const [r, g, b] = hexRgb(hex); return `rgba(${r},${g},${b},${a})`; };
  const mix = (h1, h2, u) => {
    const a = hexRgb(h1), b = hexRgb(h2);
    return '#' + a.map((v, i) => Math.round(lerp(v, b[i], clamp(u))).toString(16).padStart(2, '0')).join('');
  };

  // ---------- geometry helpers (return point lists) ----------
  const ellipsePts = (cx, cy, rx, ry, n = 28, rot = 0) => {
    const p = []; for (let i = 0; i < n; i++) {
      const a = i / n * TAU, x = Math.cos(a) * rx, y = Math.sin(a) * ry;
      p.push([cx + x * Math.cos(rot) - y * Math.sin(rot), cy + x * Math.sin(rot) + y * Math.cos(rot)]);
    } return p;
  };
  const rectPts = (x, y, w, h, per = 3) => {           // a rectangle with `per` points per side, for boiling edges
    const p = [], c = [[x, y], [x + w, y], [x + w, y + h], [x, y + h]];
    for (let s = 0; s < 4; s++) { const a = c[s], b = c[(s + 1) % 4]; for (let i = 0; i < per; i++) p.push([lerp(a[0], b[0], i / per), lerp(a[1], b[1], i / per)]); }
    return p;
  };
  const roundRectPts = (x, y, w, h, r, n = 6) => {
    const p = [], cs = [[x + w - r, y + r, -Math.PI / 2], [x + w - r, y + h - r, 0], [x + r, y + h - r, Math.PI / 2], [x + r, y + r, Math.PI]];
    for (const [cx, cy, a0] of cs) for (let i = 0; i <= n; i++) { const a = a0 + i / n * Math.PI / 2; p.push([cx + Math.cos(a) * r, cy + Math.sin(a) * r]); }
    return p;
  };
  const tx = (pts, dx = 0, dy = 0, s = 1, rot = 0, ox = 0, oy = 0) => pts.map(([x, y]) => {
    x = (x - ox) * s; y = (y - oy) * s;
    return [ox + dx + x * Math.cos(rot) - y * Math.sin(rot), oy + dy + x * Math.sin(rot) + y * Math.cos(rot)];
  });
  // Catmull-Rom resample so a few control points become a smooth brush path
  function smoothPts(pts, closed = false, sub = 4) {
    if (pts.length < 3) return pts.slice();
    const out = [], n = pts.length, P = i => closed ? pts[(i + n) % n] : pts[clamp(i, 0, n - 1)];
    const last = closed ? n : n - 1;
    for (let i = 0; i < last; i++) {
      const p0 = P(i - 1), p1 = P(i), p2 = P(i + 1), p3 = P(i + 2);
      for (let k = 0; k < sub; k++) {
        const u = k / sub, u2 = u * u, u3 = u2 * u;
        out.push([0, 1].map(j => 0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * u + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * u2 + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * u3)));
      }
    }
    if (!closed) out.push(pts[n - 1]);
    return out;
  }

  // ---------- ink ----------
  // o: {w, color, key, t, amp (px of boil), taper (0..1), passes, alpha, closed, dry (0..1 gaps), sub}
  function jitterPts(pts, r, amp) { return pts.map(([x, y]) => [x + (r() - 0.5) * 2 * amp, y + (r() - 0.5) * 2 * amp]); }
  function ribbon(ctx, pts, widthAt) {
    const n = pts.length; if (n < 2) return;
    const L = [], R = [];
    for (let i = 0; i < n; i++) {
      const a = pts[Math.max(0, i - 1)], b = pts[Math.min(n - 1, i + 1)];
      let dx = b[0] - a[0], dy = b[1] - a[1]; const d = Math.hypot(dx, dy) || 1; dx /= d; dy /= d;
      const w = widthAt(i / (n - 1)) / 2;
      L.push([pts[i][0] - dy * w, pts[i][1] + dx * w]); R.push([pts[i][0] + dy * w, pts[i][1] - dx * w]);
    }
    ctx.beginPath(); ctx.moveTo(L[0][0], L[0][1]);
    for (let i = 1; i < n; i++) ctx.lineTo(L[i][0], L[i][1]);
    for (let i = n - 1; i >= 0; i--) ctx.lineTo(R[i][0], R[i][1]);
    ctx.closePath(); ctx.fill();
  }
  function inkLine(ctx, pts, o = {}) {
    const w = o.w ?? 4, amp = o.amp ?? 1.4, passes = o.passes ?? 2, taper = o.taper ?? 0.8;
    const key = o.key ?? 'ink', t = o.t ?? 0, closed = !!o.closed;
    if (!pts || pts.length < 2) return;
    ctx.save(); ctx.fillStyle = o.color ?? '#231a15';
    for (let p = 0; p < passes; p++) {
      const r = boil(key + ':' + p, t);
      let q = jitterPts(pts, r, amp * (p ? 0.8 : 1));
      q = smoothPts(q, closed, o.sub ?? 4);
      if (closed) q.push(q[0]);
      const ph = r() * 10, wob = o.wobble ?? 0.25;
      ctx.globalAlpha = (o.alpha ?? 1) * (p ? 0.55 : 1);
      const wp = p ? w * 0.55 : w;
      ribbon(ctx, q, u => {
        const tp = closed ? 1 : Math.min(1, Math.min(u, 1 - u) / 0.12 * (1 - taper) + (1 - taper) + Math.min(u, 1 - u) * taper * 8);
        return wp * clamp(tp, 0.25, 1) * (1 + wob * noise1(u * 7 + ph, key));
      });
    }
    ctx.restore();
  }
  const inkPoly = (ctx, pts, o = {}) => inkLine(ctx, pts, Object.assign({}, o, { closed: true }));
  // flat colour fill with a boiling edge (the "wash" of cel animation)
  function wash(ctx, pts, color, o = {}) {
    const key = o.key ?? 'wash', t = o.t ?? 0, amp = o.amp ?? 1.2;
    let q = smoothPts(jitterPts(pts, boil(key + ':w', t), amp), true, o.sub ?? 3);
    ctx.save(); ctx.globalAlpha = o.alpha ?? 1; ctx.fillStyle = color;
    ctx.beginPath(); ctx.moveTo(q[0][0], q[0][1]); for (const [x, y] of q) ctx.lineTo(x, y); ctx.closePath(); ctx.fill();
    if (o.tex !== false && G.__grainPat) {       // printed-ink texture inside the shape
      ctx.globalCompositeOperation = 'multiply'; ctx.globalAlpha = (o.alpha ?? 1) * (o.tex ?? 0.35);
      ctx.fillStyle = G.__grainPat; ctx.fill();
    }
    ctx.restore();
  }
  // ---------- cut paper ----------
  // A piece of paper: flat colour + fibre texture + a soft cast shadow (depth between layers), with an
  // optional thin ink edge. Stop-motion "boil": the piece shifts by a fraction of a pixel at 12 Hz.
  // o.sh = shadow scale (pass the on-screen scale of the piece: canvas shadows ignore the transform).
  function paperShape(ctx, pts, color, o = {}) {
    const key = o.key ?? 'pp', t = o.t ?? 0, r = boil(key + ':j', t), j = o.jit ?? 0.5, sh = o.sh ?? 1;
    const dx = (r() - .5) * j, dy = (r() - .5) * j;
    let q = jitterPts(pts.map(([x, y]) => [x + dx, y + dy]), rng(key + ':cut'), o.cut ?? 0.9);
    if (!o.sharp) q = smoothPts(q, true, o.sub ?? 3);   // sharp: straight cut edges and corners (architecture)
    ctx.save(); ctx.globalAlpha = o.alpha ?? 1;
    ctx.beginPath(); ctx.moveTo(q[0][0], q[0][1]); for (const [x, y] of q) ctx.lineTo(x, y); ctx.closePath();
    if (o.shadow !== false) { ctx.shadowColor = o.shadowColor ?? 'rgba(46,28,14,0.38)'; ctx.shadowBlur = (o.blur ?? 9) * sh; ctx.shadowOffsetX = (o.sx ?? 3) * sh; ctx.shadowOffsetY = (o.sy ?? 5) * sh; }
    ctx.fillStyle = color; ctx.fill();
    ctx.shadowColor = 'transparent';
    if (G.__grainPat && o.tex !== false) { ctx.globalCompositeOperation = 'multiply'; ctx.globalAlpha = (o.alpha ?? 1) * (o.tex ?? 0.55); ctx.fillStyle = G.__grainPat; ctx.fill(); ctx.globalCompositeOperation = 'source-over'; }
    if (o.light !== false) {                    // a faint lit edge on the top-left of every cut piece
      ctx.globalAlpha = (o.alpha ?? 1) * 0.22; ctx.strokeStyle = '#fff8e8'; ctx.lineWidth = 1.6; ctx.save(); ctx.translate(-1, -1); ctx.stroke(); ctx.restore();
    }
    ctx.restore();
    if (o.ink) inkPoly(ctx, q, { w: o.lw ?? 2.2, color: o.ink, key: key + ':o', t, amp: o.amp ?? .7, alpha: o.inkAlpha ?? .75, passes: 1, sub: o.sharp ? 1 : undefined });
    return q;
  }
  // a tapered paper strip along a path (limbs, scarves, stems)
  function paperStrip(ctx, pts, w0, w1, color, o = {}) {
    const q = smoothPts(pts, false, 6), n = q.length, L = [], R = [];
    for (let i = 0; i < n; i++) {
      const a = q[Math.max(0, i - 1)], b = q[Math.min(n - 1, i + 1)];
      let dx = b[0] - a[0], dy = b[1] - a[1]; const d = Math.hypot(dx, dy) || 1; dx /= d; dy /= d;
      const w = lerp(w0, w1, i / (n - 1)) / 2; L.push([q[i][0] - dy * w, q[i][1] + dx * w]); R.push([q[i][0] + dy * w, q[i][1] - dx * w]);
    }
    const cap = (c, w, a0) => { const p = []; for (let i = 0; i <= 6; i++) { const a = a0 + i / 6 * Math.PI; p.push([c[0] + Math.cos(a) * w / 2, c[1] + Math.sin(a) * w / 2]); } return p; };
    const a0 = Math.atan2(q[1][1] - q[0][1], q[1][0] - q[0][0]), a1 = Math.atan2(q[n - 1][1] - q[n - 2][1], q[n - 1][0] - q[n - 2][0]);
    const poly = [...L, ...cap(q[n - 1], w1, a1 - Math.PI / 2), ...R.reverse(), ...cap(q[0], w0, a0 + Math.PI / 2)];
    return paperShape(ctx, poly, color, Object.assign({ sub: 1, cut: 0.4 }, o));
  }

  // shape = wash + ink outline, the default for characters and props
  function shape(ctx, pts, fill, o = {}) {
    if (fill) wash(ctx, pts, fill, o);
    if (o.line !== false) inkPoly(ctx, pts, { w: o.lw ?? 3.5, color: o.ink, key: (o.key ?? 's') + ':o', t: o.t, amp: o.amp ?? 1.2, alpha: o.lineAlpha });
  }
  // dry-brush hatching clipped to a region
  function hatch(ctx, region, o = {}) {
    const key = o.key ?? 'h', t = o.t ?? 0, ang = o.angle ?? -0.8, gap = o.gap ?? 14, w = o.w ?? 1.6;
    const xs = region.map(p => p[0]), ys = region.map(p => p[1]);
    const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys);
    const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2, R = Math.hypot(x1 - x0, y1 - y0) / 2 + 10;
    ctx.save(); ctx.beginPath(); ctx.moveTo(region[0][0], region[0][1]); for (const [x, y] of region) ctx.lineTo(x, y); ctx.closePath(); ctx.clip();
    const r = rng(key); let i = 0;
    for (let d = -R; d < R; d += gap, i++) {
      const c = Math.cos(ang), s = Math.sin(ang);
      const a = [cx + c * -R - s * d, cy + s * -R + c * d], b = [cx + c * R - s * d, cy + s * R + c * d];
      if (r() < (o.density ?? 1)) inkLine(ctx, [a, [lerp(a[0], b[0], .5), lerp(a[1], b[1], .5)], b], { w, color: o.color, key: key + i, t, amp: 1.5, passes: 1, alpha: o.alpha ?? 0.8 });
    }
    ctx.restore();
  }

  // ---------- paper, grain, light ----------
  function makePaper(pal) {
    const c = document.createElement('canvas'); c.width = W + 80; c.height = H + 80;
    const g = c.getContext('2d'), r = rng('paper');
    g.fillStyle = pal.paper; g.fillRect(0, 0, c.width, c.height);
    for (let i = 0; i < 26; i++) {           // soft blotches (uneven sizing of old paper)
      const x = r() * c.width, y = r() * c.height, rad = 120 + r() * 420;
      const gr = g.createRadialGradient(x, y, 0, x, y, rad);
      gr.addColorStop(0, rgba(pal.paperDark, 0.07 * r())); gr.addColorStop(1, rgba(pal.paperDark, 0));
      g.fillStyle = gr; g.fillRect(x - rad, y - rad, rad * 2, rad * 2);
    }
    for (let i = 0; i < 2600; i++) {         // fibres
      const x = r() * c.width, y = r() * c.height, a = r() * TAU, l = 4 + r() * 18;
      g.strokeStyle = rgba(r() < 0.5 ? pal.paperDark : '#ffffff', 0.05 + r() * 0.08); g.lineWidth = 0.6 + r() * 0.8;
      g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo(x + Math.cos(a + 0.6) * l * .5, y + Math.sin(a + .6) * l * .5, x + Math.cos(a) * l, y + Math.sin(a) * l); g.stroke();
    }
    for (let i = 0; i < 900; i++) { g.fillStyle = rgba(pal.paperDark, 0.08 + r() * 0.15); g.fillRect(r() * c.width, r() * c.height, 1 + r() * 1.6, 1 + r() * 1.6); }
    return c;
  }
  function makeGrain() {                      // a tile multiplied over everything: printed-paper tooth
    const c = document.createElement('canvas'); c.width = c.height = 256;
    const g = c.getContext('2d'), img = g.createImageData(256, 256), r = rng('grain');
    for (let i = 0; i < img.data.length; i += 4) { const v = 225 + r() * 30; img.data[i] = v; img.data[i + 1] = v - 2; img.data[i + 2] = v - 6; img.data[i + 3] = 255; }
    g.putImageData(img, 0, 0); return c;
  }
  // background paper, drifting a few px at the boil rate so even a still frame breathes
  function paper(ctx, t, o = {}) {
    const r = boil('paperdrift', t), dx = -40 + (r() - 0.5) * (o.drift ?? 3), dy = -40 + (r() - 0.5) * (o.drift ?? 3);
    ctx.drawImage(G.__paper, dx, dy);
    if (o.tint) { ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = o.tint; ctx.globalAlpha = o.tintAlpha ?? 1; ctx.fillRect(0, 0, W, H); ctx.restore(); }
  }
  // final pass on the whole frame: grain, vignette, optional flicker. Call once, in screen space.
  function finish(ctx, t, o = {}) {
    ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0);
    const r = boil('grainoff', t);
    ctx.globalCompositeOperation = 'multiply'; ctx.globalAlpha = o.grain ?? 0.55;
    ctx.translate(-r() * 256, -r() * 256); ctx.fillStyle = G.__grainPat; ctx.fillRect(0, 0, W + 256, H + 256);
    ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1;
    const v = o.vignette ?? 0.35;
    if (v > 0) {
      const gr = ctx.createRadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, H * 0.95);
      gr.addColorStop(0, 'rgba(0,0,0,0)'); gr.addColorStop(1, `rgba(40,25,15,${v})`);
      ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = gr; ctx.fillRect(0, 0, W, H);
    }
    if (o.fade) { ctx.globalCompositeOperation = 'source-over'; ctx.fillStyle = o.fadeColor ?? '#000'; ctx.globalAlpha = clamp(o.fade); ctx.fillRect(0, 0, W, H); }
    ctx.restore();
  }
  function glow(ctx, x, y, r, color, a = 0.6, op = 'screen') {
    ctx.save(); ctx.globalCompositeOperation = op;
    const g = ctx.createRadialGradient(x, y, 0, x, y, r);
    g.addColorStop(0, rgba(color, a)); g.addColorStop(0.45, rgba(color, a * 0.35)); g.addColorStop(1, rgba(color, 0));
    ctx.fillStyle = g; ctx.fillRect(x - r, y - r, r * 2, r * 2); ctx.restore();
  }

  // ---------- camera ----------
  // cam = {x, y, z, r}: the world point at the screen centre, zoom, roll
  function applyCam(ctx, cam) {
    ctx.translate(W / 2, H / 2); ctx.scale(cam.z ?? 1, cam.z ?? 1); ctx.rotate(cam.r ?? 0); ctx.translate(-(cam.x ?? W / 2), -(cam.y ?? H / 2));
  }
  const worldToScreen = (cam, x, y) => {
    const z = cam.z ?? 1, r = cam.r ?? 0, dx = x - (cam.x ?? W / 2), dy = y - (cam.y ?? H / 2);
    return [W / 2 + z * (dx * Math.cos(r) - dy * Math.sin(r)), H / 2 + z * (dx * Math.sin(r) + dy * Math.cos(r))];
  };
  // handheld drift so no shot is ever dead-still
  const drift = (t, key = 'cam', amt = 1) => ({ x: noise1(t * 0.23, key + 'x') * 6 * amt, y: noise1(t * 0.19, key + 'y') * 4 * amt, r: noise1(t * 0.13, key + 'r') * 0.003 * amt });

  // ---------- layers: depth of field, portals, compositing ----------
  const __layers = {};
  function layer(name) {
    let c = __layers[name];
    if (!c) { c = __layers[name] = document.createElement('canvas'); c.width = W; c.height = H; }
    const g = c.getContext('2d'); g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1; g.globalCompositeOperation = 'source-over'; g.filter = 'none'; g.clearRect(0, 0, W, H);
    return [c, g];
  }
  // draw fn into its own layer, then composite with blur (depth of field), alpha and blend mode
  function plate(ctx, name, fn, o = {}) {
    const [c, g] = layer(name); fn(g);
    ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0);
    if (o.blur) ctx.filter = `blur(${o.blur}px)`;
    ctx.globalAlpha = o.alpha ?? 1; ctx.globalCompositeOperation = o.op ?? 'source-over';
    ctx.drawImage(c, 0, 0); ctx.restore();
  }
  // render a whole other shot/frame into rect [x,y,w,h] (screen space): the zoom-through-a-window portal
  function portal(ctx, rect, drawFn, o = {}) {
    const [c, g] = layer(o.name ?? 'portal'); drawFn(g);
    ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.beginPath();
    if (o.clip) { const p = o.clip; ctx.moveTo(p[0][0], p[0][1]); for (const q of p) ctx.lineTo(q[0], q[1]); ctx.closePath(); } else ctx.rect(rect[0], rect[1], rect[2], rect[3]);
    ctx.clip(); ctx.globalAlpha = o.alpha ?? 1;
    ctx.drawImage(c, rect[0], rect[1], rect[2], rect[3]); ctx.restore();
  }

  // ---------- Hebrew text ----------
  // Canvas runs the bidi algorithm for a plain RTL string when ctx.direction = 'rtl'. Keep digits and Latin
  // in fonts that have them (FrankRuehl has no Latin: set o.font to 'David' or 'Guttman Frnew' for dates).
  // reveal: 0..1 wipes the text in from the RIGHT, the way Hebrew is written.
  // A number run like 1950–2020 inside RTL text is laid out right-to-left ("2020–1950") unless it is
  // isolated as LTR. ltrIsolate wraps every digit run (with its dashes, dots, colons) in LRI...PDI.
  const ltrIsolate = s => s.replace(/[0-9][0-9–—\-.:/,]*[0-9]|[0-9]/g, m => '⁦' + m + '⁩');
  function inkText(ctx, str, x, y, o = {}) {
    const size = o.size ?? 64, font = o.font ?? 'FrankRuehl', t = o.t ?? 0, key = o.key ?? str;
    str = ltrIsolate(str);
    ctx.save(); ctx.font = `${o.weight ?? ''} ${size}px "${font}"`.trim(); ctx.direction = 'rtl';
    ctx.textAlign = o.align ?? 'center'; ctx.textBaseline = 'middle';
    const wdt = ctx.measureText(str).width, reveal = o.reveal ?? 1;
    const left = o.align === 'right' ? x - wdt : o.align === 'left' ? x : x - wdt / 2;
    if (reveal < 1) { ctx.beginPath(); ctx.rect(left + wdt * (1 - reveal) - 4, y - size, wdt * reveal + 30, size * 2.2); ctx.clip(); }
    const r = boil(key, t), a = o.amp ?? 0.8;
    ctx.fillStyle = o.color ?? '#231a15'; ctx.globalAlpha = o.alpha ?? 1;
    ctx.fillText(str, x + (r() - .5) * a, y + (r() - .5) * a);
    ctx.globalAlpha = (o.alpha ?? 1) * 0.35; ctx.fillText(str, x + (r() - .5) * a * 2, y + (r() - .5) * a * 2);   // ink bleed
    ctx.restore();
    return wdt;
  }

  // ---------- timeline ----------
  // shots: [{name, t0, t1, fn(ctx, t, lt, dur, info)}]. A shot paints the ENTIRE frame.
  // Transitions live inside shots (a shot may call drawShot() for its neighbour, e.g. through a portal).
  const TL = { shots: [], byName: {} };
  function addShot(s) { TL.shots.push(s); TL.byName[s.name] = s; TL.shots.sort((a, b) => a.t0 - b.t0); }
  function shotAt(t) { let s = TL.shots[0]; for (const x of TL.shots) if (t >= x.t0) s = x; return s; }
  const __drawing = new Set();             // re-entry guard: two shots drawing each other through portals
  function drawShot(ctx, name, t) {
    const s = TL.byName[name]; if (!s) throw new Error('no shot ' + name);
    if (__drawing.has(name)) return;
    __drawing.add(name);
    try { ctx.save(); s.fn(ctx, t, t - s.t0, s.t1 - s.t0, s); ctx.restore(); } finally { __drawing.delete(name); }
  }

  let __ctx = null;
  function setup(canvas, pal) {
    __ctx = canvas.getContext('2d');
    G.__paper = makePaper(pal); G.__grain = makeGrain(); G.__grainPat = __ctx.createPattern(G.__grain, 'repeat');
  }
  // the one entry point the renderer calls
  function renderAt(t) {
    const ctx = __ctx; ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over'; ctx.filter = 'none';
    ctx.clearRect(0, 0, W, H);
    const s = shotAt(t); drawShot(ctx, s.name, t);
    return s.name;
  }

  G.E = {
    W, H, TAU, BOIL_HZ, clamp, lerp, inv, smooth, smoother, easeIn, easeOut, easeInOut, backOut, seg, spring, keys,
    hashStr, rng, hash01, boil, boilStep, noise1, rgba, mix, hexRgb,
    ellipsePts, rectPts, roundRectPts, tx, smoothPts, inkLine, inkPoly, wash, shape, hatch, paperShape, paperStrip,
    paper, finish, glow, applyCam, worldToScreen, drift, layer, plate, portal, inkText, ltrIsolate,
    TL, addShot, shotAt, drawShot, setup, renderAt,
  };
})(window);

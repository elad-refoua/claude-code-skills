// cast.js - one parametric paper-puppet rig for the whole film, so no character drifts between chapters.
// person(ctx, P, o): P = who (proportions, colours, hair, clothes), o = where / pose / face / time.
// Style: cut-paper puppets. Every part is a piece of paper (paperShape / paperStrip) with a soft cast
// shadow; faces and small details are drawn in ink on the paper. Front view; `turn` fakes a 3/4 view.
// Origin = the point between the feet; y grows downward; 1 unit = 1 px at scale 1.
// No state between frames: blinks, breathing, boil and sway are all functions of t.
(function () {
  const { lerp, clamp, mix, ellipsePts, paperShape, paperStrip, wash, inkLine, inkPoly, hash01, noise1, TAU, rgba } = E;
  const INK = () => FILM.pal.ink;

  // ---------- who ----------
  const BOY = {
    name: 'boy', head: 58, headY: 252, shoulder: 188, hip: 96, shoulderW: 36, hipW: 31,
    armU: 44, armL: 42, leg: 96, limbW: 13, belly: 5,
    skin: '#f5c9a0', blush: '#ec8870', hair: '#2b1e18', hairStyle: 'tuft',
    shirt: '#f3e9d6', stripes: '#c8412e', sleeve: '#c8412e', sleeveLen: 'short', pants: '#2f4166', pantsLen: 'shorts',
    shoes: '#8a5230', ears: 1.0, freckles: true, glasses: 0, wrinkles: 0, stoop: 0, cardigan: null, mustache: 0,
  };
  const DAD = {
    name: 'dad', head: 52, headY: 470, shoulder: 402, hip: 246, shoulderW: 60, hipW: 46,
    armU: 90, armL: 84, leg: 240, limbW: 20, belly: 12,
    skin: '#e6b58c', blush: '#d7876d', hair: '#3b302a', hairStyle: 'receding',
    shirt: '#ece6d7', stripes: null, sleeve: '#7d8a5a', sleeveLen: 'long', pants: '#6a5843', pantsLen: 'long',
    shoes: '#3c2a20', ears: 0.9, freckles: false, glasses: 0.9, wrinkles: 0.35, stoop: 0, cardigan: '#7d8a5a', mustache: 1,
  };
  const MOM = {
    name: 'mom', head: 50, headY: 424, shoulder: 360, hip: 224, shoulderW: 52, hipW: 58,
    armU: 80, armL: 74, leg: 218, limbW: 17, belly: 14,
    skin: '#eebd96', blush: '#df866c', hair: '#4b2b1b', hairStyle: 'curly',
    shirt: '#d9a441', stripes: null, sleeve: '#d9a441', sleeveLen: 'short', pants: '#9d4b3a', pantsLen: 'skirt',
    shoes: '#5a3522', ears: 0.8, freckles: false, glasses: 0, wrinkles: 0.15, stoop: 0, cardigan: null, mustache: 0, apron: '#f4eee2',
  };
  const LADY = {
    name: 'lady', head: 47, headY: 484, shoulder: 418, hip: 264, shoulderW: 54, hipW: 50,
    armU: 86, armL: 80, leg: 258, limbW: 15, belly: 4,
    skin: '#efceb0', blush: '#e07a79', hair: '#8b4a2b', hairStyle: 'hat',
    shirt: '#2f4d5c', stripes: null, sleeve: '#2f4d5c', sleeveLen: 'long', pants: '#2f4d5c', pantsLen: 'dress',
    shoes: '#7a1f2a', ears: 0.7, freckles: false, glasses: 0, wrinkles: 0.2, stoop: 0, cardigan: null, mustache: 0,
    lipstick: '#b8283a', hatColor: '#6b1f2e', feather: '#d9a441', stole: '#dcc7a6', pearls: true,
  };
  // the boy grown old: the same tuft and ears, gone white
  const OLDBOY = Object.assign({}, BOY, {
    name: 'oldboy', head: 52, headY: 452, shoulder: 386, hip: 234, shoulderW: 54, hipW: 44,
    armU: 86, armL: 80, leg: 228, limbW: 18, belly: 10,
    skin: '#e6b792', hair: '#eeede8', shirt: '#dde3ea', stripes: '#a4b6c8', sleeve: '#8a6f55', sleeveLen: 'long',
    pants: '#4a4f5c', pantsLen: 'long', freckles: false, glasses: 1, wrinkles: 1, stoop: 0.35, cardigan: '#8a6f55',
  });
  const OLDDAD = Object.assign({}, DAD, { name: 'olddad', hair: '#ebeae4', skin: '#e2b490', wrinkles: 1.2, stoop: 0.55, cardigan: '#6e7152', sleeve: '#6e7152' });

  // blend two people: numbers lerp, colours mix, everything else switches at u = 0.5
  function blend(A, B, u) {
    const out = {};
    for (const k of new Set([...Object.keys(A), ...Object.keys(B)])) {
      const a = A[k], b = B[k];
      if (typeof a === 'number' && typeof b === 'number') out[k] = lerp(a, b, u);
      else if (typeof a === 'string' && typeof b === 'string' && a[0] === '#' && b[0] === '#') out[k] = mix(a, b, u);
      else if ((a == null || a === 0) && typeof b === 'string' && b[0] === '#') out[k] = u < 0.5 ? a : b;
      else out[k] = u < 0.5 ? (a ?? b) : (b ?? a);
    }
    return out;
  }

  // ---------- poses ----------
  // arms: [shoulder, elbow], radians from hanging straight down, + = OUTWARD on that side (front view).
  // liftL / liftR: 0..1 raises that foot (a step). lean: tilt of the body. crouch: 0..1.
  const STAND = { lean: 0, headTilt: 0, armL: [0.14, 0.12], armR: [0.14, 0.12], liftL: 0, liftR: 0, squash: 0, crouch: 0, bob: 0 };
  function walk(phase, amt = 1) {                 // a front-view paper-doll walk: alternate steps + bob + sway
    const s = Math.sin(phase * TAU);
    return {
      lean: 0, headTilt: 0.03 * s * amt, squash: 0, crouch: 0,
      liftL: Math.max(0, s) * amt, liftR: Math.max(0, -s) * amt,
      armL: [0.16 + 0.22 * s * amt, 0.3], armR: [0.16 - 0.22 * s * amt, 0.3],
      bob: Math.abs(Math.cos(phase * TAU)) * 7 * amt, sway: 0.025 * s * amt,
    };
  }
  const poseMix = (A, B, u) => {
    const o = {}; for (const k of new Set([...Object.keys(A), ...Object.keys(B)])) {
      const a = A[k] ?? B[k], b = B[k] ?? A[k];
      o[k] = Array.isArray(a) ? a.map((v, i) => lerp(v, b[i], u)) : typeof a === 'number' ? lerp(a, b, u) : (u < .5 ? a : b);
    } return o;
  };

  // ---------- faces (ink on paper) ----------
  // face: {eyes:'open'|'closed'|'wide'|'squint'|'happy', look:[dx,dy], brows -1 angry .. +1 worried,
  //        mouth:'smile'|'grin'|'o'|'flat'|'frown'|'wobble'|'open'|'pout', blush 0..1, turn -1..1, tears 0..1}
  function blinking(key, t) {
    const period = 2.6 + hash01(key, 1) * 2.4, ph = hash01(key, 2) * period;
    return ((t + ph) % period) < 0.11;
  }
  function drawFace(ctx, P, f, hx, hy, R, t, key) {
    const ink = INK(), turn = f.turn ?? 0, fx = hx + turn * R * 0.3, look = f.look ?? [0, 0];
    const eyeDX = R * 0.33, eyeY = hy + R * 0.02;
    const eyes = (blinking(key, t) && f.eyes !== 'closed' && f.eyes !== 'happy') ? 'closed' : (f.eyes ?? 'open');
    const lw = R * 0.055;
    for (const side of [-1, 1]) {
      const ex = fx + side * eyeDX * (1 - turn * side * 0.18);
      if (eyes === 'closed' || eyes === 'happy') {
        const up = eyes === 'happy' ? -1 : 1;
        inkLine(ctx, [[ex - R * .11, eyeY], [ex, eyeY + up * R * .06], [ex + R * .11, eyeY]], { w: lw, key: key + 'ec' + side, t, amp: .4, passes: 1 });
      } else {
        const k = eyes === 'wide' ? 1.3 : eyes === 'squint' ? .5 : 1;
        if (eyes === 'wide') wash(ctx, ellipsePts(ex, eyeY, R * .14, R * .17, 16), '#fbf7ee', { key: key + 'ew' + side, t, amp: .3, tex: false });
        wash(ctx, ellipsePts(ex + look[0] * R * .07, eyeY + look[1] * R * .06, R * .068 * k, R * .092 * k, 12), ink, { key: key + 'e' + side, t, amp: .25, tex: false });
        wash(ctx, ellipsePts(ex + look[0] * R * .07 - R * .022, eyeY + look[1] * R * .06 - R * .03, R * .02, R * .02, 6), '#fffaf0', { key: key + 'eh' + side, t, amp: .1, tex: false });
      }
      const b = f.brows ?? 0, by = eyeY - R * (0.27 + (eyes === 'wide' ? .07 : 0));
      const inner = [fx + side * eyeDX * .42, by - b * R * .09], outer = [fx + side * eyeDX * 1.3, by + b * R * .05 + R * .02];
      inkLine(ctx, [inner, [lerp(inner[0], outer[0], .5), lerp(inner[1], outer[1], .5) - R * .03], outer], { w: lw * 1.1, key: key + 'b' + side, t, amp: .4, passes: 1 });
    }
    inkLine(ctx, [[fx + R * .01, hy + R * .1], [fx + R * .07 + turn * R * .07, hy + R * .23], [fx - R * .03, hy + R * .25]], { w: lw * .8, key: key + 'n', t, amp: .35, passes: 1 });
    const bl = f.blush ?? 0.4;
    for (const side of [-1, 1]) wash(ctx, ellipsePts(fx + side * R * .52, hy + R * .26, R * .17, R * .11, 14), rgba(P.blush, .42 * bl), { key: key + 'bl' + side, t, amp: .4, tex: false });
    if (P.freckles) { const r = E.rng(key + 'fr'); for (let i = 0; i < 8; i++) { const side = i % 2 ? 1 : -1; wash(ctx, ellipsePts(fx + side * R * (.3 + r() * .24), hy + R * (.12 + r() * .12), R * .02, R * .02, 5), '#b8754e', { key: key + 'f' + i, t, amp: .1, tex: false }); } }
    if (P.mustache) paperShape(ctx, [[fx - R * .36, hy + R * .42], [fx - R * .06, hy + R * .3], [fx + R * .06, hy + R * .3], [fx + R * .36, hy + R * .42], [fx + R * .2, hy + R * .47], [fx, hy + R * .4], [fx - R * .2, hy + R * .47]], P.hair, { key: key + 'mu', t, sh: .4, blur: 3, sx: 1, sy: 2 });
    const my = hy + R * .46, mw = R * .25, m = f.mouth ?? 'smile', lip = P.lipstick ?? ink;
    const line = (pts, k2) => inkLine(ctx, pts, { w: lw * 1.1, key: key + k2, t, amp: .35, passes: 1, color: lip });
    if (m === 'smile') line([[fx - mw, my - R * .04], [fx, my + R * .07], [fx + mw, my - R * .04]], 'm');
    else if (m === 'frown') line([[fx - mw * .8, my + R * .07], [fx, my - R * .02], [fx + mw * .8, my + R * .07]], 'm');
    else if (m === 'flat') line([[fx - mw * .65, my + R * .01], [fx + mw * .65, my]], 'm');
    else if (m === 'pout') line([[fx - mw * .35, my + R * .03], [fx, my - R * .02], [fx + mw * .35, my + R * .03]], 'm');
    else if (m === 'wobble') line([[fx - mw * .8, my + R * .03], [fx - mw * .3, my - R * .02], [fx + mw * .2, my + R * .05], [fx + mw * .8, my]], 'm');
    else {
      const pts = m === 'o' ? ellipsePts(fx, my + R * .04, R * .09, R * .12, 12)
        : m === 'grin' ? [[fx - mw, my - R * .05], [fx + mw, my - R * .05], [fx + mw * .6, my + R * .13], [fx, my + R * .18], [fx - mw * .6, my + R * .13]]
          : ellipsePts(fx, my + R * .05, mw * .7, R * .15, 14);
      wash(ctx, pts, '#6b2a22', { key: key + 'mm', t, amp: .3, tex: false }); inkPoly(ctx, pts, { w: lw * .9, key: key + 'mo', t, amp: .3, passes: 1 });
      if (m === 'grin') wash(ctx, [[fx - mw * .82, my - R * .04], [fx + mw * .82, my - R * .04], [fx + mw * .55, my + R * .035], [fx - mw * .55, my + R * .035]], '#fbf7ee', { key: key + 'tt', t, amp: .2, tex: false });
    }
    if (P.wrinkles > 0) {
      const a = clamp(P.wrinkles) * .75, w2 = lw * .6;
      for (const side of [-1, 1]) {
        inkLine(ctx, [[fx + side * R * .5, eyeY - R * .02], [fx + side * R * .62, eyeY + R * .05]], { w: w2, key: key + 'wr' + side, t, amp: .3, passes: 1, alpha: a });
        inkLine(ctx, [[fx + side * R * .22, hy + R * .26], [fx + side * R * .33, hy + R * .47]], { w: w2, key: key + 'wn' + side, t, amp: .3, passes: 1, alpha: a * .8 });
      }
      inkLine(ctx, [[fx - R * .24, hy - R * .55], [fx + R * .24, hy - R * .56]], { w: w2, key: key + 'wf', t, amp: .4, passes: 1, alpha: a * .7 });
      inkLine(ctx, [[fx - R * .18, hy - R * .64], [fx + R * .2, hy - R * .65]], { w: w2, key: key + 'wf2', t, amp: .4, passes: 1, alpha: a * .5 });
    }
    if (P.glasses > 0) {
      const ga = clamp(P.glasses);
      for (const side of [-1, 1]) inkPoly(ctx, ellipsePts(fx + side * eyeDX, eyeY, R * .21, R * .17, 18), { w: lw * .85, key: key + 'g' + side, t, amp: .3, passes: 1, alpha: ga });
      inkLine(ctx, [[fx - eyeDX + R * .21, eyeY - R * .03], [fx + eyeDX - R * .21, eyeY - R * .03]], { w: lw * .8, key: key + 'gb', t, amp: .2, passes: 1, alpha: ga });
    }
    if (f.tears > 0) for (const side of [-1, 1]) {
      const d = (t * 1.25 + (side > 0 ? .5 : 0)) % 1;
      wash(ctx, ellipsePts(fx + side * eyeDX, eyeY + R * (.14 + d * .5), R * .045, R * .075, 8), rgba('#86bfe6', f.tears * (1 - d)), { key: key + 'te' + side, t, amp: .2, tex: false });
    }
  }

  function drawHair(ctx, P, hx, hy, R, t, key, back, sh) {
    const hs = P.hairStyle, O = (k) => ({ key: key + k, t, sh, blur: 6, sx: 2, sy: 3 });
    if (back) {
      if (hs === 'curly') {
        const pts = []; for (let i = 0; i < 20; i++) { const a = Math.PI * .92 + i / 19 * Math.PI * 1.16; const rr = R * (1.24 + .09 * Math.sin(i * 2.7)); pts.push([hx + Math.cos(a) * rr, hy - R * .05 + Math.sin(a) * rr]); }
        pts.push([hx + R * 1.12, hy + R * .6], [hx - R * 1.12, hy + R * .6]);
        paperShape(ctx, pts, P.hair, O('hb'));
      }
      return;
    }
    if (hs === 'tuft') {
      const cap = []; for (let i = 0; i <= 16; i++) { const a = Math.PI * 1.0 + i / 16 * Math.PI; const rr = R * (1.05 + .05 * Math.sin(i * 3.1)); cap.push([hx + Math.cos(a) * rr, hy - R * .02 + Math.sin(a) * rr]); }
      cap.push([hx + R * .92, hy - R * .22], [hx + R * .62, hy - R * .42], [hx + R * .3, hy - R * .36], [hx, hy - R * .5], [hx - R * .38, hy - R * .38], [hx - R * .7, hy - R * .46], [hx - R * .98, hy - R * .18]);
      paperShape(ctx, cap, P.hair, O('h'));
      const sway = noise1(t * .7, key + 'tf') * .3 + (P.tuftSway ?? 0);
      const bx = hx + R * .12, by = hy - R * 1.0;
      paperShape(ctx, [[bx - R * .13, by + R * .08], [bx - R * .06 + sway * R * .2, by - R * .36], [bx + R * .14 + sway * R * .45, by - R * .58], [bx + R * .32 + sway * R * .52, by - R * .46], [bx + R * .18 + sway * R * .3, by - R * .32], [bx + R * .12, by + R * .06]], P.hair, O('tu'));
    } else if (hs === 'receding') {
      for (const side of [-1, 1]) paperShape(ctx, [[hx + side * R * 1.0, hy - R * .05], [hx + side * R * .92, hy - R * .62], [hx + side * R * .56, hy - R * .9], [hx + side * R * .68, hy - R * .55], [hx + side * R * 1.06, hy + R * .25]], P.hair, O('hs' + side));
    } else if (hs === 'curly') {
      const top = []; for (let i = 0; i < 18; i++) { const a = Math.PI + i / 17 * Math.PI; const rr = R * (1.13 + .1 * Math.abs(Math.sin(i * 1.9))); top.push([hx + Math.cos(a) * rr, hy - R * .1 + Math.sin(a) * rr]); }
      top.push([hx + R * .72, hy - R * .52], [hx, hy - R * .7], [hx - R * .72, hy - R * .52]);
      paperShape(ctx, top, P.hair, O('h'));
    } else if (hs === 'hat') {
      paperShape(ctx, [[hx - R * 1.05, hy - R * .5], [hx - R * .96, hy - R * .95], [hx - R * .4, hy - R * 1.2], [hx + R * .5, hy - R * 1.18], [hx + R * 1.0, hy - R * .9], [hx + R * 1.1, hy - R * .5]], P.hair, O('h'));
      const sw = noise1(t * 1.1, key + 'fe') * .3;
      paperStrip(ctx, [[hx + R * .45, hy - R * 1.25], [hx + R * 1.05 + sw * R * .3, hy - R * 1.95], [hx + R * 1.6 + sw * R * .6, hy - R * 2.15]], R * .3, R * .06, P.feather, O('fea'));
      paperShape(ctx, [[hx - R * .86, hy - R * .72], [hx - R * .76, hy - R * 1.36], [hx, hy - R * 1.56], [hx + R * .76, hy - R * 1.36], [hx + R * .86, hy - R * .72]], P.hatColor, O('crown'));
      paperShape(ctx, ellipsePts(hx, hy - R * .74, R * 1.6, R * .27, 26), P.hatColor, O('brim'));
    }
  }

  // ---------- the person ----------
  // o: {x, y, s, flip, t, key, pose, face, sh (on-screen scale for shadows), holding(ctx, handL, handR)}
  function person(ctx, P, o) {
    const t = o.t ?? 0, key = o.key ?? P.name, s = o.s ?? 1, sh = o.sh ?? s;
    const pose = Object.assign({}, STAND, o.pose || {}), face = o.face || {};
    const breathe = Math.sin(t * TAU / 3.4 + hash01(key) * 6) * 0.012;
    const PO = (k, extra) => Object.assign({ key: key + k, t, sh, ink: INK(), lw: 2.1, tex: 0.38 }, extra || {});
    ctx.save();
    ctx.translate(o.x ?? 0, (o.y ?? 0) - (pose.bob ?? 0) * s); ctx.scale(s * (o.flip ?? 1), s);
    ctx.rotate(pose.sway ?? 0);
    const sq = pose.squash ?? 0; ctx.scale(1 + sq * 0.14, 1 - sq * 0.14 + breathe);
    const crouch = pose.crouch ?? 0, drop = P.hip * crouch * .35;
    const hipY = -P.hip + drop, shY = -P.shoulder + drop, stoop = P.stoop ?? 0;

    // legs: paper strips hip -> knee -> ankle; a lifted foot rises and its knee bends outward
    const legC = P.pantsLen === 'long' ? P.pants : P.skin, lw0 = P.limbW * (P.pantsLen === 'long' ? 1.45 : 1.05);
    for (const side of [-1, 1]) {
      const lift = side < 0 ? pose.liftL : pose.liftR, hx0 = side * P.hipW * .5;
      const footY = -lift * P.leg * .22, kneeOut = side * (P.leg * .08 * lift + crouch * P.leg * .12);
      const knee = [hx0 + kneeOut, lerp(hipY, footY, .5) - lift * 6], foot = [hx0 + side * 2, footY - 4];
      paperStrip(ctx, [[hx0, hipY + 6], knee, foot], lw0, lw0 * .82, legC, PO('leg' + side));
      paperShape(ctx, [[foot[0] - 11 - (P.limbW - 13), foot[1] - 6], [foot[0] + 12, foot[1] - 7], [foot[0] + 17 + side * 3, foot[1] + 3], [foot[0] - 13 - (P.limbW - 13), foot[1] + 5]], P.shoes, PO('sh' + side));
    }
    ctx.save(); ctx.translate(0, hipY); ctx.rotate((pose.lean ?? 0) + stoop * 0.12); ctx.translate(0, -hipY);
    // lower garment
    if (P.pantsLen === 'shorts') paperShape(ctx, [[-P.hipW - 3, hipY - 10], [P.hipW + 3, hipY - 10], [P.hipW + 8, hipY + 34], [5, hipY + 37], [0, hipY + 20], [-5, hipY + 37], [-P.hipW - 8, hipY + 34]], P.pants, PO('pa'));
    else if (P.pantsLen === 'long') paperShape(ctx, [[-P.hipW - 3, hipY - 10], [P.hipW + 3, hipY - 10], [P.hipW + 6, hipY + 34], [-P.hipW - 6, hipY + 34]], P.pants, PO('pa'));
    else paperShape(ctx, [[-P.hipW * .95, hipY - 34], [P.hipW * .95, hipY - 34], [P.hipW * 1.55, hipY + P.leg * .72], [0, hipY + P.leg * .76], [-P.hipW * 1.55, hipY + P.leg * .72]], P.pants, PO('sk'));
    // torso
    const b = P.belly, midY = (shY + hipY) / 2;
    const torso = [[-P.shoulderW, shY + 8], [-P.shoulderW * .6, shY], [P.shoulderW * .6, shY], [P.shoulderW, shY + 8], [P.shoulderW + b * .5, midY], [P.hipW + b, hipY - 6], [0, hipY + 4], [-P.hipW - b, hipY - 6], [-P.shoulderW - b * .5, midY]];
    const body = P.cardigan || P.shirt;
    const tq = paperShape(ctx, torso, body, PO('to'));
    if (P.stripes && !P.cardigan) {
      ctx.save(); ctx.beginPath(); ctx.moveTo(tq[0][0], tq[0][1]); for (const p of tq) ctx.lineTo(p[0], p[1]); ctx.closePath(); ctx.clip();
      const n = 5, gap = (hipY - shY) / n;
      for (let i = 0; i < n; i++) wash(ctx, [[-P.shoulderW - 20, shY + 16 + i * gap], [P.shoulderW + 20, shY + 13 + i * gap], [P.shoulderW + 20, shY + 16 + i * gap + gap * .44], [-P.shoulderW - 20, shY + 19 + i * gap + gap * .44]], P.stripes, { key: key + 'st' + i, t, amp: .8, tex: .5 });
      ctx.restore();
    }
    if (P.cardigan) {                              // the shirt shows through a V; three buttons
      const v = [[-P.shoulderW * .42, shY + 2], [P.shoulderW * .42, shY + 2], [0, lerp(shY, hipY, .55)]];
      paperShape(ctx, v, P.shirt, PO('v', { shadow: false }));
      if (P.stripes) { ctx.save(); ctx.beginPath(); ctx.moveTo(v[0][0], v[0][1]); ctx.lineTo(v[1][0], v[1][1]); ctx.lineTo(v[2][0], v[2][1]); ctx.closePath(); ctx.clip(); for (let i = 0; i < 4; i++) wash(ctx, [[-60, shY + 8 + i * 22], [60, shY + 8 + i * 22], [60, shY + 18 + i * 22], [-60, shY + 18 + i * 22]], P.stripes, { key: key + 'vs' + i, t, amp: .5 }); ctx.restore(); }
      for (let i = 0; i < 3; i++) wash(ctx, ellipsePts(P.shoulderW * .06, lerp(shY, hipY, .62) + i * (hipY - shY) * .12, P.limbW * .18, P.limbW * .18, 8), '#3a2a1e', { key: key + 'bt' + i, t, amp: .2, tex: false });
    }
    if (P.apron) {
      paperShape(ctx, [[-P.hipW * .78, shY + 38], [P.hipW * .78, shY + 38], [P.hipW * 1.12, hipY + 70], [-P.hipW * 1.12, hipY + 70]], P.apron, PO('ap'));
      const r = E.rng(key + 'dots'); for (let i = 0; i < 16; i++) wash(ctx, ellipsePts(lerp(-P.hipW * .75, P.hipW * .75, r()), lerp(shY + 58, hipY + 58, r()), 4.5, 4.5, 7), '#c8412e', { key: key + 'd' + i, t, amp: .2, tex: false });
    }
    // arms (in front of the torso): a sleeve piece, the forearm strip, a mitten hand with a thumb
    const hands = [];
    for (const [side, a] of [[-1, pose.armL], [1, pose.armR]]) {
      const sx = side * (P.shoulderW - 7), sy = shY + 14;
      const el = [sx + side * Math.sin(a[0]) * P.armU, sy + Math.cos(a[0]) * P.armU];
      const hd = [el[0] + side * Math.sin(a[0] + a[1]) * P.armL, el[1] + Math.cos(a[0] + a[1]) * P.armL];
      if (P.sleeveLen === 'long') paperStrip(ctx, [[sx, sy], el, [lerp(el[0], hd[0], .85), lerp(el[1], hd[1], .85)]], P.limbW * 1.7, P.limbW * 1.3, P.sleeve, PO('arm' + side));
      else {
        paperStrip(ctx, [[sx, sy], el, hd], P.limbW * 1.05, P.limbW * .9, P.skin, PO('arm' + side));
        paperStrip(ctx, [[sx, sy - 2], [lerp(sx, el[0], .42), lerp(sy, el[1], .42)]], P.limbW * 1.75, P.limbW * 1.5, P.sleeve, PO('sl' + side));
      }
      const ang = Math.atan2(hd[1] - el[1], hd[0] - el[0]);
      const hand = ellipsePts(hd[0] + Math.cos(ang) * P.limbW * .35, hd[1] + Math.sin(ang) * P.limbW * .35, P.limbW * .8, P.limbW * .72, 12, ang);
      paperShape(ctx, hand, P.skin, PO('hd' + side));
      paperShape(ctx, ellipsePts(hd[0] + Math.cos(ang - side * 1.2) * P.limbW * .6, hd[1] + Math.sin(ang - side * 1.2) * P.limbW * .6, P.limbW * .32, P.limbW * .22, 8, ang - side * 1.2), P.skin, PO('th' + side, { shadow: false }));
      hands.push([hd[0] + Math.cos(ang) * P.limbW * .45, hd[1] + Math.sin(ang) * P.limbW * .45]);
    }
    if (P.stole) paperShape(ctx, [[-P.shoulderW - 12, shY + 32], [-P.shoulderW + 4, shY - 8], [P.shoulderW - 4, shY - 8], [P.shoulderW + 12, shY + 32], [P.shoulderW * .4, shY + 46], [-P.shoulderW * .4, shY + 46]], P.stole, PO('stole'));
    if (P.pearls) for (let i = 0; i < 9; i++) wash(ctx, ellipsePts(-P.shoulderW * .45 + i * P.shoulderW * .11, shY + 14 + Math.sin(i / 8 * Math.PI) * 18, 4, 4, 7), '#f8f3ea', { key: key + 'p' + i, t, amp: .1, tex: false });
    // head
    const R = P.head, hx = 0, hy = -P.headY + drop + stoop * 22;
    ctx.save(); ctx.translate(hx, hy + R * .95); ctx.rotate(pose.headTilt ?? 0); ctx.translate(-hx, -(hy + R * .95));
    drawHair(ctx, P, hx, hy, R, t, key, true, sh);
    paperShape(ctx, [[-P.limbW * .75, hy + R * .7], [P.limbW * .75, hy + R * .7], [P.limbW * .85, shY + 12], [-P.limbW * .85, shY + 12]], mix(P.skin, '#a0674a', .15), PO('neck', { shadow: false }));
    for (const side of [-1, 1]) paperShape(ctx, ellipsePts(hx + side * R * 1.0 * (1 - (face.turn ?? 0) * side * .08), hy + R * .06, R * .22 * P.ears, R * .3 * P.ears, 12), P.skin, PO('ear' + side));
    paperShape(ctx, ellipsePts(hx, hy, R, R * 1.03, 30), P.skin, PO('head'));
    drawHair(ctx, P, hx, hy, R, t, key, false, sh);
    drawFace(ctx, P, face, hx, hy, R, t, key);
    ctx.restore();
    if (o.holding) o.holding(ctx, hands[0], hands[1]);
    ctx.restore();
    ctx.restore();
    return hands;
  }

  window.CAST = { BOY, DAD, MOM, LADY, OLDBOY, OLDDAD, blend, person, STAND, walk, poseMix };
})();

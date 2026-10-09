# Animation guide (for every agent that writes a chapter)

Read this whole file before writing code. It is the contract that lets several agents build one
film in parallel without the characters, the paper or the timing drifting apart.

## 1. The contract

- A chapter is one file, `src/ch/<name>.js`, an IIFE that calls `E.addShot({name, t0, t1, fn})`
  one or more times. Only edit your own file. If a shared helper is missing, write it privately
  inside your IIFE. If you find a bug in a shared file (`core.js`, `cast.js`, your world module), report
  it in your final message; do not edit it.
- `fn(ctx, t, lt, dur, shot)` paints the ENTIRE 1920x1080 frame: background, everything, and a
  final `E.finish(ctx, t)`. `t` = film seconds, `lt` = seconds since the shot's t0, `dur` = length.
- **Pure function of t.** No `Math.random()`, no counters, no state kept between calls, no physics
  integrated frame by frame. Frames render in parallel and out of order. Use `E.rng(key)`,
  `E.hash01(key, i)`, `E.noise1(x, key)` and `E.boil(key, t)` for randomness.
- **Pre-roll and post-roll.** Your shot may be drawn at `lt < 0` (seen through a window while the
  camera flies in) and at `lt > dur` (seen while the camera pulls back out). Clamp: draw your
  opening state before 0 and your closing state after dur. Never throw on out-of-range `lt`.
- Budget: aim for under 250 ms per frame (the sheet prints ms). Hundreds of paper pieces are
  fine; thousands are not.

## 2. The look (cut paper + ink)

- Everything solid is a piece of paper: `E.paperShape(ctx, pts, color, o)` (flat colour, fibre
  texture, soft cast shadow, faint lit edge) or `E.paperStrip(ctx, path, w0, w1, color, o)` for
  limbs, stems, ribbons. Options: `key` (stable, unique per piece), `t`, `sh` (the piece's
  ON-SCREEN scale, because canvas shadows ignore the transform), `ink` (a colour for a thin ink
  edge), `lw`, `sharp: true` for architecture and furniture (straight cut edges, no rounding),
  `shadow: false`, `tex`, `alpha`, `blur/sx/sy` (shadow shape).
- Ink is for faces, small details, hatching, the red window frames: `E.inkLine`, `E.inkPoly`,
  `E.hatch`, `E.wash` (flat colour without shadow).
- Paper background: `E.paper(ctx, t)`; final pass: `E.finish(ctx, t, {grain, vignette, fade})`.
- Depth: layer your scene back-to-front; put near foreground objects in `E.plate(ctx, name, fn,
  {blur})` to blur them (depth of field). Light: `E.glow(ctx, x, y, r, colour, alpha)`.
- Palette: `FILM.pal` (paper, paperDark, ink, red, night, amber). Never pure black or pure white.
- Geometry helpers: `E.ellipsePts`, `E.rectPts(x,y,w,h,perSide)`, `E.roundRectPts`, `E.tx`.
- Time helpers: `E.seg(t, t0, t1, ease)` eased 0..1 progress, `E.keys(t, [[t,v],...])`,
  `E.spring(t, t0)`, `E.smoother`, `E.easeInOut`, `E.backOut`, `E.lerp`, `E.clamp`.
- Camera: `ctx.save(); E.applyCam(ctx, {x, y, z, r}); ...world...; ctx.restore();` with
  `E.drift(t, key)` added to x/y/r so no shot is ever dead-still.
- Hebrew text (rare, only where the storyboard says): `E.inkText(ctx, str, x, y, {size, font,
  reveal})`. Digits are isolated automatically. FrankRuehl has no Latin glyphs.

## 3. The cast (never draw a character yourself)

`CAST.person(ctx, CAST.BOY, {x, y, s, sh, t, key, pose, face, flip, holding})` draws a paper
puppet with its feet at (x, y). Characters: `BOY, DAD, MOM, LADY, OLDBOY, OLDDAD`;
`CAST.blend(A, B, u)` morphs one into another (the boy aging).

- `pose`: `{lean, headTilt, armL:[shoulder, elbow], armR:[...], liftL, liftR, crouch, squash,
  bob, sway}`. Arm angles are radians from hanging down, + = outward. `CAST.walk(phase, amt)`
  gives a paper-doll walk; `CAST.poseMix(A, B, u)` blends poses.
- `face`: `{eyes: open|closed|wide|squint|happy, look:[dx,dy], brows: -1 angry..+1 worried,
  mouth: smile|grin|o|flat|frown|wobble|open|pout, blush, turn: -1..1, tears: 0..1}`.
- Never snap a face or a pose: blend over 0.2-0.4 s with `poseMix` and eased values; change
  mouth shapes on a blink or a head move.
- `holding(ctx, handL, handR)` is called with the hand positions so a prop sits in a hand.
- `key` must be stable per character per shot (it seeds blinks and boil).

## 4. Your world module (the reference build's facade.js)

`facade.js` is the world module of the reference build (a street of windows); it is not shipped
with this skill. Write your own world module for your film and document its API here the same way.
The reference build's API, as an example:

`FAC.draw(ctx, t, cam, FAC.state(t, overrides), {world, fg, tree})` draws the whole street.
`FAC.enter(ctx, t, {t0, t1, win, next, cam0, state})` flies through window `win` into shot
`next`; `FAC.exit(ctx, t, {t0, t1, win, prev, cam1, state})` pulls back out. Windows are
`FAC.WINDOWS['f<floor>c<col>']`, and `FAC.WIDE` is the establishing camera.

## 5. The loop (do all of it)

1. Plan the beats with clock times; decide what the viewer must understand at each moment and
   how long that takes.
2. Write the code. Render stills of the key poses:
   `py <skill>/engine/render.py sheet --from <t0> --to <t1> --every 0.5 --cols 4 --out work/check/<name>_a.jpg`
   (run from the project root). Open the sheet with the Read tool and look hard.
3. Check: first and last frames; that motion reads across consecutive frames; that nothing is
   ever still for more than a second; transitions in and out; faces readable; composition
   (rule of thirds, a clear focal point, a big silhouette); nothing important cut by the frame.
4. Fix the worst thing. Repeat at least three rounds. Then render a clip and look at its sheet
   at 0.25 s spacing through the busiest part.

## 6. Never

Pure black or white. Neon or purple grades. Text explaining the picture. A static hold over one
second. A character drawn outside `CAST`. A cut without a motive. Copying a source book's
illustrations. `Math.random()`.

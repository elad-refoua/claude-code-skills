// config.js - per-film settings. Copy this file to src/config.js and edit it.
// studio.html loads core.js, timing.js, then this file, then every file in FILM.scripts in order.
window.FILM = {
  fps: 24,                 // render.py frames/clip read this; check_cuts.py and check_film.py take --fps
  dur: TIMING.dur,         // film length in seconds, from src/timing.js (written by build_timing.py)
  // palette: core.js reads paper and paperDark, cast.js reads ink, chapters read the rest.
  // These colours are placeholders: set your own in DESIGN.md and copy them here.
  pal: { paper: '#efe4cf', paperDark: '#a8865e', ink: '#231a15', red: '#c8412e', night: '#22303f', amber: '#e3a640' },
  fonts: ['64px "FrankRuehl"', '64px "David"'],   // loaded before the first frame is drawn
  scripts: ['cast.js', 'world.js', 'ch/c01.js'],  // relative to src/studio.html; your world module and chapters
  audio: '../work/mix.wav',                       // played by the studio's scrubber; the renderer ignores it
};

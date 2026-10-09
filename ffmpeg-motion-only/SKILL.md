---
name: ffmpeg-motion-only
description: Compress long screen recordings to only the moments with motion using ffmpeg's mpdecimate filter. Drops static frames; remaining frames re-timed to natural playback. Typical compression: 20 minutes of typing/streaming with long pauses → 2 minutes of pure action. Ideal for conference demos, training videos, screen-recording highlights.
---

# ffmpeg Motion-Only Edit

## When to use

A long screen recording has lots of "dead time" (waiting for LLM, reading
pauses, idle screen, processing spinners) interleaved with brief moments of
visible action (typing, streaming text, UI changes). You want to keep only
the action.

Triggers:
- "compress this video to just the motion parts"
- "remove static parts of the recording"
- "make this 20-min recording into ~2 min"
- "motion only edit"

## The recipe

```bash
ffmpeg -y \
  -ss <SKIP_INTRO_SECS> -i input.mp4 \
  -vf "mpdecimate=hi=400:lo=300:frac=0.05,setpts=N/FRAME_RATE/TB" \
  -an -c:v libx264 -crf 20 -preset slow -pix_fmt yuv420p -movflags +faststart \
  output_motion_only.mp4
```

What each piece does:
- `-ss N` — skip first N seconds of original (skips intro screens / launch)
- `mpdecimate` — drops frames that look too similar to the previous frame
  - `hi=400` — high threshold; frames above this difference are kept
  - `lo=300` — low threshold; frames below this are dropped
  - `frac=0.05` — fraction of macroblocks that must differ for "kept"
  - Lower `frac` = more frames kept = longer output
- `setpts=N/FRAME_RATE/TB` — re-time kept frames so they play at natural fps
  (without this, decimated frames would jump too fast)
- `-an` — strip audio (typically silent already; mux music after if needed)
- `crf 20 preset slow` — good visual quality, manageable file size

## Parameter tuning

| Goal | frac | Notes |
|------|------|-------|
| Very aggressive (only big changes) | 0.5 | Will look like blinks of action |
| Aggressive | 0.33 (default) | 20 min → 30s typical |
| Balanced — **recommended for demos** | 0.05 | 20 min → 2 min typical |
| Gentle | 0.02 | Keeps even subtle motion |

`hi`/`lo` rarely need adjusting. The defaults (`hi=64*12`, `lo=64*5`) are too
aggressive for screen recordings; the recipe above (400/300) is calibrated for
text-on-page motion.

## Verification

After running, check the output duration vs expected:
```bash
ffprobe -v error -show_entries format=duration \
  -of default=noprint_wrappers=1:nokey=1 output_motion_only.mp4
```

If too short (e.g. <30s from a 20-min source), `frac` is too aggressive.
If too long (>5 min), `frac` is too gentle.

## Combining with music

The output has no audio. To add background music:

```bash
ffmpeg -y \
  -i output_motion_only.mp4 \
  -i music.mp3 \
  -filter_complex "[1:a]volume=0.85,afade=t=in:st=0:d=1.5,afade=t=out:st=<DUR-4>:d=4[a]" \
  -map 0:v -map "[a]" \
  -c:v copy -c:a aac -b:a 192k -ar 44100 \
  -shortest \
  final_with_music.mp4
```

Volume 0.85 is a good default for ambient music under silent visual content.
`afade out` ends 4s before video end with a 4s fade.

## Why this beats variable-speed approaches

We tried building a Python script that parsed log timestamps to identify
motion vs static segments, then cut + reassembled with different `setpts`
factors per segment. That approach failed because:
- `setpts=PTS/N` with `-c:v libx264` produces stretched-frame outputs by default
- Concat with re-encode reset PTS
- Net result: video stayed at original duration

`mpdecimate` is purely frame-based and doesn't fight the encoder's frame-rate
assumptions. It's simpler AND more accurate (motion in the actual pixels, not
inferred from logs).

## Notes

- `mpdecimate` requires consistent resolution across the input — works perfectly
  for screen recordings, may struggle with shot changes in narrative video
- Audio is stripped (`-an`). If the source had audio you cared about, you'd
  need a different approach (variable speed via setpts, or manual editing)
- Two-pass encoding (`-pass 1` then `-pass 2`) gives slightly better quality
  but isn't necessary for talk demos

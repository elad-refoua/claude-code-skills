---
name: synth-typing-sounds
description: Procedurally synthesize keyboard typing sounds in pure Python (no external libraries beyond stdlib wave module). Each click is a bandpassed noise burst with sharp attack and low-mid body thump. Configurable rate, click length, and amplitude. Optional "gated" mode that places clicks only during specific time windows (e.g., when a parent is typing on screen, silent during agent streaming).
---

# Synthesize Typing Sounds

## When to use

User wants typing/keyboard click sounds for a video or audio track but doesn't
want to download/license a sound effect. Procedural synthesis gives:
- Zero licensing concerns
- Per-keystroke randomization (sounds natural, not loopy)
- Precise control over typing windows (start/stop per second)
- Tunable per-click pitch, length, and intensity

Triggers:
- "add typing sounds to this video"
- "fake keyboard sounds"
- "synthesize click sounds"
- "sound of typing for the demo"
- "קולות הקלדה"

## The core click sound

Each "click" is a stochastic bandpass-filtered noise burst:
- Center frequency: random 1800–3200 Hz (key-to-key variation)
- Bandpass Q: 6 (narrow, bell-like resonance)
- Envelope: exponential decay over 28-45 ms
- Body thump: 220 Hz sine pulse mixed at 0.18 amplitude for the underlying
  mechanical thud

Result: each click sounds like a distinct key, not a loop.

## Stdlib-only implementation (Python)

```python
import wave, struct, math, random

SAMPLE_RATE = 44100

def click_sound(length_ms=35, peak_amp=0.55):
    n = int(length_ms / 1000.0 * SAMPLE_RATE)
    center_hz = random.uniform(1800, 3200)
    omega = 2 * math.pi * center_hz / SAMPLE_RATE
    Q = 6.0
    alpha = math.sin(omega) / (2 * Q)
    cos_w = math.cos(omega)
    a0 = 1 + alpha
    a1 = -2 * cos_w
    a2 = 1 - alpha
    y1 = y2 = 0.0
    samples = []
    for i in range(n):
        env = math.exp(-i / (n * 0.18))
        x = random.uniform(-1, 1) * env * peak_amp
        y = (alpha * x - a1 * y1 - a2 * y2) / a0
        y2 = y1
        y1 = y
        samples.append(y)
    for i in range(int(n * 0.4)):
        env = math.exp(-i / (n * 0.08))
        samples[i] += 0.18 * env * math.sin(2 * math.pi * 220 / SAMPLE_RATE * i)
    return samples
```

## Continuous typing bed (all clicks throughout duration)

```python
DURATION = 125.0   # seconds
CLICKS_PER_SEC_AVG = 9

n_samples = int(DURATION * SAMPLE_RATE)
buf = [0.0] * n_samples

t = 0.0
while t < DURATION:
    dt = max(0.04, random.gauss(1.0 / CLICKS_PER_SEC_AVG, 0.05))
    t += dt
    if t >= DURATION: break
    click = click_sound(length_ms=random.randint(28, 45), peak_amp=random.uniform(0.40, 0.70))
    start = int(t * SAMPLE_RATE)
    for i, v in enumerate(click):
        if start + i < n_samples:
            buf[start + i] += v

# Normalize and write WAV (as in your standard wave write)
```

## Gated mode: typing sound ONLY during specific windows

This is the powerful pattern. Given a list of `(start_sec, end_sec, n_chars)`
typing windows, place ~1 click per character within each window with jittered
spacing. The rest of the buffer stays silent.

Use case from a demo video: video shows parent typing for ~5s then an AI assistant
streaming for ~7s, repeated 20 times. Typing sound should play during the 5s
typing portion only, NOT during the AI response streaming.

```python
typing_windows = [(start, end, n_chars), ...]  # in seconds

for win_start, win_end, n_chars in typing_windows:
    duration = win_end - win_start
    avg_gap = duration / max(1, n_chars)
    t = win_start
    for _ in range(n_chars):
        t += max(0.04, random.gauss(avg_gap, avg_gap * 0.3))
        if t >= win_end: break
        click = click_sound(...)
        start = int(t * SAMPLE_RATE)
        for i, v in enumerate(click):
            if start + i < n_samples:
                buf[start + i] += v
```

## Estimating the typing window from a chat log

If the screen recording captured a user typing N characters at a known rate,
the window is approximately:

```python
def estimate_typing_duration(text, ms_per_char=95, punct_pause_ms=275, thinking_chance=0.04, thinking_ms=650):
    chars = len(text)
    punct = sum(1 for c in text if c in '.,?!')
    base = chars * ms_per_char / 1000
    punct_pause = punct * punct_pause_ms / 1000
    thinking = chars * thinking_chance * thinking_ms / 1000
    pre_post = 0.5  # focus click + brief pause before send
    return base + punct_pause + thinking + pre_post
```

The default constants match a humanType pacing of 60-130ms per character
with punctuation extras and occasional thinking pauses.

## WAV write boilerplate

```python
with wave.open('typing_bed.wav', 'wb') as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(SAMPLE_RATE)
    for s in buf:
        wf.writeframes(struct.pack('<h', max(-32768, min(32767, int(s * 32767)))))
```

## Tuning knobs

| Knob | Effect |
|------|--------|
| `CLICKS_PER_SEC_AVG` higher | Faster typing feel |
| `peak_amp` higher | Louder, more aggressive |
| Center freq range (1800-3200) | Brighter / darker keys |
| `Q` higher | More ringing/bell-like |
| `length_ms` higher | Softer, more wood-like |
| Body thump amplitude (0.18) | More mechanical heft |

## Mux with video (silent input)

```bash
ffmpeg -y \
  -i video_silent.mp4 \
  -i typing_bed.wav \
  -filter_complex "[1:a]volume=0.7[a]" \
  -map 0:v -map "[a]" \
  -c:v copy -c:a aac -b:a 160k -ar 44100 \
  -shortest \
  video_with_typing.mp4
```

Volume 0.7 is comfortable for typing under a silent demo. 0.5-0.6 if there's
also music; 0.85-1.0 if typing is the only sound.

# -*- coding: utf-8 -*-
"""
Narration generator for a project submission video (the worked example: an AI study
aid used in an anatomy lab). Replace SEGMENTS with your own script.

Keep the script in ../01_script/ and copy each beat's spoken text into SEGMENTS below.
One MP3 per segment, so the assembly step can place each one at an exact offset.
That is also how the brief's "audio ducking" requirement is met: no narration
segment is ever scheduled over Scene 3's in-clip dialogue.

MANDATORY QC GATE (audio-producer skill): no audio is delivered un-QC'd.
  1. deterministic duration gate  - English narration runs ~13-16 chars/sec
  2. listen-QC every segment      - Gemini audio understanding, accept >= 4/5
  3. whole-file check             - done by the caller on the concatenated track
"""
import base64
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
import wave

sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, 'takes')
FINALDIR = HERE

API_KEY = os.environ.get('GEMINI_API_KEY')     # used by the listen-QC call below
if not API_KEY:
    raise SystemExit('Set GEMINI_API_KEY in the environment.')

sys.path.insert(0, os.path.expanduser('~/.claude/skills/audio-producer/scripts'))
from gemini_tts import synthesize, wav_to_mp3  # noqa: E402  the ONE TTS caller (audio-producer skill)

TTS_MODEL = 'gemini-3.8-flash-tts'   # was gemini-3.1-flash-tts-preview until 2026-09-24
QC_MODEL = 'gemini-2.5-flash'
VOICE = 'Erinome'          # clear, educational - matches an academic explainer

# English narration pace. Measured band for this voice at this tone is ~13-16 c/s;
# anything outside 9-22 is a truncation or a babble loop, not a stylistic difference.
MIN_CPS, MAX_CPS = 9.0, 22.0

SPEECH_DIR = (
    'Add micro-pauses (0.3-0.5s) between sentences. '
    'Vary pace naturally - slightly faster for lists, slower for key points. '
    'Speak numbers and abbreviations clearly and separately. '
    'Clear falling intonation at the end, no clipping. '
)

TONE = ('Clear, confident academic explainer. A student presenting a class project: '
        'engaged and precise, never salesy, never breathless.')

# text  = what is spoken (abbreviations written the way they must be pronounced)
# label = the human-readable line, used for QC comparison and the transcript check
SEGMENTS = [
    dict(id='s1', scene='Scene 1 - The problem',
         text="As medical students, we face a problem no textbook prepares "
              "us for. Real tissue is monochromatic. Nerves, vessels and fascia look alike. The "
              "colourful atlas on the table does not match what is in front of us."),
    dict(id='s2', scene='Scene 2 - No instructor',
         text="There is one instructor for dozens of students. Raising your hand can mean waiting "
              "ten minutes for a thirty-second answer, and losing your place in the dissection."),
    dict(id='s3', scene='Scene 3 - The solution',
         text="Gloved hands cannot touch a screen without breaking sterility. So we built an "
              "A I guide for the dissection lab: a voice-operated visual question answering system on a "
              "tablet mounted above the table. The student speaks. She never touches anything."),
    dict(id='s4a', scene='Scene 4 - Demo part A',
         text="This is the actual prototype, built with a no-code app builder. The spoken question is "
              "captured in the browser and sent, with the specimen photograph, to a multimodal "
              "model, G P T five point four, under a strict instruction: use Latin anatomical "
              "nomenclature, and return a confidence score."),
    dict(id='s4b', scene='Scene 4 - Demo part B',
         # The number is read off the actual capture (94%), not assumed. Playwright
         # records video without page audio, so this line stays with what is
         # visibly on screen rather than promising speech the viewer will not hear.
         text="Ninety-four percent. Above the threshold. Musculus serratus anterior, with its "
              "region, its layer, and its clinical function."),
    dict(id='s4c', scene='Scene 4 - Demo part C',
         text="But when the model is unsure, it does not guess. Below eighty-five percent the "
              "system refuses, and sends the student to a human."),
    dict(id='s5', scene='Scene 5 - Resolution',
         # Measured from the capture's own session timeline: query submitted to
         # analysis complete is about thirty seconds. The earlier draft said
         # "in seconds", which the screen recording would have contradicted.
         text="About thirty seconds, instead of ten minutes. Her hands stay sterile, her train "
              "of thought holds, and she knows how much to trust the answer."),
    dict(id='s6', scene='Scene 6 - Honest limits',
         text="Three honest limitations. The prototype uploads images to cloud storage. A "
              "production version needs on-device processing and automatic deletion, to protect "
              "donor dignity and meet G D P R. The confidence score is the model's own estimate, "
              "not a validated measure. And this is a study aid: it never replaces a qualified "
              "instructor."),
]


def _post(url, payload, timeout=180):
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode('utf-8'),
        # The key travels in a header, never in the URL, so it cannot land in
        # proxy logs or in a traceback that prints the request URL.
        headers={'Content-Type': 'application/json', 'x-goog-api-key': API_KEY})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode('utf-8'))


def generate(seg, take, outdir):
    """One TTS take. Returns (mp3_path, duration_seconds) or (None, 0)."""
    # Through the audio-producer skill's gemini_tts module (2026-09-24): 3.8 returns a finished
    # WAV and takes delivery instructions as a separate style, so the text is sent verbatim and
    # SPEECH_DIR + TONE travel as the style. A blocked prompt raises a RuntimeError that says
    # BLOCKED - with the blockReason on the 3.1 endpoint, as "no audio ... possibly BLOCKED" on
    # 3.8 (Gemini TTS refuses text that reads as voice-cloning intent). Rephrase the line; a
    # definite block is not a transient failure.
    for attempt in range(3):
        try:
            wav_bytes, secs = synthesize(seg['text'], voice=VOICE, style=SPEECH_DIR + TONE,
                                         model=TTS_MODEL)
            mp3 = os.path.join(outdir, f"{seg['id']}_t{take}.mp3")
            wav_to_mp3(wav_bytes, mp3)
            return mp3, secs
        except Exception as e:
            print(f"    attempt {attempt+1} failed: {e}", flush=True)
            time.sleep(6)
    return None, 0


def listen_qc(seg, mp3):
    """Gemini listens to the take and rates it. Returns (score, problems)."""
    audio_b64 = base64.b64encode(open(mp3, 'rb').read()).decode()
    prompt = (
        "You are checking a text-to-speech take for an academic project video.\n"
        "EXPECTED SCRIPT (exact):\n" + seg['text'] + "\n\n"
        "Listen to the audio. Reply ONLY with JSON: "
        '{"score": <1-5>, "problems": "<short>"}\n'
        "score 5 = clean English narration, every word of the expected script present and "
        "correctly pronounced, natural pace.\n"
        "Deduct hard for: gibberish or babble, repeated/looped words, truncation, missing or "
        "extra sentences, wrong language, the tone/stage directions being read aloud, "
        "mispronounced abbreviations, or robotic clipping."
    )
    url = ('https://generativelanguage.googleapis.com/v1beta/models/'
           f'{QC_MODEL}:generateContent')
    payload = {
        'contents': [{'parts': [
            {'inlineData': {'mimeType': 'audio/mp3', 'data': audio_b64}},
            {'text': prompt}]}],
        'generationConfig': {'temperature': 0.1, 'maxOutputTokens': 4000}
    }
    for attempt in range(3):
        try:
            result = _post(url, payload, timeout=150)
            if 'candidates' not in result:   # blocked: promptFeedback and no candidates
                return 0, 'QC BLOCKED: ' + str(
                    result.get('promptFeedback', {}).get('blockReason', 'no candidates'))
            parts = result['candidates'][0]['content']['parts']
            txt = ''.join(p.get('text', '') for p in parts)
            m = re.search(r'\{.*\}', txt, re.S)
            if m:
                d = json.loads(m.group(0))
                return int(d.get('score', 0)), str(d.get('problems', ''))
            raise RuntimeError('no JSON in QC reply: ' + txt[:120])
        except Exception as e:
            print(f"    QC attempt {attempt+1} failed: {e}", flush=True)
            time.sleep(5)
    return 0, 'QC INFRASTRUCTURE FAILED'


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    only = sys.argv[sys.argv.index('--only') + 1:] if '--only' in sys.argv else None
    segments = [s for s in SEGMENTS if not only or s['id'] in only]

    report = []
    for i, seg in enumerate(segments, 1):
        print(f"[{i}/{len(segments)}] {seg['id']}  ({seg['scene']})", flush=True)
        best = None
        for take in range(1, 4):
            mp3, dur = generate(seg, take, OUTDIR)
            if not mp3:
                continue
            cps = len(seg['text']) / dur if dur else 0
            if not (MIN_CPS <= cps <= MAX_CPS):
                print(f"    take {take}: REJECT on duration gate "
                      f"({dur:.1f}s, {cps:.1f} chars/sec)", flush=True)
                time.sleep(4)
                continue
            score, problems = listen_qc(seg, mp3)
            print(f"    take {take}: {dur:.1f}s, {cps:.1f} c/s, QC {score}/5  {problems[:70]}",
                  flush=True)
            if best is None or score > best['score']:
                best = dict(path=mp3, dur=dur, cps=cps, score=score, problems=problems, take=take)
            if score >= 5:
                break
            time.sleep(4)

        if not best:
            print(f"    !! {seg['id']} produced no usable take", flush=True)
            report.append(dict(id=seg['id'], status='FAILED'))
            continue

        final = os.path.join(FINALDIR, f"{seg['id']}.mp3")
        subprocess.run(['ffmpeg', '-y', '-i', best['path'], '-codec:a', 'libmp3lame',
                        '-qscale:a', '2', final], capture_output=True)
        status = 'OK' if best['score'] >= 4 else 'BELOW_FLOOR'
        print(f"    -> {seg['id']}.mp3  take {best['take']}, QC {best['score']}/5  [{status}]",
              flush=True)
        report.append(dict(id=seg['id'], scene=seg['scene'], status=status,
                           duration=round(best['dur'], 2), cps=round(best['cps'], 1),
                           qc_score=best['score'], problems=best['problems'],
                           chars=len(seg['text'])))
        time.sleep(4)

    json.dump(report, open(os.path.join(FINALDIR, 'qc_report.json'), 'w', encoding='utf-8'),
              indent=2, ensure_ascii=False)
    total = sum(r.get('duration', 0) for r in report)
    print(f"\nTotal narration audio: {total:.1f}s across {len(report)} segments")
    bad = [r for r in report if r['status'] != 'OK']
    print("ALL SEGMENTS PASSED" if not bad else f"NEEDS ATTENTION: {[r['id'] for r in bad]}")


if __name__ == '__main__':
    main()

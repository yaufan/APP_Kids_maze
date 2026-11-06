"""迷宮小冒險 (Little Maze Adventure): every sound in the app, made here from
sine waves and noise, so every one is ours: nothing recorded, nothing
downloaded, and every tune written for this app.

- Music (WAV, 16,000 Hz): a tune for the world map, one for each of the six
  worlds, and a lullaby for rest time. Each has its own metre, key and
  instruments, so a child can hear where they are, and each is unlike the
  sibling apps' tunes:
  - music_home: a friendly stroll with 土豆 (4/4, G): a clay ocarina over a
    walking bass, a banjo on two and four.
  - music_garden (the bee): a sunny spring lilt (6/8, D): a recorder over a
    rippling harp; a glockenspiel joins in the second half.
  - music_tunnel (土豆's tunnels): cosy and a little sneaky (4/4, E dorian):
    a bouncy bassoon, a low marimba, wooden pats like a little spade,
    crystal gems glinting, soft cave echoes.
  - music_sea (the fish): a sunny calypso (4/4, F, three-three-two): steel
    pans, a bouncing bass, bubbles at the end of each phrase.
  - music_city (the little bus): a happy shuffle (4/4, A): an accordion, a
    felt piano, soft claps, and the bus going beep-beep.
  - music_snow (the penguin): a skating waltz (3/4, B): a toy piano,
    pizzicato oom-pah-pah, sleigh bells, a glassy pad.
  - music_space (the astronaut): floating among the stars (4/4, G flat): a
    soft space whistle sliding from note to note, an electric bell
    twinkling with its echo, a warm pad.
  - music_rest: a quiet lullaby (12/8, B flat): someone humming over a
    rocking harp.
  Each tune is as long as its bars, and what still rings at the end is
  carried round to the start, so it loops without a seam.
- Footsteps (WAV, 22,050 Hz): one tiny sound per hero, played once for each
  square walked, so they are short, soft and pleasant said many times over.
- Short sounds (WAV, 22,050 Hz): taps, stars, keys, gates, the fanfare home,
  and 土豆's voice.
- For children from 2: fun, warm and soft. Nothing harsh or sudden; slipping
  off the road is a soft, friendly "boing", never a buzzer.
- Voices are a buzz through formant filters, as in the sibling apps.
- Every random choice uses a fixed seed, so each run writes the same files.
- Every short sound is set to the same loudness as heard through a phone
  speaker (A-weighting, and nothing under 250 Hz), plus or minus a few dB
  where it should sit softer, with its peak at most 0.72. The music is set
  the same way, about 8 dB under the short sounds. Low sounds get a little
  of their own overtones added (`carry`), so a phone still carries them.

The helpers (t_of, env, sweep, decay, lowpass, bandpass, highpass, norm,
partial, bell, marimba, place, tune_loop, resonator, voice, ease, glide,
above, spans, melody, root_of, pluck_bass, metal, shaker, kick, jingle,
noise_through, carry, celesta, chime, a_weight, loudness, chord_tones,
harmonics, pizz, toy_horn, pad, chord_at, chirp, yay, tidy, phone_ready,
level, write, seam, report, read, preview) come from 眼尖尖大挑戰's
design/sounds/make_sounds.py (which took most of them from 想一想樂園,
小卡認天下, 動物小餐廳 and 字母寵物); bubble, plink, clack and soft_piano from
想一想樂園's. New here: the ocarina, banjo, recorder, harp, bassoon, steel
pan, accordion, toy piano, electric bell, space whistle, humming voice,
sleigh bells, hand claps, the looping cave echo, every tune and every sound.

    python3 design/sounds/make_sounds.py                  # writes app/assets/sounds/*.wav
    python3 design/sounds/make_sounds.py preview OUT.m4a  # and a listening preview
"""
import os
import pathlib
import subprocess
import sys
import tempfile
import wave

import numpy as np
from scipy.signal import lfilter, resample_poly

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "app" / "assets" / "sounds"
SR = 22050       # short sounds, footsteps and voices
LOOP_SR = 16000  # music
LIMIT = 5_000_000  # bytes, the whole folder (eight 16 s tunes at 16 kHz alone are 4.1 MB)

# Notes (Hz), with flats as well as sharps.
NOTE = {f"{n}{o}": 440 * 2 ** ((k - 9) / 12 + o - 4)
        for o in range(1, 9) for k, n in enumerate("C C# D D# E F F# G G# A A# B".split())}
for _o in range(1, 9):
    for _flat, _sharp in (("Db", "C#"), ("Eb", "D#"), ("Gb", "F#"), ("Ab", "G#"), ("Bb", "A#")):
        NOTE[f"{_flat}{_o}"] = NOTE[f"{_sharp}{_o}"]


# ---------------------------------------------------------------- helpers (from 眼尖尖大挑戰 and 想一想樂園)


def t_of(dur, sr=SR):
    return np.arange(int(dur * sr)) / sr


def env(n, attack=0.005, release=0.05, sr=SR):
    """Up quickly, down smoothly: no clicks at either end."""
    e = np.ones(n)
    a, r = max(1, min(n, int(attack * sr))), max(1, min(n, int(release * sr)))
    e[:a] = np.linspace(0, 1, a) ** 2
    e[-r:] *= np.linspace(1, 0, r) ** 2
    return e


def sweep(f, sr=SR):
    """A sine whose frequency follows the array [f] (Hz per sample)."""
    return np.sin(2 * np.pi * np.cumsum(f) / sr)


def decay(n, tau, sr=SR):
    return np.exp(-np.arange(n) / (tau * sr))


def lowpass(x, cutoff, sr=SR):
    spec = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(len(x), 1 / sr)
    spec *= 1 / (1 + (freqs / cutoff) ** 4)
    return np.fft.irfft(spec, len(x))


def bandpass(x, lo, hi, sr=SR):
    spec = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(len(x), 1 / sr)
    spec *= 1 / (1 + (lo / np.maximum(freqs, 1)) ** 4) / (1 + (freqs / hi) ** 4)
    return np.fft.irfft(spec, len(x))


def highpass(x, cutoff, sr=SR):
    spec = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(len(x), 1 / sr)
    spec *= 1 / (1 + (cutoff / np.maximum(freqs, 1e-3)) ** 4)
    return np.fft.irfft(spec, len(x))


def norm(x):
    return x / max(1e-9, np.abs(x).max())


def partial(freq, t, sr):
    """A sine at [freq], or silence if it is too high for [sr] (it would fold
    back down as a wrong note)."""
    return np.sin(2 * np.pi * freq * t) if freq < 0.45 * sr else np.zeros_like(t)


def bell(freq, dur=0.5, sr=SR, bright=1.0):
    """A soft glockenspiel note: a few partials, the high ones dying first."""
    t = t_of(dur, sr)
    x = (partial(freq, t, sr) * np.exp(-t / (dur * 0.35))
         + 0.35 * bright * partial(freq * 2.76, t, sr) * np.exp(-t / (dur * 0.12))
         + 0.15 * bright * partial(freq * 5.4, t, sr) * np.exp(-t / (dur * 0.06)))
    return x * env(len(t), 0.002, 0.03, sr)


def marimba(freq, dur=0.5, sr=SR):
    t = t_of(dur, sr)
    x = partial(freq, t, sr) * np.exp(-t / (dur * 0.3)) + 0.2 * partial(freq * 4, t, sr) * np.exp(-t / (dur * 0.05))
    return x * env(len(t), 0.003, 0.03, sr)


def place(total, parts, sr=SR):
    """[parts]: (start seconds, signal) mixed into [total] seconds."""
    out = np.zeros(int(total * sr))
    for start, sig in parts:
        i = int(start * sr)
        j = min(len(out), i + len(sig))
        out[i:j] += sig[: j - i]
    return out


def tune_loop(seconds, notes, sr=LOOP_SR):
    """[notes]: (start seconds, signal); what rings past [seconds] wraps to the start."""
    n = int(round(seconds * sr))
    tail = max(len(sig) + int(start * sr) for start, sig in notes) - n
    out = np.zeros(n + max(0, tail))
    for start, sig in notes:
        i = int(start * sr)
        out[i:i + len(sig)] += sig
    loop = out[:n].copy()
    if tail > 0:
        loop[:tail] += out[n:]
    return loop


def resonator(x, freq, bw, sr=SR, block=64):
    """A two-pole resonance at [freq] Hz (a number, or one per sample, for a
    sound that changes) of bandwidth [bw] Hz."""
    freq = np.broadcast_to(np.asarray(freq, dtype=float), x.shape)
    y, zi = np.zeros_like(x), np.zeros(2)
    r = np.exp(-np.pi * bw / sr)
    for i in range(0, len(x), block):
        th = 2 * np.pi * freq[i] / sr
        y[i:i + block], zi = lfilter([1 - r], [1, -2 * r * np.cos(th), r * r], x[i:i + block], zi=zi)
    return y


def voice(f0, formants, rng, breath=0.03, rough=0.0, sr=SR):
    """A voice at pitch [f0] (Hz per sample) through [formants]: (Hz or Hz
    per sample, bandwidth, gain). [rough] jitters the pitch, for a growl."""
    n = len(f0)
    if rough:
        f0 = f0 * (1 + rough * lowpass(rng.standard_normal(n), 60, sr) * 3)
    buzz = 2 * (np.cumsum(f0) / sr % 1) - 1 + breath * rng.standard_normal(n)
    out = np.zeros(n)
    for f, bw, gain in formants:
        y = resonator(buzz, f, bw, sr)
        out += gain * y / max(1e-9, np.abs(y).max())
    return lowpass(out, 3800, sr)  # soft, not a kazoo


def ease(u):
    """0 to 1, smoothly, over u in 0..1."""
    u = np.clip(u, 0, 1)
    return u * u * (3 - 2 * u)


def glide(t, *points):
    """A value that moves smoothly between (time, value) [points]."""
    ts, vs = zip(*points)
    out = np.interp(t, ts, vs)
    return lowpass(out - out.mean(), 25) + out.mean() if len(t) > 64 else out


def bubble(rng, sr=SR, low=(300, 550), rise=(2.2, 3.2), dur=(0.04, 0.08)):
    """One little bubble: a quick rising blip that starts and ends at zero."""
    d = rng.uniform(*dur)
    t = t_of(d, sr)
    f0 = rng.uniform(*low)
    f = np.geomspace(f0, f0 * rng.uniform(*rise), len(t))
    return sweep(f, sr) * np.sin(np.pi * t / d)


def above(name, low):
    """The note called [name] (no octave) at or just above the note [low]."""
    for o in range(1, 9):
        if NOTE[f"{name}{o}"] >= NOTE[low] * 0.999:
            return f"{name}{o}"
    raise ValueError(name)


def spans(bars, beats_per_bar):
    """Bars like "F" or "Gm-C" (two chords, half a bar each) -> (beat, length in beats, chord)."""
    out = []
    for i, bar in enumerate(bars):
        parts = bar.split("-")
        each = beats_per_bar / len(parts)
        out += [(i * beats_per_bar + k * each, each, c) for k, c in enumerate(parts)]
    return out


def melody(tune, beat, start=0.0, swing=0.0, bars=None, beats_per_bar=4):
    """[tune]: (note or None for a rest, beats) one after another ->
    (seconds, note, seconds long). [swing] (in beats) delays each note that
    falls halfway through a beat, for a lilt. [bars]: check the tune fills them."""
    if bars is not None:
        assert abs(sum(b for _, b in tune) - bars * beats_per_bar) < 1e-9, tune
    out, b = [], 0.0
    for name, beats in tune:
        if name:
            late = swing if abs(b % 1 - 0.5) < 1e-6 else 0.0
            out.append((start + (b + late) * beat, name, (beats - late) * beat))
        b += beats
    return out


def root_of(chord):
    return chord[:2] if len(chord) > 1 and chord[1] in "#b" else chord[0]


def pluck_bass(freq, dur=1.0, sr=LOOP_SR):
    """A plucked double bass: round, short, warm."""
    t = t_of(dur, sr)
    x = (partial(freq, t, sr) * np.exp(-t / (dur * 0.35))
         + 0.45 * partial(freq * 2, t, sr) * np.exp(-t / (dur * 0.15))
         + 0.15 * partial(freq * 3, t, sr) * np.exp(-t / (dur * 0.08)))
    return x * env(len(t), 0.006, 0.08, sr)


def metal(freq, dur, sr=SR, ratios=(1, 1.59, 2.14, 2.65, 3.15), amps=(1, .6, .45, .3, .2), taus=(.5, .3, .2, .15, .1)):
    """A small metal ting (a bell, a coin): partials that are not
    whole-number multiples; [taus] are fractions of [dur]."""
    t = t_of(dur, sr)
    x = sum(a * partial(freq * r, t, sr) * np.exp(-t / (dur * k)) for r, a, k in zip(ratios, amps, taus))
    return x * env(len(t), 0.0008, 0.03, sr)


def shaker(rng, sr=LOOP_SR, dur=0.06, lo=3000, hi=7000):
    n = int(dur * sr)
    return norm(bandpass(rng.standard_normal(n), lo, hi, sr)) * env(n, 0.006, dur * 0.8, sr)


def kick(sr=LOOP_SR, dur=0.16):
    n = int(dur * sr)
    return sweep(np.geomspace(130, 55, n), sr) * decay(n, 0.05, sr) * env(n, 0.002, 0.04, sr)


def jingle(rng, dur=0.2, sr=SR):
    """A tambourine's little cymbals."""
    t = t_of(dur, sr)
    x = sum(rng.uniform(0.4, 1.0) * partial(f, t, sr) * np.exp(-t / rng.uniform(0.03, 0.07))
            for f in rng.uniform(4500, 9000, 8))
    x += 0.5 * norm(bandpass(rng.standard_normal(len(t)), 5000, 10000, sr)) * np.exp(-t / 0.02)
    return x * env(len(t), 0.001, 0.04, sr)


def noise_through(rng, centre, bw, n, sr=SR):
    """Noise through a resonance that can move: the voice of air and water."""
    return norm(resonator(rng.standard_normal(n), centre, bw, sr))


def soft_piano(freq, dur=2.5, sr=LOOP_SR):
    """A felt piano: a marimba's warm knock and a bell's soft ring, blended,
    over a plain tone that rings a little longer."""
    t = t_of(dur, sr)
    body = (partial(freq, t, sr) * np.exp(-t / (dur * 0.32))
            + 0.25 * partial(freq * 2, t, sr) * np.exp(-t / (dur * 0.12)))
    x = 0.45 * marimba(freq, dur, sr) + 0.3 * bell(freq, dur, sr, bright=0.25) + 0.5 * body
    return x * env(len(t), 0.006, 0.08, sr)


def carry(x, amount=0.3, lo=500, hi=3000, drive=2.5, sr=SR):
    """Phone speakers hardly play anything under about 300 Hz. For a low
    sound, add its own overtones (a soft saturation of it, kept to [lo]..[hi]
    Hz): a phone plays those, and the ear still hears the low note."""
    peak = max(1e-9, np.abs(x).max())
    over = bandpass(np.tanh(drive * x / peak), lo, hi, sr)
    return x + amount * peak * norm(over)


def celesta(freq, dur=1.0, sr=LOOP_SR):
    """A celesta: a felt hammer on a small steel bar over a wooden box. A
    sweet, round tone with a little of its octave, and a soft tick."""
    t = t_of(dur, sr)
    x = (partial(freq, t, sr) * np.exp(-t / (dur * 0.3))
         + 0.25 * partial(freq * 2, t, sr) * np.exp(-t / (dur * 0.12))
         + 0.06 * partial(freq * 4.1, t, sr) * np.exp(-t / 0.02))
    return x * env(len(t), 0.0015, 0.05, sr)


def chime(freq, dur, sr=SR):
    """A soft, warm bell: whole-number partials (no glockenspiel clang), two
    tones a hair apart so it shimmers as it rings."""
    t = t_of(dur, sr)
    x = ((partial(freq, t, sr) + 0.5 * partial(freq * 1.003, t, sr)) * np.exp(-t / (dur * 0.38))
         + 0.28 * partial(freq * 2.0, t, sr) * np.exp(-t / (dur * 0.16))
         + 0.1 * partial(freq * 3.01, t, sr) * np.exp(-t / (dur * 0.07)))
    return x * env(len(t), 0.003, 0.08, sr)


def plink(freq, dur=0.25, sr=LOOP_SR):
    """A little glassy plink, like a bead dropped on a toy block."""
    t = t_of(dur, sr)
    x = partial(freq, t, sr) * np.exp(-t / 0.05) + 0.3 * partial(freq * 2.76, t, sr) * np.exp(-t / 0.012)
    return x * env(len(t), 0.0008, 0.03, sr)


def clack(rng, sr=LOOP_SR, dur=0.06):
    """Two wooden blocks knocked together: a short, hollow clack."""
    n = int(dur * sr)
    t = np.arange(n) / sr
    hit = rng.standard_normal(n) * np.exp(-t / 0.002)
    x = norm(resonator(hit, 1250, 120, sr)) + 0.6 * norm(resonator(hit, 2650, 200, sr))
    return x * np.exp(-t / 0.018) * env(n, 0.0005, 0.015, sr)


def a_weight(x, sr):
    """[x] as the ear hears it out of a phone: A-weighting (the ear is less
    sensitive to low and very high sounds) and nothing under about 250 Hz."""
    spec = np.fft.rfft(x)
    f2 = np.fft.rfftfreq(len(x), 1 / sr) ** 2
    ra = 12194 ** 2 * f2 ** 2 / ((f2 + 20.6 ** 2) * np.sqrt((f2 + 107.7 ** 2) * (f2 + 737.9 ** 2)) * (f2 + 12194 ** 2))
    phone = 1 / (1 + (250 ** 2 / np.maximum(f2, 1e-6)) ** 2)
    return np.fft.irfft(spec * ra * 1.2589 * phone, len(x))


def loudness(x, sr):
    """How loud [x] sounds, roughly, in dB: the weighted power in 200 ms
    windows (the ear adds up about that long, so a click sounds softer than
    a note as loud), over the windows within 20 dB of the loudest one."""
    y = a_weight(np.asarray(x, dtype=np.float64), sr) ** 2
    w, hop = int(0.2 * sr), int(0.025 * sr)
    y = np.concatenate([y, np.zeros(max(0, w - len(y)))])
    c = np.concatenate([[0], np.cumsum(y)])
    e = (c[w::hop] - c[:len(c) - w:hop]) / w
    return 10 * np.log10(max(1e-12, np.mean(e[e >= e.max() * 0.01])))


QUALITY = {"": (0, 4, 7), "m": (0, 3, 7), "7": (0, 4, 7, 10), "m7": (0, 3, 7, 10),
           "maj7": (0, 4, 7, 11), "7sus": (0, 5, 7, 10)}


def chord_tones(chord, low):
    """The notes (Hz) of [chord], root first, the root at or just above [low]."""
    root = root_of(chord)
    f = NOTE[above(root, low)]
    return [f * 2 ** (s / 12) for s in QUALITY[chord[len(root):]]]


def chord_at(span_list, b):
    """The chord sounding at beat [b]."""
    return [c for s, _, c in span_list if s <= b + 1e-9][-1]


def harmonics(f, sr=SR, tilt=1.0):
    """A bright tone at pitch [f] (Hz per sample) with every harmonic up to
    near half the sample rate, each 1/k^[tilt]: a sawtooth without the
    harsh folded-back tones."""
    ph = 2 * np.pi * np.cumsum(f) / sr
    top = int(0.45 * sr // np.max(f))
    return sum(np.sin(k * ph) / k ** tilt for k in range(1, max(2, top + 1)))


def pizz(freq, dur=0.5, sr=LOOP_SR, pos=0.14):
    """A pizzicato string, plucked with a finger: it rings only a moment,
    the high harmonics dying first; low notes ring a little longer."""
    t = t_of(dur, sr)
    tau = min(0.3, 0.07 + 50 / freq)
    x = np.zeros_like(t)
    for k in range(1, 9):
        x += abs(np.sin(np.pi * k * pos)) / k * partial(freq * k, t, sr) * np.exp(-t * (1 + 0.7 * (k - 1)) / tau)
    return x * env(len(t), 0.0012, 0.04, sr)


def toy_horn(freq, dur, sr=SR):
    """A soft toy trumpet: every harmonic, the high ones quieter, opening up
    as it speaks; a little vibrato on a long note."""
    t = t_of(dur, sr)
    vib = 1 + 0.006 * np.sin(2 * np.pi * 5.5 * t) * ease((t - 0.15) / 0.2)
    ph = 2 * np.pi * np.cumsum(freq * vib) / sr
    opening = ease(t / 0.05)
    x = np.zeros_like(t)
    for k in range(1, 9):
        if freq * k < 0.4 * sr:
            x += (1 if k == 1 else opening) / k ** 1.4 * np.sin(k * ph)
    return lowpass(x, 3500, sr) * env(len(t), 0.015, min(0.1, dur * 0.4), sr)


def pad(chord, length, low="Ab3", sr=LOOP_SR):
    """A warm pad, like soft strings far away: the chord held, fading in over
    most of a second and out over a second after [length] (so it melts into
    the next), each tone three voices a hair apart (so it breathes), with a
    little of their octave."""
    d = length + 1.0
    t = t_of(d, sr)
    shape = ease(t / 0.7) * (1 - ease((t - length + 0.1) / 1.0))
    x = np.zeros_like(t)
    for f in chord_tones(chord, low)[:3]:
        for det in (0.996, 1.0, 1.004):
            x += np.sin(2 * np.pi * f * det * t) + 0.22 * np.sin(2 * np.pi * 2 * f * det * t)
    return x * shape / 9


def chirp(points, dur, sr=SR):
    """A bird's chirp: a pure whistle whose pitch follows (fraction of
    [dur], Hz) [points], swelling in and out."""
    t = t_of(dur, sr)
    fs, hz = zip(*points)
    f = np.interp(t / dur, fs, hz)
    return (sweep(f, sr) + 0.12 * sweep(2 * f, sr)) * np.sin(np.pi * t / dur) ** 1.2


def yay(rng, f, dur=0.32, size=1.15):
    """A small, happy "yay!" (ye-ay), jumping up."""
    t = t_of(dur)
    f0 = glide(t, (0, f), (0.08, f * 1.25), (dur, f * 1.05))
    f1 = np.interp(t, [0, 0.05, 0.2, dur], [300, 750, 700, 450]) * size
    f2 = np.interp(t, [0, 0.05, 0.2, dur], [2300, 1800, 1900, 2200]) * size
    return voice(f0, [(f1, 130, 1.0), (f2, 180, 0.55), (3000 * size, 300, 0.12)], rng, breath=0.1) * env(len(t), 0.02, 0.1)


# ---------------------------------------------------------------- new instruments


def ocarina(freq, dur, rng, sr=LOOP_SR):
    """A clay ocarina: an almost pure, round, hollow tone (a vessel flute has
    hardly any overtones), a soft breath of air around it, a little puff as
    each note speaks and a slow vibrato on long notes."""
    t = t_of(dur, sr)
    n = len(t)
    vib = 1 + 0.005 * np.sin(2 * np.pi * 4.8 * t) * ease((t - 0.25) / 0.3)
    ph = 2 * np.pi * np.cumsum(freq * vib) / sr
    x = np.sin(ph) + 0.06 * np.sin(2 * ph) + 0.035 * np.sin(3 * ph)
    breath = 0.045 * norm(bandpass(rng.standard_normal(n), freq * 0.8, min(freq * 2.5, 0.45 * sr), sr))
    puff = 0.12 * norm(bandpass(rng.standard_normal(n), freq, min(freq * 4, 0.45 * sr), sr)) * np.exp(-t / 0.02)
    return (x + breath + puff) * env(n, 0.03, min(0.08, dur * 0.35), sr)


def banjo(freq, dur=0.6, sr=LOOP_SR, pos=0.1):
    """A banjo string, picked: bright and twangy (picked near the bridge, so
    many harmonics), dying quickly, with the ring of its drum head."""
    t = t_of(dur, sr)
    x = np.zeros_like(t)
    for k in range(1, 13):
        a = abs(np.sin(np.pi * k * pos)) / k
        x += a * partial(freq * k * (1 + 0.0004 * k * k), t, sr) * np.exp(-t * (1 + 0.6 * (k - 1)) / 0.25)
    head = norm(resonator(x, 900, 450, sr)) * np.abs(x).max()
    return (x + 0.5 * head) * env(len(t), 0.001, 0.04, sr)


def recorder(freq, dur, rng, sr=LOOP_SR):
    """A soprano recorder: a clear, sweet tone, a little brighter than a
    flute (a touch of its octave and twelfth), the quick "t" of the tongue
    as each note starts, and no vibrato."""
    t = t_of(dur, sr)
    n = len(t)
    ph = 2 * np.pi * freq * t
    x = np.sin(ph) + 0.22 * np.sin(2 * ph) + 0.1 * np.sin(3 * ph) + 0.04 * np.sin(4 * ph)
    breath = 0.04 * norm(resonator(rng.standard_normal(n), freq * 2, 600, sr))
    chiff = 0.25 * norm(bandpass(rng.standard_normal(n), freq * 2, min(freq * 6, 0.45 * sr), sr)) * np.exp(-t / 0.008)
    return (x + breath + chiff) * env(n, 0.012, min(0.06, dur * 0.3), sr)


def harp(freq, dur=1.6, sr=LOOP_SR):
    """A harp string, plucked with the fingertip: round and warm, ringing
    long, the high harmonics fading first."""
    t = t_of(dur, sr)
    x = np.zeros_like(t)
    for k in range(1, 8):
        a = abs(np.sin(np.pi * k * 0.3)) / k ** 1.5
        x += a * partial(freq * k, t, sr) * np.exp(-t / (dur * 0.35 / (1 + 0.6 * (k - 1))))
    return x * env(len(t), 0.004, 0.08, sr)


def bassoon(freq, dur, rng, sr=LOOP_SR):
    """A bassoon, played short and bouncy: a reedy buzz (every harmonic)
    through the bassoon's own resonances (a warm one about 480 Hz, a reedier
    one about 1,150 Hz), a breath of air, each note swelling in quickly."""
    t = t_of(dur, sr)
    n = len(t)
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5 * t) * ease((t - 0.3) / 0.3)
    buzz = harmonics(np.full(n, freq) * vib, sr, tilt=1.0)
    x = (0.2 * norm(bandpass(buzz, 220, 700, sr)) + norm(resonator(buzz, 480, 260, sr))
         + 0.5 * norm(resonator(buzz, 1150, 320, sr)))
    breath = 0.03 * norm(bandpass(rng.standard_normal(n), 800, 3000, sr))
    return lowpass(x + breath, 3200, sr) * env(n, 0.02, min(0.04, dur * 0.3), sr)


def steel_pan(freq, dur=0.9, sr=LOOP_SR):
    """A steel pan, struck with a rubber stick: a sweet, round note, its
    octave swelling up a moment after the strike (the steel passes its
    energy up), a little twelfth, and a metal glint at the very start."""
    t = t_of(dur, sr)
    swell = (1 - np.exp(-t / 0.025)) * np.exp(-t / (dur * 0.3))
    x = (partial(freq, t, sr) * np.exp(-t / (dur * 0.4))
         + 0.55 * partial(2.005 * freq, t, sr) * swell
         + 0.2 * partial(3.01 * freq, t, sr) * np.exp(-t / (dur * 0.15))
         + 0.08 * partial(4.6 * freq, t, sr) * np.exp(-t / 0.01))
    return x * env(len(t), 0.002, 0.06, sr)


def accordion(freq, dur, sr=LOOP_SR, musette=1.005):
    """An accordion in musette: two reeds a hair apart (the note shimmers as
    they beat against each other), each a bright, reedy tone, breathed in by
    the bellows."""
    t = t_of(dur, sr)
    x = np.zeros_like(t)
    for det in (1.0, musette):
        ph = 2 * np.pi * freq * det * t
        for k in range(1, 9):
            if freq * k < 0.4 * sr:
                x += (1 if k == 1 else 0.8) / k ** 1.2 * np.sin(k * ph)
    return lowpass(x, 3000, sr) * env(len(t), 0.025, min(0.06, dur * 0.3), sr)


def toy_piano(freq, dur=0.7, sr=LOOP_SR):
    """A toy piano: a little hammer on a metal rod. A sweet, tinkly note
    (the rod's next modes are not whole multiples) with a second rod a hair
    out of tune, as on a real toy, and a tiny wooden knock."""
    t = t_of(dur, sr)
    x = ((partial(freq, t, sr) + 0.35 * partial(freq * 1.004, t, sr)) * np.exp(-t / (dur * 0.3))
         + 0.3 * partial(freq * 2.0, t, sr) * np.exp(-t / (dur * 0.1))
         + 0.18 * partial(freq * 5.4, t, sr) * np.exp(-t / 0.02)
         + 0.1 * partial(1250, t, sr) * np.exp(-t / 0.006))
    return x * env(len(t), 0.0015, 0.06, sr)


def fm_bell(freq, dur=1.2, sr=LOOP_SR, ratio=1.0, index=1.2):
    """A soft electric bell: one sine wobbling another so fast that it makes
    new overtones, which fade as the note rings (like a struck tine), with a
    faint glassy tine above."""
    t = t_of(dur, sr)
    idx = index * np.exp(-t / 0.15)
    x = np.sin(2 * np.pi * freq * t + idx * np.sin(2 * np.pi * freq * ratio * t)) * np.exp(-t / (dur * 0.35))
    x += 0.06 * partial(freq * 4.03, t, sr) * np.exp(-t / 0.02)
    return x * env(len(t), 0.002, 0.08, sr)


def space_whistle(notes, seconds, sr=LOOP_SR, slide=0.045):
    """A soft space whistle, like a theremin: one tone gliding from note to
    note, swelling in and out with each, with a slow vibrato. [notes]:
    (seconds, Hz, seconds long); the tune must end on a rest, so the tone is
    silent where the loop joins."""
    n = int(round(seconds * sr))
    t = np.arange(n) / sr
    target = np.full(n, np.log2(notes[0][1]))
    amp = np.zeros(n)
    for at, hz, d in notes:
        target[int(at * sr):] = np.log2(hz)
        amp = np.maximum(amp, ease((t - at) / 0.06) * (1 - ease((t - at - d + 0.02) / 0.12)))
    a = np.exp(-1 / (slide * sr))  # the pitch slides there, quickly at first
    pitch = 2 ** lfilter([1 - a], [1, -a], target, zi=[a * target[0]])[0]
    pitch *= 1 + 0.005 * np.sin(2 * np.pi * 5.2 * t)
    ph = 2 * np.pi * np.cumsum(pitch) / sr
    assert amp[0] < 1e-3 and amp[-1] < 1e-3
    return (np.sin(ph) + 0.12 * np.sin(2 * ph) + 0.04 * np.sin(3 * ph)) * amp


def hum_voice(freq, dur, rng, sr=LOOP_SR):
    """Someone humming softly, mouth closed ("mmm"): a gentle voice that
    comes out mostly as its lowest tone, a slow vibrato and a little drift,
    a breath of air."""
    t = t_of(dur, sr)
    n = len(t)
    drift = 1 + 0.002 * norm(lowpass(rng.standard_normal(n), 3, sr))
    f0 = freq * drift * (1 + 0.005 * np.sin(2 * np.pi * 5.2 * t) * ease((t - 0.3) / 0.4))
    x = voice(f0, [(300, 90, 1.0), (900, 150, 0.12), (2400, 250, 0.03)], rng, breath=0.04, sr=sr)
    return lowpass(x, 1400, sr) * env(n, 0.08, min(0.25, dur * 0.4), sr)


def sleigh(rng, dur=0.22, sr=LOOP_SR):
    """Sleigh bells shaken once: a few tiny round bells, each a moment
    apart, and a little rattle."""
    t = t_of(dur, sr)
    x = np.zeros_like(t)
    for f in rng.uniform(2800, 5200, 6):
        d = rng.uniform(0, 0.02)
        tt = np.clip(t - d, 0, None)
        x += rng.uniform(0.5, 1) * (partial(f, tt, sr) + 0.3 * partial(2.4 * f, tt, sr)) * np.exp(-tt / rng.uniform(0.04, 0.08))
    rattle = norm(bandpass(rng.standard_normal(len(t)), 3500, 7000, sr)) * np.exp(-t / 0.03)
    return (norm(x) + 0.3 * rattle) * env(len(t), 0.001, 0.05, sr)


def clap(rng, sr=LOOP_SR):
    """A soft hand clap: three quick slaps of air close together, and the
    clap itself."""
    n = int(0.12 * sr)
    shape = np.zeros(n)
    for k, d in enumerate((0, 0.008, 0.017, 0.026)):
        i = int(d * sr)
        shape[i:] += (0.6 if k < 3 else 1) * np.exp(-np.arange(n - i) / sr / (0.004 if k < 3 else 0.03))
    return norm(bandpass(rng.standard_normal(n), 900, 4000, sr) * shape) * env(n, 0.0005, 0.03, sr)


def loop_echo(x, rng, tau=0.3, sr=LOOP_SR):
    """The echoes of a cave around a whole loop (a soft tail of noise dying
    away over about [tau] seconds), as loud as [x]: the echoes of the end
    come round into the start, as they will when it repeats."""
    n = int(4 * tau * sr)
    ir = lowpass(rng.standard_normal(n), 2500, sr) * np.exp(-np.arange(n) / sr / tau)
    ir[:int(0.02 * sr)] = 0  # the first echoes come a moment after the sound
    y = np.fft.irfft(np.fft.rfft(x) * np.fft.rfft(ir, len(x)), len(x))
    return norm(y) * np.abs(x).max()


# ---------------------------------------------------------------- music


class Tune:
    """A tune: its length, the tune itself and the band (lists of (seconds,
    signal)), the soft top it is played through, and how much cave echo."""

    def __init__(self, seconds, lead, band, cutoff, echo=0.0):
        self.seconds, self.lead, self.band, self.cutoff, self.echo = seconds, lead, band, cutoff, echo

    def render(self, lead=True, band=True):
        x = tune_loop(self.seconds, (self.lead if lead else []) + (self.band if band else []))
        if self.echo:
            x = x + self.echo * loop_echo(x, np.random.default_rng(99))
        return lowpass(x, self.cutoff, LOOP_SR)


def music_home():
    """The world map, with 土豆: a friendly stroll, "let's go!", 4/4 in G,
    straight and easy. A clay ocarina sings the tune (leaping up G-B-D like
    happy steps); a plucked bass walks every beat; a banjo strums on two and
    four; a soft drum and a shaker keep the step. In the second half a
    glockenspiel twinkles on the beats with the tune and the banjo picks in
    between; the last bar runs down a D7 chord into the start again."""
    beat = 0.52
    bars = ["G", "C", "D", "G", "Em", "C", "A7-D", "D7"]
    tune = [("G4", .5), ("B4", .5), ("D5", 1), ("B4", .5), ("D5", .5), ("G5", 1),
            ("E5", 1), ("C5", .5), ("E5", .5), ("G5", 1.5), (None, .5),
            ("F#5", .5), ("E5", .5), ("D5", .5), ("E5", .5), ("F#5", 1), ("A5", 1),
            ("G5", 1.5), ("D5", .5), ("B4", 1), (None, 1),
            ("B4", .5), ("E5", .5), ("G5", 1), ("F#5", .5), ("E5", .5), ("B4", 1),
            ("C5", .5), ("E5", .5), ("G5", 1), ("A5", .5), ("G5", .5), ("E5", 1),
            ("E5", .5), ("C#5", .5), ("E5", .5), ("G5", .5), ("F#5", 1), ("A5", .5), ("F#5", .5),
            ("A5", 1), ("F#5", .5), ("D5", .5), ("C5", .5), ("A4", .5), ("F#4", 1)]
    walk = ["G2 B2 D3 B2", "C3 B2 A2 C#3", "D3 A2 F#2 A2", "G2 B2 D3 D#3",
            "E3 B2 G2 B2", "C3 E3 G2 G#2", "A2 C#3 D3 A2", "D3 C3 A2 F#2"]
    rng = np.random.default_rng(101)
    sp = spans(bars, 4)
    lead, band = [], []
    for at, n, d in melody(tune, beat, bars=8):
        f = NOTE[n]
        lead.append((at, 0.34 * ocarina(f, d * (0.92 if d >= beat - 1e-9 else 0.78), rng)))
        if at >= 16 * beat - 1e-9 and abs(at / beat - round(at / beat)) < 1e-6:
            lead.append((at, 0.045 * bell(2 * f, 0.4, LOOP_SR, bright=0.4)))
    for i, bar in enumerate(walk):
        for k, name in enumerate(bar.split()):
            band.append(((4 * i + k) * beat, 0.7 * pluck_bass(NOTE[name], 0.6)))
    for b in range(32):
        chord = chord_at(sp, b)
        tones = chord_tones(chord, "G3")[:3]
        if b % 2 == 1:  # two and four: a banjo strum
            band += [(b * beat + 0.012 * k, 0.15 * banjo(f, 0.5)) for k, f in enumerate(tones)]
        elif b >= 16:  # the second half: a banjo pick on the "and" of one and three
            band.append(((b + 0.5) * beat, 0.09 * banjo(2 * tones[0], 0.35)))
        if b % 2 == 0:
            band.append((b * beat, 0.22 * kick()))
        band.append(((b + 0.5) * beat, (0.045 if b >= 16 else 0.03) * shaker(rng)))
    return Tune(len(bars) * 4 * beat, lead, band, 4500)


def music_garden():
    """花園 (the bee's world): a sunny spring lilt, 6/8 in D (six quavers a
    bar, two swinging beats). A recorder sings the tune; a harp ripples up
    and down each chord; a plucked bass on each of the two beats; a light
    shaker. In the second half a glockenspiel doubles the tune softly an
    octave up; the last bar runs down an A7 chord into the start again."""
    eighth = 0.17
    bars = ["D", "D", "G", "D", "Bm", "Em", "A", "A7", "D", "F#m", "G", "D", "Em", "A", "D-G", "A7"]
    tune = [("F#5", 2), ("A5", 1), ("D6", 2), ("A5", 1),
            ("B5", 1), ("A5", 1), ("F#5", 1), ("A5", 3),
            ("B5", 2), ("D6", 1), ("B5", 2), ("G5", 1),
            ("A5", 3), ("F#5", 2), ("E5", 1),
            ("D5", 2), ("F#5", 1), ("B5", 2), ("A5", 1),
            ("G5", 2), ("F#5", 1), ("E5", 2), ("G5", 1),
            ("A5", 2), ("C#6", 1), ("E6", 2), ("C#6", 1),
            ("B5", 1), ("A5", 1), ("G5", 1), ("E5", 3),
            ("F#5", 2), ("A5", 1), ("D6", 2), ("E6", 1),
            ("C#6", 2), ("A5", 1), ("F#5", 3),
            ("G5", 2), ("B5", 1), ("D6", 2), ("B5", 1),
            ("A5", 2), ("F#5", 1), ("D5", 3),
            ("E5", 2), ("G5", 1), ("B5", 2), ("E6", 1),
            ("C#6", 2), ("B5", 1), ("A5", 3),
            ("F#5", 1), ("A5", 1), ("F#5", 1), ("G5", 1), ("B5", 1), ("D6", 1),
            ("E6", 1), ("C#6", 1), ("A5", 1), ("G5", 2), ("E5", 1)]
    rng = np.random.default_rng(102)
    lead, band = [], []
    for at, n, d in melody(tune, eighth, bars=16, beats_per_bar=6):
        f = NOTE[n]
        lead.append((at, 0.31 * recorder(f, d * (0.9 if d > eighth * 1.5 else 0.8), rng)))
        if at >= 8 * 6 * eighth - 1e-9:  # the second half: a glockenspiel an octave up
            lead.append((at, 0.035 * bell(2 * f, 0.45, LOOP_SR, bright=0.35)))
    for b, length, chord in spans(bars, 6):
        c = chord_tones(chord, "D3")
        ripple = [c[0], c[2], 2 * c[0], 2 * c[1], 2 * c[0], c[2]][:int(length)]
        for k, f in enumerate(ripple):
            band.append(((b + k) * eighth, (0.2 if k == 0 else 0.13) * rng.uniform(0.9, 1.1) * harp(f, 1.2)))
        r = NOTE[above(root_of(chord), "A2")]
        band.append((b * eighth, 0.6 * pluck_bass(r, 0.8)))
        if length == 6:
            band.append(((b + 3) * eighth, 0.4 * pluck_bass(r * 2 ** (7 / 12) / (2 if r > NOTE["D3"] else 1), 0.6)))
    for e in range(16 * 6):
        band.append((e * eighth, (0.045 if e % 3 == 0 else 0.022) * shaker(rng, dur=0.05)))
    return Tune(len(bars) * 6 * eighth, lead, band, 5000)


def music_tunnel():
    """地底隧道 (土豆's tunnels): cosy and a little sneaky, 4/4 in E dorian (a
    minor key with a bright, folky sixth: the A major chord). A bassoon plays
    a bouncy tune of short, light notes, high in its tenor range (clear on a
    phone); a low marimba goes dum . . da-dum under it with a soft plucked
    bass; wooden blocks pat on two and four like a little spade; earth
    trickles softly on the quavers; now and then a crystal gem glints high
    above; and it all sounds a little like a cave (soft echoes, the top a
    little dark). The last bar steps down a B7 chord into the start again."""
    beat = 0.52
    bars = ["Em", "A", "Em", "A", "C", "D", "G-A", "B7"]
    tune = [("E4", .5), (None, .5), ("E4", .5), ("G4", .5), ("B4", 1), (None, .5), ("A4", .5),
            ("C#5", .5), (None, .5), ("C#5", .5), ("B4", .5), ("A4", 1), ("E4", 1),
            ("G4", .5), ("B4", .5), ("E5", 1), ("D5", .5), ("B4", .5), ("G4", 1),
            ("A4", .5), ("C#5", .5), ("E5", .5), ("C#5", .5), ("A4", 1), (None, 1),
            ("G4", .5), (None, .5), ("G4", .5), ("C5", .5), ("E5", 1), ("D5", .5), ("C5", .5),
            ("A4", .5), (None, .5), ("A4", .5), ("D5", .5), ("F#5", 1), ("E5", .5), ("D5", .5),
            ("B4", .5), ("D5", .5), ("G4", 1), ("C#5", .5), ("E5", .5), ("A4", 1),
            ("D#5", 1), ("B4", .5), ("A4", .5), ("F#4", .5), ("A4", .5), ("D#4", 1)]
    rng = np.random.default_rng(103)
    sp = spans(bars, 4)
    lead, band = [], []
    for at, n, d in melody(tune, beat, bars=8):
        lead.append((at, 0.4 * bassoon(NOTE[n], d * (0.8 if d >= beat - 1e-9 else 0.55), rng)))
    for b, n in ((7.5, "E7"), (15.5, "C#7"), (23.5, "F#7"), (29.5, "D7")):  # crystal gems glinting
        lead.append((b * beat, 0.05 * plink(NOTE[n], 0.35)))
        lead.append(((b + 0.25) * beat, 0.025 * plink(NOTE[n] * 1.5, 0.3)))
    for b in range(32):
        chord = chord_at(sp, b)
        r = NOTE[above(root_of(chord), "E2")]
        if b % 2 == 0:  # dum . . da-dum
            band.append((b * beat, 0.5 * marimba(2 * r, 0.45, LOOP_SR)))
            band.append((b * beat, 0.4 * pluck_bass(r, 0.7)))
            band.append(((b + 1.5) * beat, 0.32 * marimba(2 * r * 2 ** (7 / 12), 0.35, LOOP_SR)))
        else:  # the little spade pats, and a soft chord
            band.append((b * beat, 0.07 * clack(rng)))
            band += [(b * beat + 0.008 * k, 0.12 * marimba(f, 0.3, LOOP_SR)) for k, f in enumerate(chord_tones(chord, "G3")[:3])]
        band.append(((b + 0.5) * beat, 0.025 * shaker(rng, dur=0.07, lo=1500, hi=4000)))
    return Tune(len(bars) * 4 * beat, lead, band, 3500, echo=0.25)


def music_sea():
    """海底 (the fish's world): a sunny calypso, 4/4 in F, three-three-two. A
    steel pan plays the tune (rolling its long notes, as players do); a lower
    steel pan answers with chords on the three-three-two; a soft bass
    bounces; a shaker keeps time; and bubbles rise at the end of each half."""
    beat = 0.5
    bars = ["F", "Bb", "C7", "F", "F7", "Bb", "Gm-C7", "F-C7"]
    tune = [("C5", .5), ("F5", .5), ("A5", 1), ("G5", .5), ("A5", 1), ("F5", .5),
            ("D5", .5), ("F5", .5), ("Bb5", 1), ("A5", .5), ("G5", .5), ("F5", 1),
            ("E5", .5), ("G5", .5), ("C6", 1), ("Bb5", .5), ("G5", 1), ("E5", .5),
            ("F5", 1.5), ("A5", .5), ("C6", 1), (None, 1),
            ("C6", .5), ("A5", .5), ("F5", .5), ("Eb5", 1), ("F5", .5), ("A5", 1),
            ("Bb5", 1.5), ("D6", .5), ("C6", .5), ("Bb5", .5), ("F5", 1),
            ("G5", .5), ("Bb5", .5), ("D6", 1), ("C6", .5), ("Bb5", .5), ("G5", 1),
            ("A5", 1), ("F5", 1), ("G5", .5), ("E5", .5), ("D5", .5), ("Bb4", .5)]
    rng = np.random.default_rng(104)
    sp = spans(bars, 4)
    lead, band = [], []
    for at, n, d in melody(tune, beat, bars=8):
        f = NOTE[n]
        if d >= 1.5 * beat - 1e-9:  # a long note: rolled
            s = 0.0
            while s < d - 0.12:
                lead.append((at + s, (0.33 if s == 0 else 0.16 * rng.uniform(0.85, 1.1)) * steel_pan(f, 0.4)))
                s += 0.085
        else:
            lead.append((at, 0.33 * steel_pan(f, max(0.6, d + 0.3))))
    for b, length, chord in sp:
        c = chord_tones(chord, "A3")[:3]
        hits = (0, 1.5, 3) if length == 4 else (0, 1.5)  # three-three-two
        for h in hits:
            band += [((b + h) * beat + 0.006 * k, 0.11 * steel_pan(f, 0.45)) for k, f in enumerate(c)]
        r = NOTE[above(root_of(chord), "F2")]
        fifth = r * 2 ** (7 / 12)
        band.append((b * beat, 0.7 * pluck_bass(r, 0.7)))
        band.append(((b + 1.5) * beat, 0.45 * pluck_bass(fifth, 0.4)))
        if length == 4:
            band.append(((b + 2) * beat, 0.55 * pluck_bass(2 * r if 2 * r < NOTE["D3"] else r, 0.7)))
            band.append(((b + 3.5) * beat, 0.4 * pluck_bass(fifth, 0.4)))
    for e in range(64):
        band.append((e * 0.5 * beat, (0.045 if e % 8 in (0, 3, 6) else 0.022) * shaker(rng, dur=0.07)))
    for start in (14.5, 30.5):  # bubbles rising at the end of each half
        for k in range(5):
            band.append(((start + 0.3 * k + rng.uniform(0, 0.08)) * beat,
                         0.12 * bubble(rng, LOOP_SR, (500 + 80 * k, 650 + 80 * k), (1.8, 2.4), (0.05, 0.08))))
    return Tune(len(bars) * 4 * beat, lead, band, 4500)


def music_city():
    """城市 (the little bus's world): a busy, happy shuffle, 4/4 in A. An
    accordion plays the tune; a plucked bass goes oom on one and three, a
    felt piano answers pah on two and four; soft hand claps on two and
    four, a swinging shaker; and in the fourth bar, in the gap in the tune,
    the bus says beep-beep."""
    beat, swing = 0.5, 0.15
    bars = ["A", "C#m", "D", "E", "F#m", "D", "B7", "E7"]
    tune = [("E5", .5), ("A5", .5), ("C#6", .5), ("A5", .5), ("E5", 1), (None, .5), ("C#5", .5),
            ("E5", .5), ("G#5", .5), ("E5", .5), ("C#5", .5), ("G#4", 1), (None, 1),
            ("F#5", .5), ("A5", .5), ("D6", 1), ("C#6", .5), ("B5", .5), ("A5", 1),
            ("G#5", 1), ("E5", .5), ("B4", .5), ("E5", 1), (None, 1),
            ("C#6", .5), ("A5", .5), ("F#5", 1), ("E5", .5), ("F#5", .5), ("A5", 1),
            ("A5", .5), ("F#5", .5), ("D5", 1), ("E5", .5), ("F#5", .5), ("A5", 1),
            ("B5", .5), ("A5", .5), ("F#5", .5), ("D#5", .5), ("F#5", 1), ("A5", 1),
            ("G#5", .5), ("B5", .5), ("D6", .5), ("B5", .5), ("G#5", .5), ("E5", .5), ("D5", .5), ("B4", .5)]
    rng = np.random.default_rng(105)
    sp = spans(bars, 4)
    lead, band = [], []
    for at, n, d in melody(tune, beat, swing=swing, bars=8):
        lead.append((at, 0.23 * accordion(NOTE[n], d * (0.88 if d >= beat - 1e-9 else 0.75))))
    for k, at in enumerate((15.0, 15.5 + swing)):  # beep-beep
        for f in (NOTE["E5"], NOTE["G#5"]):
            lead.append((at * beat, 0.09 * toy_horn(f, 0.16, LOOP_SR)))
    for b in range(32):
        chord = chord_at(sp, b)
        r = NOTE[above(root_of(chord), "E2")]
        if b % 2 == 0:  # oom
            band.append((b * beat, 0.7 * pluck_bass(r if b % 4 == 0 else r * 2 ** (7 / 12), 0.5)))
        else:  # pah, and a clap
            band += [(b * beat + 0.006 * k, 0.11 * soft_piano(f, 0.4)) for k, f in enumerate(chord_tones(chord, "E4")[:3])]
            band.append((b * beat, 0.07 * clap(rng)))
        band.append((b * beat, 0.022 * shaker(rng, dur=0.05)))
        band.append(((b + 0.5 + swing) * beat, 0.04 * shaker(rng, dur=0.05)))
    return Tune(len(bars) * 4 * beat, lead, band, 4500)


def music_snow():
    """雪地 (the penguin's world): a skating waltz, 3/4 in B. A toy piano
    tinkles the tune; pizzicato strings go oom-pah-pah; sleigh bells shake
    softly on the pah-pahs; a glassy pad holds each chord; in the second
    half a celesta sings along an octave lower."""
    beat = 0.34
    bars = ["B", "B", "E", "B", "G#m", "C#m", "F#7", "F#7", "B", "D#m", "E", "B", "G#m", "C#7", "F#7", "F#7"]
    tune = [("F#5", 2), ("B5", 1),
            ("D#6", 2), ("C#6", 1),
            ("B5", 2), ("G#5", 1),
            ("F#5", 3),
            ("G#5", 2), ("B5", 1),
            ("E6", 2), ("C#6", 1),
            ("A#5", 1), ("C#6", 1), ("E6", 1),
            ("C#6", 2), ("A#5", 1),
            ("F#5", 2), ("B5", 1),
            ("D#6", 2), ("F#6", 1),
            ("E6", 1), ("D#6", 1), ("C#6", 1),
            ("B5", 2), ("F#5", 1),
            ("G#5", 1), ("B5", 1), ("D#6", 1),
            ("C#6", 1), ("G#5", 1), ("B5", 1),
            ("A#5", 2), ("C#6", 1),
            ("E6", 1), ("C#6", 1), ("A#5", 1)]
    rng = np.random.default_rng(106)
    lead, band = [], []
    for at, n, d in melody(tune, beat, bars=16, beats_per_bar=3):
        f = NOTE[n]
        lead.append((at, 0.5 * toy_piano(f, max(0.7, d + 0.4))))
        if at >= 8 * 3 * beat - 1e-9:  # the second half: a celesta an octave lower
            lead.append((at, 0.2 * celesta(f / 2, max(0.8, d + 0.4))))
    for b, length, chord in spans(bars, 3):
        r = NOTE[above(root_of(chord), "F#2")]
        band.append((b * beat, 0.8 * pizz(r, 0.5)))
        for off in (1, 2):
            band += [((b + off) * beat + 0.005 * k, 0.17 * pizz(f, 0.3)) for k, f in enumerate(chord_tones(chord, "D#4")[:3])]
            band.append(((b + off) * beat, 0.035 * sleigh(rng)))
        band.append((b * beat, 0.22 * pad(chord, length * beat, low="F#3")))
    for b in (0, 24):
        band.append((b * beat, 0.05 * metal(4200, 0.9, LOOP_SR, ratios=(1, 2.7, 4.1), amps=(1, .4, .2), taus=(.5, .2, .1))))
    return Tune(len(bars) * 3 * beat, lead, band, 5500)


def music_space():
    """太空 (the astronaut's world): floating among the stars, 4/4 in G flat,
    unhurried and dreamy (the second chord, A flat major, borrows the
    raised fourth). A soft space whistle, like a theremin, glides from note
    to note; an electric bell twinkles up and down each chord, its echo
    following a dotted beat later; a warm pad glows; a soft round bass on one
    and three; little stars blink high above."""
    beat = 0.52
    bars = ["Gbmaj7", "Ab", "Gbmaj7", "Ab", "Ebm7", "Bbm7", "Bmaj7", "Db7sus-Db7"]
    tune = [("Db5", 1), ("Gb5", 1), ("Bb5", 2),
            ("C6", 2), ("Bb5", 1), ("Ab5", 1),
            ("F5", 2), ("Db5", 1), ("Bb4", 1),
            ("C5", 3), (None, 1),
            ("Bb5", 1), ("Gb5", 1), ("Eb5", 1), ("Db5", 1),
            ("F5", 2), ("Ab5", 1), ("Db6", 1),
            ("Bb5", 2), ("Gb5", 1), ("Eb5", 1),
            ("Gb5", 2), ("F5", 1.5), (None, .5)]
    rng = np.random.default_rng(107)
    seconds = len(bars) * 4 * beat
    notes = [(at, NOTE[n], d) for at, n, d in melody(tune, beat, bars=8)]
    lead = [(0, 0.42 * space_whistle(notes, seconds))]
    band = []
    for b, length, chord in spans(bars, 4):
        c = chord_tones(chord, "Gb4")
        up = c + [2 * c[0]]
        pattern = up + up[-2:0:-1]
        for k in range(int(length * 2)):
            at = (b + 0.5 * k) * beat
            f = pattern[k % len(pattern)]
            band.append((at, 0.13 * fm_bell(f, 1.0)))
            band.append((at + 0.75 * beat, 0.04 * fm_bell(f, 0.8)))
        band.append((b * beat, 0.3 * pad(chord, length * beat, low="Gb3")))
        r = NOTE[above(root_of(chord), "Db2")]
        band.append((b * beat, 0.6 * pluck_bass(r, 1.4)))
        if length == 4:
            band.append(((b + 2) * beat, 0.4 * pluck_bass(r, 1.2)))
        star = 4 * rng.choice(c)
        band.append(((b + 0.5 + rng.integers(0, int(length * 2) - 1) * 0.5) * beat, 0.05 * plink(star, 0.4)))
    return Tune(seconds, lead, band, 4000)


def music_rest():
    """Rest time (土豆 goes to sleep): a quiet lullaby, 12/8 in B flat, slow
    and rocking (four long beats a bar, each of three). Someone hums the
    tune softly ("mmm"), taking a breath at the end; a harp rocks up and
    down each chord; a warm pad holds it; soft chimes ring at the end of
    each half."""
    eighth = 0.34
    bars = ["Bb-Gm", "Eb-Bb", "Gm-Cm", "Eb-F7"]
    tune = [("F5", 3), ("D5", 3), ("D5", 2), ("C5", 1), ("Bb4", 3),
            ("G5", 3), ("Eb5", 3), ("F5", 2), ("D5", 1), ("Bb4", 3),
            ("Bb4", 2), ("D5", 1), ("G5", 3), ("G5", 2), ("F5", 1), ("Eb5", 3),
            ("Bb4", 3), ("G4", 3), ("A4", 2), ("C5", 2), (None, 2)]
    rng = np.random.default_rng(108)
    lead, band = [], []
    for at, n, d in melody(tune, eighth, bars=4, beats_per_bar=12):
        lead.append((at, 0.8 * hum_voice(NOTE[n], d + 0.12, rng)))
    for b, length, chord in spans(bars, 12):
        c = chord_tones(chord, "G2")
        for k, f in enumerate([c[0], c[2], 2 * c[0], 2 * c[1], 2 * c[0], c[2]]):
            band.append(((b + k) * eighth, (0.3 if k == 0 else 0.18) * harp(f, 1.8)))
        band.append((b * eighth, 0.12 * pad(chord, length * eighth, low="Bb3")))
    for b, n in ((21, "D6"), (22, "Bb5"), (45, "F6"), (46, "C6"), (47, "A5")):
        band.append((b * eighth, 0.09 * chime(NOTE[n], 1.6, LOOP_SR)))
    return Tune(len(bars) * 12 * eighth, lead, band, 2600)


# name: (make, loudness in dB beside the short sounds: about 8 under them).
MUSIC = {
    "music_home": (music_home, -8),
    "music_garden": (music_garden, -9),
    "music_tunnel": (music_tunnel, -9),
    "music_sea": (music_sea, -9),
    "music_city": (music_city, -9.5),
    "music_snow": (music_snow, -9),
    "music_space": (music_space, -9),
    "music_rest": (music_rest, -9),
}


# ---------------------------------------------------------------- footsteps (one per square walked)


def step_garden():
    """The bee's step: a soft, short "bzz", its wings fluttering, rising a
    touch as it flies on."""
    dur = 0.16
    t = t_of(dur)
    f = np.linspace(225, 262, len(t)) * (1 + 0.015 * np.sin(2 * np.pi * 9 * t))
    x = bandpass(harmonics(f, tilt=1.4), 350, 2200) * (0.8 + 0.2 * np.sin(2 * np.pi * 36 * t))
    return x * np.sin(np.pi * t / dur) ** 1.5


def step_tunnel():
    """土豆's step: a little dig in soft earth, a crumbly "pff" over a soft,
    round pat."""
    rng = np.random.default_rng(602)
    dur = 0.13
    t = t_of(dur)
    n = len(t)
    crumbs = np.zeros(2 * n)  # filtered with room after it, so its ringing does not wrap round to the end
    for i in rng.integers(0, int(0.05 * SR), 14):
        k = rng.integers(30, 90)
        crumbs[i:i + k] += rng.uniform(0.3, 1) * rng.standard_normal(k) * np.exp(-np.arange(k) / (k / 4))
    crumbs = norm(bandpass(crumbs, 600, 3500)[:n]) * np.exp(-t / 0.04)
    pat = sweep(np.geomspace(320, 200, n)) * np.exp(-t / 0.025)
    return carry((0.6 * crumbs + 0.5 * pat) * env(n, 0.001, 0.03), 0.3, lo=500, hi=2500)


def step_sea():
    """The fish's step: one round bubble, "blup", and a tiny one after it."""
    def blob(f0, rise, d):
        t = t_of(d)
        f = np.geomspace(f0, f0 * rise, len(t))
        return (sweep(f) + 0.12 * sweep(2 * f)) * np.sin(np.pi * t / d)
    return place(0.15, [(0, blob(420, 2.3, 0.085)), (0.07, 0.4 * blob(700, 2.0, 0.05))])


def step_city():
    """The bus's step: a tiny toy engine going "putt-putt", two quick,
    round puffs."""
    rng = np.random.default_rng(604)

    def puff(f):
        d = 0.06
        t = t_of(d)
        n = len(t)
        burst = rng.standard_normal(n) * np.exp(-t / 0.006)
        body = norm(resonator(burst, f, 120)) + 0.5 * norm(resonator(burst, f * 2.6, 300))
        tone = sweep(np.geomspace(f * 0.9, f * 0.7, n)) * np.exp(-t / 0.02)
        return (0.6 * body + 0.6 * tone) * np.exp(-t / 0.022) * env(n, 0.0008, 0.015)
    return lowpass(carry(place(0.14, [(0, puff(420)), (0.065, 0.75 * puff(380))]), 0.25, lo=600, hi=2800), 3500)


def step_snow():
    """The penguin's step: a soft pat of a little flat foot on snow, with the
    tiny crunch of the snow under it."""
    rng = np.random.default_rng(605)
    dur = 0.12
    t = t_of(dur)
    n = len(t)
    crunch = np.zeros(2 * n)  # filtered with room after it, as in step_tunnel
    for i in rng.integers(0, int(0.045 * SR), 18):
        crunch[i:i + 40] += rng.uniform(0.2, 1) * rng.choice([-1, 1]) * np.exp(-np.arange(40) / 6)
    crunch = norm(bandpass(crunch, 1800, 6000)[:n]) * np.exp(-t / 0.035)
    pat = norm(lowpass(rng.standard_normal(n), 1200)) * np.exp(-t / 0.01) + 0.6 * sweep(np.geomspace(330, 220, n)) * np.exp(-t / 0.02)
    return carry((0.7 * norm(pat) + 0.3 * crunch) * env(n, 0.001, 0.03), 0.2, lo=600, hi=2800)


def step_space():
    """The astronaut's step: a soft space "bip", a round tone that bends up
    with a glassy shimmer, and a quiet echo of itself."""
    def bip(a):
        d = 0.07
        t = t_of(d)
        f = 660 * 1.5 ** ease(t / 0.04)
        ph = 2 * np.pi * np.cumsum(f) / SR
        return a * np.sin(ph + 0.6 * np.exp(-t / 0.02) * np.sin(2 * ph)) * np.sin(np.pi * t / d) ** 0.8
    return place(0.19, [(0, bip(1.0)), (0.1, bip(0.3))])


# ---------------------------------------------------------------- playing


def tap():
    """A button: a soft, round "pok", like a finger on a felt button."""
    t = t_of(0.08)
    f = np.interp(t, [0, 0.008, 0.08], [640, 760, 720])
    x = (sweep(f) + 0.18 * sweep(2 * f)) * np.exp(-t / 0.016) + 0.12 * partial(2400, t, SR) * np.exp(-t / 0.003)
    return lowpass(x * env(len(t), 0.0008, 0.02), 3500)


def bump():
    """The finger slipped off the road: a very soft, friendly "boing", a
    small round spring that wobbles and settles, cushioned like a bump into
    a pillow. Never scary: not low, not loud, over in a moment."""
    rng = np.random.default_rng(402)
    dur = 0.3
    t = t_of(dur)
    f = 300 * (1 + 0.4 * ease(t / 0.05)) * (1 + 0.07 * np.sin(2 * np.pi * 11 * t) * np.exp(-t / 0.12))
    boing = (sweep(f) + 0.15 * sweep(2 * f)) * env(len(t), 0.004, 0.08) * np.exp(-t / 0.1)
    m = int(0.05 * SR)
    puff = norm(lowpass(rng.standard_normal(m), 900)) * np.exp(-np.arange(m) / SR / 0.01) * env(m, 0.001, 0.01)
    return lowpass(carry(place(dur, [(0, 0.35 * puff), (0.005, boing)]), 0.25, lo=600, hi=2400), 2500)


def star():
    """A star picked up: a bright, sparkly "ding!" A quick grace note from a
    fourth below, the ding itself (two tones a hair apart, so it glitters,
    its octave and a tiny strike), and two little twinkles above."""
    t = t_of(0.6)
    f = NOTE["A6"]
    ding = ((np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 1.004 * t)) * np.exp(-t / 0.2)
            + 0.25 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.07)
            + 0.08 * np.sin(2 * np.pi * 4.2 * f * t) * np.exp(-t / 0.008)) * env(len(t), 0.0015, 0.08)
    return place(0.7, [(0, 0.3 * celesta(NOTE["E6"], 0.1, SR)), (0.035, 0.75 * ding),
                       (0.13, 0.15 * bell(NOTE["E7"], 0.25, bright=0.3)), (0.2, 0.1 * bell(NOTE["A7"], 0.25, bright=0.2))])


def fork():
    """A fork in the road: a curious little "coo?" (咕？), a soft, round,
    voiced sound rising like a question, and a tiny chirp after it, up."""
    rng = np.random.default_rng(404)
    dur = 0.34
    t = t_of(dur)
    f0 = glide(t, (0, 360), (0.12, 340), (0.26, 470), (dur, 520))
    f1 = glide(t, (0, 250), (0.04, 330), (dur, 360))
    f2 = glide(t, (0, 1100), (0.05, 800), (dur, 850))
    x = voice(f0, [(f1, 100, 1.0), (f2, 140, 0.35), (2300, 250, 0.06)], rng, breath=0.04)
    x *= ease(t / 0.015) * (1 - ease((t - 0.24) / 0.1))
    return carry(place(0.46, [(0, x), (0.35, 0.16 * chirp([(0, 1500), (1, 2100)], 0.07))]), 0.3, lo=500, hi=2500)


def key():
    """A key picked up: the little jingle of keys on a ring (three small
    metal tings, one after another, and a rattle), then a bright two-note
    "ta-da!" going up."""
    rng = np.random.default_rng(405)
    ring = dict(ratios=(1, 2.32, 4.25), amps=(1, .5, .25), taus=(.35, .18, .08))
    m = int(0.1 * SR)
    rattle = norm(bandpass(rng.standard_normal(m), 4000, 9000)) * np.exp(-np.arange(m) / (0.02 * SR)) * env(m, 0.001, 0.02)
    parts = [(0.0, 0.4 * metal(2600, 0.3, **ring)), (0.03, 0.3 * metal(3150, 0.28, **ring)),
             (0.065, 0.22 * metal(2850, 0.25, **ring)), (0, 0.06 * rattle)]
    parts += [(0.16, 0.45 * celesta(NOTE["E6"], 0.25, SR)), (0.26, 0.55 * celesta(NOTE["B6"], 0.5, SR)),
              (0.26, 0.22 * chime(NOTE["E6"], 0.55))]
    return place(0.85, parts)


def gate():
    """The gate swinging open: the latch lifts with a little wooden
    click-clack, the gate swings wide with a soft whoosh (no creak), and a
    harp runs up as if to say "come in!"."""
    rng = np.random.default_rng(406)
    parts = [(0, 0.5 * clack(rng, SR)), (0.07, 0.4 * clack(rng, SR))]
    d = 0.45
    t = t_of(d)
    whoosh = noise_through(rng, glide(t, (0, 500), (0.25, 1300), (d, 800)), 600, len(t)) * np.sin(np.pi * t / d) ** 2
    parts.append((0.12, 0.3 * whoosh))
    for k, n in enumerate(["C5", "D5", "E5", "G5", "A5", "C6", "D6", "E6"]):
        parts.append((0.2 + 0.04 * k, (0.25 + 0.02 * k) * harp(NOTE[n], 0.6, SR)))
    parts.append((0.53, 0.25 * chime(NOTE["C6"], 0.6)))
    return place(1.2, parts)


def arrive():
    """The hero is home: a happy little fanfare, 1.5 s. Two ocarinas and a
    glockenspiel go da-da-da up D-G-B, land on a big G chord (DAA!) with a
    banjo strum, a plucked bass, a tambourine and a soft cymbal, and
    sparkles rain down."""
    rng = np.random.default_rng(407)
    parts = []
    for at, n in ((0.0, "D5"), (0.11, "G5"), (0.22, "B5")):
        parts += [(at, 0.4 * ocarina(NOTE[n], 0.1, rng, SR)), (at, 0.2 * bell(NOTE[n] * 2, 0.3, bright=0.4))]
    land = 0.34
    parts += [(land, 0.42 * ocarina(NOTE["D6"], 0.62, rng, SR)), (land, 0.26 * ocarina(NOTE["B5"], 0.62, rng, SR)),
              (land, 0.3 * bell(NOTE["G6"], 0.8, bright=0.4)),
              (land, 0.4 * carry(pluck_bass(NOTE["G2"], 0.8, SR), 0.3)), (land, 0.2 * jingle(rng))]
    parts += [(land + 0.012 * k, 0.22 * banjo(NOTE[n], 0.8, SR)) for k, n in enumerate(["G3", "B3", "D4", "G4", "B4"])]
    m = int(0.6 * SR)
    cym = norm(bandpass(rng.standard_normal(m), 5000, 10000)) * np.exp(-np.arange(m) / (0.18 * SR)) * env(m, 0.002, 0.1)
    parts.append((land, 0.07 * cym))
    for k, n in enumerate(["G7", "D7", "B6", "D7", "G6", "B6", "G6"]):
        parts.append((0.66 + 0.075 * k + rng.uniform(-0.01, 0.01), (0.2 - 0.018 * k) * bell(NOTE[n], 0.35, bright=0.4)))
    return place(1.48, parts)


def cheer():
    """The hero's family cheers: a little crowd of tiny "yay!"s, small high
    voices one after another, each a little different, then soft claps."""
    rng = np.random.default_rng(408)
    parts = []
    for at, f, size in ((0.0, 560, 1.2), (0.04, 690, 1.3), (0.08, 500, 1.15), (0.13, 760, 1.35),
                        (0.18, 620, 1.25), (0.24, 720, 1.3), (0.3, 580, 1.2)):
        parts.append((at + rng.uniform(0, 0.015), rng.uniform(0.1, 0.14) * yay(rng, f, rng.uniform(0.28, 0.36), size)))
    for k, at in enumerate((0.45, 0.62, 0.79, 0.96, 1.13)):
        parts.append((at, (0.1 - 0.012 * k) * clap(rng, SR)))
    return place(1.35, parts)


def sticker():
    """A sticker popping into the book: a round, bubbly "pop!" going up, a
    soft pat as it sticks, and a tiny twinkle."""
    rng = np.random.default_rng(409)
    d = 0.075
    t = t_of(d)
    f = np.geomspace(350, 1250, len(t))
    pop = (sweep(f) + 0.15 * sweep(2 * f)) * np.sin(np.pi * t / d) ** 0.8
    tp = t_of(0.06)
    pat = (0.6 * norm(lowpass(rng.standard_normal(len(tp)), 1400)) * np.exp(-tp / 0.008)
           + 0.5 * sweep(np.geomspace(420, 280, len(tp))) * np.exp(-tp / 0.018)) * env(len(tp), 0.0008, 0.015)
    return place(0.45, [(0, 0.8 * pop), (0.07, 0.55 * pat), (0.1, 0.2 * bell(NOTE["E7"], 0.3, bright=0.3)),
                        (0.16, 0.14 * bell(NOTE["B7"], 0.25, bright=0.2))])


def hint():
    """土豆 pops out of his hole to help: a little scrabble of earth (soft
    crumbly patters), a springy "fwip!" up as his head comes out, and a
    friendly two-note "here!" on the marimba."""
    rng = np.random.default_rng(410)
    parts = []
    for k in range(6):
        m = int(0.03 * SR)
        crumb = norm(lowpass(rng.standard_normal(m), 2200)) * np.exp(-np.arange(m) / SR / 0.006) * env(m, 0.0005, 0.01)
        parts.append((0.03 * k + rng.uniform(0, 0.01), rng.uniform(0.15, 0.3) * crumb))
    d = 0.11
    t = t_of(d)
    f = 350 * 3.2 ** ease(t / d)
    up = (sweep(f) + 0.12 * sweep(2 * f)) * np.sin(np.pi * t / d) ** 0.6
    parts += [(0.2, 0.7 * up), (0.36, 0.5 * marimba(NOTE["G5"], 0.35)), (0.47, 0.6 * marimba(NOTE["C6"], 0.5))]
    return place(1.0, parts)


def giggle():
    """土豆's little giggle: a chubby "heh-heh-heh-hehh", lower and rounder
    than a chirp, bouncing down, the last one longer, curling up happily."""
    rng = np.random.default_rng(411)
    parts = []
    for k, (at, f, dur) in enumerate([(0.0, 480, 0.065), (0.095, 530, 0.065), (0.19, 500, 0.065),
                                      (0.285, 455, 0.065), (0.39, 430, 0.15)]):
        t = t_of(dur)
        if k == 4:
            f0 = glide(t, (0, f), (dur * 0.4, f * 0.96), (dur, f * 1.18))
        else:
            f0 = np.linspace(f * 1.05, f * 0.93, len(t))
        x = voice(f0, [(620, 140, 1.0), (1700, 200, 0.5), (2600, 280, 0.12)], rng, breath=0.18)
        x *= np.sin(np.pi * t / dur) ** 0.7
        m = int(0.025 * SR)
        h = norm(bandpass(rng.standard_normal(m), 1200, 4500)) * np.hanning(m) * 0.18  # the "h"
        parts += [(at, h), (at + 0.018, x)]
    return place(0.6, parts)


def next_level():
    """On to the next level: a quick harp run up five notes (G-A-B-D-G),
    with a soft whoosh carrying it along."""
    rng = np.random.default_rng(412)
    parts = [(0.045 * k, (0.35 + 0.04 * k) * harp(NOTE[n], 0.5, SR)) for k, n in enumerate(["G5", "A5", "B5", "D6", "G6"])]
    d = 0.32
    t = t_of(d)
    whoosh = noise_through(rng, glide(t, (0, 800), (d, 2600)), 900, len(t)) * np.sin(np.pi * t / d) ** 2
    return place(0.65, parts + [(0, 0.15 * whoosh)])


def switch_style():
    """Changing the drawing style: a magic swish (a shimmering whoosh that
    rises and falls back), a ripple of little bells inside it, and a round
    "bloop" as the new look settles."""
    rng = np.random.default_rng(413)
    dur = 0.5
    t = t_of(dur)
    n = len(t)
    swish = noise_through(rng, glide(t, (0, 700), (0.25, 4200), (dur, 1500)), 1200, n) * np.sin(np.pi * t / dur) ** 1.5
    shimmer = norm(bandpass(rng.standard_normal(n), 6000, 9500)) * np.sin(np.pi * t / dur) ** 2 * (0.6 + 0.4 * np.sin(2 * np.pi * 14 * t))
    parts = [(0, 0.45 * swish), (0, 0.08 * shimmer)]
    parts += [(0.06 + 0.05 * k, (0.16 - 0.015 * k) * bell(NOTE[m], 0.3, bright=0.3)) for k, m in enumerate(["G6", "B6", "D7", "G7", "D7", "B6"])]
    d = 0.12
    tb = t_of(d)
    fb = np.geomspace(480, 900, len(tb))
    bloop = (sweep(fb) + 0.15 * sweep(2 * fb)) * np.sin(np.pi * tb / d) ** 0.8
    return place(0.75, parts + [(0.48, 0.45 * bloop)])


def rest_time():
    """Time to rest: 土豆 yawns, a small, breathy "haa-aum" that sinks and
    closes into a sleepy hum, then a soft celesta falls G-E-C."""
    rng = np.random.default_rng(414)
    dur = 0.95
    t = t_of(dur)
    f0 = glide(t, (0, 380), (0.15, 450), (0.55, 330), (dur, 260))
    f1 = glide(t, (0, 550), (0.2, 900), (0.55, 760), (0.75, 450), (dur, 320))
    f2 = glide(t, (0, 1500), (0.2, 1350), (0.6, 1000), (dur, 900))
    yawn = voice(f0, [(f1, 150, 1.0), (f2, 190, 0.45), (2800, 300, 0.07)], rng, breath=0.35) * env(len(t), 0.12, 0.3)
    closing = ease((t - 0.6) / 0.25)
    yawn = yawn * (1 - closing) + 1.6 * lowpass(yawn, 700) * closing  # the mouth closes: mmm
    return place(1.5, [(0, 0.85 * yawn), (0.8, 0.35 * celesta(NOTE["G5"], 0.5, SR)),
                       (0.98, 0.3 * celesta(NOTE["E5"], 0.5, SR)), (1.16, 0.26 * celesta(NOTE["C5"], 0.32, SR))])


def page():
    """Turning a page of the sticker book: a light, papery "fwip" as it
    swings over, and a soft pat as it lands."""
    rng = np.random.default_rng(415)
    dur = 0.2
    t = t_of(dur)
    n = len(t)
    air = noise_through(rng, glide(t, (0, 700), (0.12, 1800), (dur, 1200)), 700, n)
    paper = norm(bandpass(rng.standard_normal(n), 1500, 7000)) * (0.6 + 0.4 * norm(lowpass(rng.standard_normal(n), 60)))
    flip = (0.6 * air + 0.45 * paper) * ease(t / 0.05) * (1 - ease((t - 0.12) / 0.08))
    tp = t_of(0.05)
    pat = norm(lowpass(rng.standard_normal(len(tp)), 1500)) * np.exp(-tp / 0.007) * env(len(tp), 0.0008, 0.01)
    return place(0.3, [(0, 0.8 * flip), (0.19, 0.35 * pat)])


# ---------------------------------------------------------------- the list

# name: (make, loudness in dB beside the others: below 0 sits softer).
STEPS = {
    "step_garden": (step_garden, -8), "step_tunnel": (step_tunnel, -7), "step_sea": (step_sea, -7),
    "step_city": (step_city, -7), "step_snow": (step_snow, -7), "step_space": (step_space, -8),
}
EFFECTS = {
    "tap": (tap, -4), "bump": (bump, -6), "star": (star, -1), "fork": (fork, -2), "key": (key, -1),
    "gate": (gate, -2), "arrive": (arrive, 0), "cheer": (cheer, -1), "sticker": (sticker, -2),
    "hint": (hint, -2), "giggle": (giggle, -1), "next": (next_level, -4), "switch_style": (switch_style, -2),
    "rest": (rest_time, -2), "page": (page, -4),
}
SHORT = {**STEPS, **EFFECTS}
LONGEST = {**{k: 0.25 for k in STEPS}, **{k: 1.5 for k in EFFECTS}}  # seconds
TARGET = -21.0  # dB, the loudness of a short sound at 0 (about where the sibling apps' sit)
MAX_PEAK = 0.72


# ---------------------------------------------------------------- writing and checking


def tidy(x, sr=SR):
    """A short sound: drop the silent end, then fade both ends so neither clicks."""
    x = np.asarray(x, dtype=np.float64)
    loud = np.nonzero(np.abs(x) > np.abs(x).max() * 1e-3)[0]
    x = x[: min(len(x), loud[-1] + int(0.01 * sr))]
    return x * env(len(x), 0.002, 0.012, sr)


def phone_ready(x, sr=SR):
    """Take out what a phone cannot play anyway (under 70 Hz), for more room
    under the peak. The filter works on the whole sound at once and wraps
    round, so pad it with silence on both sides first: what it rings before
    the start and after the end then stays out of the sound."""
    pad_ = int(0.1 * sr)
    return highpass(np.concatenate([np.zeros(pad_), x, np.zeros(pad_)]), 70, sr)[pad_:]


def level(x, offset, sr=SR):
    """[x] at the loudness TARGET + [offset] dB, unless that would put its
    peak over MAX_PEAK: then at MAX_PEAK. Returns the peak."""
    x = norm(x)
    return min(MAX_PEAK, 10 ** ((TARGET + offset - loudness(x, sr)) / 20))


def write(path, x, peak, sr):
    x = np.asarray(x, dtype=np.float64)
    x = x / max(1e-9, np.abs(x).max()) * peak
    data = np.round(x * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(data.tobytes())
    return data


def seam(data, sr):
    """A loop's seam, checked two ways: the jump from the last sample back to
    the first (beside the biggest step from one sample to the next in the
    20 ms either side of it: a click would stand out above them), and the
    sound over 3 kHz in the 20 ms around the seam (a click would show as a
    burst there) beside the loudest 20 ms anywhere else in the loop."""
    x = data.astype(np.float64)
    steps = np.abs(np.diff(x))
    jump = abs(x[0] - x[-1])
    half = len(x) // 2
    h = highpass(np.roll(x, half), 3000, sr) ** 2  # the seam now sits at [half]
    w = int(0.02 * sr)
    c = np.concatenate([[0], np.cumsum(h)])
    starts = np.arange(0, len(h) - w + 1, w // 2)
    at = half - w // 2
    here = c[at + w] - c[at]
    others = (c[starts + w] - c[starts])[np.abs(starts - at) >= w]
    near = np.concatenate([steps[-w:], steps[:w]]).max()  # the biggest step in the 20 ms either side
    return jump, near, here / max(1e-9, others.max())


def report(name, data, sr, loop, want=None):
    x = data.astype(np.float64) / 32767
    peak = np.abs(x).max()
    loud = loudness(x, sr)
    clipped = int(np.sum(np.abs(data) >= 32767))
    assert clipped == 0, name
    if loop:
        jump, near, burst = seam(data, sr)
        assert jump <= near and burst < 0.5, (name, jump, near, burst)
        edge = f"seam jump {jump:3.0f} (biggest step near it {near:.0f}), seam highs {burst:.2f} of the loudest elsewhere"
    else:
        edge = f"ends {int(data[0]):+d} / {int(data[-1]):+d}"
    short = "" if want is None or loud > want - 0.5 else f"  ({want - loud:.1f} dB under, held by the peak)"
    print(f"  {name:15s} {len(x) / sr:5.2f} s  {len(data) * 2 + 44:9,d} bytes  peak {peak:.2f}  "
          f"loudness {loud:6.1f} dB  clipped {clipped}  {edge}{short}")


def read(path):
    with wave.open(str(path), "rb") as w:
        return np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(np.float64) / 32767, w.getframerate()


def preview(path, loop_seconds=5.0, gap=0.5, steps=4, step_every=0.3):
    """A listening preview: [loop_seconds] of each tune, then every short
    sound in order, [gap] apart; each footstep [steps] times, [step_every]
    seconds apart, as if walking. Prints where each one starts."""
    path = pathlib.Path(path)
    sr, pieces, at = 22050, [], 0.0
    print(f"preview {path}:")
    for name in list(MUSIC) + list(SHORT):
        x, rate = read(OUT / f"{name}.wav")
        if rate != sr:
            x = resample_poly(x, sr, rate)
        if name in MUSIC:
            x = x[: int(loop_seconds * sr)] * env(int(loop_seconds * sr), 0.01, 0.5, sr)
        elif name in STEPS:
            x = place(step_every * (steps - 1) + len(x) / sr, [(step_every * k, x) for k in range(steps)], sr)
        print(f"  {int(at // 60)}:{at % 60:04.1f}  {name}")
        pieces += [x, np.zeros(int((0.8 if name in MUSIC else gap) * sr))]
        at += (len(x) + len(pieces[-1])) / sr
    whole = np.concatenate(pieces)
    scratch = "/dev/shm" if os.path.isdir("/dev/shm") else tempfile.gettempdir()
    fd, wav = tempfile.mkstemp(suffix=".wav", dir=scratch)
    os.close(fd)
    try:
        write(wav, whole, np.abs(whole).max(), sr)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-c:a", "aac", "-b:a", "96k", str(path)], check=True)
    finally:
        os.unlink(wav)
    print(f"  total {at:.1f} s")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / ".keep").unlink(missing_ok=True)
    print("music (16,000 Hz, loops), about 8 dB under the short sounds:")
    for name, (make, offset) in MUSIC.items():
        tune = make()
        x = tune.render()
        assert 16 <= len(x) / LOOP_SR <= 20, (name, len(x) / LOOP_SR)
        report(name, write(OUT / f"{name}.wav", x, level(x, offset, LOOP_SR), LOOP_SR), LOOP_SR, True)
        over = loudness(tune.render(band=False), LOOP_SR) - loudness(tune.render(lead=False), LOOP_SR)
        print(f"  {'':15s} the tune is {over:.1f} dB over the band (through a phone)")
    print(f"footsteps and short sounds (22,050 Hz), loudness {TARGET:.0f} dB plus or minus, peaks at most {MAX_PEAK}:")
    for name, (make, offset) in SHORT.items():
        x = tidy(phone_ready(make()))
        assert len(x) / SR <= LONGEST[name], (name, len(x) / SR)
        data = write(OUT / f"{name}.wav", x, level(x, offset), SR)
        assert data[0] == 0 and data[-1] == 0, name
        report(name, data, SR, False, TARGET + offset)
    names = {p.stem for p in OUT.glob("*.wav")}
    assert names == set(MUSIC) | set(SHORT), names ^ (set(MUSIC) | set(SHORT))
    assert {p.name for p in OUT.iterdir()} == {f"{n}.wav" for n in names}, "only the sounds belong in the folder"
    total = sum(p.stat().st_size for p in OUT.glob("*.wav"))
    print(f"{len(MUSIC) + len(SHORT)} sounds, {total:,} bytes ({total / 1024 / 1024:.2f} MiB) in {OUT}")
    assert total < LIMIT, f"the sounds must stay under {LIMIT:,} bytes"
    if len(sys.argv) == 3 and sys.argv[1] == "preview":
        preview(sys.argv[2])


if __name__ == "__main__":
    main()

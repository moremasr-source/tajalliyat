"""Calm soundtrack per video: sea waves as the bed, a quiet pad, one soft bell at the name reveal.
usage: audio.py <id> <out.wav>   (loudness is normalised afterwards with ffmpeg loudnorm)"""
import numpy as np, wave, sys
vid, out = sys.argv[1], sys.argv[2]
SR, DUR = 44100, 44.0
n = int(SR * DUR); t = np.arange(n) / SR
rng = np.random.default_rng(11)
env = lambda a, b, fi, fo: np.clip((t - a) / fi, 0, 1) * np.clip((b - t) / fo, 0, 1) * ((t >= a) & (t <= b))

def onepole(x, fc):
    """simple low-pass, cutoff fc (Hz), via cumulative exponential smoothing"""
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); acc = 0.0
    # vectorised in blocks for speed
    from scipy.signal import lfilter
    return lfilter([1 - a], [1, -a], x)

def waves(seed, period=9.5):
    r = np.random.default_rng(seed)
    white = r.standard_normal(n)
    body = onepole(onepole(white, 380), 380)          # deep rumble of the water
    foam = onepole(white, 2400) - onepole(white, 700)  # hiss of the breaking crest
    body /= np.abs(body).max(); foam /= np.abs(foam).max()
    out = np.zeros(n)
    # each wave: slow swell, then a soft break and a long wash back
    starts = np.cumsum(r.uniform(period * .8, period * 1.2, 12)) - period * .6
    for s in starts:
        tt = t - s
        swell = np.where((tt > 0) & (tt < 3.2), (tt / 3.2) ** 2, 0)
        wash = np.where(tt >= 3.2, np.exp(-(tt - 3.2) / 2.6), 0)
        e = swell + wash
        out += e * (.75 * body + .35 * foam * np.where(tt >= 2.8, np.exp(-(tt - 2.8) / 1.4), 0))
    return out / np.abs(out).max()

def pad(freqs):
    return sum(np.sin(2 * np.pi * f * t + i) * (.55 + .45 * np.sin(2 * np.pi * .05 * t + i)) for i, f in enumerate(freqs)) / len(freqs)

def bell(at, base):
    b = np.zeros(n); m = t >= at; tt = t[m] - at
    for f, a, d in ((base, 1, 2.6), (base * 2, .35, 1.6), (base * 3, .15, 1.0)):
        b[m] += a * np.sin(2 * np.pi * f * tt) * np.exp(-tt / d) * np.clip(tt / .01, 0, 1)
    return b

CH = {'latif': ([98,146.83,196,246.94],[130.81,196,261.63,329.63],523.25),
      'hakim': ([110,164.81,220,277.18],[146.83,220,293.66,369.99],587.33),
      'wali': ([98,130.81,196,233.08],[130.81,196,261.63,311.13],440),
      'wadud': ([110,138.59,220,277.18],[146.83,185,293.66,369.99],554.37),
      'wakil': ([98,146.83,196,293.66],[130.81,196,261.63,392],659.25)}
sea = waves({'rahman': 1, 'tawwab': 2, 'shakur': 3, 'latif': 4, 'hakim': 5, 'wali': 6, 'wadud': 7, 'wakil': 8}[vid])
if vid == 'rahman':
    music = .22 * pad([110, 164.81, 220, 261.63]) * env(2, 34.5, 6, 2) + .25 * pad([130.81, 196, 261.63, 329.63]) * env(33.5, 44, 3, 3)
    hb = np.zeros(n)
    for k in range(14, 24):
        for off, amp in ((0, 1.0), (.26, .55)):
            m = (t >= k + off) & (t < k + off + .25); tt = t[m] - k - off
            hb[m] += amp * np.sin(2 * np.pi * (55 - 20 * tt) * tt) * np.exp(-tt * 22)
    extra = .22 * hb * env(14, 23.6, 1, .4) + .05 * bell(34.0, 523.25)
    quiet = env(23.6, 25.6, .4, .4)  # the pause before the question
elif vid == 'tawwab':
    music = .22 * pad([98, 146.83, 196, 233.08]) * env(2, 31, 6, 2) + .25 * pad([130.81, 196, 261.63, 329.63]) * env(30, 44, 3, 3)
    extra = .05 * bell(31.6, 440); quiet = np.zeros(n)
elif vid in CH:
    a, b, bf = CH[vid]
    music = .22 * pad(a) * env(2, 34, 6, 2) + .25 * pad(b) * env(32, 44, 3, 3)
    extra = .05 * bell(33.8, bf); quiet = np.zeros(n)
else:
    music = .22 * pad([110, 146.83, 220, 277.18]) * env(2, 34, 6, 2) + .25 * pad([146.83, 220, 293.66, 369.99]) * env(32, 44, 3, 3)
    steps = np.zeros(n)
    for k in np.arange(1.0, 10.6, .66):
        m = (t >= k) & (t < k + .12); tt = t[m] - k
        steps[m] += np.sin(2 * np.pi * (90 - 200 * tt) * tt) * np.exp(-tt * 40)
    extra = .12 * steps * env(.8, 10.8, .8, .4) + .05 * bell(33.6, 587.33); quiet = np.zeros(n)

mix = .55 * sea * (1 - .7 * quiet) + music * (1 - quiet) + extra
mix *= np.clip(t / 3.0, 0, 1) ** 1.5 * np.clip((DUR - t) / 2.5, 0, 1)   # slow fade in, gentle fade out
mix = mix / np.abs(mix).max() * .7
d = int(.006 * SR)
st = (np.stack([mix, np.concatenate([np.zeros(d), mix[:-d]])], 1) * 32767).astype(np.int16)
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes())

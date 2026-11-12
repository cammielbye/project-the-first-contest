# Procedural placeholder textures for the playtest table (Nov 11, 2026). Every texture tiles seamlessly: its noise is
# white noise filtered in frequency space, which is periodic by construction.
# Usage: python3 tools/textures/make_textures.py [out_dir]   (default: img/)
#   table-wood.jpg     walnut planks running left to right, for the tabletop
#   runner-weave.png   a grey twill weave with alpha, laid over the runner's colors with an overlay blend
#   binder-leather.jpg pebbled brown leather for the binder cover
#   binder-paper.jpg   cream paper with fibers for the binder's pages
import os, sys
import numpy as np
from PIL import Image

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', '..', 'img')
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(1103)

def noise(h, w, sy, sx, seed=None):
    """Periodic Gaussian-filtered noise, std 1. sy, sx: blur radius in pixels along y and x."""
    r = np.random.default_rng(seed) if seed is not None else rng
    f = np.fft.fft2(r.standard_normal((h, w)))
    ky = np.fft.fftfreq(h)[:, None]; kx = np.fft.fftfreq(w)[None, :]
    g = np.exp(-2 * (np.pi ** 2) * ((ky * sy) ** 2 + (kx * sx) ** 2))
    n = np.real(np.fft.ifft2(f * g))
    return (n - n.mean()) / (n.std() + 1e-9)

def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)

def hexrgb(s):
    s = s.lstrip('#'); return np.array([int(s[i:i + 2], 16) for i in (0, 2, 4)], float) / 255

def save(img, name, **kw):
    path = os.path.join(OUT, name)
    Image.fromarray(np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8)).save(path, **kw)
    print(name, os.path.getsize(path) // 1024, 'KB')

# ---------------------------------------------------------------- walnut planks
def wood(W=1024, H=1024, planks=5):
    ph = H // planks
    y, x = np.mgrid[0:H, 0:W].astype(float)
    out = np.zeros((H, W, 3))
    warp_big = noise(H, W, 60, 260)        # slow sway of the grain along the board
    warp_mid = noise(H, W, 10, 90)
    streak = noise(H, W, 0.9, 40)          # fine fibers along the board
    streak2 = noise(H, W, 2.2, 120)
    mottle = noise(H, W, 40, 160)
    pores = noise(H, W, 0.7, 6)
    early, late = hexrgb('#5a3a24'), hexrgb('#2a170c')
    for i in range(planks):
        y0 = i * ph
        rows = slice(y0, y0 + ph)
        r = np.random.default_rng(50 + i)
        tone = r.uniform(-0.06, 0.06)                       # each board a little lighter or darker
        k = r.uniform(0.045, 0.075)                         # ring spacing
        yl = y[rows] - y0 - ph * r.uniform(0.2, 0.8)
        # flat-sawn grain: rings bend into long cathedral arches where the board's centre wanders
        arch = (yl / ph) ** 2 * r.uniform(30, 55)
        field = arch + yl * k * r.uniform(0.3, 0.6) + warp_big[rows] * r.uniform(2.5, 4) + warp_mid[rows] * 0.6
        ring = field - np.floor(field)
        band = smoothstep(0.0, 0.55, ring) * (1 - smoothstep(0.7, 1.0, ring))   # light earlywood, sharp dark latewood
        t = 0.55 * band + 0.18 * (streak[rows] * 0.5 + 0.5) + 0.12 * (streak2[rows] * 0.5 + 0.5) + 0.06 * mottle[rows]
        t = np.clip(t + tone, 0, 1)
        col = late[None, None, :] * (1 - t[..., None]) + early[None, None, :] * t[..., None]
        # pores: short dark dashes along the grain
        pd = (pores[rows] > 2.3) * 0.35
        col *= (1 - pd[..., None])
        # board ends: one butt joint per row of boards
        jx = int(r.uniform(0.1, 0.9) * W)
        d = np.abs(((x[rows] - jx + W / 2) % W) - W / 2)
        col *= (1 - 0.55 * np.exp(-(d / 1.1) ** 2))[..., None]
        col += (0.05 * np.exp(-((x[rows] - jx - 2) / 1.2) ** 2))[..., None]
        # bevelled edges between boards: dark gap, a lit top edge, a shaded bottom edge
        yy = y[rows] - y0
        col *= (1 - 0.75 * np.exp(-(yy / 1.3) ** 2))[..., None]
        col += (0.07 * np.exp(-((yy - 3) / 1.6) ** 2))[..., None]
        col *= (1 - 0.22 * np.exp(-((ph - 1 - yy) / 3.0) ** 2))[..., None]
        out[rows] = col
    # a little varnish sheen breakup
    out *= (1 + 0.04 * noise(H, W, 3, 30))[..., None]
    return out

# ---------------------------------------------------------------- twill weave (luminance + alpha, for an overlay blend)
def weave(N=256, t=4):
    y, x = np.mgrid[0:N, 0:N].astype(float)
    i = (x // t).astype(int); j = (y // t).astype(int)
    up = ((i + j) % 4) < 2                       # 2/2 twill: warp on top two of every four
    fx = (x % t + 0.5) / t; fy = (y % t + 0.5) / t
    warp_prof = np.sin(np.pi * fx)               # a thread is a cylinder: lit in the middle
    weft_prof = np.sin(np.pi * fy)
    # where a thread dives under its neighbour it darkens
    nxt_up = (((i + j + 1) % 4) < 2); prv_up = (((i + j - 1) % 4) < 2)
    warp_dive = np.where(up & ~nxt_up, 1 - smoothstep(0.6, 1.0, fy), 1.0) * np.where(up & ~prv_up, smoothstep(0.0, 0.4, fy), 1.0)
    weft_dive = np.where(~up & nxt_up, 1 - smoothstep(0.6, 1.0, fx), 1.0) * np.where(~up & prv_up, smoothstep(0.0, 0.4, fx), 1.0)
    per_warp = np.random.default_rng(7).normal(0, 0.035, N // t)[i]    # threads vary a little
    per_weft = np.random.default_rng(8).normal(0, 0.035, N // t)[j]
    fib_v = noise(N, N, 3, 0.5, seed=11); fib_h = noise(N, N, 0.5, 3, seed=12)
    h = np.where(up, 0.35 + 0.5 * warp_prof * warp_dive + per_warp + 0.05 * fib_v,
                     0.30 + 0.5 * weft_prof * weft_dive + per_weft + 0.05 * fib_h)
    h += 0.012 * noise(N, N, 20, 20, seed=13)         # uneven dye, faint
    lum = np.clip(h - h.mean() + 0.5, 0, 1)             # centred on 0.5, so the overlay keeps the runner's own color
    lum = 0.5 + (lum - 0.5) * 1.15
    rgba = np.zeros((N, N, 4))
    rgba[..., :3] = np.clip(lum, 0, 1)[..., None]
    rgba[..., 3] = 0.9
    return rgba

# ---------------------------------------------------------------- pebbled leather
def leather(N=512, cell=9):
    g = N // cell
    r = np.random.default_rng(21)
    px = (np.arange(g)[None, :] + r.uniform(0.1, 0.9, (g, g))) * cell
    py = (np.arange(g)[:, None] + r.uniform(0.1, 0.9, (g, g))) * cell
    y, x = np.mgrid[0:N, 0:N].astype(float)
    cx = (x // cell).astype(int); cy = (y // cell).astype(int)
    d1 = np.full((N, N), 1e9); d2 = np.full((N, N), 1e9)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            gx = (cx + dx) % g; gy = (cy + dy) % g
            qx = px[gy, gx] + ((cx + dx) - gx) * cell * 0 + (np.floor((cx + dx) / g) * N)
            qy = py[gy, gx] + (np.floor((cy + dy) / g) * N)
            d = np.hypot(x - qx, y - qy)
            m = d < d1
            d2 = np.where(m, d1, np.minimum(d2, d)); d1 = np.where(m, d, d1)
    crease = d2 - d1
    hgt = smoothstep(0, cell * 0.45, crease) + 0.15 * noise(N, N, 1.2, 1.2, seed=22)
    hgt = hgt + 0.08 * noise(N, N, 30, 30, seed=23)
    gy_, gx_ = np.gradient(hgt)
    light = np.clip(0.8 + 1.1 * (-gx_ - gy_), 0, 1.35)       # lit from the top left
    base = hexrgb('#4e301e')
    mott = 1 + 0.10 * noise(N, N, 40, 40, seed=24) + 0.04 * noise(N, N, 6, 6, seed=25)
    col = base[None, None, :] * (light * mott)[..., None]
    col *= (0.82 + 0.18 * smoothstep(0, cell * 0.35, crease))[..., None]   # dark creases
    return col

# ---------------------------------------------------------------- paper
def paper(N=512):
    base = hexrgb('#e8dbbb')
    m = 0.014 * noise(N, N, 50, 50, seed=31) + 0.012 * noise(N, N, 8, 8, seed=32) + 0.014 * noise(N, N, 0.8, 0.8, seed=33)
    fib = np.zeros((N, N))
    r = np.random.default_rng(34)
    for _ in range(260):                          # stray fibers: short soft curves
        x0, y0 = r.uniform(0, N, 2); a = r.uniform(0, np.pi); L = r.uniform(8, 26); bend = r.uniform(-0.08, 0.08)
        for s in np.linspace(0, L, int(L * 2)):
            xx = int(x0 + np.cos(a + bend * s) * s) % N; yy = int(y0 + np.sin(a + bend * s) * s) % N
            fib[yy, xx] += 1
    from scipy.ndimage import gaussian_filter
    fib = gaussian_filter(fib, 0.6, mode='wrap')
    col = base[None, None, :] * (1 + m)[..., None] - 0.05 * fib[..., None] * np.array([0.6, 0.7, 0.9])
    return col

if __name__ == '__main__':
    save(wood(), 'table-wood.jpg', quality=84, optimize=True, progressive=True)
    w = weave()
    Image.fromarray(np.clip(w * 255 + 0.5, 0, 255).astype(np.uint8), 'RGBA').save(os.path.join(OUT, 'runner-weave.png'), optimize=True)
    print('runner-weave.png', os.path.getsize(os.path.join(OUT, 'runner-weave.png')) // 1024, 'KB')
    save(leather(), 'binder-leather.jpg', quality=86, optimize=True, progressive=True)
    save(paper(), 'binder-paper.jpg', quality=86, optimize=True, progressive=True)

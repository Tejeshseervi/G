import base64
import io
import os
from pathlib import Path

import streamlit as st
from PIL import Image, ImageFilter, ImageOps

st.set_page_config(
    page_title="A Little Surprise ♡",
    page_icon="♡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

BASE_DIR = Path(__file__).parent
PHOTO_PATH = BASE_DIR / "gai3.jpg"
AUDIO_PATH = BASE_DIR / "jahan.mp3"
# Local Windows fallback, useful if the assets are still in Downloads.
if not PHOTO_PATH.exists():
    PHOTO_PATH = Path(r"C:\Users\seerv\Downloads\gai3.jpg")
if not AUDIO_PATH.exists():
    AUDIO_PATH = Path(r"C:\Users\seerv\Downloads\jahan.mp3")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=Playfair+Display:wght@400;500;600&display=swap');
  html, body, [data-testid="stAppViewContainer"] {
      background: #ffffff !important;
      color: #242424 !important;
      font-family: 'DM Sans', sans-serif;
  }
  [data-testid="stHeader"], [data-testid="stToolbar"], #MainMenu, footer {
      visibility: hidden;
  }
  [data-testid="stMainBlockContainer"] {
      max-width: 760px;
      padding-top: 2.4rem;
      padding-bottom: 3rem;
  }
  .eyebrow {
      text-align:center; color:#858585; font-size:11px; letter-spacing:3px;
      margin: 8px 0 24px; font-weight:600;
  }
  .headline {
      font-family:'Playfair Display', Georgia, serif;
      text-align:center; font-size:clamp(30px, 6vw, 44px);
      line-height:1.15; font-weight:400; color:#242424; margin:0 0 12px;
  }
  .subheadline {
      text-align:center; color:#858585; font-size:14px; line-height:1.7;
      margin:0 auto 25px; max-width:400px;
  }
  .portrait-shell {
      max-width: 360px; margin: 0 auto 22px; padding: 9px;
      background:#fafafa; border:1px solid #f0f0f0; border-radius:18px;
  }
  .portrait-shell img { display:block; width:100%; height:auto; border-radius:11px; }
  .button-hint { text-align:center; color:#929292; font-size:12px; margin-top:12px; }
  .birthday-message {
      font-family:'Playfair Display', Georgia, serif; text-align:center;
      font-size:clamp(25px, 5vw, 36px); color:#282828; line-height:1.3;
      margin:26px auto 10px;
  }
  .birthday-note {
      text-align:center; max-width:480px; margin:0 auto; color:#777;
      line-height:1.8; font-size:14px; white-space:pre-wrap;
  }
  .stButton > button {
      display:block; margin:0 auto; border:0; border-radius:999px;
      padding:14px 27px; background:#222222; color:white;
      font-family:'DM Sans', sans-serif; font-size:14px; font-weight:500;
      transition:transform .2s ease, background .2s ease;
  }
  .stButton > button:hover { background:#3b3b3b; color:white; transform:translateY(-1px); }
  .stButton > button:focus { color:white; border:0; box-shadow:none; }
  @media(max-width:600px) {
      [data-testid="stMainBlockContainer"] { padding:1.4rem 1rem 2rem; }
      .portrait-shell { max-width:100%; }
  }
</style>
""", unsafe_allow_html=True)

def load_portrait():
    if PHOTO_PATH.exists():
        try:
            im = Image.open(PHOTO_PATH).convert("RGB")
            return ImageOps.fit(im, (720, 900), method=Image.Resampling.LANCZOS)
        except Exception:
            return None
    return None

def oilify(image):
    """Create a soft, painterly base image using Pillow filters."""
    # Smooth fine photographic detail while preserving recognizable shapes.
    im = image.filter(ImageFilter.ModeFilter(size=3))
    # Preserve facial features and fine details; avoid aggressive smoothing.
    im = im.filter(ImageFilter.SMOOTH)
    im = ImageOps.autocontrast(im, cutoff=0.5)
    # Very subtle color smoothing gives a painterly feel without changing the subject.
    return im

def image_data_uri(image, fmt="JPEG", quality=88):
    buff = io.BytesIO()
    image.save(buff, format=fmt, quality=quality)
    encoded = base64.b64encode(buff.getvalue()).decode("ascii")
    mime = "image/jpeg" if fmt.upper() in ("JPEG", "JPG") else "image/png"
    return f"data:{mime};base64,{encoded}"

def audio_data_uri(path):
    if not path.exists():
        return ""
    try:
        raw = path.read_bytes()
        return "data:audio/mpeg;base64," + base64.b64encode(raw).decode("ascii")
    except Exception:
        return ""


HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  * { box-sizing:border-box; }
  body { margin:0; background:#fff; }
  .stage { width:100%; max-width:600px; margin:0 auto; }
  canvas { display:block; width:100%; height:auto; background:#fff; border-radius:12px; }
</style>
</head>
<body>
<div class="stage"><canvas id="c" width="720" height="900"></canvas></div>
__AUDIO__
<script>
(() => {
  const canvas = document.getElementById('c');
  const ctx = canvas.getContext('2d', { alpha:false });
  const W = canvas.width, H = canvas.height;
  ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, W, H);

  const audio = document.getElementById('birthday-audio');
  if (audio) {
    audio.volume = 0.75;
    const tryPlay = () => audio.play().catch(() => {});
    tryPlay();
    // Fallback if the browser blocks autoplay: first tap starts the music.
    document.addEventListener('pointerdown', () => { if (audio.paused) tryPlay(); }, { once:true });
  }

  const img = new Image();
  img.onload = () => {
    // Coarse -> fine brush passes. Every stroke takes its colour from the ORIGINAL photo,
    // so the painting converges to the real image with no final "snap".
    const layers = [
      { step:30, r:20, ms:2500, jitter:.6, ang:.9 },
      { step:15, r:10, ms:3000, jitter:.6, ang:.9 },
      { step:8,  r:5.5, ms:3500, jitter:.5, ang:.6 },
      { step:4,  r:3.2, ms:4000, jitter:.3, ang:.4 },
      { step:2,  r:2.2, ms:3000, jitter:0,  ang:0  },
    ];

    const small = document.createElement('canvas');
    const sctx = small.getContext('2d', { willReadFrequently:true });

    const plan = layers.map(L => {
      const cols = Math.ceil(W / L.step), rows = Math.ceil(H / L.step);
      small.width = cols; small.height = rows;
      sctx.drawImage(img, 0, 0, cols, rows);          // downscale = averaged colour per cell
      const d = sctx.getImageData(0, 0, cols, rows).data;
      const strokes = [];
      for (let j = 0; j < rows; j++) for (let i = 0; i < cols; i++) {
        const k = (j * cols + i) * 4;
        strokes.push({
          x: (i + .5) * L.step + (Math.random() - .5) * L.step * L.jitter,
          y: (j + .5) * L.step + (Math.random() - .5) * L.step * L.jitter,
          c: `rgb(${d[k]},${d[k+1]},${d[k+2]})`,
          rx: L.r * (.8 + Math.random() * .5),
          ry: L.r * (.5 + Math.random() * .4) + (L.ang ? 0 : L.r * .4),
          a: (Math.random() - .5) * L.ang
        });
      }
      for (let i = strokes.length - 1; i > 0; i--) {   // shuffle
        const j = Math.floor(Math.random() * (i + 1));
        [strokes[i], strokes[j]] = [strokes[j], strokes[i]];
      }
      return { L, strokes, done:0 };
    });

    const total = layers.reduce((s, L) => s + L.ms, 0);
    const t0 = performance.now();

    function frame(now) {
      const elapsed = now - t0;
      let acc = 0;
      for (const p of plan) {
        const prog = Math.min(1, Math.max(0, (elapsed - acc) / p.L.ms));
        const target = Math.floor(prog * p.strokes.length);
        while (p.done < target) {
          const s = p.strokes[p.done++];
          ctx.save();
          ctx.translate(s.x, s.y); ctx.rotate(s.a);
          ctx.fillStyle = s.c;
          ctx.beginPath(); ctx.ellipse(0, 0, s.rx, s.ry, 0, 0, Math.PI * 2); ctx.fill();
          ctx.restore();
        }
        acc += p.L.ms;
      }
      if (elapsed < total) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  };
  img.src = "__PHOTO__";
})();
</script>
</body>
</html>
"""

portrait = load_portrait()
portrait_uri = image_data_uri(portrait, quality=92) if portrait is not None else ""

st.markdown('<div class="eyebrow">A LITTLE SURPRISE</div>', unsafe_allow_html=True)
st.markdown('<h1 class="headline">A little something<br>made just for you ♡</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="subheadline">Some things are better revealed one little stroke at a time.</p>',
    unsafe_allow_html=True,
)

if "started" not in st.session_state:
    st.session_state.started = False

if not st.session_state.started:
    if st.button("Begin your surprise ✨", use_container_width=False):
        st.session_state.started = True
        st.rerun()
else:
    if portrait is None:
        st.error("Photo not found. Keep gai3.jpg in the same folder as app.py.")
    else:
        # Canvas animation is client-side; no page refresh is needed during painting.
        audio_uri = audio_data_uri(AUDIO_PATH)
        audio_markup = (
            f'<audio id="birthday-audio" src="{audio_uri}" preload="auto"></audio>'
            if audio_uri else ""
        )
        html = HTML_TEMPLATE.replace("__PHOTO__", portrait_uri).replace("__AUDIO__", audio_markup)
        st.components.v1.html(html, height=950, scrolling=False)

    if st.button("Start the surprise again ↻"):
        st.session_state.started = False
        st.rerun()
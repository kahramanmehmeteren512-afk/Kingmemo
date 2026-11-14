from flask import Flask, request, render_template_string, send_from_directory
from PIL import Image, ImageEnhance, ImageOps, ImageFilter
from werkzeug.utils import secure_filename
import os, uuid

app = Flask(__name__)

os.makedirs("static/uploads", exist_ok=True)
os.makedirs("static/edited", exist_ok=True)

HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>KING PHOTO STUDIO</title>
<style>
*{box-sizing:border-box}
body{margin:0;background:#0d0c14;color:white;font-family:Arial}
header{text-align:center;padding:24px;background:#191426}
h1{color:#c18aff;margin:0}
main{max-width:600px;margin:auto;padding:16px}
.card{background:#1c1929;padding:17px;border-radius:18px;margin-bottom:16px}
h3{color:#c18aff}
img{width:100%;max-height:420px;object-fit:contain;border-radius:12px;background:#08080c}
input[type=file]{width:100%;padding:12px;background:#302940;color:white}
input[type=range]{width:100%;accent-color:#b66aff}
label{display:block;margin-top:15px;color:#ddd}
button{background:#914cff;color:white;border:0;border-radius:10px;padding:13px;margin-top:10px;width:100%;font-weight:bold}
.secondary{background:#383044}
.ai{background:linear-gradient(90deg,#7135d5,#bd68ff)}
small{color:#aaa}
</style>
</head>
<body>
<header>
<h1>👑 KING PHOTO STUDIO</h1>
<p>YOUR PHOTO. YOUR ART. YOUR KINGDOM.</p>
</header>
<main>
<div class="card">
<h3>📸 Fotoğraf yükle</h3>
<form action="/upload" method="post" enctype="multipart/form-data">
<input type="file" name="photo" accept="image/*" required>
<button>FOTOĞRAF SEÇ</button>
</form>
</div>

{% if filename %}
<div class="card">
<h3>🖼️ Fotoğrafın</h3>
<img src="/static/edited/{{filename}}">
</div>

<div class="card">
<h3>🤖 KING AI STUDIO</h3>
<p>Yapay zekâ ile arka planı otomatik kaldır.</p>
<form action="/remove-bg" method="post">
<input type="hidden" name="filename" value="{{filename}}">
<button class="ai">✂️ AI ARKA PLANI SİL</button>
</form>

{% if ai_filename %}
<h3>✨ AI SONUCU</h3>
<img src="/static/edited/{{ai_filename}}">
<a href="/download-ai/{{ai_filename}}">
<button class="secondary">⬇ ŞEFFAF PNG İNDİR</button>
</a>
{% endif %}
</div>

<div class="card">
<h3>🎨 Profesyonel filtreler</h3>
<form action="/filter" method="post">
<input type="hidden" name="filename" value="{{filename}}">
<button name="preset" value="cinematic">🎬 CINEMATIC</button>
<button name="preset" value="vintage">📷 VINTAGE</button>
<button name="preset" value="bw">⚫ SİYAH BEYAZ</button>
<button name="preset" value="hdr">✨ HDR</button>
<button name="preset" value="auto">🤖 OTOMATİK İYİLEŞTİR</button>
</form>
</div>

<div class="card">
<h3>⚙️ Manuel düzenleme</h3>
<form action="/edit" method="post">
<input type="hidden" name="filename" value="{{filename}}">
<label>☀️ Parlaklık</label>
<input type="range" name="brightness" min="0" max="200" value="100">
<label>◐ Kontrast</label>
<input type="range" name="contrast" min="0" max="200" value="100">
<label>🌈 Doygunluk</label>
<input type="range" name="color" min="0" max="200" value="100">
<label>✨ Keskinlik</label>
<input type="range" name="sharpness" min="0" max="300" value="100">
<button>AYARLARI UYGULA</button>
</form>
<form action="/reset" method="post">
<input type="hidden" name="filename" value="{{filename}}">
<button class="secondary">↩ ORİJİNALE DÖN</button>
</form>
<a href="/download/{{filename}}">
<button class="secondary">⬇ FOTOĞRAFI İNDİR</button>
</a>
</div>
{% endif %}
</main>
</body>
</html>
"""

def page(filename=None, ai_filename=None):
    return render_template_string(
        HTML, filename=filename, ai_filename=ai_filename
    )

def safe_name():
    return os.path.basename(request.form.get("filename", ""))

def original(filename):
    return Image.open("static/uploads/" + filename).convert("RGB")

@app.route("/")
def home():
    return page()

@app.route("/upload", methods=["POST"])
def upload():
    photo = request.files.get("photo")
    if not photo or not photo.filename:
        return "Fotoğraf seçilmedi", 400
    try:
        img = ImageOps.exif_transpose(Image.open(photo)).convert("RGB")
        filename = uuid.uuid4().hex + ".jpg"
        img.save("static/uploads/" + filename, quality=95)
        img.save("static/edited/" + filename, quality=95)
        return page(filename)
    except Exception:
        return "Fotoğraf okunamadı", 400

@app.route("/remove-bg", methods=["POST"])
def remove_bg():
    filename = safe_name()
    source = "static/uploads/" + filename

    if not filename or not os.path.isfile(source):
        return "Fotoğraf bulunamadı", 404

    from ai_engine import remove_background

    try:
        output = remove_background(source)
        ai_filename = os.path.basename(output)
        return page(filename, ai_filename)
    except Exception as error:
        return "AI işlem hatası: " + str(error), 500

@app.route("/filter", methods=["POST"])
def filter_photo():
    filename = safe_name()
    if not os.path.isfile("static/uploads/" + filename):
        return "Fotoğraf bulunamadı", 404

    img = original(filename)
    preset = request.form.get("preset")

    if preset == "cinematic":
        img = ImageEnhance.Contrast(img).enhance(1.25)
        img = ImageEnhance.Color(img).enhance(1.2)
        r, g, b = img.split()
        img = Image.merge("RGB", (
            r.point(lambda x: min(255, int(x * 1.06))),
            g.point(lambda x: min(255, int(x * 1.01))),
            b.point(lambda x: min(255, int(x * 0.94)))
        ))
    elif preset == "vintage":
        gray = ImageOps.grayscale(img)
        img = ImageOps.colorize(gray, "#34251d", "#f2d6a0")
        img = ImageEnhance.Contrast(img).enhance(0.9)
    elif preset == "bw":
        img = ImageOps.grayscale(img).convert("RGB")
        img = ImageEnhance.Contrast(img).enhance(1.2)
    elif preset == "hdr":
        img = ImageOps.autocontrast(img, cutoff=1)
        img = ImageEnhance.Color(img).enhance(1.25)
        img = ImageEnhance.Contrast(img).enhance(1.25)
        img = img.filter(ImageFilter.UnsharpMask(2, 140, 3))
    elif preset == "auto":
        img = ImageOps.autocontrast(img, cutoff=1)
        img = ImageEnhance.Color(img).enhance(1.08)
        img = ImageEnhance.Contrast(img).enhance(1.12)
        img = ImageEnhance.Sharpness(img).enhance(1.2)

    img.save("static/edited/" + filename, quality=95)
    return page(filename)

@app.route("/edit", methods=["POST"])
def edit():
    filename = safe_name()
    if not os.path.isfile("static/uploads/" + filename):
        return "Fotoğraf bulunamadı", 404

    img = original(filename)
    for key, cls in [
        ("brightness", ImageEnhance.Brightness),
        ("contrast", ImageEnhance.Contrast),
        ("color", ImageEnhance.Color),
        ("sharpness", ImageEnhance.Sharpness)
    ]:
        value = max(0, min(300, float(request.form.get(key, 100)))) / 100
        img = cls(img).enhance(value)

    img.save("static/edited/" + filename, quality=95)
    return page(filename)

@app.route("/reset", methods=["POST"])
def reset():
    filename = safe_name()
    if not filename or not os.path.isfile("static/uploads/" + filename):
        return "Fotoğraf bulunamadı", 404
    original(filename).save("static/edited/" + filename, quality=95)
    return page(filename)

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(
        "static/edited", os.path.basename(filename), as_attachment=True
    )

@app.route("/download-ai/<filename>")
def download_ai(filename):
    return send_from_directory(
        "static/edited", os.path.basename(filename), as_attachment=True
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
PY

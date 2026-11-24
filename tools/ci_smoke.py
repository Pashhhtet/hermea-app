"""Проверка после установки (GitHub Actions на Windows и macOS).
Запуск: <venv python> tools/ci_smoke.py "<папка Hermea Photo>"."""
import json, os, subprocess, sys, time, urllib.request

ROOT = sys.argv[1]
PROG = os.path.join(ROOT, "_program")
sys.path.insert(0, PROG)
os.chdir(PROG)
ok = lambda m: print("OK  ", m, flush=True)

import numpy as np, cv2
import hermea, quality, app_contract, app_svk, app_clients, app_market, app_searches  # noqa
ok("модули загружаются")

# фото: синтетическая «комната» с наклонёнными вертикалями
img = np.full((900, 1200, 3), 200, np.uint8)
for x in range(150, 1100, 160):
    cv2.line(img, (x, 60), (x + 40, 860), (60, 60, 60), 6)
img[:, :, 0] = (img[:, :, 0] * 0.8).astype(np.uint8)
out, how = quality.straighten(img, verbose=True)
out = hermea.add_logo(quality.sharpen(hermea.enhance(out)))
assert out.shape == img.shape
ok(f"обработка фото ({how})")

# договор: на пустом шаблоне из 4 страниц
from reportlab.pdfgen import canvas
os.makedirs(os.path.dirname(app_contract.TEMPLATE), exist_ok=True)
had = os.path.exists(app_contract.TEMPLATE)
if not had:
    c = canvas.Canvas(app_contract.TEMPLATE, pagesize=(594.96, 841.92))
    for i in range(4):
        c.drawString(40, 800, f"page {i + 1}"); c.showPage()
    c.save()
outpdf = os.path.join(ROOT, "smoke_contract.pdf")
app_contract.build({"name": "Олена Коваленко", "address": "ul. Marszałkowska 1, Warszawa", "id_doc": "FE 123456",
                    "pesel": "95010112345", "package": "SMART", "viewed": [{"date": "24.11.2026", "address": "ul. Test 1", "rooms": "2", "rent": 3500}]}, outpdf)
from pypdf import PdfReader
assert len(PdfReader(outpdf).pages) == 4
if not had:
    os.remove(app_contract.TEMPLATE)
ok("договор PDF")

# окно-сервер
env = dict(os.environ)
p = subprocess.Popen([sys.executable, os.path.join(PROG, "hermea_app.py"), "--no-window"], cwd=PROG, env=env)
port_file = os.path.join(PROG, ".app_port")
for _ in range(120):
    if os.path.exists(port_file):
        break
    time.sleep(1)
port, tok = open(port_file, encoding="utf-8").read().split()
base = f"http://127.0.0.1:{port}"
op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
def get(path):
    return op.open(urllib.request.Request(base + path, headers={"X-Hermea": tok}), timeout=30).read()
def post(path, body):
    r = urllib.request.Request(base + path, data=json.dumps(body).encode(), headers={"X-Hermea": tok, "Content-Type": "application/json"})
    return json.loads(op.open(r, timeout=30).read())
assert get(f"/api/hello?t={tok}") == b"hermea"
st = json.loads(get("/api/state"))
assert st["version"], st
html = get(f"/?t={tok}").decode("utf-8")
assert "clients.js" in html and "__TOKEN__" not in html
for f in ("svk.js", "clients.js", "templates.js", "svk.css", "clients.css", "hermea.ico"):
    assert len(get("/app/" + f)) > 500, f
c = post("/api/client", {"op": "create", "data": {"name": "Test", "source": "direct"}})
assert c["svk"] == ["direct"], c
assert json.loads(get("/api/clients"))["clients"][0]["name"] == "Test"
ok(f"окно-сервер версии {st['version']} на порту {port}")
try:
    post("/api/quit", {})
except Exception:
    pass
time.sleep(2)
if p.poll() is None:
    p.kill()
print("SMOKE OK", flush=True)

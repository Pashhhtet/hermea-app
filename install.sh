#!/bin/bash
# Установка Hermea на Mac.
# Запуск: открыть «Терминал» и вставить одну строку:
#   curl -fsSL https://raw.githubusercontent.com/Pashhhtet/hermea-app/main/install.sh | bash
# Повторный запуск обновляет программу и ничего не стирает (квартиры, клиенты, СВК, настройки остаются).
set -e
REPO="Pashhhtet/hermea-app"
ROOT="${HERMEA_DIR:-$HOME/Desktop/Hermea Photo}"
PROG="$ROOT/_program"
step() { printf "\n\033[33m==> %s\033[0m\n" "$1"; }
get() { curl -fL --retry 3 --retry-delay 3 -o "$2" "$1"; }

printf "\033[36m=== Hermea: установка ===\033[0m\nПапка: %s\n" "$ROOT"

step "Python"
PY=""
for c in /usr/bin/python3 python3; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c "import sys; assert sys.version_info >= (3, 9)" 2>/dev/null; then PY="$(command -v "$c")"; break; fi
done
if [ -z "$PY" ]; then
  echo "Нужны инструменты разработчика macOS. Сейчас откроется окно установки."
  echo "Нажмите «Установить», дождитесь конца и вставьте эту команду ещё раз."
  xcode-select --install 2>/dev/null || true
  exit 1
fi
echo "Python: $PY"

step "Скачиваю программу"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
get "https://codeload.github.com/$REPO/tar.gz/refs/heads/main" "$TMP/hermea.tgz"
tar -xzf "$TMP/hermea.tgz" -C "$TMP"
SRC="$(find "$TMP" -maxdepth 1 -type d -name 'hermea-app*' | head -1)"
[ -n "$SRC" ] || { echo "Архив программы пустой"; exit 1; }
mkdir -p "$PROG" "$ROOT/Квартиры" "$ROOT/Hermea.app"
cp -R "$SRC/program/." "$PROG/"
cp -R "$SRC/bundle/." "$ROOT/Hermea.app/"
cp "$SRC/VERSION" "$PROG/VERSION"
printf '{"repo": "%s", "branch": "main"}\n' "$REPO" > "$PROG/update.json"
[ -f "$ROOT/ссылки.txt" ] || : > "$ROOT/ссылки.txt"
[ -f "$PROG/telegram.txt" ] || printf '# Токен бота от @BotFather после TOKEN=\nTOKEN=\nCHAT_ID=\n' > "$PROG/telegram.txt"
chmod +x "$ROOT/Hermea.app/Contents/MacOS/Hermea" "$PROG"/*.command 2>/dev/null || true

step "Библиотеки (5-10 минут, один раз)"
if [ -d "$PROG/.venv" ] && ! "$PROG/.venv/bin/python" -m pip --version >/dev/null 2>&1; then rm -rf "$PROG/.venv"; fi
[ -d "$PROG/.venv" ] || "$PY" -m venv "$PROG/.venv"
VPY="$PROG/.venv/bin/python"
"$VPY" -m pip install --upgrade pip -q --disable-pip-version-check
"$VPY" -m pip install -q --disable-pip-version-check torch opencv-python-headless pillow numpy curl_cffi certifi open_clip_torch pypdf "reportlab>=4,<4.3"

if [ -z "$HERMEA_SKIP_MODELS" ]; then
  step "Нейросети (около 600 МБ, один раз)"
  fetch_model() {   # имя, ссылка
    if [ -s "$PROG/$1" ] && [ "$(stat -f%z "$PROG/$1" 2>/dev/null || stat -c%s "$PROG/$1")" -gt 1000000 ]; then return; fi
    echo "Скачиваю $1..."
    get "$2" "$PROG/$1" || { rm -f "$PROG/$1"; echo "Не скачалось: $1 (программа будет работать без него)"; }
  }
  fetch_model big-lama.pt https://github.com/enesmsahin/simple-lama-inpainting/releases/download/v0.1.0/big-lama.pt
  fetch_model realesr-general-x4v3.pth https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-general-x4v3.pth
  fetch_model clip-rn50-cc12m.pt https://github.com/mlfoundations/open_clip/releases/download/v0.2-weights/rn50-quickgelu-cc12m-f000538c.pt
fi

xattr -dr com.apple.quarantine "$ROOT" 2>/dev/null || true
printf "\n\033[32mГотово! Hermea.app лежит в папке «Hermea Photo» на рабочем столе.\033[0m\n"
echo "Обновления приходят сами: в программе появится кнопка «Обновить»."
if [ -z "$HERMEA_NO_LAUNCH" ]; then open "$ROOT/Hermea.app"; fi

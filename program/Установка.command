#!/bin/bash
# Установка программы HERMEA (запускается один раз)
D="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$D/hermea.py" ]; then cd "$D"; else cd "$D/_program"; fi
echo "=== Установка HERMEA ==="
# снять блокировку macOS с файлов, полученных через Telegram/интернет
xattr -dr com.apple.quarantine "$D" 2>/dev/null
chmod +x "$D"/*.command "$D"/_program/*.command 2>/dev/null
if ! python3 -c "import sys; assert sys.version_info >= (3,9)" 2>/dev/null; then
  echo "Не найден Python 3. Сейчас откроется окно установки инструментов macOS."
  echo "Установи их, затем запусти эту установку ещё раз."
  xcode-select --install 2>/dev/null
  read -p "Нажми Enter, чтобы закрыть..."; exit 1
fi
# если папку переносили, старое окружение ломается — тогда создаём заново
if [ -d .venv ] && ! .venv/bin/python -m pip --version >/dev/null 2>&1; then
  echo "Окружение от старого места папки — пересоздаю..."
  rm -rf .venv
fi
python3 -m venv .venv || { echo "Ошибка создания окружения"; read -p "Enter..."; exit 1; }
.venv/bin/python -m pip install --upgrade pip -q
echo "Ставлю библиотеки (несколько минут)..."
.venv/bin/python -m pip install -q torch opencv-python-headless pillow numpy curl_cffi certifi open_clip_torch || { echo "Ошибка установки библиотек"; read -p "Enter..."; exit 1; }
if [ ! -s big-lama.pt ]; then
  echo "Скачиваю нейросеть для удаления водяного знака (~200 МБ)..."
  curl -L --fail -o big-lama.pt https://github.com/enesmsahin/simple-lama-inpainting/releases/download/v0.1.0/big-lama.pt || { echo "Не удалось скачать модель"; read -p "Enter..."; exit 1; }
fi
if [ ! -s realesr-general-x4v3.pth ]; then
  curl -L --fail -o realesr-general-x4v3.pth https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-general-x4v3.pth || rm -f realesr-general-x4v3.pth
fi
if [ ! -s clip-rn50-cc12m.pt ]; then
  echo "Скачиваю нейросеть для поиска кухни (~400 МБ)..."
  curl -L --fail -o clip-rn50-cc12m.pt https://github.com/mlfoundations/open_clip/releases/download/v0.2-weights/rn50-quickgelu-cc12m-f000538c.pt || { rm -f clip-rn50-cc12m.pt; echo "Не удалось скачать модель кухни — программа будет работать без неё"; }
fi
chmod +x Запустить.command ../Запустить.command Установка.command 2>/dev/null
echo ""
echo "✓ Готово! Теперь вставь ссылки в «ссылки.txt» и дважды кликни «Запустить.command»."
read -p "Нажми Enter, чтобы закрыть..."
osascript -e 'tell application "Terminal" to close (every window whose name contains "Установка.command")' >/dev/null 2>&1 &
exit 0

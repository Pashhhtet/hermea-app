#!/bin/bash
D="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$D/hermea.py" ]; then cd "$D"; else cd "$D/_program"; fi
if [ ! -x .venv/bin/python ]; then
  echo "Сначала запусти установку: Установка.command"
else
  .venv/bin/python -W ignore hermea.py --test-telegram
fi
echo ""
read -p "Нажми Enter, чтобы закрыть..."
osascript -e 'tell application "Terminal" to close (every window whose name contains "Проверить Telegram.command")' >/dev/null 2>&1 &
exit 0

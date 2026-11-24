#!/bin/bash
# Запасной способ открыть окно Hermea, если Hermea.app почему-то не открывается.
# Здесь будут видны ошибки — пришли скриншот этого окна, если что-то не так.
D="$(cd -P "$(dirname "$0")" && pwd -P)"
if [ -f "$D/hermea_app.py" ]; then cd "$D"; else cd "$D/_program"; fi
if [ ! -x .venv/bin/python ]; then
  echo "Сначала запусти установку: Установка.command"
  read -p "Нажми Enter, чтобы закрыть..."; exit 1
fi
echo "Окно Hermea открывается… Это окно Терминала можно свернуть (не закрывай, пока работаешь)."
.venv/bin/python -W ignore hermea_app.py || { echo ""; read -p "Hermea закрылась с ошибкой. Нажми Enter, чтобы закрыть..."; }
exit 0

# Hermea

Программа агента Hermea для Mac: обработка фото квартир (Otodom, OLX, Morizon, Gratka), отправка в Telegram,
слежение за поиском Otodom и ежедневная СВК.

Этот репозиторий — канал обновлений. Установленная программа читает `manifest.json`,
скачивает изменённые файлы, проверяет sha256 и перезапускается сама.

* `program/` — содержимое папки `_program`
* `bundle/` — содержимое `Hermea.app`
* новая версия: поменять файлы, дописать заметки в `tools/notes.json`, запустить `python3 tools/build_manifest.py X.Y.Z`, закоммитить.

Токен Telegram, модели и личные данные (`telegram.txt`, `app_*.json`, `*.pt`) сюда не попадают.

## Установка на новый компьютер

**Mac** — открыть «Терминал» и вставить:

    curl -fsSL https://raw.githubusercontent.com/Pashhhtet/hermea-app/main/install.sh | bash

**Windows 10/11** — открыть PowerShell и вставить:

    irm https://raw.githubusercontent.com/Pashhhtet/hermea-app/main/install.ps1 | iex

Установка занимает 10–15 минут (библиотеки и нейросети скачиваются один раз).
Повторный запуск команды обновляет программу и ничего не стирает.
Шаблон договора каждый загружает сам: Настройки → «Шаблон договора» → «Загрузить PDF».

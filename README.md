# Hermea

Программа агента Hermea для Mac: обработка фото квартир (Otodom, OLX, Morizon, Gratka), отправка в Telegram,
слежение за поиском Otodom и ежедневная СВК.

Этот репозиторий — канал обновлений. Установленная программа читает `manifest.json`,
скачивает изменённые файлы, проверяет sha256 и перезапускается сама.

* `program/` — содержимое папки `_program`
* `bundle/` — содержимое `Hermea.app`
* новая версия: поменять файлы, дописать заметки в `tools/notes.json`, запустить `python3 tools/build_manifest.py X.Y.Z`, закоммитить.

Токен Telegram, модели и личные данные (`telegram.txt`, `app_*.json`, `*.pt`) сюда не попадают.

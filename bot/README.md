# ReverseX — NORMAL Windows installer project

Как получить обычный установщик (.exe) без PowerShell-танцев:
1) Создай приватный репозиторий на GitHub.
2) Залей сюда всё содержимое этой папки.
3) Вкладка **Actions** → запусти workflow **Build ReverseX Installer** (кнопка "Run workflow").
4) Через пару минут в **Artifacts** появится:
   - `installer\dist\ReverseXSetup.exe` — обычный инсталлятор (Next → Next → Finish).
   - `dist\ReverseX\` — portable-версия (папка с `ReverseX.exe`).

Дальше просто запускаешь `ReverseXSetup.exe` на своём ПК — и всё ставится как обычная программа:
- `C:\Program Files\ReverseX\ReverseX.exe`
- Ярлык на рабочем столе и в "Пуск"
- Ассоциация `.stl` файлов → двойной клик открывает ReverseX

Примечание: для тяжёлых библиотек используется mambaforge (conda-forge) на runner'е. На твоём ПК ничего ставить не надо.

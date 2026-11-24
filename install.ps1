# Установка Hermea на Windows 10/11.
# Запуск: открыть PowerShell и вставить одну строку:
#   irm https://raw.githubusercontent.com/Pashhhtet/hermea-app/main/install.ps1 | iex
# Повторный запуск обновляет программу и ничего не стирает (квартиры, клиенты, СВК, настройки остаются).

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

$Repo = "Pashhhtet/hermea-app"
$Desktop = [Environment]::GetFolderPath("Desktop")
$Root = if ($env:HERMEA_DIR) { $env:HERMEA_DIR } else { Join-Path $Desktop "Hermea Photo" }
$Prog = Join-Path $Root "_program"

function Step($t) { Write-Host ""; Write-Host "==> $t" -ForegroundColor Yellow }
function Get-File($url, $out) {
    for ($i = 1; $i -le 3; $i++) {
        try { Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $out; return } catch {
            if ($i -eq 3) { throw }
            Start-Sleep -Seconds (3 * $i)
        }
    }
}

Write-Host "=== Hermea: установка ===" -ForegroundColor Cyan
Write-Host "Папка: $Root"

# ---------------------------------------------------------------- Python 3.11 (только для этого пользователя)
Step "Python"
$py = $null
$cands = @("$env:LOCALAPPDATA\Programs\Python\Python311\python.exe", "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe")
foreach ($c in $cands) { if (Test-Path $c) { $py = $c; break } }
if (-not $py) {
    try {
        $p = & py -3.11 -c "import sys; print(sys.executable)" 2>$null
        if ($LASTEXITCODE -eq 0 -and $p) { $py = $p.Trim() }
    } catch {}
}
if (-not $py) {
    Write-Host "Скачиваю Python 3.11 (около 25 МБ)..."
    $exe = Join-Path $env:TEMP "python-3.11.9-amd64.exe"
    Get-File "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe" $exe
    Start-Process -Wait -FilePath $exe -ArgumentList "/quiet InstallAllUsers=0 PrependPath=0 Include_launcher=0 Include_test=0 Shortcuts=0 AssociateFiles=0"
    $py = "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe"
    if (-not (Test-Path $py)) { throw "Python не установился. Запустите команду ещё раз." }
}
Write-Host "Python: $py"

# ---------------------------------------------------------------- программа с GitHub
Step "Скачиваю программу"
$tmp = Join-Path $env:TEMP ("hermea_" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$zip = Join-Path $tmp "hermea.zip"
Get-File "https://codeload.github.com/$Repo/zip/refs/heads/main" $zip
Expand-Archive -Path $zip -DestinationPath $tmp -Force
$src = Get-ChildItem -Path $tmp -Directory | Where-Object { $_.Name -like "hermea-app*" } | Select-Object -First 1
if (-not $src) { throw "Архив программы пустой" }

New-Item -ItemType Directory -Force -Path $Prog, (Join-Path $Root "Квартиры") | Out-Null
Get-ChildItem -Path (Join-Path $src.FullName "program") -Recurse -File | Where-Object { $_.Extension -ne ".command" } | ForEach-Object {
    $rel = $_.FullName.Substring((Join-Path $src.FullName "program").Length + 1)
    $dst = Join-Path $Prog $rel
    New-Item -ItemType Directory -Force -Path (Split-Path $dst) | Out-Null
    Copy-Item -Force $_.FullName $dst
}
Copy-Item -Force (Join-Path $src.FullName "VERSION") (Join-Path $Prog "VERSION")
[IO.File]::WriteAllText((Join-Path $Prog "update.json"), '{"repo": "' + $Repo + '", "branch": "main"}', (New-Object System.Text.UTF8Encoding $false))
$links = Join-Path $Root "ссылки.txt"
if (-not (Test-Path $links)) { [IO.File]::WriteAllText($links, "", (New-Object System.Text.UTF8Encoding $false)) }
$tg = Join-Path $Prog "telegram.txt"
if (-not (Test-Path $tg)) {
    [IO.File]::WriteAllText($tg, "# Токен бота от @BotFather после TOKEN=`r`nTOKEN=`r`nCHAT_ID=`r`n", (New-Object System.Text.UTF8Encoding $false))
}

# ---------------------------------------------------------------- библиотеки
Step "Библиотеки (5-10 минут, один раз)"
$venv = Join-Path $Prog ".venv"
if ((Test-Path $venv) -and -not (Test-Path (Join-Path $venv "Scripts\python.exe"))) { Remove-Item -Recurse -Force $venv }
if (-not (Test-Path $venv)) { & $py -m venv $venv; if ($LASTEXITCODE -ne 0) { throw "Не получилось создать окружение Python" } }
$vpy = Join-Path $venv "Scripts\python.exe"
& $vpy -m pip install --upgrade pip -q --disable-pip-version-check
& $vpy -m pip install -q --disable-pip-version-check torch torchvision --index-url https://download.pytorch.org/whl/cpu
if ($LASTEXITCODE -ne 0) { throw "Не установилась библиотека torch" }
& $vpy -m pip install -q --disable-pip-version-check opencv-python-headless pillow numpy curl_cffi certifi open_clip_torch pypdf reportlab pillow-heif
if ($LASTEXITCODE -ne 0) { throw "Не установились библиотеки" }

# ---------------------------------------------------------------- нейросети
if (-not $env:HERMEA_SKIP_MODELS) {
    Step "Нейросети (около 600 МБ, один раз)"
    $models = @(
        @("big-lama.pt", "https://github.com/enesmsahin/simple-lama-inpainting/releases/download/v0.1.0/big-lama.pt"),
        @("realesr-general-x4v3.pth", "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-general-x4v3.pth"),
        @("clip-rn50-cc12m.pt", "https://github.com/mlfoundations/open_clip/releases/download/v0.2-weights/rn50-quickgelu-cc12m-f000538c.pt")
    )
    foreach ($m in $models) {
        $out = Join-Path $Prog $m[0]
        if ((Test-Path $out) -and ((Get-Item $out).Length -gt 1MB)) { continue }
        Write-Host "Скачиваю $($m[0])..."
        try { Get-File $m[1] $out } catch { Write-Host "Не скачалось: $($m[0]) (программа будет работать без него)" -ForegroundColor Red }
    }
}

# ---------------------------------------------------------------- ярлык на рабочем столе
Step "Ярлык Hermea на рабочем столе"
$ws = New-Object -ComObject WScript.Shell
$lnk = $ws.CreateShortcut((Join-Path $Desktop "Hermea.lnk"))
$lnk.TargetPath = Join-Path $venv "Scripts\pythonw.exe"
$lnk.Arguments = '"' + (Join-Path $Prog "hermea_app.py") + '"'
$lnk.WorkingDirectory = $Prog
$lnk.IconLocation = (Join-Path $Prog "app\hermea.ico")
$lnk.Description = "Hermea"
$lnk.Save()

Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
Write-Host ""
Write-Host "Готово! На рабочем столе появился ярлык Hermea." -ForegroundColor Green
Write-Host "Обновления приходят сами: в программе появится кнопка «Обновить»."
if (-not $env:HERMEA_NO_LAUNCH) {
    Start-Process -FilePath (Join-Path $venv "Scripts\pythonw.exe") -ArgumentList ('"' + (Join-Path $Prog "hermea_app.py") + '"') -WorkingDirectory $Prog
}

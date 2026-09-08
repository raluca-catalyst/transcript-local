# Setup transcript-local pe Windows (rulat o singură dată):
# instalează dependențele Python, creează folderele și pune un shortcut pe Desktop.
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "1/3 Instalez dependențele Python..."
python -m pip install --upgrade pip | Out-Null
python -m pip install -r requirements.txt

Write-Host "2/3 Creez folderele de lucru..."
foreach ($dir in @("recordings", "transcripts", "minute")) {
    New-Item -ItemType Directory -Force $dir | Out-Null
}

Write-Host "3/3 Pun shortcut-ul 'Transcript meeting' pe Desktop..."
$desktop = [Environment]::GetFolderPath("Desktop")
$shell = New-Object -ComObject WScript.Shell
$lnk = $shell.CreateShortcut((Join-Path $desktop "Transcript meeting.lnk"))
$lnk.TargetPath = $env:ComSpec
$lnk.Arguments = "/k python meet.py"
$lnk.WorkingDirectory = $PSScriptRoot
$lnk.Description = "Înregistrează meetingul și scoate transcriptul (Ctrl+C la final)"
$lnk.Save()

Write-Host ""
Write-Host "Setup complet."
Write-Host "Modelul de transcriere (~1,6 GB) se descarcă singur la prima înregistrare;"
Write-Host "prima transcriere durează mai mult din cauza asta. Ai nevoie de internet doar atunci."

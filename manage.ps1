param(
    [ValidateSet('help', 'install', 'run', 'test', 'check')]
    [string]$Task = 'help',

    [ValidateRange(1, 65535)]
    [int]$Port = 8000
)

$ErrorActionPreference = 'Stop'

if ($Task -eq 'help') {
    Write-Output 'Uso: .\manage.ps1 <install|run|test|check> [-Port 8000]'
    Write-Output 'Crie primeiro a .venv com: py -m venv .venv'
    exit 0
}

# Resolve os caminhos a partir do script, mesmo quando chamado de outra pasta.
$projectPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $projectPython)) {
    throw 'Ambiente virtual ausente. Na raiz do projeto, execute: py -m venv .venv'
}

$resultCode = 0
Push-Location -LiteralPath $PSScriptRoot
try {
    switch ($Task) {
        'install' { & $projectPython -m pip install -r requirements.txt }
        'run' { & $projectPython -m uvicorn app.main:app --host 127.0.0.1 --port $Port }
        'test' { & $projectPython -m pytest tests/test_tasks.py -v }
        'check' { & $projectPython -m pip check }
    }
    # Propaga falhas do Python para o terminal ou ferramenta de automação.
    $resultCode = $LASTEXITCODE
}
finally {
    Pop-Location
}
exit $resultCode

Param(
    [int]$Port = 3000,
    [switch]$Reinstall
)

Write-Host "Iniciando API (porta $Port) com Python 3.11 e venv..."

$ErrorActionPreference = "Stop"

# Projeto raiz
$Root = Split-Path (Split-Path $PSScriptRoot -Parent)
$Backend = $PSScriptRoot
$VenvPath = Join-Path $Root ".venv"
$Python311 = "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python311\python.exe"

function Ensure-Venv {
    if (!(Test-Path $VenvPath)) {
        Write-Host "Criando venv com Python 3.11..."
        & $Python311 -m venv $VenvPath
    }
}

function Activate-Venv {
    $activate = Join-Path $VenvPath "Scripts\Activate.ps1"
    if (Test-Path $activate) {
        . $activate
    } else {
        throw "Arquivo de ativação do venv não encontrado: $activate"
    }
}

function Install-Requirements {
    $Req = Join-Path $Backend "requirements.txt"
    if (!(Test-Path $Req)) { throw "Arquivo de requisitos não encontrado: $Req" }
    Write-Host "Instalando dependências de $Req..."
    python -m pip install -U pip wheel
    pip install -r $Req
}

# Fluxo
Ensure-Venv
Activate-Venv

if ($Reinstall) {
    Write-Host "Reinstalação solicitada (-Reinstall)."
    Install-Requirements
} else {
    # Verifica se Pillow está instalado (para evitar erro PIL)
    try {
        python -c "import PIL"
    } catch {
        Write-Host "Pillow não encontrado. Instalando dependências..."
        Install-Requirements
    }
}

# Subir API
Set-Location $Backend

# Determinar IP host e argumentos
$HostIP = "0.0.0.0"
$reloadArg = "--reload"
Write-Host ("[run] Iniciando uvicorn em {0}:{1} {2}" -f $HostIP, $Port, $reloadArg)

python -m uvicorn app.main:app --host $HostIP --port $Port $reloadArg

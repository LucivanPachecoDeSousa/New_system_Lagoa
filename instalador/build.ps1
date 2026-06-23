param(
    [switch]$Clean,
    [switch]$SkipPyInstaller,
    [switch]$SkipInno
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$instalador = $PSScriptRoot
$output = Join-Path $instalador "output"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Build - Sistema Campo Fértil" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($Clean) {
    Write-Host ">>> Limpando builds anteriores..." -ForegroundColor Yellow
    $folders = @(
        (Join-Path $root "build"),
        (Join-Path $root "dist"),
        (Join-Path $instalador "__pycache__"),
        $output
    )
    foreach ($f in $folders) {
        if (Test-Path $f) { Remove-Item -Recurse -Force $f; Write-Host "  Removido: $f" }
    }
    $specFiles = @(
        (Join-Path $root "*.spec"),
        (Join-Path $instalador "*.spec")
    )
    foreach ($p in $specFiles) { Remove-Item -Force $p -ErrorAction SilentlyContinue }
    Write-Host "  Limpeza concluida!" -ForegroundColor Green
    Write-Host ""
}

# Step 1: Install dependencies
Write-Host ">>> Instalando dependencias..." -ForegroundColor Yellow
try {
    py -m pip install -r "$root\requirements.txt" --quiet 2>&1 | Out-Null
    Write-Host "  Dependencias OK!" -ForegroundColor Green
} catch {
    Write-Warning "  Aviso: erro ao instalar dependencias. Continuando..."
}

# Step 2: Generate icon
Write-Host ">>> Gerando icone..." -ForegroundColor Yellow
py "$instalador\gerar_icone.py"
if (-not (Test-Path "$instalador\icone.ico")) {
    throw "Falha ao gerar icone!"
}
Write-Host "  Icone gerado!" -ForegroundColor Green
Write-Host ""

if (-not $SkipPyInstaller) {
    # Step 3: Build with PyInstaller
    Write-Host ">>> Compilando executavel com PyInstaller..." -ForegroundColor Yellow

    $specFile = "$instalador\sistema_fazenda.spec"
    $prevLocation = Get-Location
    try {
        Set-Location $instalador
        py -m PyInstaller --clean $specFile --noconfirm 2>&1
        if ($LASTEXITCODE -ne 0) { throw "PyInstaller falhou (exit code: $LASTEXITCODE)" }
    } finally {
        Set-Location $prevLocation
    }

    Write-Host "  Executavel compilado!" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host ">>> Pulando PyInstaller (--SkipPyInstaller)" -ForegroundColor DarkYellow
}

if (-not $SkipInno) {
    # Step 4: Build installer with Inno Setup
    Write-Host ">>> Criando instalador com Inno Setup..." -ForegroundColor Yellow

    $isccPaths = @(
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
        "${env:ProgramFiles}\Inno Setup 6\ISCC.exe",
        "${env:ProgramFiles(x86)}\Inno Setup 5\ISCC.exe",
        "${env:ProgramFiles}\Inno Setup 5\ISCC.exe"
    )
    $iscc = $null
    foreach ($p in $isccPaths) { if (Test-Path $p) { $iscc = $p; break } }
    if (-not $iscc) { throw "Inno Setup nao encontrado!" }

    $distPath = Join-Path $root "dist\SistemaFazenda"
    if (-not (Test-Path $distPath)) {
        throw "Diretorio do executavel nao encontrado em: $distPath. Execute sem -SkipPyInstaller primeiro."
    }

    # Copy build output to instalador folder for Inno Setup
    $innoSource = Join-Path $instalador "SistemaFazenda"
    if (Test-Path $innoSource) { Remove-Item -Recurse -Force $innoSource }
    Copy-Item -Recurse $distPath $innoSource
    Copy-Item "$instalador\icone.ico" "$innoSource\" -Force

    # Ensure output folder exists
    if (-not (Test-Path $output)) { New-Item -ItemType Directory -Path $output -Force | Out-Null }

    $prevLocation = Get-Location
    try {
        Set-Location $instalador
        & $iscc "instalador.iss" /O$output 2>&1
        if ($LASTEXITCODE -ne 0) { throw "Inno Setup falhou (exit code: $LASTEXITCODE)" }
    } finally {
        Set-Location $prevLocation
    }

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  INSTALADOR CRIADO COM SUCESSO!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green

    $installerFile = Get-ChildItem $output -Filter "*.exe" | Select-Object -First 1
    if ($installerFile) {
        Write-Host ""
        Write-Host "  Arquivo: $($installerFile.FullName)" -ForegroundColor White
        Write-Host "  Tamanho: $('{0:N2} MB' -f ($installerFile.Length / 1MB))" -ForegroundColor White
    }
} else {
    Write-Host ">>> Pulando Inno Setup (--SkipInno)" -ForegroundColor DarkYellow
}

Write-Host ""
Write-Host ">>> Build finalizado!" -ForegroundColor Cyan

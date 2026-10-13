# One-command launcher (Windows): bring the stack up AND open the CTF in a browser.
# The browser lands on the provisioning loading screen and auto-advances to CTFd
# the moment the seeder finishes.
Set-Location -Path $PSScriptRoot

# First run on a fresh clone has no .env (it's gitignored). Create one from the
# template with freshly generated secrets so the stack is self-contained — no
# manual editing required. Delete .env to regenerate.
if (-not (Test-Path ".env")) {
    Write-Host "[start] no .env found - generating one from .env.example with fresh secrets"
    Copy-Item ".env.example" ".env"
    function New-Hex([int]$n){ -join (1..$n | ForEach-Object { '{0:x}' -f (Get-Random -Maximum 16) }) }
    $dbp = New-Hex 32; $sk = New-Hex 48; $adminpw = New-Hex 18
    (Get-Content ".env") `
        -replace '^DB_PASSWORD=.*', "DB_PASSWORD=$dbp" `
        -replace '^CTFD_SECRET_KEY=.*', "CTFD_SECRET_KEY=$sk" `
        -replace '^CTFD_ADMIN_PASSWORD=.*', "CTFD_ADMIN_PASSWORD=$adminpw" |
        Set-Content ".env" -Encoding ascii
    Write-Host "[start] admin account -> user: admin  password: $adminpw"
    Write-Host "[start] (saved in .env - keep it; it is gitignored and not shared)"
}

$labip = "127.0.0.1"
if (Test-Path ".env") {
    $line = Select-String -Path ".env" -Pattern '^LAB_IP=' | Select-Object -First 1
    if ($line) {
        $val = ($line.Line -replace '^LAB_IP=', '').Trim()
        if ($val) { $labip = $val }
    }
}
$url = "http://${labip}:8000/"

Write-Host "[start] bringing the stack up (first run builds + provisions - ~1-2 min)..."
# Prefer the project's subnet (172.20.0.0/24) when it is free; if another Docker
# network already uses it, fall back to Docker's auto-assignment so the stack
# still comes up instead of failing with "pool overlaps".
$composeArgs = @("-f","docker-compose.yml","-f","docker-compose.pin.yml")
$nets = docker network ls -q
if ($nets) {
    $info = (docker network inspect $nets 2>$null | Out-String)
    if ($info -match "172\.20\.0\.0/24") {
        Write-Host "[start] 172.20.0.0/24 is already in use - letting Docker auto-assign a subnet"
        $composeArgs = @()
    }
}
docker compose @composeArgs up -d --build

Write-Host "[start] opening $url"
Start-Process $url

Write-Host "[start] The loading screen switches to the CTF automatically when ready."
Write-Host "[start] Follow provisioning with:  docker compose logs -f seeder"

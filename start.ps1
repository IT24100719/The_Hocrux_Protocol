# One-command launcher (Windows): bring the stack up AND open the CTF in a browser.
# The browser lands on the provisioning loading screen and auto-advances to CTFd
# the moment the seeder finishes.
Set-Location -Path $PSScriptRoot

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
docker compose up -d --build

Write-Host "[start] opening $url"
Start-Process $url

Write-Host "[start] The loading screen switches to the CTF automatically when ready."
Write-Host "[start] Follow provisioning with:  docker compose logs -f seeder"

# CHAMP-QN Crypto Readiness Scanner launcher (Windows PowerShell).
#
# Docker Compose cannot reliably pick-and-print a free host port through a
# static port mapping, so this script finds one starting at 8080, exports it
# for docker-compose.yml to consume, brings the stack up, and prints the
# final browser URL.

$ErrorActionPreference = "Stop"

Set-Location (Join-Path $PSScriptRoot "..")

function Test-PortFree {
    param([int]$Port)
    try {
        $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $Port)
        $listener.Start()
        $listener.Stop()
        return $true
    } catch {
        return $false
    }
}

$startPort = if ($env:CHAMPQN_HOST_PORT) { [int]$env:CHAMPQN_HOST_PORT } else { 8080 }
$port = $startPort

for ($i = 0; $i -le 20; $i++) {
    if (Test-PortFree -Port $port) { break }
    $port += 1
}

$env:CHAMPQN_HOST_PORT = "$port"

Write-Host "Starting CHAMP-QN Crypto Readiness Scanner..."
Write-Host "Selected host port: $port"

docker compose up --build -d

Write-Host ""
Write-Host "CHAMP-QN Crypto Readiness Scanner is available at:"
Write-Host "http://localhost:$port"

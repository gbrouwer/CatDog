#!/usr/bin/env pwsh

# === CONFIG ===
$piUser = "gbrouwer"
$piHostName = "192.168.178.80"
$remoteSessionName = "catdog_agent"
$pythonMatch = "agent.py|sound_emitter|ultrasonic_sensor|vibes.py|gcc.py|launcher.py"

function Cleanup-Remote {
    param(
        [string]$TargetHost,
        [string]$User,
        [string]$Label
    )

    Write-Host "`nCleaning $Label ($User@$TargetHost)..."

    $remoteScript = @"
echo 'Killing Python processes...'
ps aux | grep -E "$pythonMatch" | grep -v grep | awk '{print $2}' | xargs -r kill -9

echo 'Killing leftover tmux sessions...'
tmux ls 2>/dev/null | grep -i '$remoteSessionName' | cut -d: -f1 | xargs -r tmux kill-session -t

echo 'Done cleaning $Label.'
"@

    ssh "$User@$TargetHost" $remoteScript
}

function Cleanup-Local {
    Write-Host "`nCleaning local PC..."

    Write-Host "Killing Python processes..."
    Get-Process python -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.Id -Force }

    Write-Host "Killing tmux sessions (if applicable)..."
    bash -c "tmux ls 2>/dev/null | grep -i $remoteSessionName | cut -d: -f1 | xargs -r tmux kill-session -t"

    Write-Host "Done cleaning local PC."
}

# === EXECUTION ===
Cleanup-Remote -TargetHost $piHostName -User $piUser -Label "Raspberry Pi"
Cleanup-Local
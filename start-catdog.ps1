# Run the cleanup script first
Write-Host "🔁 Running cleanup..."
& "$PSScriptRoot\\reset.ps1"

# Launch the primary agent
Write-Host "🚀 Launching CatDog agent..."
python "C:\Core\Dev\CatDog\src\agent.py" --config "C:\Core\Dev\CatDog\configs\catdog_test.yaml" --primary

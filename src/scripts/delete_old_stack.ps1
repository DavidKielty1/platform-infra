# Delete Old Stack Script

Write-Host "Starting old stack deletion..." -ForegroundColor Yellow

# Function to handle errors
function Write-ErrorLog {
    param($Message)
    Write-Host "ERROR: $Message" -ForegroundColor Red
    exit 1
}

function Write-SuccessLog {
    param($Message)
    Write-Host "SUCCESS: $Message" -ForegroundColor Green
}

try {
    Write-Host "Deleting old PlatformStack..."
    npx cdk destroy --force --app "py app.py" PlatformStack
    Write-SuccessLog "Old PlatformStack deleted successfully"
} catch {
    Write-ErrorLog "Failed to delete old PlatformStack: $($_.Exception.Message)"
}

Write-Host "`nOld stack deletion completed!" -ForegroundColor Green 
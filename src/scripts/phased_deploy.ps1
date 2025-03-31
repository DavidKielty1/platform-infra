# Phased Deployment Script

Write-Host "Starting phased deployment..." -ForegroundColor Yellow

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

# Phase 1: Deploy VPC and networking components
Write-Host "`nPhase 1: Deploying VPC and networking components..." -ForegroundColor Yellow
$response = Read-Host "Do you want to proceed with Phase 1? (y/n)"
if ($response -eq 'y') {
    try {
        Write-Host "Deploying networking stack..."
        npx cdk deploy --app "py app.py" NetworkingStack
        Write-SuccessLog "Networking stack deployed successfully"
        
        # Wait for networking resources to be ready
        Write-Host "Waiting for networking resources to be ready..."
        Start-Sleep -Seconds 30
    } catch {
        Write-ErrorLog "Failed to deploy networking stack: $($_.Exception.Message)"
    }
} else {
    Write-Host "Skipping Phase 1"
}

# Phase 2: Deploy container infrastructure
Write-Host "`nPhase 2: Deploying container infrastructure..." -ForegroundColor Yellow
$response = Read-Host "Do you want to proceed with Phase 2? (y/n)"
if ($response -eq 'y') {
    try {
        Write-Host "Deploying container stack..."
        npx cdk deploy --app "py app.py" ContainerStack
        Write-SuccessLog "Container stack deployed successfully"
    } catch {
        Write-ErrorLog "Failed to deploy container stack: $($_.Exception.Message)"
    }
} else {
    Write-Host "Skipping Phase 2"
}

Write-Host "`nPhased deployment completed!" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Push your container image to ECR"
Write-Host "2. Deploy your application using the container infrastructure" 
# Delete CloudFormation Stacks Script

Write-Host "Starting CloudFormation stacks deletion..." -ForegroundColor Yellow

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
    # List all stacks
    Write-Host "Listing CloudFormation stacks..."
    $stacks = aws cloudformation list-stacks --query 'StackSummaries[?contains(StackName, `platform-infra`) || contains(StackName, `PlatformStack`) || contains(StackName, `NetworkingStack`) || contains(StackName, `ContainerStack`)].StackName' --output text
    
    if ($stacks) {
        Write-Host "Found stacks:"
        $stacks.Split() | ForEach-Object {
            if ($_) {
                $stackName = $_
                Write-Host "Deleting stack: $stackName"
                aws cloudformation delete-stack --stack-name $stackName
                Write-Host "Waiting for stack deletion..."
                aws cloudformation wait stack-delete-complete --stack-name $stackName
                Write-SuccessLog "Successfully deleted stack: $stackName"
            }
        }
        Write-SuccessLog "All stacks deleted successfully"
    } else {
        Write-Host "No matching stacks found"
    }
} catch {
    Write-ErrorLog "Failed to delete stacks: $($_.Exception.Message)"
}

Write-Host "`nStack deletion completed!" -ForegroundColor Green 
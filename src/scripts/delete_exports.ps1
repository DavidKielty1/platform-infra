# Delete CloudFormation Exports Script

Write-Host "Starting CloudFormation exports deletion..." -ForegroundColor Yellow

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
    # List all exports
    Write-Host "Listing CloudFormation exports..."
    $exports = aws cloudformation list-exports --query 'Exports[*].[Name,ExportingStackId]' --output text
    
    if ($exports) {
        Write-Host "Found exports:"
        $exports.Split("`n") | ForEach-Object {
            if ($_) {
                $parts = $_.Split("`t")
                if ($parts.Count -eq 2) {
                    $exportName = $parts[0]
                    $stackId = $parts[1]
                    Write-Host "Found export: $exportName from stack: $stackId"
                    
                    # If this is a platform-infra export, we need to handle it
                    if ($exportName -like "platform-infra-*") {
                        Write-Host "Attempting to delete export: $exportName"
                        # First, try to delete the stack that created this export
                        $stackName = $stackId.Split("/")[-1]
                        Write-Host "Deleting stack: $stackName"
                        aws cloudformation delete-stack --stack-name $stackName
                        
                        # Wait for the stack to be deleted
                        Write-Host "Waiting for stack deletion..."
                        aws cloudformation wait stack-delete-complete --stack-name $stackName
                    }
                }
            }
        }
        Write-SuccessLog "CloudFormation exports deletion completed"
    } else {
        Write-Host "No CloudFormation exports found"
    }
} catch {
    Write-ErrorLog "Failed to delete CloudFormation exports: $($_.Exception.Message)"
}

Write-Host "`nCloudFormation exports cleanup completed!" -ForegroundColor Green 
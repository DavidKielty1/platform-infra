# AWS Resource Cleanup Script

Write-Host "Starting AWS resource cleanup..." -ForegroundColor Green

# Function to handle errors
function Write-ErrorLog {
    param($Message)
    Write-Host "ERROR: $Message" -ForegroundColor Red
}

function Write-SuccessLog {
    param($Message)
    Write-Host "SUCCESS: $Message" -ForegroundColor Green
}

# Get the current user's ARN
$userArn = aws sts get-caller-identity --query 'Arn' --output text
Write-Host "Current user ARN: $userArn" -ForegroundColor Yellow

# KMS keys to update
$kmsKeys = @(
    "04ec043d-2ef6-47ad-bdd0-da67c8918e65",
    "2f14ab3f-c021-45bd-a7f6-6683f31b6a32",
    "63ab1732-41bf-4426-b839-38811b14c821",
    "8696b399-74fa-46aa-95a6-7cc65c468e3f"
)

# First, update KMS key policies
Write-Host "`nUpdating KMS key policies..." -ForegroundColor Yellow

# Create a policy that allows key deletion
$policy = @"
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Enable IAM User Permissions",
            "Effect": "Allow",
            "Principal": {
                "AWS": "$userArn"
            },
            "Action": [
                "kms:ScheduleKeyDeletion",
                "kms:Delete*"
            ],
            "Resource": "*"
        }
    ]
}
"@

# Save the policy to a temporary file
$policy | Out-File -FilePath "kms-policy.json" -Encoding UTF8

foreach ($keyId in $kmsKeys) {
    try {
        Write-Host "`nUpdating policy for KMS key: $keyId" -ForegroundColor Yellow
        
        # First, get the current key policy
        Write-Host "Getting current policy..."
        $currentPolicy = aws kms get-key-policy --key-id $keyId --policy-name default --output text
        
        # Update the key policy
        Write-Host "Updating policy..."
        aws kms put-key-policy --key-id $keyId --policy-name default --policy (Get-Content "kms-policy.json" -Raw)
        
        Write-SuccessLog "Successfully updated policy for key: $keyId"
    } catch {
        Write-ErrorLog "Failed to update policy for KMS key $keyId`: $($_.Exception.Message)"
    }
}

# Clean up the temporary policy file
Remove-Item "kms-policy.json"

# Now proceed with resource cleanup
Write-Host "`nStarting resource cleanup..." -ForegroundColor Green

# Delete CloudWatch Log Groups
Write-Host "`nCleaning up CloudWatch Log Groups..." -ForegroundColor Yellow
try {
    $logGroups = aws logs describe-log-groups --query 'logGroups[*].logGroupName' --output text
    if ($logGroups) {
        $logGroups.Split() | ForEach-Object {
            if ($_) {
                Write-Host "Deleting log group: $_"
                aws logs delete-log-group --log-group-name $_
            }
        }
        Write-SuccessLog "CloudWatch Log Groups cleanup completed"
    } else {
        Write-Host "No CloudWatch Log Groups found"
    }
} catch {
    Write-ErrorLog "Failed to cleanup CloudWatch Log Groups: $($_.Exception.Message)"
}

# Delete ECS Clusters
Write-Host "`nCleaning up ECS Clusters..." -ForegroundColor Yellow
try {
    $clusters = aws ecs list-clusters --query 'clusterArns[]' --output text
    if ($clusters) {
        $clusters.Split() | ForEach-Object {
            if ($_) {
                Write-Host "Deleting ECS cluster: $_"
                aws ecs delete-cluster --cluster $_
            }
        }
        Write-SuccessLog "ECS Clusters cleanup completed"
    } else {
        Write-Host "No ECS Clusters found"
    }
} catch {
    Write-ErrorLog "Failed to cleanup ECS Clusters: $($_.Exception.Message)"
}

# Delete Security Groups (excluding default)
Write-Host "`nCleaning up Security Groups..." -ForegroundColor Yellow
try {
    $sgs = aws ec2 describe-security-groups --query 'SecurityGroups[?GroupName!=`default`].GroupId' --output text
    if ($sgs) {
        $sgs.Split() | ForEach-Object {
            if ($_) {
                Write-Host "Deleting security group: $_"
                aws ec2 delete-security-group --group-id $_
            }
        }
        Write-SuccessLog "Security Groups cleanup completed"
    } else {
        Write-Host "No Security Groups found (excluding default)"
    }
} catch {
    Write-ErrorLog "Failed to cleanup Security Groups: $($_.Exception.Message)"
}

# Delete VPCs (excluding default)
Write-Host "`nCleaning up VPCs..." -ForegroundColor Yellow
try {
    $vpcs = aws ec2 describe-vpcs --query 'Vpcs[?IsDefault==`false`].VpcId' --output text
    if ($vpcs) {
        $vpcs.Split() | ForEach-Object {
            if ($_) {
                Write-Host "Deleting VPC: $_"
                # Delete associated Internet Gateways
                $igws = aws ec2 describe-internet-gateways --filters "Name=attachment.vpc-id,Values=$_" --query 'InternetGateways[].InternetGatewayId' --output text
                $igws.Split() | ForEach-Object {
                    if ($_) {
                        Write-Host "Detaching and deleting Internet Gateway: $_"
                        aws ec2 detach-internet-gateway --internet-gateway-id $_ --vpc-id $_
                        aws ec2 delete-internet-gateway --internet-gateway-id $_
                    }
                }
                # Delete the VPC
                aws ec2 delete-vpc --vpc-id $_
            }
        }
        Write-SuccessLog "VPCs cleanup completed"
    } else {
        Write-Host "No VPCs found (excluding default)"
    }
} catch {
    Write-ErrorLog "Failed to cleanup VPCs: $($_.Exception.Message)"
}

# Delete KMS keys
Write-Host "`nCleaning up KMS Keys..." -ForegroundColor Yellow
foreach ($keyId in $kmsKeys) {
    try {
        Write-Host "Attempting to schedule deletion for KMS key: $keyId"
        aws kms schedule-key-deletion --key-id $keyId --pending-window-in-days 7
        Write-SuccessLog "Successfully scheduled deletion for key: $keyId"
    } catch {
        Write-ErrorLog "Failed to schedule deletion for KMS key $keyId`: $($_.Exception.Message)"
    }
}

Write-Host "`nCleanup script completed!" -ForegroundColor Green
Write-Host "Note: Some resources may require additional permissions to delete." -ForegroundColor Yellow
Write-Host "Please check the output above for any errors that may need manual intervention." -ForegroundColor Yellow 
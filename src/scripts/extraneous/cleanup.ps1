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

function Write-WarningLog {
    param($Message)
    Write-Host "WARNING: $Message" -ForegroundColor Yellow
}

# Get the current user's ARN
$userArn = aws sts get-caller-identity --query 'Arn' --output text
Write-Host "Current user ARN: $userArn" -ForegroundColor Yellow

# Set AWS Region if not set
if (-not $env:AWS_DEFAULT_REGION) {
    $env:AWS_DEFAULT_REGION = "eu-west-2"
    Write-WarningLog "AWS Region set to: $env:AWS_DEFAULT_REGION"
}

# Create KMS policy for key deletion
$kmsPolicy = @"
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
$kmsPolicy | Out-File -FilePath "kms-policy.json" -Encoding UTF8

# First, destroy CDK stack if it exists
Write-Host "`nDestroying CDK stack..." -ForegroundColor Yellow
try {
    npx cdk destroy --force --app "py app.py"
    Write-SuccessLog "CDK stack destroyed successfully"
} catch {
    Write-ErrorLog "Failed to destroy CDK stack: $($_.Exception.Message)"
}

# Clean up ECS resources
Write-Host "`nCleaning up ECS resources..." -ForegroundColor Yellow
try {
    $clusters = aws ecs list-clusters --query 'clusterArns[]' --output text
    if ($clusters) {
        $clusters.Split() | ForEach-Object {
            if ($_) {
                Write-Host "Processing ECS cluster: $_"
                
                # Get and delete services
                $services = aws ecs list-services --cluster $_ --query 'serviceArns[]' --output text
                if ($services) {
                    $services.Split() | ForEach-Object {
                        if ($_) {
                            Write-Host "Updating service desired count to 0: $_"
                            aws ecs update-service --cluster $_ --service $_ --desired-count 0
                            Write-Host "Deleting service: $_"
                            aws ecs delete-service --cluster $_ --service $_ --force
                        }
                    }
                }
                
                Write-Host "Deleting cluster: $_"
                aws ecs delete-cluster --cluster $_
            }
        }
        Write-SuccessLog "ECS resources cleanup completed"
    } else {
        Write-Host "No ECS Clusters found"
    }
} catch {
    Write-ErrorLog "Failed to cleanup ECS resources: $($_.Exception.Message)"
}

# Clean up VPC resources
Write-Host "`nCleaning up VPC resources..." -ForegroundColor Yellow
try {
    $vpcs = aws ec2 describe-vpcs --query 'Vpcs[?IsDefault==`false`].VpcId' --output text
    if ($vpcs) {
        $vpcs.Split() | ForEach-Object {
            if ($_) {
                $vpcId = $_
                Write-Host "Processing VPC: $vpcId"
                
                # Release Elastic IPs
                Write-Host "Releasing Elastic IPs..."
                $eips = aws ec2 describe-addresses --filters "Name=domain,Values=vpc" --query 'Addresses[*].AllocationId' --output text
                if ($eips) {
                    $eips.Split() | ForEach-Object {
                        if ($_) {
                            aws ec2 release-address --allocation-id $_
                            Write-Host "Released Elastic IP: $_"
                        }
                    }
                }
                
                # Delete NAT Gateways
                Write-Host "Deleting NAT Gateways..."
                $natGateways = aws ec2 describe-nat-gateways --filter "Name=vpc-id,Values=$vpcId" --query 'NatGateways[*].NatGatewayId' --output text
                if ($natGateways) {
                    $natGateways.Split() | ForEach-Object {
                        if ($_) {
                            aws ec2 delete-nat-gateway --nat-gateway-id $_
                            Write-Host "Waiting for NAT Gateway deletion: $_"
                            aws ec2 wait nat-gateway-available --nat-gateway-ids $_
                            Write-Host "Deleted NAT Gateway: $_"
                        }
                    }
                }
                
                # Delete Network Interfaces
                Write-Host "Deleting Network Interfaces..."
                $networkInterfaces = aws ec2 describe-network-interfaces --filters "Name=vpc-id,Values=$vpcId" --query 'NetworkInterfaces[*].NetworkInterfaceId' --output text
                if ($networkInterfaces) {
                    $networkInterfaces.Split() | ForEach-Object {
                        if ($_) {
                            aws ec2 delete-network-interface --network-interface-id $_
                            Write-Host "Deleted Network Interface: $_"
                        }
                    }
                }
                
                # Delete Security Groups
                Write-Host "Deleting Security Groups..."
                $securityGroups = aws ec2 describe-security-groups --filters "Name=vpc-id,Values=$vpcId" --query 'SecurityGroups[?GroupName!=`default`].GroupId' --output text
                if ($securityGroups) {
                    $securityGroups.Split() | ForEach-Object {
                        if ($_) {
                            aws ec2 delete-security-group --group-id $_
                            Write-Host "Deleted Security Group: $_"
                        }
                    }
                }
                
                # Detach and Delete Internet Gateway
                Write-Host "Detaching and Deleting Internet Gateway..."
                $igwId = aws ec2 describe-internet-gateways --filters "Name=attachment.vpc-id,Values=$vpcId" --query 'InternetGateways[*].InternetGatewayId' --output text
                if ($igwId) {
                    aws ec2 detach-internet-gateway --internet-gateway-id $igwId --vpc-id $vpcId
                    aws ec2 delete-internet-gateway --internet-gateway-id $igwId
                    Write-Host "Deleted Internet Gateway: $igwId"
                }
                
                # Delete Subnets
                Write-Host "Deleting Subnets..."
                $subnets = aws ec2 describe-subnets --filters "Name=vpc-id,Values=$vpcId" --query 'Subnets[*].SubnetId' --output text
                if ($subnets) {
                    $subnets.Split() | ForEach-Object {
                        if ($_) {
                            aws ec2 delete-subnet --subnet-id $_
                            Write-Host "Deleted Subnet: $_"
                        }
                    }
                }
                
                # Delete Route Tables
                Write-Host "Deleting Route Tables..."
                $routeTables = aws ec2 describe-route-tables --filters "Name=vpc-id,Values=$vpcId" --query 'RouteTables[?Associations[0].Main!=`true`].RouteTableId' --output text
                if ($routeTables) {
                    $routeTables.Split() | ForEach-Object {
                        if ($_) {
                            # Disassociate subnet associations
                            $associations = aws ec2 describe-route-tables --route-table-id $_ --query 'RouteTables[*].Associations[*].RouteTableAssociationId' --output text
                            if ($associations) {
                                $associations.Split() | ForEach-Object {
                                    if ($_) {
                                        aws ec2 disassociate-route-table --association-id $_
                                        Write-Host "Disassociated Route Table: $_"
                                    }
                                }
                            }
                            aws ec2 delete-route-table --route-table-id $_
                            Write-Host "Deleted Route Table: $_"
                        }
                    }
                }
                
                # Finally, delete the VPC
                Write-Host "Deleting VPC: $vpcId"
                aws ec2 delete-vpc --vpc-id $vpcId
                Write-Host "Deleted VPC: $vpcId"
            }
        }
        Write-SuccessLog "VPC resources cleanup completed"
    } else {
        Write-Host "No VPCs found (excluding default)"
    }
} catch {
    Write-ErrorLog "Failed to cleanup VPC resources: $($_.Exception.Message)"
}

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

# Clean up KMS keys
Write-Host "`nCleaning up KMS Keys..." -ForegroundColor Yellow
try {
    # Get all KMS keys
    $kmsKeys = aws kms list-keys --query 'Keys[*].KeyId' --output text
    if ($kmsKeys) {
        $kmsKeys.Split() | ForEach-Object {
            if ($_) {
                $keyId = $_
                Write-Host "Processing KMS key: $keyId"
                
                try {
                    # First, get the current key policy
                    Write-Host "Getting current policy..."
                    $currentPolicy = aws kms get-key-policy --key-id $keyId --policy-name default --output text
                    
                    # Update the key policy
                    Write-Host "Updating policy..."
                    aws kms put-key-policy --key-id $keyId --policy-name default --policy (Get-Content "kms-policy.json" -Raw)
                    
                    # Now try to schedule deletion
                    Write-Host "Scheduling deletion..."
                    aws kms schedule-key-deletion --key-id $keyId --pending-window-in-days 7
                    
                    Write-SuccessLog "Successfully scheduled deletion for key: $keyId"
                } catch {
                    if ($_.Exception.Message -like "*KMSInvalidStateException*") {
                        Write-Host "Key $keyId is already pending deletion"
                    } else {
                        Write-ErrorLog "Failed to process key $keyId`: $($_.Exception.Message)"
                    }
                }
            }
        }
        Write-SuccessLog "KMS keys cleanup completed"
    } else {
        Write-Host "No KMS keys found"
    }
} catch {
    Write-ErrorLog "Failed to cleanup KMS keys: $($_.Exception.Message)"
}

# Clean up Docker resources if docker-compose.yml exists
Write-Host "`nCleaning up Docker resources..." -ForegroundColor Yellow
try {
    if (Test-Path "docker-compose.yml") {
        docker-compose down -v
        docker system prune -f
        Write-SuccessLog "Docker resources cleaned up successfully"
    } else {
        Write-Host "docker-compose.yml not found, skipping Docker cleanup"
    }
} catch {
    Write-ErrorLog "Failed to cleanup Docker resources: $($_.Exception.Message)"
}

# Clean up CDK output
Write-Host "`nCleaning up CDK output..." -ForegroundColor Yellow
try {
    if (Test-Path "cdk.out") {
        Remove-Item -Recurse -Force "cdk.out"
        Write-SuccessLog "CDK output cleaned up successfully"
    } else {
        Write-Host "No CDK output directory found"
    }
} catch {
    Write-ErrorLog "Failed to cleanup CDK output: $($_.Exception.Message)"
}

# Clean up the temporary KMS policy file
Remove-Item "kms-policy.json"

Write-Host "`nCleanup script completed!" -ForegroundColor Green
Write-Host "Note: Some resources may require additional permissions to delete." -ForegroundColor Yellow
Write-Host "Please check the output above for any errors that may need manual intervention." -ForegroundColor Yellow 
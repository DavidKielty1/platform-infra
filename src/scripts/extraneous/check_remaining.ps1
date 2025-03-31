# AWS Resource Check Script

Write-Host "Checking for remaining AWS resources..." -ForegroundColor Yellow

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

# Check ECS Resources
Write-Host "`nChecking ECS Resources..." -ForegroundColor Yellow
try {
    $clusters = aws ecs list-clusters --query 'clusterArns[]' --output text
    if ($clusters) {
        Write-WarningLog "Found ECS Clusters:"
        $clusters.Split() | ForEach-Object {
            Write-Host "  - $_"
        }
    } else {
        Write-SuccessLog "No ECS Clusters found"
    }
} catch {
    Write-ErrorLog "Failed to check ECS resources: $($_.Exception.Message)"
}

# Check VPC Resources
Write-Host "`nChecking VPC Resources..." -ForegroundColor Yellow
try {
    $vpcs = aws ec2 describe-vpcs --query 'Vpcs[?IsDefault==`false`].VpcId' --output text
    if ($vpcs) {
        Write-WarningLog "Found VPCs:"
        $vpcs.Split() | ForEach-Object {
            Write-Host "  - $_"
        }
    } else {
        Write-SuccessLog "No VPCs found (excluding default)"
    }
} catch {
    Write-ErrorLog "Failed to check VPC resources: $($_.Exception.Message)"
}

# Check CloudWatch Log Groups
Write-Host "`nChecking CloudWatch Log Groups..." -ForegroundColor Yellow
try {
    $logGroups = aws logs describe-log-groups --query 'logGroups[*].logGroupName' --output text
    if ($logGroups) {
        Write-WarningLog "Found CloudWatch Log Groups:"
        $logGroups.Split() | ForEach-Object {
            Write-Host "  - $_"
        }
    } else {
        Write-SuccessLog "No CloudWatch Log Groups found"
    }
} catch {
    Write-ErrorLog "Failed to check CloudWatch Log Groups: $($_.Exception.Message)"
}

# Check KMS Keys
Write-Host "`nChecking KMS Keys..." -ForegroundColor Yellow
try {
    $kmsKeys = aws kms list-keys --query 'Keys[*].KeyId' --output text
    if ($kmsKeys) {
        Write-WarningLog "Found KMS Keys:"
        $kmsKeys.Split() | ForEach-Object {
            $keyId = $_
            $keyState = aws kms describe-key --key-id $keyId --query 'KeyMetadata.KeyState' --output text
            Write-Host "  - $keyId (State: $keyState)"
        }
    } else {
        Write-SuccessLog "No KMS Keys found"
    }
} catch {
    Write-ErrorLog "Failed to check KMS Keys: $($_.Exception.Message)"
}

# Check Security Groups
Write-Host "`nChecking Security Groups..." -ForegroundColor Yellow
try {
    $securityGroups = aws ec2 describe-security-groups --query 'SecurityGroups[?GroupName!=`default`].GroupId' --output text
    if ($securityGroups) {
        Write-WarningLog "Found Security Groups:"
        $securityGroups.Split() | ForEach-Object {
            Write-Host "  - $_"
        }
    } else {
        Write-SuccessLog "No Security Groups found (excluding default)"
    }
} catch {
    Write-ErrorLog "Failed to check Security Groups: $($_.Exception.Message)"
}

# Check Subnets
Write-Host "`nChecking Subnets..." -ForegroundColor Yellow
try {
    $subnets = aws ec2 describe-subnets --query 'Subnets[?VpcId!=`vpc-default`].SubnetId' --output text
    if ($subnets) {
        Write-WarningLog "Found Subnets:"
        $subnets.Split() | ForEach-Object {
            Write-Host "  - $_"
        }
    } else {
        Write-SuccessLog "No Subnets found (excluding default VPC)"
    }
} catch {
    Write-ErrorLog "Failed to check Subnets: $($_.Exception.Message)"
}

# Check Route Tables
Write-Host "`nChecking Route Tables..." -ForegroundColor Yellow
try {
    $routeTables = aws ec2 describe-route-tables --query 'RouteTables[?Associations[0].Main!=`true`].RouteTableId' --output text
    if ($routeTables) {
        Write-WarningLog "Found Route Tables:"
        $routeTables.Split() | ForEach-Object {
            Write-Host "  - $_"
        }
    } else {
        Write-SuccessLog "No Route Tables found (excluding main)"
    }
} catch {
    Write-ErrorLog "Failed to check Route Tables: $($_.Exception.Message)"
}

# Check Internet Gateways
Write-Host "`nChecking Internet Gateways..." -ForegroundColor Yellow
try {
    $igws = aws ec2 describe-internet-gateways --query 'InternetGateways[*].InternetGatewayId' --output text
    if ($igws) {
        Write-WarningLog "Found Internet Gateways:"
        $igws.Split() | ForEach-Object {
            Write-Host "  - $_"
        }
    } else {
        Write-SuccessLog "No Internet Gateways found"
    }
} catch {
    Write-ErrorLog "Failed to check Internet Gateways: $($_.Exception.Message)"
}

# Check NAT Gateways
Write-Host "`nChecking NAT Gateways..." -ForegroundColor Yellow
try {
    $natGateways = aws ec2 describe-nat-gateways --query 'NatGateways[*].NatGatewayId' --output text
    if ($natGateways) {
        Write-WarningLog "Found NAT Gateways:"
        $natGateways.Split() | ForEach-Object {
            Write-Host "  - $_"
        }
    } else {
        Write-SuccessLog "No NAT Gateways found"
    }
} catch {
    Write-ErrorLog "Failed to check NAT Gateways: $($_.Exception.Message)"
}

# Check Elastic IPs
Write-Host "`nChecking Elastic IPs..." -ForegroundColor Yellow
try {
    $eips = aws ec2 describe-addresses --query 'Addresses[*].AllocationId' --output text
    if ($eips) {
        Write-WarningLog "Found Elastic IPs:"
        $eips.Split() | ForEach-Object {
            Write-Host "  - $_"
        }
    } else {
        Write-SuccessLog "No Elastic IPs found"
    }
} catch {
    Write-ErrorLog "Failed to check Elastic IPs: $($_.Exception.Message)"
}

Write-Host "`nResource check completed!" -ForegroundColor Green
Write-Host "Please review the output above for any remaining resources." -ForegroundColor Yellow 
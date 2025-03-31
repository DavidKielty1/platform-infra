# NAT Gateway Cleanup Script

Write-Host "Starting NAT Gateway cleanup..." -ForegroundColor Yellow

# Function to handle errors
function Write-ErrorLog {
    param($Message)
    Write-Host "ERROR: $Message" -ForegroundColor Red
}

function Write-SuccessLog {
    param($Message)
    Write-Host "SUCCESS: $Message" -ForegroundColor Green
}

# Get all NAT Gateways
$natGateways = aws ec2 describe-nat-gateways --query 'NatGateways[*].NatGatewayId' --output text
if ($natGateways) {
    Write-Host "Found NAT Gateways:"
    $natGateways.Split() | ForEach-Object {
        if ($_) {
            $natId = $_
            Write-Host "Processing NAT Gateway: $natId"
            
            try {
                # Get the Elastic IP associated with this NAT Gateway
                $eipAllocationId = aws ec2 describe-nat-gateways --nat-gateway-ids $natId --query 'NatGateways[0].NatGatewayAddresses[0].AllocationId' --output text
                
                # Delete the NAT Gateway
                Write-Host "Deleting NAT Gateway: $natId"
                aws ec2 delete-nat-gateway --nat-gateway-id $natId
                
                # Wait for the NAT Gateway to be deleted
                Write-Host "Waiting for NAT Gateway deletion..."
                aws ec2 wait nat-gateway-available --nat-gateway-ids $natId
                
                # Release the Elastic IP if it exists
                if ($eipAllocationId) {
                    Write-Host "Releasing Elastic IP: $eipAllocationId"
                    aws ec2 release-address --allocation-id $eipAllocationId
                }
                
                Write-SuccessLog "Successfully deleted NAT Gateway: $natId"
            } catch {
                Write-ErrorLog "Failed to delete NAT Gateway $natId`: $($_.Exception.Message)"
            }
        }
    }
    Write-SuccessLog "NAT Gateway cleanup completed"
} else {
    Write-Host "No NAT Gateways found"
} 
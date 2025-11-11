#!/usr/bin/env powershell
# Test Call Initiation API using PowerShell
# This shows exactly what to send to the API

$url = "https://uncontortioned-na-ponderously.ngrok-free.dev/api/hume-twilio/initiate-call/"
$phone = "923403471112"
$agent_id = 1

Write-Host "="*80
Write-Host "TESTING CALL INITIATION API"
Write-Host "="*80

Write-Host "`n📋 REQUEST PARAMETERS:"
Write-Host "   URL: $url"
Write-Host "   Phone: $phone"
Write-Host "   Agent ID: $agent_id"

Write-Host "`n📤 SENDING REQUEST..."

$body = @{
    phone_no = $phone
    agent_id = $agent_id
} | ConvertTo-Json

Write-Host "`nRequest Body:"
Write-Host $body

try {
    $response = Invoke-WebRequest -Uri $url -Method Post -Body $body -ContentType "application/json"
    
    Write-Host "`n✅ RESPONSE RECEIVED!"
    Write-Host "Status: $($response.StatusCode)"
    
    $result = $response.Content | ConvertFrom-Json
    
    Write-Host "`n📊 RESPONSE DATA:"
    Write-Host ($result | ConvertTo-Json -Depth 10)
    
    if ($result.success) {
        Write-Host "`n✅ CALL SUCCESSFUL!"
        Write-Host "Call ID: $($result.call_id)"
        Write-Host "UUID: $($result.call_uuid)"
    } else {
        Write-Host "`n❌ CALL FAILED!"
        Write-Host "Error: $($result.error)"
    }
}
catch {
    Write-Host "`n❌ ERROR: $_"
    Write-Host "Make sure Django server is running!"
}

Write-Host "`n" + "="*80

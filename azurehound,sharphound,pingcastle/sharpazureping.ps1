# Define the domain variable for SharpHound
$Domain = ""

# Define AzureHound configuration variables
$TenantId = ""
$ClientId = ""
$AdminUsername = ""
$AdminPassword = ""
$SecretValue = ""

# PowerShell Script to Download, Unzip, and Execute AzureHound, SharpHound, and PingCastle

# Function to disable Windows Defender Real-Time Protection
function Disable-WindowsDefender {
    Write-Output "Disabling Windows Defender Real-Time Protection..."
    Set-MpPreference -DisableRealtimeMonitoring $true
    Write-Output "Windows Defender Real-Time Protection Disabled."
}

# Function to enable Windows Defender Real-Time Protection
function Enable-WindowsDefender {
    Write-Output "Enabling Windows Defender Real-Time Protection..."
    Set-MpPreference -DisableRealtimeMonitoring $false
    Write-Output "Windows Defender Real-Time Protection Enabled."
}

# Function to download files
function Download-File {
    param (
        [string]$url,
        [string]$output
    )

    try {
        Write-Output "Downloading $url to $output..."
        Invoke-WebRequest -Uri $url -OutFile $output
        Write-Output "Downloaded $url to $output."
    } catch {
        Write-Output "Failed to download $url. Error: $_"
    }
}

# Function to unzip files
function Unzip-File {
    param (
        [string]$zipPath,
        [string]$extractPath
    )

    try {
        Write-Output "Unzipping $zipPath to $extractPath..."
        Expand-Archive -Path $zipPath -DestinationPath $extractPath
        Write-Output "Unzipped $zipPath to $extractPath."
    } catch {
        Write-Output "Failed to unzip $zipPath. Error: $_"
    }
}

# URLs to download AzureHound, SharpHound, and PingCastle
$azureHoundUrl = "https://github.com/BloodHoundAD/AzureHound/releases/latest/download/azurehound-windows-amd64.zip"
$sharpHoundUrl = "https://github.com/BloodHoundAD/BloodHound/raw/master/Collectors/SharpHound.exe"
$pingCastleUrl = "https://github.com/vletoux/pingcastle/releases/download/3.2.0.1/PingCastle_3.2.0.1.zip"

# Output paths
$downloadPath = "C:\Users\Administrator\Desktop\claritas"
$azureHoundPath = "$downloadPath\azurehound-windows-amd64.zip"
$sharpHoundPath = "$downloadPath\SharpHound.exe"
$pingCastlePath = "$downloadPath\PingCastle_3.2.0.1.zip"
$pingCastleExtractedPath = "$downloadPath"

# Create download directory if it doesn't exist
if (-not (Test-Path -Path $downloadPath)) {
    New-Item -ItemType Directory -Path $downloadPath | Out-Null
}

# Disable Windows Defender
Disable-WindowsDefender

# Download AzureHound
Download-File -url $azureHoundUrl -output $azureHoundPath

# Download SharpHound
Download-File -url $sharpHoundUrl -output $sharpHoundPath

# Download PingCastle
Download-File -url $pingCastleUrl -output $pingCastlePath

# Unzip AzureHound to the download path
Unzip-File -zipPath $azureHoundPath -extractPath $downloadPath

# Unzip PingCastle to the download path
Unzip-File -zipPath $pingCastlePath -extractPath $pingCastleExtractedPath

# Execute AzureHound in PowerShell using variables
try {
    Write-Output "Executing AzureHound..."
    $azureHoundCmd = ".\azurehound.exe list -u `"$AdminUsername`" -p `"$AdminPassword`" -t `"$TenantId`" -a `"$ClientId`" -s `"$SecretValue`" az-ad -o `"$downloadPath\azure-output.json`""
    Invoke-Expression $azureHoundCmd
    Write-Output "AzureHound execution completed."
} catch {
    Write-Output "Failed to execute AzureHound. Error: $_"
}

# Execute SharpHound with the specified domain
try {
    Write-Output "Executing SharpHound with domain $Domain..."
    Start-Process -FilePath $sharpHoundPath -ArgumentList "-d $Domain" -NoNewWindow -Wait
    Write-Output "SharpHound execution completed."
} catch {
    Write-Output "Failed to execute SharpHound. Error: $_"
}

# Execute PingCastle with simulated keyboard input
try {
    Write-Output "Executing PingCastle..."
    $pingCastlePath = "$downloadPath\PingCastle.exe"
    Start-Process -FilePath $pingCastlePath -NoNewWindow
    Start-Sleep -Seconds 2
    Add-Type -AssemblyName System.Windows.Forms
    [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
    Start-Sleep -Seconds 1
    [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
    Write-Output "PingCastle execution completed."
} catch {
    Write-Output "Failed to execute PingCastle. Error: $_"
}

# Enable Windows Defender
Enable-WindowsDefender

Write-Output "Script execution completed."

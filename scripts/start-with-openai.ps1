$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

$credentialDirectory = Join-Path $env:LOCALAPPDATA "AIActComplianceNavigator"
$credentialFile = Join-Path $credentialDirectory "openai-api-key.dpapi"

if (-not $env:OPENAI_API_KEY) {
    if (Test-Path -LiteralPath $credentialFile) {
        try {
            # Set-Content terminates the encrypted value with a newline. Trim
            # only that surrounding whitespace before DPAPI decryption.
            $encryptedKey = (Get-Content -LiteralPath $credentialFile -Raw).Trim()
            $secureKey = $encryptedKey | ConvertTo-SecureString
        }
        catch {
            Remove-Item -LiteralPath $credentialFile -Force -ErrorAction SilentlyContinue
            $secureKey = $null
        }
    }

    if (-not $secureKey) {
        Write-Host "Enter an OpenAI Platform API key. It will be encrypted for this Windows account."
        $secureKey = Read-Host "OpenAI API key" -AsSecureString
        if ($secureKey.Length -gt 0) {
            New-Item -ItemType Directory -Path $credentialDirectory -Force | Out-Null
            $secureKey | ConvertFrom-SecureString | Set-Content -LiteralPath $credentialFile -Encoding ASCII
        }
    }

    $keyPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)
    try {
        $env:OPENAI_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($keyPointer)
    }
    finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($keyPointer)
    }
}

if (-not $env:OPENAI_API_KEY) {
    throw "An OpenAI Platform API key is required."
}

Write-Host "Starting Dr. G.D.P.R. & AI Act navigator with gpt-5.6-sol."
& (Join-Path $projectRoot "Start dashboard.bat")

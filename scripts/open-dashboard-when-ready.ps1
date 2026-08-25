param(
    [int]$Port = 8771,
    [int]$TimeoutSeconds = 180
)

$url = "http://localhost:$Port/"
$deadline = (Get-Date).AddSeconds($TimeoutSeconds)

do {
    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri "${url}api/health" -TimeoutSec 2
        if ($response.StatusCode -eq 200) {
            Start-Process $url
            exit 0
        }
    }
    catch {
        # The server is still starting; retry until the deadline.
    }
    Start-Sleep -Milliseconds 400
} while ((Get-Date) -lt $deadline)

exit 1

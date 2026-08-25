$ErrorActionPreference = "Stop"

$composeFile = "module_web_scraping\packages\docker-compose.yml"
$mainComposeFile = "module_web_scraping\docker-compose.yml"
$services = @(
    "source-monitoring",
    "eurlex-connector",
    "validation-engine",
    "scoring-engine",
    "regulatory-data-storage"
)

function Invoke-DemoCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string[]] $Command
    )

    & $Command[0] $Command[1..($Command.Length - 1)]
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code ${LASTEXITCODE}: $($Command -join ' ')"
    }
}

Write-Host ""
Write-Host "Dr. G.D.P.R. & AI Act navigator - Web Scraping Docker Demo" -ForegroundColor Cyan
Write-Host "Building package images..." -ForegroundColor Cyan
Invoke-DemoCommand @("docker", "compose", "-f", $composeFile, "build")

foreach ($service in $services) {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor DarkGray
    Write-Host "Running $service" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor DarkGray
    Invoke-DemoCommand @("docker", "compose", "-f", $composeFile, "run", "--rm", $service)
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor DarkGray
Write-Host "Generating consolidated demo report" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor DarkGray
Invoke-DemoCommand @("docker", "compose", "-f", $mainComposeFile, "build")
Invoke-DemoCommand @(
    "docker",
    "compose",
    "-f",
    $mainComposeFile,
    "run",
    "--rm",
    "web-scraping",
    "demo-report",
    "--output",
    "/app/storage/demo_report.md",
    "--json-output",
    "/app/storage/demo_report.json"
)

Write-Host ""
Write-Host "============================================================" -ForegroundColor DarkGray
Write-Host "Generating concrete web scraping outputs" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor DarkGray
Invoke-DemoCommand @(
    "docker",
    "compose",
    "-f",
    $mainComposeFile,
    "run",
    "--rm",
    "web-scraping",
    "demo-outputs",
    "--output-dir",
    "/app/storage/web_scraping_outputs"
)

Write-Host ""
Write-Host "Demo completed successfully." -ForegroundColor Green
Write-Host "Generated files:" -ForegroundColor Green
Write-Host "- storage\demo_report.md"
Write-Host "- storage\demo_report.json"
Write-Host "- storage\web_scraping_outputs\run_summary.md"
Write-Host "- storage\web_scraping_outputs\run_summary.json"
Write-Host "- storage\web_scraping_outputs\regulatory_events.json"
Write-Host "- storage\web_scraping_outputs\scraped_monitored_items.json"
Write-Host "- storage\web_scraping_outputs\articles_and_news_feed.html"

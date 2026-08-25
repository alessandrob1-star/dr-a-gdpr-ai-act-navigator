# Installation and Evaluation Guide

The runtime runs locally and can start either the browser web page or the native
desktop dashboard. Dr. A can use the official OpenAI API or a local
OpenAI-compatible Ollama/Qwen endpoint.

## Requirements

- Python 3.11 or later, or Docker Desktop for the web page
- PySide6 for the native desktop dashboard; the launcher installs it when needed
- An OpenAI Platform API key for OpenAI mode, or Ollama with Qwen for local mode
- Internet access for OpenAI API requests or source refreshes

Platform subscriptions and OpenAI API billing are separate. Never add an API
key to the repository, screenshots, or reports.

## Download the project

Clone or download the GitHub repository after access has been granted.

```bash
git clone <repository-url>
cd ai-act-compliance-navigator
```

## Windows Web Page With OpenAI

Double-click `Start with OpenAI.bat`. The launcher requests the API key in a
private prompt, keeps it only in the process environment, starts the dashboard,
and opens `http://localhost:8771`.

The key is not written to disk. Keep the launcher window open while using the
application and press `Ctrl+C` to stop it.

## Windows Web Page With Ollama/Qwen

Start Ollama, ensure Qwen is available, then double-click
`Start web page with Qwen.bat`.

```powershell
ollama pull qwen2.5:14b-instruct
.\Start web page with Qwen.bat
```

Equivalent manual configuration:

```powershell
$env:MODEL_PROVIDER = "local"
$env:LOCAL_MODEL_ENDPOINT = "http://localhost:11434/v1/chat/completions"
$env:LOCAL_MODEL_NAME = "qwen2.5:14b-instruct"
& ".\Start dashboard.bat"
```

## Windows Desktop Dashboard

Double-click `Start desktop dashboard.bat`. It opens the PySide6 desktop
dashboard and uses `LOCAL_MODEL_*` or legacy `QWEN_*` settings, defaulting to
Ollama at `http://localhost:11434/v1/chat/completions`.

## macOS and Linux Web Page

Set the key in the current shell and run the dashboard launcher:

```bash
export OPENAI_API_KEY="your-project-key"
chmod +x Start-Dashboard.sh
./Start-Dashboard.sh
```

Avoid placing the key directly in shell history on shared computers. A secure
shell secret manager is preferable.

For Ollama/Qwen web mode:

```bash
ollama pull qwen2.5:14b-instruct
chmod +x Start-Web-Page-Qwen.sh
./Start-Web-Page-Qwen.sh
```

For the native desktop dashboard:

```bash
chmod +x Start-Desktop-Dashboard.sh
./Start-Desktop-Dashboard.sh
```

## Docker

Set `OPENAI_API_KEY` in the current process, then start the dashboard:

```bash
docker compose -f module_company_profile/docker-compose.yml up -d --build dashboard
```

Stop it with:

```bash
docker compose -f module_company_profile/docker-compose.yml down
```

The Compose file passes provider settings only as runtime environment variables.
It does not bake API keys into the image.

## Verify the runtime

Open `http://localhost:8771/api/health`. A correctly configured instance reports:

```json
{
  "ok": true,
  "model_configured": true,
  "model_reachable": true,
  "model_name": "gpt-5.6-sol",
  "model_provider": "openai",
  "assistant_name": "Dr. A"
}
```

Then load a sample company and ask Dr. A one short question. A successful
streamed response confirms that the selected provider is producing real model
output rather than only displaying configuration state.

## Troubleshooting

- `OPENAI_API_KEY is required`: restart with a valid OpenAI Platform project key,
  or set `MODEL_PROVIDER=local` for Ollama/Qwen.
- `The local model is not configured`: set `LOCAL_MODEL_ENDPOINT` or use the
  Qwen launcher.
- HTTP `401`: verify the key and its project.
- HTTP `429`: verify API credits, billing, and project usage limits.
- Port `8771` already in use: stop the earlier dashboard process before restarting.
- Reports unavailable: install dependencies with
  `python -m pip install -r module_company_profile/requirements.txt`.

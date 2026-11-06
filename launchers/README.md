# Launchers

Run the two Qwen entry points from the repository root for the local browser UI:

- Windows: `Start web page with Qwen.bat`
- macOS/Linux: `./Start-Web-Page-Qwen.sh`

The files in this folder support the same application in other configurations:

| Launcher | Platform | Purpose |
|---|---|---|
| `Start dashboard.bat` | Windows | Shared native launcher; honors `MODEL_PROVIDER` (default: OpenAI) |
| `Start-Dashboard.sh` | macOS/Linux | Shared native launcher; honors `MODEL_PROVIDER` (default: OpenAI) |
| `Start with OpenAI.bat` | Windows | Starts OpenAI mode using the existing private credential prompt |
| `Start with Docker.bat` | Windows | Builds and starts the OpenAI Docker configuration |
| `Stop Docker.bat` | Windows | Stops that Docker configuration |
| `start-demo.sh` | macOS/Linux | Builds and starts the OpenAI Docker configuration |
| `stop-demo.sh` | macOS/Linux | Stops that Docker configuration |

These launchers locate the repository root relative to their own paths.
For prerequisites and configuration, see [Installation](../docs/INSTALLATION.md).

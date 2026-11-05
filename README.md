# Desktop Fox

A macOS menu-bar app with a wandering desktop companion and local AI chat.
The app bundles the Ollama runtime and automatically downloads the llama3.2
model the first time you send a chat message.

> **Download:** [Get the latest Desktop Fox release for Apple silicon](https://github.com/GlassC0ffin/Desktop-Helper/releases/latest).
> The model is a separate release asset and downloads automatically on first
> chat. This app is not signed or notarized; see the security notes below.

## Requirements

- macOS. Apple silicon is the tested configuration. Builds use the CPU
  architecture of the Mac that creates them.
- Internet access and about 4 GB of free disk space for the one-time model
  download and installation.
- Python 3.12+ and Ollama for macOS are required only to build the app and
  release assets. People installing the prebuilt app do not need to install
  Python or Ollama separately.

## Install the prebuilt app

1. Open the [latest Desktop Fox release](https://github.com/GlassC0ffin/Desktop-Helper/releases/latest)
   and download `DesktopFox-macOS.zip`.
2. Unzip it, move `DesktopFox.app` into Applications if desired, and open the
   app from Finder.
3. Type a message in the speech bubble. The first chat attempts to download
   the approximately 1.9 GB llama3.2 model automatically. Keep the app open
   and connected to the internet until setup finishes. Later chats use the
   local model.

If GitHub reports that the model asset cannot be found (for example, because
the repository is private):

1. While signed in to GitHub with an account that can access this repository,
   open the [v1.1.0 model release](https://github.com/GlassC0ffin/Desktop-Helper/releases/tag/v1.1.0)
   and download `DesktopFox-llama3.2-model.tar` (not the source-code archive).
2. In Desktop Fox, open the menu-bar menu and choose **Install AI Model from
   File…**, then select the downloaded `.tar`.

The app verifies the archive's SHA-256 before safely installing it. It does
not need or store your GitHub password or access token.

The app bundles Ollama and starts its local server automatically when chat is
used. The model and server log are stored in
`~/Library/Application Support/DesktopHelper/DesktopFox` and reused between
launches.

## Build from source

1. Install [Python 3.12 or newer](https://www.python.org/downloads/macos/) and
   [Ollama for macOS](https://ollama.com/download).
2. Download or clone the repository. Then, from Terminal, go to the
   `Desktop-Helper` project folder and prepare the model:

   ```bash
   ollama pull llama3.2
   ./prepare_model_archive.sh
   ```

3. Build the macOS app:

   ```bash
   ./build_macos.sh
   ```

The scripts create an isolated `.venv-build` and produce:

- `dist/DesktopFox.app` and `dist/DesktopFox-macOS.zip`
- `dist/DesktopFox-llama3.2-model.tar`, to upload as a separate GitHub Release
  asset named exactly `DesktopFox-llama3.2-model.tar`

The model archive is about 1.9 GB and is intentionally kept out of Git source
history. GitHub limits each release asset to under 2 GiB, so publish the model
separately from the app ZIP. The app's first-run model download URL is defined
in `desktop_pet.py`.

## First launch and macOS security

This app is not signed or notarized with an Apple Developer ID, so macOS may
show a warning when opening it. Only open apps you trust. If Gatekeeper blocks
an app you built yourself, use **Control-click → Open** in Finder to review
and open it.

## Use the pet

- Click the character's menu-bar icon to turn the pet on or off.
- Use **Choose Character** in the menu-bar menu to switch between Fox, Jane,
  and Ellen. Each has its own artwork, affectionate personality, and saved name.
- Choose **Settings…** to change its name, wandering behavior, and walking
  speed.
- Type in the speech bubble and press Return or the send button to chat.
- The first chat downloads and installs the local model. A progress message
  appears in the bubble.
- For a private repository, download `DesktopFox-llama3.2-model.tar` from the
  v1.1.0 release in a signed-in browser, then choose **Install AI Model from
  File…** in the menu-bar menu.
- If setup fails, check your internet connection and available disk space.
  The Ollama server log is at
  `~/Library/Application Support/DesktopFox/ollama.log`.
- If the model download reports an SSL certificate error, install the latest
  app update and retry on a network that permits HTTPS access to GitHub.
- Choose **Quit Desktop Pet** from the menu-bar menu to exit.

Each character has a distinct AI personality prompt in `desktop_pet.py`.
Preferences such as each character's name persist across launches.

## Model and third-party licenses

This app redistributes Meta Llama 3.2 under the Llama 3.2 Community License and
its Acceptable Use Policy. License terms and the required notice are included
in the app's `licenses` directory. The chat bubble displays **Built with
Llama**. The Ollama runtime and its third-party license notices are also
bundled with the app.

## Run from Python

Running the source script uses the locally installed Ollama app:

```bash
python3 -m pip install -r requirements-desktop.txt
python3 desktop_pet.py
```

## Project files

- `desktop_pet.py` — PySide6 app, menu-bar controls, movement, and Ollama chat.
- `assets/` — fox, guardian, and maid character artwork.
- `build_macos.sh` — app bundle and app ZIP build script.
- `prepare_model_archive.sh` — prepares the separately published model asset.
- `licenses/` — third-party license terms and required notices.
- `requirements-desktop.txt` — Python dependencies for running and packaging.

The repository also contains an independent browser canvas demo. Open
`index.html` in a browser, or run `python3 -m http.server 8000` and visit
`http://localhost:8000` if the browser blocks ES module imports over `file://`.

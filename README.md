# Desktop Fox

A small macOS menu-bar app with a wandering desktop companion and a local
Ollama-powered chat bubble. The app can be hidden or shown from the menu-bar
icon, and its name and walking behavior can be changed in Settings.

> **Prebuilt download:** There is not currently a prebuilt app published on
> GitHub. Follow the build steps below to create `DesktopFox.app` on your Mac.
> The app bundle is not included in the repository source download.

## Requirements

- macOS. Build on the Mac where you plan to use the app; the build uses that
  Mac's CPU architecture. Apple silicon is the tested configuration. An app
  built for Apple silicon will not run natively on an Intel Mac, or vice versa.
- Python 3.12 or newer ([download Python](https://www.python.org/downloads/macos/))
  and an internet connection for the first build.
- [Ollama for macOS](https://ollama.com/download) for AI chat. The fox works
  without Ollama, but it cannot answer chat questions until Ollama is running
  with a model installed.

## Build and install

1. Install Ollama from [ollama.com/download](https://ollama.com/download).
   Open Ollama and download the default model from Terminal:

   ```bash
   ollama pull llama3.2
   ```

2. Download this repository from GitHub using **Code → Download ZIP**, then
   unzip it. Or clone it with Git:

   ```bash
   git clone https://github.com/GlassC0ffin/Descktop-Helper.git
   ```

3. Open Terminal and change to the unzipped project folder. For a cloned
   repository, run `cd Descktop-Helper`. For a downloaded ZIP, type `cd ` in
   Terminal, drag the unzipped `Descktop-Helper-main` folder from Finder into
   the Terminal window, then press Return. Build the app:

   ```bash
   ./build_macos.sh
   ```

   The build script creates an isolated `.venv-build`, installs the needed
   Python packages, and builds:

   - `dist/DesktopFox.app` — the macOS app
   - `dist/DesktopFox-macOS.zip` — an archive for another Mac with the same
     CPU architecture

4. Open `dist` in Finder and move `DesktopFox.app` into Applications if you
   want it there. Open the app from Finder. Once it has launched, you can quit
   Terminal; the pet app does not need to stay attached to that Terminal
   session.

The first build needs internet access to install build dependencies. It can
take a few minutes. The resulting app is self-contained; Python is not needed
to run it. Ollama remains a separate app and must be running for AI chat.

## First launch and macOS security

The app built from this repository is not signed or notarized with an Apple
Developer ID. macOS may warn when opening it. Only open apps you trust. If
Gatekeeper blocks an app that you built yourself from this source, use
**Control-click → Open** in Finder to review and open it.

## Use the pet

- Click the fox's menu-bar icon to turn the pet on or off.
- Choose **Settings…** to change its name, enable or disable wandering, and
  adjust walking speed.
- Type in the pet's speech bubble and press Return or the send button to chat.
- Keep Ollama open and the `llama3.2` model installed for chat. If chat cannot
  connect, check that Ollama is running and try `ollama list` in Terminal.
- Choose **Quit Desktop Pet** from the menu-bar menu to exit the app.

The AI personality prompt is in `DesktopPet.build_system_prompt()` in
`desktop_pet.py`. User preferences, including the pet's name, are saved by
macOS and survive app restarts.

## Build from source / run with Python

To run the script directly instead of building the app:

```bash
python3 -m pip install -r requirements-desktop.txt
python3 desktop_pet.py
```

Building the `.app` is recommended for everyday use because it can be launched
from Finder without keeping a Terminal window open.

## Project files

- `desktop_pet.py` — PySide6 app, menu-bar controls, pet movement, and Ollama
  chat.
- `assets/chibi_fox.png` — companion artwork used by the app and its icon.
- `build_macos.sh` — macOS app and ZIP build script.
- `requirements-desktop.txt` — Python dependencies for running and packaging.

The repository also contains a small, independent browser canvas demo. To run
it, open `index.html` in a browser. If ES module imports are blocked over
`file://`, run `python3 -m http.server 8000` from the repository folder and
visit `http://localhost:8000`.

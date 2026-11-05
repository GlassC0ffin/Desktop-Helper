# Reusable Studio Engine

A minimal, framework-free Canvas starter I reuse to begin every new
build in this course — clean file structure, a docs ritual, and a
tiny working sketch that proves the engine runs.

## What it does

One signal (mouse X position) drives one parameter (radius), which
drives one visible behavior: a ring that pulses faster the farther
right the mouse moves. See `/docs/SYSTEM_CHARTER.md` for the full
template definition.

## Run locally

Just open `index.html` in a browser — no build step required.

If your browser blocks ES module imports over `file://`, run a
simple local server from the project root instead:

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

## Desktop Fox macOS app

The Python desktop pet can be packaged as a normal macOS app bundle, so it
doesn't need to stay attached to a Terminal window.

On a Mac, build it with:

```bash
chmod +x build_macos.sh
./build_macos.sh
```

The script creates `dist/DesktopFox.app` and a shareable
`dist/DesktopFox-macOS.zip`. Open the app from Finder or move it into
Applications. Ollama must also be installed and running, with the model
available locally:

```bash
ollama pull llama3.2
```

The app bundle and archive are local build outputs and are not committed.
To distribute the app broadly, sign it with an Apple Developer ID and
notarize it; otherwise macOS may warn recipients when they open it.

## Deploy

This project deploys with **[Cloudflare Pages / GitHub Pages — pick
one]**:

- Framework preset: None
- Build command: (blank)
- Output directory: `/` (root)

Every push to `main` updates the live link automatically.

## How I use this to start projects

1. Copy this repo as the starting point for a new assignment.
2. Rewrite `/docs/SYSTEM_CHARTER.md` first — intent, constraints,
   tensions, taste vow — before writing any code.
3. Follow `/docs/ROADMAP.md` step by step.
4. Use `/docs/PROMPTS.md` as the only way I talk to Copilot, so AI
   help stays inside my own constraints instead of replacing them.
5. Log real direction changes in `/process/changelog.md` as I go.

## Links

- GitHub template repo: [add link]
- Live deployed engine: [add link]

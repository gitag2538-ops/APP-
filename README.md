# VLE — Benzène / Toluène

Static calculator (Raoult’s law) in [`docs/`](docs/), ready for **GitHub Pages**.

## Publish on GitHub Pages

1. Push this repository to GitHub.
2. **Settings** → **Pages** → **Build and deployment** → **Deploy from a branch**.
3. Branch: your default branch, folder: **`/docs`** → Save.

The site URL is shown on the Pages settings page (e.g. `https://<username>.github.io/<repo>/`).

## Preview locally

```bash
cd /path/to/APPWEB-.PY
python3 -m http.server 8080 --directory docs
```

Open http://127.0.0.1:8080

# Talk to Tree

A Flask-based plant knowledge explorer that lets users browse Indian tree profiles, ask plant-related questions, and explore botanical information through a local RAG-style knowledge base.

## Features

- Browse curated tree profiles from the local knowledge base
- Search plants by name, family, habitat, and type
- Explore detailed plant information and cultural/ecological notes
- Chat with the app using the local retrieval pipeline
- Upload a plant image for demo identification
- Compare two plants side by side
- Demo mode fallback when external AI providers are unavailable

## Project structure

- `app.py` — Flask app entry point
- `data/plants/` — local plant knowledge documents
- `rag/` — retrieval and generation pipeline
- `services/` — business logic for plants, chat, and images
- `templates/` — Jinja HTML pages
- `static/` — CSS and JavaScript assets
- `vector_store/` — local Chroma vector database

## Local setup

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
# On Windows PowerShell:
# .\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

## Environment variables

Create a `.env` file if needed:

```env
FLASK_DEBUG=False
PORT=5000
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
```

## GitHub Pages

This repository includes a lightweight documentation landing page in the `docs/` folder that can be published via GitHub Pages.

## Deployment notes

This app is ready for container or platform deployments that support Python web apps, such as Render, Railway, Fly.io, or any WSGI-capable host.

For production deployments, set:

- `FLASK_DEBUG=False`
- `PORT` to the platform-assigned port
- API keys only if using external LLM providers

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Contributing

Pull requests are welcome. Please keep the project focused on botanical education, safety, and accessible plant information.

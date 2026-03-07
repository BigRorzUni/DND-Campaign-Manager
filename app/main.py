from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.db.session import engine
from app.db.base import Base
import app.models
from app.api.v1.router import router as api_v1_router


def create_app() -> FastAPI:
    application = FastAPI(title="DnD Campaign Manager API")

    # auto creates tables
    Base.metadata.create_all(bind=engine)

    # mounting api routes
    application.include_router(api_v1_router, prefix="/api/v1")

    @application.get("/", response_class=HTMLResponse)
    def home() -> str:
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <title>DnD Campaign Manager API</title>
            <style>
                :root {
                    --bg: #0f172a;
                    --panel: #111827;
                    --panel-2: #1f2937;
                    --text: #e5e7eb;
                    --muted: #94a3b8;
                    --accent: #8b5cf6;
                    --accent-2: #22c55e;
                    --border: #334155;
                }

                * {
                    box-sizing: border-box;
                }

                body {
                    margin: 0;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                    background: linear-gradient(180deg, var(--bg), #111827);
                    color: var(--text);
                    line-height: 1.6;
                }

                .container {
                    max-width: 1000px;
                    margin: 0 auto;
                    padding: 48px 24px 64px;
                }

                .hero {
                    background: rgba(17, 24, 39, 0.85);
                    border: 1px solid var(--border);
                    border-radius: 20px;
                    padding: 32px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.25);
                }

                h1, h2, h3 {
                    margin-top: 0;
                }

                h1 {
                    font-size: 2.4rem;
                    margin-bottom: 12px;
                }

                .subtitle {
                    color: var(--muted);
                    font-size: 1.05rem;
                    max-width: 720px;
                }

                .button-row {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 12px;
                    margin-top: 24px;
                }

                .button {
                    display: inline-block;
                    padding: 12px 18px;
                    border-radius: 12px;
                    text-decoration: none;
                    color: white;
                    font-weight: 600;
                    border: 1px solid transparent;
                }

                .button.primary {
                    background: var(--accent);
                }

                .button.secondary {
                    background: var(--panel-2);
                    border-color: var(--border);
                }

                .grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
                    gap: 18px;
                    margin-top: 28px;
                }

                .card {
                    background: rgba(17, 24, 39, 0.9);
                    border: 1px solid var(--border);
                    border-radius: 16px;
                    padding: 20px;
                }

                .card h3 {
                    margin-bottom: 10px;
                }

                .muted {
                    color: var(--muted);
                }

                code {
                    background: #0b1220;
                    border: 1px solid var(--border);
                    border-radius: 8px;
                    padding: 2px 8px;
                    color: #c4b5fd;
                }

                ul {
                    padding-left: 20px;
                    margin-bottom: 0;
                }

                .footer {
                    margin-top: 32px;
                    color: var(--muted);
                    font-size: 0.95rem;
                }

                .pill {
                    display: inline-block;
                    padding: 6px 10px;
                    border-radius: 999px;
                    background: rgba(34, 197, 94, 0.12);
                    color: #86efac;
                    border: 1px solid rgba(34, 197, 94, 0.25);
                    font-size: 0.9rem;
                    font-weight: 600;
                    margin-bottom: 16px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <section class="hero">
                    <div class="pill">COMP3011 Coursework Project</div>
                    <h1>DnD Campaign Manager API</h1>
                    <p class="subtitle">
                        A REST API for managing Dungeons & Dragons campaigns, sessions, encounters, and event logs,
                        with analytics for damage, encounter difficulty, and event breakdowns.
                    </p>

                    <div class="button-row">
                        <a class="button primary" href="/docs">Open Swagger Docs</a>
                        <a class="button secondary" href="/redoc">Open ReDoc</a>
                        <a class="button secondary" href="/health">Health Check</a>
                    </div>
                </section>

                <section class="grid">
                    <div class="card">
                        <h3>Core Hierarchy</h3>
                        <p class="muted">
                            The API models campaign activity with a simple relational structure:
                        </p>
                        <p>
                            <code>Campaign → Session → Encounter → Event</code>
                        </p>
                    </div>

                    <div class="card">
                        <h3>Core Features</h3>
                        <ul>
                            <li>Campaign CRUD</li>
                            <li>Session management</li>
                            <li>Encounter tracking</li>
                            <li>Event logging</li>
                        </ul>
                    </div>

                    <div class="card">
                        <h3>Analytics</h3>
                        <ul>
                            <li><code>/api/v1/analytics/campaigns/{id}/damage-leaderboard</code></li>
                            <li><code>/api/v1/analytics/campaigns/{id}/encounter-difficulty</code></li>
                            <li><code>/api/v1/analytics/campaigns/{id}/event-breakdown</code></li>
                        </ul>
                    </div>

                    <div class="card">
                        <h3>Suggested Demo Flow</h3>
                        <ol>
                            <li>Create a campaign</li>
                            <li>Add a session</li>
                            <li>Add an encounter</li>
                            <li>Log events</li>
                            <li>View analytics</li>
                        </ol>
                    </div>
                </section>

                <p class="footer">
                    Built with FastAPI, SQLAlchemy, SQLite, and pytest.
                </p>
            </div>
        </body>
        </html>
        """

    @application.get("/health")
    def health():
        return {"status": "ok"}

    return application


app = create_app()
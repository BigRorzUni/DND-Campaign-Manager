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
    def home():
        return """
    <!DOCTYPE html>
    <html>
    <head>
    <title>DnD Campaign Manager</title>

    <style>

    body{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto;
        background:#0f172a;
        color:#e5e7eb;
        margin:0;
    }

    .container{
        max-width:900px;
        margin:auto;
        padding:40px;
    }

    h1{
        margin-bottom:5px;
    }

    .card{
        background:#111827;
        padding:20px;
        border-radius:12px;
        margin-bottom:20px;
        border:1px solid #334155;
    }

    button{
        padding:10px 14px;
        border:none;
        border-radius:8px;
        background:#8b5cf6;
        color:white;
        cursor:pointer;
    }

    input,textarea{
        width:100%;
        padding:8px;
        margin-top:5px;
        margin-bottom:10px;
        border-radius:6px;
        border:1px solid #334155;
        background:#020617;
        color:white;
    }

    .campaign{
        padding:12px;
        border-radius:8px;
        border:1px solid #334155;
        margin-bottom:10px;
    }

    .linkbtn{
        margin-left:10px;
        text-decoration:none;
        color:#22c55e;
    }

    </style>

    </head>

    <body>

    <div class="container">

    <h1>DnD Campaign Manager</h1>
    <p>Manage campaigns, sessions, encounters and events.</p>

    <div class="card">

    <h2>Create Campaign</h2>

    <form id="campaign-form">
    <input id="name" placeholder="Campaign name" required>
    <textarea id="description" placeholder="Description"></textarea>
    <button>Create Campaign</button>
    </form>

    </div>

    <div class="card">

    <h2>Campaigns</h2>
    <div id="campaigns"></div>

    </div>

    <div class="card">

    <h2>API Tools</h2>

    <p>
    <a href="/docs">Swagger Docs</a><br>
    <a href="/redoc">ReDoc Documentation</a><br>
    <a href="/health">Health Check</a>
    </p>

    </div>

    </div>

    <script>

    async function loadCampaigns(){

        const res = await fetch("/api/v1/campaigns")
        const data = await res.json()

        const container = document.getElementById("campaigns")
        container.innerHTML = ""

        for(const c of data){

            const div = document.createElement("div")
            div.className = "campaign"

            div.innerHTML = `
            <strong>${c.name}</strong><br>
            ${c.description ?? ""}
            <br>
            <a class="linkbtn" href="/campaigns/${c.id}/view">Open</a>
            `

            container.appendChild(div)
        }
    }

    document.getElementById("campaign-form").addEventListener("submit", async e => {

        e.preventDefault()

        await fetch("/api/v1/campaigns",{
            method:"POST",
            headers:{"Content-Type":"application/json"},
            body:JSON.stringify({
                name:document.getElementById("name").value,
                description:document.getElementById("description").value
            })
        })

        document.getElementById("campaign-form").reset()

        loadCampaigns()
    })

    loadCampaigns()

    </script>

    </body>
    </html>
    """

    @application.get("/health")
    def health():
        return {"status": "ok"}

    return application


app = create_app()
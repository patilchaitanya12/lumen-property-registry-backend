import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.history import router as history_router
from app.api.routes.locations import router as locations_router
from app.api.routes.orders import router as orders_router
from app.api.routes.owners import router as owners_router
from app.api.routes.search import router as search_router
from app.api.routes.units import router as units_router


app = FastAPI(
    title="Lumen Property Registry API",
    version="0.1.0",
)


frontend_url = os.getenv(
    "FRONTEND_URL",
    "http://localhost:5173",
)

allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

if frontend_url not in allowed_origins:
    allowed_origins.append(frontend_url)


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(dashboard_router)
app.include_router(search_router)
app.include_router(owners_router)
app.include_router(units_router)
app.include_router(locations_router)
app.include_router(history_router)
app.include_router(orders_router)


@app.api_route("/health", methods=["GET", "HEAD"])
def health_check():
    return {
        "status": "ok",
        "service": "lumen-property-registry-backend",
    }

@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Lumen Property Registry - Backend</title>
        <style>
            body {
                margin: 0;
                padding: 40px;
                background: #0f1115;
                color: #e8eaed;
                font-family: Arial, sans-serif;
            }

            .container {
                max-width: 900px;
                margin: 0 auto;
            }

            h1 {
                margin-bottom: 8px;
            }

            .subtitle {
                color: #9aa0a6;
                margin-bottom: 32px;
            }

            .card {
                background: #171a21;
                border: 1px solid #2a2f3a;
                border-radius: 12px;
                padding: 24px;
                margin-bottom: 20px;
            }

            h2 {
                margin-top: 0;
                font-size: 18px;
            }

            ul {
                line-height: 1.9;
            }

            a {
                color: #8ab4f8;
                text-decoration: none;
            }

            a:hover {
                text-decoration: underline;
            }

            code {
                background: #222630;
                padding: 3px 7px;
                border-radius: 5px;
            }

            .status {
                color: #81c995;
                font-weight: bold;
            }

            .footer {
                color: #777d87;
                font-size: 13px;
                margin-top: 32px;
            }
        </style>
    </head>

    <body>
        <div class="container">

            <h1>Lumen Property Registry</h1>

            <div class="subtitle">
                Backend API
            </div>

            <div class="card">
                <h2>Welcome</h2>
                <p>
                    Welcome to the Lumen Property Registry Backend.
                </p>

                <p>
                    This API provides structured access to property units,
                    owners, locations, orders, and ownership history.
                </p>

                <p>
                    Status:
                    <span class="status">Operational</span>
                </p>
            </div>

            <div class="card">
                <h2>API Documentation</h2>

                <p>
                    <a href="/docs">Open Swagger API Documentation</a>
                </p>

                <p>
                    <a href="/redoc">Open ReDoc Documentation</a>
                </p>

                <p>
                    <a href="/openapi.json">OpenAPI Schema</a>
                </p>
            </div>

            <div class="card">
                <h2>API Endpoints</h2>

                <ul>
                    <li><code>/api/dashboard</code> - Registry statistics</li>
                    <li><code>/api/owners</code> - Owner registry</li>
                    <li><code>/api/units</code> - Unit registry</li>
                    <li><code>/api/locations</code> - Location registry</li>
                    <li><code>/api/orders</code> - Order registry</li>
                    <li><code>/api/history</code> - Registry history</li>
                    <li><code>/api/search</code> - Global search</li>
                </ul>
            </div>

            <div class="card">
                <h2>Health</h2>

                <p>
                    <a href="/health">Health Check</a>
                </p>
            </div>

            <div class="card">
                <h2>Technology</h2>

                <p>
                    FastAPI |
                    SQLAlchemy |
                    Supabase PostgreSQL |
                    Alembic
                </p>
            </div>

            <div class="footer">
                Lumen Property Registry Backend - API v1.0.0
            </div>

        </div>
    </body>
    </html>
    """
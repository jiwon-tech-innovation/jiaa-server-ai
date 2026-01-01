from fastapi import FastAPI
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

@app.get("/")
async def root():
    return {"message": "JIAA Intelligence Worker is running"}

from app.api.v1.api import api_router
app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import asyncio
    import uvicorn
    from app.core.grpc_server import serve_grpc

    config = uvicorn.Config(app=app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)

    async def main():
        print("Starting JIAA Intelligence Worker (HTTP: 8000, gRPC: 50051)...")
        await asyncio.gather(
            server.serve(),
            serve_grpc()
        )

    asyncio.run(main())


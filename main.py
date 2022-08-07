from pydantic import BaseModel
from fastapi import FastAPI
from typing import List

from cache import Cache
from config import load_config

config = load_config()


class ManageDropletsInput(BaseModel):
    password: str
    urls: List[str]

class AuthInput(BaseModel):
    password: str


app = FastAPI()
cache = Cache(
    config["redis-connection-url"],
    config["cache-duration-seconds"]
)

@app.get('/api/fetch-middleware')
async def fetch_droplet():
    try:
        droplet = await cache.fetch_droplet()
        error = None
    except Exception as e:
        error = str(e)
        droplet = None
    
    return {
        "error": error,
        "url": droplet
    }

@app.post('/admin/add-droplets')
async def add_droplets(inp: ManageDropletsInput):
    if inp.password != config["admin-password"]:
        return {"error": "invalid auth."}
    
    try:
        await cache.add_droplets(inp.urls)
        error = None
    except Exception as e:
        error = str(e)
    
    return {"error": error}

@app.post('/admin/remove-droplets')
async def remove_droplets(inp: ManageDropletsInput):
    if inp.password != config["admin-password"]:
        return {"error": "invalid auth."}
    
    try:
        await cache.remove_droplets(inp.urls)
        error = None
    except Exception as e:
        error = str(e)
    
    return {"error": error}

@app.post('/admin/reset-droplets')
async def reset_droplets(inp: AuthInput):
    if inp.password != config["admin-password"]:
        return {"error": "invalid auth."}
    
    try:
        await cache.reset_droplets(inp.urls)
        error = None
    except Exception as e:
        error = str(e)
    
    return {"error": error}


if __name__ == "__main__":
    print("Please run using uvicorn.")

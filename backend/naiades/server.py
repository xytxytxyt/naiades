import asyncio
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from naiades.downloads import DownloadSubdirDisplay
from naiades.downloads import get_downloads as get_downloads_internal
from naiades.rss import rss_downloader_loop

app = FastAPI()

origins = [
    f"http://{allowed_origin_host.strip()}:5174"
    for allowed_origin_host in os.environ["ALLOWED_ORIGIN_HOSTS"].split(",")
]
origins = list(set(origins) | set(["http://localhost:5174"]))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    # https://stackoverflow.com/questions/70854314/use-fastapi-to-interact-with-async-loop
    asyncio.create_task(rss_downloader_loop())


class DownloadSubdirDisplayAPI(BaseModel):
    data: DownloadSubdirDisplay


@app.get("/downloads")
async def get_downloads() -> dict[str, list[DownloadSubdirDisplayAPI]]:
    downloads = get_downloads_internal()
    results: dict[str, list[DownloadSubdirDisplayAPI]] = {}
    for download_dir in downloads.downloads:
        subdirs_by_mtime = download_dir.list_subdirs_by_mtime()
        results[download_dir.path] = [
            DownloadSubdirDisplayAPI(data=subdir) for subdir in subdirs_by_mtime
        ]
    return results

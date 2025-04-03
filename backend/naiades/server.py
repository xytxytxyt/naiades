from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from naiades.downloads import list_subdirs_by_time

app = FastAPI()

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DownloadDir(BaseModel):
    name: str
    date_time: str


@app.get("/downloads")
async def get_downloads() -> list[DownloadDir]:
    download_dir = "/Volumes/My Passport/Anime"
    downloads = list_subdirs_by_time(download_dir)
    return [
        DownloadDir(name=name, date_time=date_time) for name, date_time in downloads
    ]

import asyncio
import datetime
import logging
import re
import shutil
import subprocess
import sys

import requests
import xmltodict

from naiades.downloads import Downloads, downloads_date_time_format, get_downloads

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

rss_date_time_format = "%a, %d %b %Y %H:%M:%S %z"
rss_check_period_s = 3600


class RSSDownloader(object):
    downloads: Downloads
    url: str
    last_checked_time: datetime.datetime
    patterns_paths: dict[str, str] = {}

    def __init__(
        self,
        downloads: Downloads,
    ):
        self.logger = logging.getLogger("RSSDownloader")
        self.downloads = downloads
        self.url = self.downloads.rss_url
        self.last_checked_time = self.approximate_last_checked_time()
        self.patterns_paths = self.get_patterns_paths()
        self.logger.info(f"initializing; last check time was {self.last_checked_time}")

    def approximate_last_checked_time(self) -> datetime.datetime:
        mtimes: list[datetime.datetime] = []
        for download in self.downloads.downloads:
            subdirs_mtimes = [
                datetime.datetime.strptime(str(e.date_time), downloads_date_time_format)
                for e in download.list_subdirs_by_mtime()
            ]
            mtimes.append(
                max(subdirs_mtimes, default=datetime.datetime.fromtimestamp(0))
            )
        return (max(mtimes) - datetime.timedelta(days=1)).astimezone()

    def get_patterns_paths(self):
        patterns_paths: dict[str, str] = {}
        for download_dir in self.downloads.downloads:
            for subdir in download_dir.subdirs:
                if subdir.path is not None and subdir.pattern is not None:
                    patterns_paths[subdir.pattern] = subdir.path
        return patterns_paths

    def get_last_checked_time_for_rss(self):
        return self.last_checked_time.astimezone(datetime.timezone.utc).strftime(
            rss_date_time_format
        )

    def update_new_downloads_from_xml(self, xml: str, new_downloads: dict[str, str]):
        self.logger.info(f"last check time was {self.last_checked_time}")
        xmld = xmltodict.parse(xml)
        for item in xmld["rss"]["channel"]["item"]:
            title = item["title"]
            link = item["link"]
            pub_date = datetime.datetime.strptime(item["pubDate"], rss_date_time_format)
            for pattern in self.patterns_paths:
                if re.search(pattern, title) is not None:
                    if pub_date > self.last_checked_time:
                        self.logger.info(
                            f"new download: {title}, {self.patterns_paths[pattern]}, {link}"
                        )
                        new_downloads[self.patterns_paths[pattern]] = link
                    else:
                        self.logger.info(
                            f"found match {title}, but skipping because its pub date {item['pubDate']} is too old"
                        )
        now = datetime.datetime.today().astimezone()
        self.last_checked_time = now

    def get_new_downloads(self) -> dict[str, str]:
        new_downloads: dict[str, str] = {}
        resp = requests.get(
            self.url,
            headers={
                "If-Modified-Since": self.get_last_checked_time_for_rss(),
            },
        )
        if resp.status_code == requests.codes.ok:
            self.logger.info(f"new updates from rss {self.url}")
            self.update_new_downloads_from_xml(resp.text, new_downloads)
        elif resp.status_code == requests.codes.not_modified:
            self.logger.info(f"no updates from rss {self.url}")
        else:
            self.logger.error(
                f"error getting updates from rss {self.url}: {resp.status_code}, {resp.text}"
            )
        return new_downloads

    async def download(self, downloads: dict[str, str]):
        processes: dict[str, subprocess.Popen] = {}
        for output_path in downloads:
            link = downloads[output_path]
            self.logger.info(f"downloading to {output_path}: {link}")
            webtorrent_path = shutil.which("webtorrent")
            assert webtorrent_path, "could not find webtorrent"
            processes[output_path] = subprocess.Popen(
                [
                    webtorrent_path,
                    "download",
                    link,
                    "--out",
                    output_path,
                    "--quiet",
                ]
            )
        while True:
            await asyncio.sleep(1)
            returncodes: list[int | None] = []
            for output_path in processes:
                process = processes[output_path]
                returncode = process.poll()
                if returncode is None:
                    self.logger.info(f"still waiting for download to {output_path}")
                returncodes.append(returncode)
            if all(returncode is not None for returncode in returncodes):
                self.logger.info("all downloads done")
                break
        self.logger.info("results:")
        for output_path in processes:
            process = processes[output_path]
            try:
                stdout, stderr = process.communicate()
                self.logger.info(stdout)
                self.logger.error(stderr)
            except Exception as e:
                self.logger.error(e)

    async def check_possibly_download(self):
        new_downloads = self.get_new_downloads()
        self.logger.info(f"checked and found {len(new_downloads)} new downloads")
        if len(new_downloads) > 0:
            await self.download(new_downloads)


rss_downloader = None


def get_rss_downloader() -> RSSDownloader:
    global rss_downloader
    if rss_downloader is None:
        rss_downloader = RSSDownloader(get_downloads())
    return rss_downloader


async def rss_downloader_loop():
    # https://stackoverflow.com/questions/37512182/how-can-i-periodically-execute-a-function-with-asyncio
    while True:
        assert rss_downloader is not None, "rss downloader failed to initialize"
        await asyncio.gather(
            rss_downloader.check_possibly_download(),
            asyncio.sleep(rss_check_period_s),
        )


rss_downloader = get_rss_downloader()

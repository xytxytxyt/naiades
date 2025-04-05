import datetime
import logging
import re
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

    def get_new_downloads(self) -> dict[str, str]:
        new_downloads: dict[str, str] = {}
        now = datetime.datetime.today().astimezone()
        resp = requests.get(
            self.url,
            headers={
                "If-Modified-Since": self.get_last_checked_time_for_rss(),
            },
        )
        if resp.status_code == requests.codes.ok:
            self.logger.info(f"new updates from rss {self.url}")
            self.last_checked_time = now
            self.update_new_downloads_from_xml(resp.text, new_downloads)
        elif resp.status_code == requests.codes.not_modified:
            self.logger.info(f"no updates from rss {self.url}")
        else:
            self.logger.error(
                f"error getting updates from rss {self.url}: {resp.status_code}, {resp.text}"
            )
        return new_downloads

    def check_and_possibly_download(self):
        # new_downloads = self.get_new_downloads()
        pass


rss_downloader = None


def get_rss_downloader() -> RSSDownloader:
    global rss_downloader
    if rss_downloader is None:
        rss_downloader = RSSDownloader(get_downloads())
    return rss_downloader

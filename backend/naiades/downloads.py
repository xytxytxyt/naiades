import datetime
import os
import re
from dataclasses import dataclass, field
from typing import Optional

import yaml
from dataclasses_json import DataClassJsonMixin

downloads_config_path = "configs/downloads.yaml"
downloads_date_time_format = "%Y-%m-%d %H:%M:%S"


@dataclass
class DownloadSubdir(DataClassJsonMixin):
    name: str
    path: Optional[str] = None
    pattern: Optional[str] = None

    def __post_init__(self):
        if self.pattern is None:
            self.pattern = rf".*{self.name}.*"
        self.compiled_pattern = re.compile(self.pattern)


@dataclass
class DownloadSubdirDisplay(DataClassJsonMixin):
    name: str
    most_recent_file: str | None
    date_time: str | datetime.datetime


@dataclass
class DownloadDir(DataClassJsonMixin):
    path: str
    subdirs: list[DownloadSubdir]
    subdirs_dict: Optional[dict[str, DownloadSubdir]] = field(default=None, repr=False)

    def __post_init__(self):
        if self.subdirs_dict is None:
            self.subdirs_dict = {}
        for subdir in self.subdirs:
            if subdir.path is None:
                subdir.path = os.path.join(self.path, subdir.name)
            self.subdirs_dict[subdir.name] = subdir

    def list_subdirs_by_mtime(self) -> list[DownloadSubdirDisplay]:
        subdirs = os.listdir(self.path)
        results_unsorted: list[DownloadSubdirDisplay] = []
        for subdir in subdirs:
            subdir_path = os.path.join(self.path, subdir)
            if os.path.isdir(subdir_path):
                subdir_ename_times: list[tuple[str | None, float]] = []
                for e in os.listdir(subdir_path):
                    e_path = os.path.join(subdir_path, e)
                    if os.path.isfile(e_path):
                        subdir_ename_times.append((e, os.path.getmtime(e_path)))
                subdir_ename_time = max(
                    subdir_ename_times,
                    default=(None, 0),
                    key=(lambda e: e[1]),
                )
                results_unsorted.append(
                    DownloadSubdirDisplay(
                        name=subdir,
                        most_recent_file=subdir_ename_time[0],
                        date_time=datetime.datetime.fromtimestamp(subdir_ename_time[1]),
                    )
                )

        results_sorted = sorted(
            results_unsorted, reverse=True, key=(lambda e: e.date_time)
        )

        for result in results_sorted:
            # the time is off... have not figured out why
            if isinstance(result.date_time, datetime.datetime):
                result.date_time = result.date_time.strftime(downloads_date_time_format)

        return results_sorted


@dataclass
class Downloads(DataClassJsonMixin):
    rss_url: str
    downloads: list[DownloadDir]


downloads = None


def get_downloads() -> Downloads:
    global downloads
    if downloads is None:
        with open(downloads_config_path) as f:
            downloads = Downloads.from_dict(yaml.safe_load(f.read()))
    return downloads


downloads = get_downloads()

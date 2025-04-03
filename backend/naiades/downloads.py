import datetime
import os
import re
from dataclasses import dataclass
from typing import Optional

import yaml
from dataclasses_json import DataClassJsonMixin

downloads_config_path = "configs/downloads.yaml"


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
class DownloadDir(DataClassJsonMixin):
    path: str
    subdirs: list[DownloadSubdir]

    def __post_init__(self):
        for subdir in self.subdirs:
            if subdir.path is None:
                subdir.path = os.path.join(self.path, subdir.name)


@dataclass
class Downloads(DataClassJsonMixin):
    rss_url: str
    downloads: list[DownloadDir]


def get_downloads() -> Downloads:
    with open(downloads_config_path) as f:
        return Downloads.from_dict(yaml.safe_load(f.read()))


def list_subdirs_by_time(dir: str) -> list[tuple[str, str]]:
    subdirs = os.listdir(dir)
    subdirs_datetimes: list[tuple[str, datetime.datetime]] = []
    for subdir in subdirs:
        subdir_path = os.path.join(dir, subdir)
        if os.path.isdir(subdir_path):
            subdir_times: list[float] = []
            for e in os.listdir(subdir_path):
                e_path = os.path.join(subdir_path, e)
                if os.path.isfile(e_path):
                    subdir_times.append(os.path.getmtime(e_path))
            subdir_time = max(subdir_times, default=0)
            subdirs_datetimes.append(
                (subdir, datetime.datetime.fromtimestamp(subdir_time))
            )
    subdirs_datetimes_sorted = sorted(
        subdirs_datetimes, reverse=True, key=(lambda e: e[1])
    )

    # the time is off... have not figured out why
    return [
        (subdir, subdir_time.strftime("%Y-%m-%d %H:%M:%S"))
        for subdir, subdir_time in subdirs_datetimes_sorted
    ]

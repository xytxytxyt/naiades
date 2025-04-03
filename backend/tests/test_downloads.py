import json

from naiades.downloads import get_downloads, list_subdirs_by_time


def test_get_downloads():
    downloads = get_downloads()
    print(json.dumps(downloads.to_dict(), indent=4))


def test_list_subdirs_by_time():
    dir = "/Volumes/My Passport/Anime"
    subdirs = list_subdirs_by_time(dir)
    print(subdirs)

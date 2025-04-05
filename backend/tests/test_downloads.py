import json

from naiades.downloads import get_downloads


def test_get_downloads():
    downloads = get_downloads()
    print(json.dumps(downloads.to_dict(), indent=2))
    assert len(downloads.downloads) > 0


def test_list_subdirs_by_time():
    downloads = get_downloads()
    subdirs = downloads.downloads[0].list_subdirs_by_mtime()
    print(json.dumps([subdir.to_dict() for subdir in subdirs], indent=2))
    assert len(subdirs) > 0

import datetime
import json

from naiades.rss import get_rss_downloader, rss_date_time_format


def test_approximate_last_checked_time():
    rss_downloader = get_rss_downloader()
    print(rss_downloader.last_checked_time)
    assert rss_downloader.last_checked_time > datetime.datetime(2025, 1, 1).astimezone()


def test_get_patterns_paths():
    rss_downloader = get_rss_downloader()
    patterns_paths = rss_downloader.patterns_paths
    print(json.dumps(patterns_paths, indent=2))
    assert len(patterns_paths) > 0


def test_get_last_checked_time_for_rss():
    rss_downloader = get_rss_downloader()
    last_checked_time = rss_downloader.get_last_checked_time_for_rss()
    print(last_checked_time)
    datetime.datetime.strptime(last_checked_time, rss_date_time_format)


def test_get_new_downloads():
    rss_downloader = get_rss_downloader()
    new_downloads = rss_downloader.get_new_downloads()
    print(json.dumps(new_downloads, indent=2))
    assert isinstance(new_downloads, dict)

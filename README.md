# Naiades

This is an app that automates my downloads. It has a very simple RSS poller, and makes use of the [webtorrent](https://github.com/webtorrent/webtorrent) CLI. There's a simple FastAPI backend and React frontend.

There has been no attempt to make this production-ready as it runs on maybe two machines on my local network.

There are commands in Makefiles to run the frontend and backend in dev mode.
```
ALLOWED_ORIGIN_HOSTS=<server's IP address> make run

VITE_BACKEND_HOST=<server's IP address> make run
```

FastAPI comes by default with Swagger: http://127.0.0.1:8001/docs

from typing import Any

from pytest_django.live_server_helper import LiveServer

from django.contrib.staticfiles.handlers import StaticFilesHandler

static_404s: list[str] = []


class RecordingStaticFilesHandler(StaticFilesHandler):
    def get_response(self, request):
        from django.conf import settings

        response = super().get_response(request)
        if response.status_code == 404 and request.path.startswith(settings.STATIC_URL):
            static_404s.append(request.get_full_path())
        return response


class WatchingLiveServer(LiveServer):
    def __init__(self, addr: str, *, start: bool = True) -> None:
        from django.db import connections
        from django.test.testcases import LiveServerThread
        from django.test.utils import modify_settings

        liveserver_kwargs: dict[str, Any] = {"static_handler": RecordingStaticFilesHandler}

        connections_override = {}
        for conn in connections.all():
            if conn.vendor == "sqlite" and conn.is_in_memory_db():
                connections_override[conn.alias] = conn

        liveserver_kwargs["connections_override"] = connections_override

        try:
            host, port = addr.split(":")
        except ValueError:
            host = addr
        else:
            liveserver_kwargs["port"] = int(port)
        self.thread = LiveServerThread(host, **liveserver_kwargs)

        self._live_server_modified_settings = modify_settings(
            ALLOWED_HOSTS={"append": host},
        )

        self.thread.daemon = True

        if start:
            self.start()

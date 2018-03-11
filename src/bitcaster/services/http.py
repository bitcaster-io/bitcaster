import sys

from gunicorn.app.wsgiapp import WSGIApplication
from gunicorn.arbiter import Arbiter

from .base import Service


class Application(WSGIApplication):
    def __init__(self, options):
        super().__init__(self, None)
        self.usage = None
        self.cfg = None
        self.config_file = options.get("config") or ""
        self.options = options
        self.callable = None
        self.project_path = None

        self.do_load_config()

        for k, v in self.options.items():
            if k.lower() in self.cfg.settings and v is not None:
                self.cfg.set(k.lower(), v)

    def load_config(self):
        pass

    def init(self, parser, opts, args):
        pass

    def load(self):
        from bitcaster.config.wsgi import application
        return application


class HTTPServer(Service):
    name = 'http'

    def __init__(self, *, host='localhost', port='8000', debug=False, daemonize=False,
                 workers=0, pidfile=None, logfile=None, reload=False):
        super().__init__(debug=debug)
        self.host = host
        self.port = port
        self.app = Application({
            'bind': '%s:%s' % (self.host, self.port),
            'debug': debug,
            'daemon': daemonize,
            'workers': workers,
            'reload': reload,
            'pidfile': pidfile,
            'errorlog': logfile,
        })

    def run(self):
        try:
            Arbiter(self.app).run()
        except RuntimeError as e:
            sys.stderr.write("\nError: %s\n\n" % e)
            sys.stderr.flush()
            sys.exit(1)

    start = run

import sys

from gunicorn.app.wsgiapp import WSGIApplication

from .base import Service


class BitApplication(WSGIApplication):
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
        # disable argument parsing
        pass

    def init(self, parser, opts, args):
        # disable argument parsing
        pass

    def load(self):
        from bitcaster.config.wsgi import application
        return application

    def run(self):
        super().run()


class HTTPServer(Service):
    name = 'http'

    def __init__(self, *, host='localhost', port='8000', debug=False, daemonize=False,
                 workers=0, pidfile=None, logfile=None, reload=False):
        super().__init__(debug=debug)
        self.host = host
        self.port = port
        self.app = BitApplication({
            'proc_name': 'bitcaster',
            'bind': '%s:%s' % (self.host, self.port),
            'debug': debug,
            'daemon': daemonize,
            'workers': workers,
            'worker_int': None,
            'reload': reload,
            'pidfile': pidfile,
            'errorlog': logfile,
        })

    def run(self):
        try:
            self.app.run()
            # Arbiter(self.app).run()
        except RuntimeError as e:
            sys.stderr.write("\nError: %s\n\n" % e)
            sys.stderr.flush()
            sys.exit(1)


class DevHTTPServer(HTTPServer):
    pass
    # def run(self):
    #     try:
    #         self.app.run()
    #     except RuntimeError as e:
    #         sys.stderr.write("\nError: %s\n\n" % e)
    #         sys.stderr.flush()
    #         sys.exit(1)

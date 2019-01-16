from constance import config


class System:

    @property
    def configured(self):
        return config.SYSTEM_CONFIGURED == 3


system = System()

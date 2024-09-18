from bitcaster.agents.base import Agent


class XAgent(Agent):

    def notify(self) -> None:
        pass

    def check(self, notify: bool = True, update: bool = True) -> None:
        pass

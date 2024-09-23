from bitcaster.agents.base import Agent


class XAgent(Agent):  # type: ignore

    def notify(self) -> None:
        pass

    def check(self, notify: bool = True, update: bool = True) -> None:
        pass

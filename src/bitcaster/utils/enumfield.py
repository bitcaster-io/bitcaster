from enum import Enum


class EnumField(Enum):

    def __new__(cls, value):
        member = object.__new__(cls)
        member._value_ = value
        return member

    def __int__(self):
        return self.value

    def __gt__(self, other):
        return int(self) > int(other or '0')

    def __lt__(self, other):
        return int(self) < int(other or '0')

    def __eq__(self, other):
        return int(self) == int(other or '0')

    def __hash__(self):
        return int(self)

    @classmethod
    def as_choices(cls):
        raise NotImplementedError

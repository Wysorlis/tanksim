# coding: utf-8

class KeyRequestError(KeyError):
    def __str__(self) -> str:
        if len(self.args) == 1:
            return str(f"\n{self.args[0]}")
        return super().__str__()

class DuplicateRequestError(KeyError):
    def __str__(self) -> str:
        if len(self.args) == 1:
            return str(f"\n{self.args[0]}")
        return super().__str__()
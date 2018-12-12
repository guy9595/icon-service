from iconservice import *


class TestInterface(InterfaceScore):
    @interface
    def set_value(self, value: int) -> None: pass

    @interface
    def get_value(self) -> int: pass

    @interface
    def get_value_wrong_type(self) -> int: pass


class TestLinkScore(IconScoreBase):
    _SCORE_ADDR = 'score_addr'

    @eventlog(indexed=1)
    def Changed(self, value: int):
        pass

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self._value = VarDB('value', db, value_type=int)
        self._addr_score = VarDB(self._SCORE_ADDR, db, value_type=Address)

    def on_install(self, value: int=0) -> None:
        super().on_install()
        self._value.set(value)

    def on_update(self) -> None:
        super().on_update()

    @external(readonly=False)
    def add_score_func(self, score_addr: Address) -> None:
        self._addr_score.set(score_addr)

    @external(readonly=True)
    def get_value(self) -> int:
        test_interface = self.create_interface_score(self._addr_score.get(), TestInterface)
        return test_interface.get_value()

    @external
    def set_value(self, value: int):
        test_interface = self.create_interface_score(self._addr_score.get(), TestInterface)
        test_interface.set_value(value)
        self.Changed(value)

    @external
    def increase_value_fail(self):
        test_interface = self.create_interface_score(self._addr_score.get(), TestInterface)
        value = test_interface.get_value_wrong_type()
        new_value = value + 1
        test_interface.set_value(new_value)
        self.Changed(new_value)

    @external(readonly=True)
    def get_value_fail(self) -> int:
        test_interface = self.create_interface_score(self._addr_score.get(), TestInterface)
        value = test_interface.get_value_wrong_type()
        return value

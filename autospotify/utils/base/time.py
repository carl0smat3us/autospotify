from random import uniform


class Time:
    def __init__(self):
        self._delay_page_loading = None
        self._delay_start_interactions = None

    @property
    def delay_page_loading(self) -> int:
        if self._delay_page_loading is None:
            self._delay_page_loading = uniform(10, 20)
        return self._delay_page_loading

    @property
    def delay_start_interactions(self) -> int:
        if self._delay_start_interactions is None:
            self._delay_start_interactions = uniform(5, 10)
        return self._delay_start_interactions

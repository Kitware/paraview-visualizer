from trame.widgets.trame import ListBrowser

SOURCES = [
    "Cone",
    "Box",
    "Cylinder",
    "Sphere",
    "Wavelet",
]

FILTERS = [
    "Clip",
    "Contour",
    "StreamTracer",
]


class Algorithms(ListBrowser):
    def __init__(self, add_defaults=True, click=None, **kwargs):
        super().__init__(
            list=("algorithm_list", []),
            click=(self._click, "[$event.value]"),
            **kwargs,
        )
        self._click_fn = click

        if add_defaults:
            self.server.state.algorithm_list = []
            for name in SOURCES:
                self.add_source(name)
            for name in FILTERS:
                self.add_filter(name)

    def add_source(self, name):
        self.add_entry(text=name, type="source", prependIcon="mdi-database-plus")

    def add_filter(self, name):
        self.add_entry(text=name, type="filter", prependIcon="mdi-filter-plus")

    def add_entry(self, **kwargs):
        """Possible keys: text, prependIcon and appendIcon"""
        self.server.state.algorithm_list += [kwargs]

    def _click(self, index):
        entry = self.server.state.algorithm_list[index]
        name = entry.get("text")
        if self._click_fn:
            self._click_fn(name)

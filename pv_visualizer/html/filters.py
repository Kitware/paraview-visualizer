from trame import state, controller as ctrl
from trame.html.widgets import ListBrowser

try:
    from paraview import simple
except:
    simple = None

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
    def __init__(self, add_defaults=True, **kwargs):
        super().__init__(
            list=("algorithm_list", []),
            click=(self._click, "[$event.value]"),
            **kwargs,
        )

        if add_defaults:
            state.algorithm_list = []
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
        state.algorithm_list += [kwargs]

    def _click(self, index):
        entry = state.algorithm_list[index]
        name = entry.get("text")
        newProxy = simple.__dict__[name]()
        rep = simple.Show(newProxy)

        # Use life cycle handler
        ctrl.on_data_change()

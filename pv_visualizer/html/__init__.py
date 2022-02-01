from trame import state, controller as ctrl
from trame.internal.app import get_app_instance
from trame.html import AbstractElement
from . import module

from trame.internal.app import get_app_instance

# Activate your Vue library
_app = get_app_instance()
_app.enable_module(module)

# Expose your vue component(s)
class CustomWidget(AbstractElement):
    def __init__(self, **kwargs):
        super().__init__(
            "your-custom-widget",
            **kwargs,
        )
        self._attr_names += [
            "attribute_name",
            ("py_attr_name", "js_attr_name"),
        ]
        self._event_names += [
            "click",
            "change",
        ]

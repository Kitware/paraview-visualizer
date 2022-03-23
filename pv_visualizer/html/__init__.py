from trame import state, controller as ctrl
from trame.internal.app import get_app_instance
from trame.html import AbstractElement
from . import module

from trame.internal.app import get_app_instance

# Activate your Vue library
_app = get_app_instance()
_app.enable_module(module)

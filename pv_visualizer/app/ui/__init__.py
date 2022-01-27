from . import main

__all__ = [
    "layout",
    "on_reload",
]

layout = main.layout

def on_reload(reload_modules):
    """Method called when the module is reloaded

    reload_modules is a function that takes modules to reload

    We only need to reload the controller if the engine is reloaded.
    """
    reload_modules(main)

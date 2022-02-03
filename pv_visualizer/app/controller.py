from . import engine


def bind_methods():
    pass


def on_start():
    engine.initialize()
    bind_methods()


def on_reload(reload_modules):
    bind_methods()

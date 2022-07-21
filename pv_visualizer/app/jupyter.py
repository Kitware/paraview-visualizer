from trame.app import get_server, jupyter
from pv_visualizer.app import engine, ui


def show(server=None, **kwargs):
    """Run and display the trame application in jupyter's event loop
    The kwargs are forwarded to IPython.display.IFrame()
    """
    if server is None:
        server = get_server()

    if isinstance(server, str):
        server = get_server(server)

    # Initilize app
    engine.initialize(server)
    ui.initialize(server)

    # Show as cell result
    jupyter.show(server, **kwargs)

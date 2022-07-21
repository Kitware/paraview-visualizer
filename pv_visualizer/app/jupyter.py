from pathlib import Path
from trame.app import get_server, jupyter
from pv_visualizer.app import engine, ui

LOGGING_PACKAGES = [
    "pv_visualizer.app.engine",
    "pv_visualizer.app.engine.proxymanager.core",
    "pv_visualizer.app.engine.proxymanager.decorators",
    "pv_visualizer.app.engine.proxymanager.definitions",
    "pv_visualizer.app.engine.proxymanager.domains",
    "pv_visualizer.app.engine.proxymanager.domain_helpers",
    "pv_visualizer.app.engine.reactions.scalar_range",
]


def show(server=None, **kwargs):
    """Run and display the trame application in jupyter's event loop
    The kwargs are forwarded to IPython.display.IFrame()
    """
    if server is None:
        server = get_server()

    if isinstance(server, str):
        server = get_server(server)

    # Disable logging
    import logging

    for package_name in LOGGING_PACKAGES:
        logging.getLogger(package_name).setLevel(logging.WARNING)

    # Fill default args
    server.cli.add_argument(
        "--data", help="Path to browse", dest="data", default=str(Path.home())
    )

    # Initialize app
    engine.initialize(server)
    ui.initialize(server)

    # Show as cell result
    jupyter.show(server, **kwargs)

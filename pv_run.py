r"""
Should run this file when running with pvpython while setting PV_VENV=
"""
from pathlib import Path
import paraview.web.venv  # noqa to get venv loaded
from pv_visualizer import main
from trame.app import get_server

if __name__ == "__main__":
    server = get_server()
    server.cli.add_argument(
        "--data", help="Path to browse", dest="data", default=str(Path.home())
    )
    print("Add data")
    server.cli.add_argument(
        "--plugins", help="List of distributed plugins to load", dest="plugins"
    )
    print("Add plugins")
    main(server)

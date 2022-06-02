import os
from pathlib import Path

from pv_visualizer.html.file_browser import ParaViewFileBrowser
from .pipeline import NAME as pipeline_name

from paraview import simple

# -----------------------------------------------------------------------------
# UI module
# -----------------------------------------------------------------------------

NAME = "files"
ICON = "mdi-file-document-outline"
ICON_STYLE = {}

# -----------------------------------------------------------------------------
# Init
# -----------------------------------------------------------------------------


def initialize(server):
    state, ctrl = server.state, server.controller
    args, _ = server.cli.parse_known_args()

    def add_prefix(file_path):
        return str(Path(os.path.join(args.data, file_path)).absolute())

    def load_file(files):
        active_change = False
        if isinstance(files, list):
            # time series
            files_to_load = map(add_prefix, files)
            reader = simple.OpenDataFile(files_to_load)
            simple.Show(reader)  # Should be deferred
        elif files.endswith(".pvsm"):
            # state file
            simple.Render()
            state_to_load = add_prefix(files)
            if state.settings_use_relative_path:
                simple.LoadState(
                    state_to_load,
                    data_directory=str(Path(state_to_load).parent.resolve().absolute()),
                    restrict_to_data_directory=True,
                )
            else:
                simple.LoadState(state_to_load)

            view = simple.GetActiveView()
            view.MakeRenderWindowInteractor(True)
            ctrl.view_replace(view)
            active_change = True
        else:
            # data file
            data_to_load = add_prefix(files)
            reader = simple.OpenDataFile(data_to_load)
            simple.Show(reader)  # Should be deferred

        # Update state
        state.active_controls = pipeline_name

        # Use life cycle handler
        ctrl.on_data_change(reset_camera=True)
        if active_change:
            ctrl.on_active_proxy_change()

    # -----------------------------------------------------------------------------
    # Update controller
    # -----------------------------------------------------------------------------

    ctrl.files_load_file = load_file


# -----------------------------------------------------------------------------
# Panel
# -----------------------------------------------------------------------------


def create_panel(server):
    args, _ = server.cli.parse_known_args()
    ctrl = server.controller
    ParaViewFileBrowser(
        args.data,
        on_load_file=ctrl.files_load_file,
        query=("search", ""),
        v_if=(f"active_controls == '{NAME}'",),
    )

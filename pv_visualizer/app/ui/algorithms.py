from pv_visualizer.html.filters import Algorithms
from .pipeline import NAME as pipeline_name

from paraview import simple

# -----------------------------------------------------------------------------
# UI module
# -----------------------------------------------------------------------------

NAME = "algorithms"
ICON = "mdi-database-edit-outline"
ICON_STYLE = {}


def initialize(server):
    state, ctrl = server.state, server.controller

    def create_filter(name):
        newProxy = simple.__dict__[name]()
        simple.Show(newProxy)

        # Update state
        state.active_controls = pipeline_name

        # Use life cycle handler
        ctrl.on_data_change()

    ctrl.algo_create_filter = create_filter


def create_panel(server):
    ctrl = server.controller
    Algorithms(
        v_if=(f"active_controls == '{NAME}'",),
        query=("search", ""),
        click=ctrl.algo_create_filter,
    )

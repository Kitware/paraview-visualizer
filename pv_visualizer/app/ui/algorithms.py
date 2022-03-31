from trame import state, controller as ctrl
from pv_visualizer.html.filters import Algorithms
from .pipeline import NAME as pipeline_name

try:
    from paraview import simple
except:
    simple = None

# -----------------------------------------------------------------------------
# UI module
# -----------------------------------------------------------------------------

NAME = "algorithms"
ICON = "mdi-database-edit-outline"
ICON_STYLE = {}


def create_filter(name):
    newProxy = simple.__dict__[name]()
    rep = simple.Show(newProxy)

    # Update state
    state.active_controls = pipeline_name

    # Use life cycle handler
    ctrl.on_data_change()


def create_panel(container):
    with container:
        Algorithms(
            v_if=(f"active_controls == '{NAME}'",),
            query=("search", ""),
            click=create_filter,
        )

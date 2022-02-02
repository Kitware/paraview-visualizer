from pv_visualizer.html.filters import Algorithms

# -----------------------------------------------------------------------------
# UI module
# -----------------------------------------------------------------------------

NAME = "algorithms"
ICON = "mdi-database-edit-outline"
ICON_STYLE = {}


def create_panel(container):
    with container:
        Algorithms(
            v_if=(f"active_controls == '{NAME}'",),
            query=("search", ""),
        )

from trame import controller as ctrl
from pv_visualizer.html.pipeline import PipelineBrowser

# -----------------------------------------------------------------------------
# UI module
# -----------------------------------------------------------------------------

NAME = "pipeline"
ICON = "mdi-source-branch"
ICON_STYLE = {"style": "transform: scale(1, -1);"}


def create_panel(container):
    with container:
        pipeline_browser = PipelineBrowser(
            v_if=(f"active_controls == '{NAME}'",),
            width=container.width,
        )
        ctrl.pipeline_update = pipeline_browser.update

from trame.app import dev
from trame.widgets import html, vuetify
from pv_visualizer.html import pipeline, proxy_editor, data_information


def _reload():
    dev.reload(
        pipeline,
        proxy_editor,
        data_information,
    )


def initialize(server):
    server.controller.on_server_reload.add(_reload)


# -----------------------------------------------------------------------------
# UI module
# -----------------------------------------------------------------------------

NAME = "pipeline"
ICON = "mdi-source-branch"
ICON_STYLE = {"style": "transform: scale(1, -1);"}

ICON_COLLAPSE = "mdi-unfold-less-horizontal"
ICON_EXPAND = "mdi-unfold-more-horizontal"

COMPACT = {
    "dense": True,
    "hide_details": True,
}

TOP_ICONS = [
    {"icon": "mdi-source-branch", "kwargs": ICON_STYLE},
    {"icon": "mdi-format-list-bulleted-type", "kwargs": {}},
    {"icon": "mdi-clock-outline", "kwargs": {}},
]


def create_panel(server, width=300):
    ctrl = server.controller
    with html.Div(
        v_if=(f"active_controls == '{NAME}'",),
        classes="pa-0 ma-0 d-flex flex-column",
        style="height: 100%;",
    ):
        with vuetify.VToolbar(
            dense=True, outlined=True, classes="pa-0 ma-0", style="flex: none;"
        ):
            with vuetify.VTabs(
                v_model=("pipeline_elem", 0),
                **COMPACT,
                outlined=True,
                rounded=True,
                required=True,
            ):
                for item in TOP_ICONS:
                    with vuetify.VTab(
                        classes="px-0 mx-0",
                        style="min-width: 40px;",
                        **COMPACT,
                    ):
                        vuetify.VIcon(item.get("icon"), **item.get("kwargs"))

            vuetify.VSpacer()
            with vuetify.VBtn(
                small=True,
                icon=True,
                click="show_pipeline = !show_pipeline",
            ):
                vuetify.VIcon(ICON_COLLAPSE, v_if=("show_pipeline",))
                vuetify.VIcon(ICON_EXPAND, v_if=("!show_pipeline",))

        with html.Div(
            style="flex: none; max-height: calc((100vh - 48px)/2 - 48px); overflow: auto;",
            v_if=("show_pipeline", 1),
        ):
            pipeline_browser = pipeline.PipelineBrowser(width=width)
            ctrl.pipeline_update = pipeline_browser.update

        # editor part
        proxy_editor.ProxyEditor(v_if=("pipeline_elem === 0",))
        data_information.DataInformation(v_show=("pipeline_elem === 1",))

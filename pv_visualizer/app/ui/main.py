from trame import controller as ctrl
from trame.layouts import SinglePageWithDrawer
from trame.html import vuetify, paraview

# from pv_visualizer import html as my_widgets
from pv_visualizer.app import assets
from pv_visualizer.app.ui import pipeline, files, algorithms, settings, state_change

from paraview import simple

# -----------------------------------------------------------------------------
# Common style properties
# -----------------------------------------------------------------------------

COMPACT = {
    "dense": True,
    "hide_details": True,
}

CONTROLS = [
    pipeline,
    files,
    algorithms,
    settings,
]

# -----------------------------------------------------------------------------
# Dynamic reloading
# -----------------------------------------------------------------------------

LIFE_CYCLES = [
    "on_data_change",
]


def bind_life_cycle_methods():
    ctrl.on_data_change.add(ctrl.view_update)
    ctrl.on_data_change.add(ctrl.pipeline_update)


def on_reload(reload_modules):
    for name in LIFE_CYCLES:
        ctrl[name].clear()
    reload_modules(*CONTROLS, state_change)
    bind_life_cycle_methods()


bind_life_cycle_methods()

# -----------------------------------------------------------------------------
# Layout
# -----------------------------------------------------------------------------

layout = SinglePageWithDrawer(
    "Visualizer",
    favicon=assets.PV_LOGO_PATH,
    show_drawer=True,
    width=300,
    show_drawer_name="drawer_visibility",
    on_ready=ctrl.view_update,
)

# -----------------------------------------------------------------------------
# Toolbar
# -----------------------------------------------------------------------------
layout.logo.children = [f'<img src="{assets.PV_LOGO_URL}" height="40" />']
layout.logo.click = None
layout.title.set_text("Visualizer")
with layout.toolbar as tb:
    tb.dense = True
    tb.clipped_right = True
    vuetify.VSpacer()
    vuetify.VTextField(
        v_show=("!!active_controls",),
        v_model=("search", ""),
        clearable=True,
        outlined=True,
        filled=True,
        rounded=True,
        prepend_inner_icon="mdi-magnify",
        style="max-width: 30vw;",
        **COMPACT,
    )
    vuetify.VSpacer()
    with vuetify.VBtnToggle(
        v_model=("active_controls", "files"), **COMPACT, outlined=True, rounded=True
    ):
        for item in CONTROLS:
            with vuetify.VBtn(value=item.NAME, **COMPACT):
                vuetify.VIcon(item.ICON, **item.ICON_STYLE)

# -----------------------------------------------------------------------------=
# Drawer
# -----------------------------------------------------------------------------
with layout.drawer as dr:
    dr.right = True
    # dr.expand_on_hover = True
    for item in CONTROLS:
        item.create_panel(dr)

# -----------------------------------------------------------------------------
# Main content
# -----------------------------------------------------------------------------
with layout.content:
    with vuetify.VContainer(fluid=True, classes="fill-height pa-0 ma-0"):
        html_view = paraview.VtkRemoteLocalView(
            simple.GetRenderView(),
            interactive_ratio=("view_interactive_ratio", 1),
            interactive_quality=("view_interactive_quality", 70),
            mode="local",
            namespace="view",
            style="width: 100%; height: 100%;",
        )
        ctrl.view_replace = html_view.replace_view
        ctrl.view_update = html_view.update
        ctrl.view_reset_camera = html_view.reset_camera

# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
# layout.footer.hide()

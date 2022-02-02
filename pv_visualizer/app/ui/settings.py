from trame import state, controller as ctrl
from trame.html import Div, vuetify
from paraview import simple

NAME = "settings"
ICON = "mdi-cog"
ICON_STYLE = {}

COMPACT = {
    "dense": True,
    "hide_details": True,
}


def to_float(hex):
    return int(hex, 16) / 255.0


def to_hex(float_value):
    v = int(float_value * 255)
    s = f"00{hex(v).split('x')[1]}"
    return s[-2:]


# Extract view BG color
view = simple.GetRenderView()
view.UseColorPaletteForBackground = 0
[red, green, blue] = view.Background
VIEW_BG_HEX = f"#{to_hex(red)}{to_hex(green)}{to_hex(blue)}"


def create_card(title, reset_fn, **kwargs):
    with vuetify.VCard(classes="pa-0", flat=True, outlined=False, tile=True, **kwargs):
        vuetify.VDivider()
        with vuetify.VCardTitle(classes="d-flex align-center py-1"):
            Div(title)
            vuetify.VSpacer()
            with vuetify.VBtn(icon=True, small=True, click=reset_fn):
                vuetify.VIcon("mdi-restore")
        vuetify.VDivider()
        return vuetify.VCardText()


def create_panel(container):
    with container:
        with vuetify.VCol(
            v_if=(f"active_controls == '{NAME}'",), classes="mx-0 pa-0", **COMPACT
        ):
            with vuetify.VRow(
                classes="my-0 py-3 mx-0 px-3 d-flex align-center justify-space-between"
            ):
                with Div(classes="d-flex align-center"):
                    vuetify.VIcon(
                        classes="mr-2",
                        v_text=("viewMode == 'local' ? 'mdi-rotate-3d' : 'mdi-image'",),
                    )
                    vuetify.VSwitch(
                        v_model=("viewMode",),
                        false_value="remote",
                        true_value="local",
                        classes="ma-0",
                        hide_details=True,
                    )

                with Div(classes="d-flex align-center"):
                    vuetify.VIcon(
                        "mdi-theme-light-dark",
                        classes="mr-2",
                    )
                    vuetify.VSwitch(
                        v_model=("$vuetify.theme.dark",),
                        classes="ma-0",
                        hide_details=True,
                        false_value=("true",),
                        true_value=("false",),
                    )

                with Div(classes="d-flex align-center"):
                    vuetify.VIcon(
                        "mdi-tune",
                        classes="mr-2",
                    )
                    vuetify.VSwitch(
                        v_model=("settings_advanced", False),
                        classes="ma-0",
                        hide_details=True,
                    )

            with create_card("Background color", reset_bg_color):
                vuetify.VColorPicker(
                    v_model=("view_background", VIEW_BG_HEX),
                    hide_mode_switch=True,
                )

            with create_card(
                "Remote rendering", reset_remote_rendering, v_if=("settings_advanced",)
            ):
                vuetify.VSlider(
                    label="Ratio",
                    v_model=("view_interactive_ratio", 1),
                    min=0.3,
                    max=1,
                    step=0.05,
                    **COMPACT,
                )
                vuetify.VSlider(
                    label="Quality",
                    v_model=("view_interactive_quality", 70),
                    min=10,
                    max=100,
                    step=2,
                    **COMPACT,
                )


@state.change("view_background")
def update_background(view_background, **kwargs):
    red = to_float(view_background[1:3])
    green = to_float(view_background[3:5])
    blue = to_float(view_background[5:7])
    view.Background = [red, green, blue]
    ctrl.view_update()


def reset_bg_color():
    state.view_background = VIEW_BG_HEX


def reset_remote_rendering():
    state.view_interactive_ratio = 1
    state.view_interactive_quality = 70

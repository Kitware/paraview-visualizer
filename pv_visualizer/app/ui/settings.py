from trame.widgets import html, vuetify, simput


NAME = "settings"
ICON = "mdi-cog"
ICON_STYLE = {}

COMPACT = {
    "dense": True,
    "hide_details": True,
}


def initialize(server):
    state, ctrl = server.state, server.controller

    def reset_remote_rendering():
        state.view_interactive_ratio = 1
        state.view_interactive_quality = 70

    def reset_state_loading():
        state.settings_use_relative_path = True

    ctrl.settings_reset_remote_rendering = reset_remote_rendering
    ctrl.settings_reset_state_loading = reset_state_loading


def create_card(title, reset_fn=None, **kwargs):
    with vuetify.VCard(classes="pa-0", flat=True, outlined=False, tile=True, **kwargs):
        vuetify.VDivider()
        with vuetify.VCardTitle(classes="d-flex align-center py-1"):
            html.Div(title)
            if reset_fn is not None:
                vuetify.VSpacer()
                if isinstance(reset_fn, tuple):
                    vuetify.VCheckbox(
                        v_model=(reset_fn[0],),
                        on_icon=reset_fn[1],
                        off_icon=reset_fn[2],
                        hide_details=True,
                        dense=True,
                        classes="mt-0 pt-0",
                    )
                else:
                    with vuetify.VBtn(icon=True, small=True, click=reset_fn):
                        vuetify.VIcon("mdi-restore")
        vuetify.VDivider()
        return vuetify.VCardText()


def create_panel(server):
    state, ctrl = server.state, server.controller
    with vuetify.VCol(
        v_if=(f"active_controls == '{NAME}'",), classes="mx-0 pa-0", **COMPACT
    ):
        with vuetify.VRow(
            classes="my-0 py-3 mx-0 px-3 d-flex align-center justify-space-between"
        ):
            with html.Div(classes="d-flex align-center"):
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

            with html.Div(classes="d-flex align-center"):
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

            with html.Div(classes="d-flex align-center"):
                vuetify.VIcon(
                    "mdi-tune",
                    classes="mr-2",
                )
                vuetify.VSwitch(
                    v_model=("settings_advanced", True),
                    classes="ma-0",
                    hide_details=True,
                )

        with create_card(
            "State loading",
            ctrl.settings_reset_state_loading,
            v_if=("settings_advanced",),
        ):
            vuetify.VSwitch(
                label="Data directory relative to file",
                v_model=("settings_use_relative_path", True),
                classes="ma-0",
                hide_details=True,
            )
        with create_card(
            "Remote rendering",
            ctrl.settings_reset_remote_rendering,
            v_if=("settings_advanced",),
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

        with vuetify.VToolbar(
            **COMPACT,
            outlined=True,
            classes="pa-0 ma-0 text-no-wrap",
            v_if=("!settings_advanced",),
        ):
            vuetify.VCheckbox(
                label=("setting_proxies[settings_tabs].name",),
                v_model=("ui_advanced",),
                on_icon="mdi-pencil-box-multiple-outline",
                off_icon="mdi-pencil-box-outline",
                hide_details=True,
                dense=True,
                classes="mt-0 pt-0 ml-n2",
            )
            vuetify.VSpacer()
            with vuetify.VTabs(
                v_model=("settings_tabs", 0),
                right=True,
                style=f"max-width: {40 * len(state.setting_proxies)}px;",
                **COMPACT,
            ):
                for entry in state.setting_proxies:
                    with vuetify.VTab(
                        classes="px-0 mx-0",
                        style="min-width: 40px;",
                        **COMPACT,
                    ):
                        vuetify.VIcon(entry.get("icon"))

        for i, entry in enumerate(state.setting_proxies):
            simput.SimputItem(
                v_if=(f"settings_tabs === {i} && !settings_advanced",),
                item_id=(f"setting_proxies[{i}].id",),
            )

from trame import state, controller as ctrl
from trame.html import vuetify, simput, Div

from pv_visualizer.app.engine.proxymanager import ParaviewProxyManager

PXM = ParaviewProxyManager()

DEFAULT_NAMES = [
    {
        "name": "active_proxy_source_id",
        "icon": "mdi-database",
        "kwargs": {
            "v_show": ("!!active_proxy_source_id",),
        },
    },
    {
        "name": "active_proxy_representation_id",
        "icon": "mdi-image-outline",
        "kwargs": {
            "v_show": ("!!active_proxy_representation_id",),
        },
    },
    {
        "name": "active_proxy_view_id",
        "icon": "mdi-cube-scan",
        "kwargs": {},
    },
    {
        "name": "active_proxy_view_id",  # FIXME setting proxy
        "icon": "mdi-cog-outline",
        "kwargs": {},
    },
]

COMPACT = {
    "dense": True,
    "hide_details": True,
}

BTN_STYLE = {
    "x_small": True,
    "fab": True,
    "elevation": 0,
    "outlined": ("!pxmChangeSet",),
    "disabled": ("!pxmChangeSet",),
}

BTN_APPLY_STYLE = {
    **BTN_STYLE,
    "color": "green",
}

BTN_RESET_STYLE = {
    **BTN_STYLE,
    "classes": "mx-3",
    "color": "orange",
}


class ProxyEditor(Div):
    def __init__(self, proxies=DEFAULT_NAMES, **kwargs):
        super().__init__(
            style="min-height: 0;", classes="d-flex flex-column pa-0 ma-0", **kwargs
        )
        self.var_names = []

        # Init state
        state.active_proxy_id = 0

        with self:
            self.toolbar = vuetify.VToolbar(
                dense=True,
                outlined=True,
                classes="pa-0 ma-0",
            )
            with self.toolbar:
                with vuetify.VTabs(
                    v_model=("active_proxy_index", 0),
                    **COMPACT,
                    outlined=True,
                    rounded=True,
                    required=True,
                ):
                    for item in proxies:
                        self.var_names.append(item.get("name"))
                        with vuetify.VTab(
                            classes="px-0 mx-0",
                            style="min-width: 40px;",
                            **COMPACT,
                            **item.get("kwargs"),
                        ):
                            vuetify.VIcon(item.get("icon"))

                vuetify.VSpacer()
                with vuetify.VBtn(**BTN_RESET_STYLE, click=ctrl.pxm_reset):
                    vuetify.VIcon("mdi-undo-variant")
                with vuetify.VBtn(**BTN_APPLY_STYLE, click=ctrl.pxm_apply):
                    vuetify.VIcon("mdi-check-bold")

            # DEBUG - WIP
            with Div(style="overflow: auto;", classes="py-2"):
                simput.SimputItem(
                    v_if=("active_proxy_index === 0",), itemId=("source_id",)
                )
                simput.SimputItem(
                    v_if=("active_proxy_index === 1",), itemId=("representation_id",)
                )

        # Attach state listener
        state.change("active_proxy_index", *self.var_names)(self.update_proxy_edit)
        self.update_proxy_edit(0)

    def update_proxy_edit(self, active_proxy_index, **kwargs):
        state.active_proxy_id = state[self.var_names[active_proxy_index]]

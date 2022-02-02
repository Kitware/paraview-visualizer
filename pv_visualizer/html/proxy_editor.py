from trame import state
from trame.html import vuetify

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
    "outlined": ("!proxy_changeset",),
    "disabled": ("!proxy_changeset",),
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


class ProxyEditor(vuetify.VCol):
    def __init__(self, proxies=DEFAULT_NAMES, **kwargs):
        super().__init__(dense=True, classes="pa-0 ma-0", **kwargs)
        self.var_names = []

        # Init state
        state.active_proxy_id = 0
        state.proxy_changeset = 1

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
                with vuetify.VBtn(**BTN_RESET_STYLE, click=self.reset):
                    vuetify.VIcon("mdi-undo-variant")
                with vuetify.VBtn(**BTN_APPLY_STYLE, click=self.apply):
                    vuetify.VIcon("mdi-check-bold")

        # Attach state listener
        state.change("active_proxy_index", *self.var_names)(self.update_proxy_edit)
        self.update_proxy_edit(0)

    def update_proxy_edit(self, active_proxy_index, **kwargs):
        state.active_proxy_id = state[self.var_names[active_proxy_index]]
        # DEBUG - fake changeset edit
        state.proxy_changeset = active_proxy_index

    def apply(self, *args, **kwargs):
        state.proxy_changeset = 0
        print("flush simput edits...")

    def reset(self, *args, **kwargs):
        state.proxy_changeset = 0
        print("reset simput edits...")

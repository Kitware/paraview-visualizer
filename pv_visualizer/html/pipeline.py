from trame.widgets.trame import GitTree
from paraview import simple, servermanager

from pv_visualizer.app.assets import asset_manager
from . import module

PXM = servermanager.ProxyManager()


def id_to_proxy(_id):
    try:
        _id = int(_id)
    except Exception:
        return None
    if _id <= 0:
        return None

    return simple.servermanager._getPyProxy(
        simple.servermanager.ActiveConnection.Session.GetRemoteObject(_id)
    )


class PipelineBrowser(GitTree):
    def __init__(self, width=50, **kwargs):
        super().__init__(
            sources=("pipeline_sources", []),
            actives=("pipeline_actives", []),
            text_color=(
                "$vuetify.theme.dark ? ['white', 'black'] : ['black', 'white']",
            ),
            width=width,
            # Actions
            action_map=("pipeline_actions", {"delete": asset_manager.icon_delete}),
            action_size=20,
            # Events
            actives_change=(self.on_active_change, "[$event]"),
            visibility_change=(self.on_visibility_change, "[]", "$event"),
            action=(self.on_action, "[]", "$event"),
            **kwargs,
        )
        self._deleted_ids = set()
        self.server.enable_module(module)

    def on_active_change(self, active_ids, **kwargs):
        proxy = None
        if len(active_ids):
            _id = active_ids[0]
            if _id in self._deleted_ids:
                return
            proxy = id_to_proxy(_id)

        simple.SetActiveSource(proxy)
        self.update_active()

        # Use life cycle handler
        self.server.controller.on_active_proxy_change()

    def on_visibility_change(self, id, visible, **kwargs):
        proxy = id_to_proxy(id)
        view_proxy = simple.GetActiveView()
        representation = simple.GetRepresentation(proxy=proxy, view=view_proxy)
        representation.Visibility = 1 if visible else 0

        # Use life cycle handler
        self.server.controller.on_data_change()

    def on_action(self, id, action):
        if action == "delete":
            self._deleted_ids.add(id)
            self.server.controller.on_delete(id)
            self.update()

    def update_active(self, **kwargs):
        actives = []
        active_proxy = simple.GetActiveSource()
        if active_proxy:
            actives.append(active_proxy.GetGlobalIDAsString())
        self.server.state.pipeline_actives = actives

    def update_sources(self, **kwargs):
        sources = []
        proxies = PXM.GetProxiesInGroup("sources")
        view_proxy = simple.GetActiveView()
        leaves = set([key[1] for key in proxies])
        node_map = {}
        for key in proxies:
            proxy = proxies[key]

            source = {"parent": "0"}
            source["name"] = key[0]
            source["id"] = key[1]

            representation = simple.GetRepresentation(proxy=proxy, view=view_proxy)
            source["rep"] = representation.GetGlobalIDAsString()
            source["visible"] = int(representation.Visibility)

            if hasattr(proxy, "Input") and proxy.Input:
                inputProp = proxy.Input
                if hasattr(inputProp, "GetNumberOfProxies"):
                    numProxies = inputProp.GetNumberOfProxies()
                    if numProxies > 1:
                        source["multiparent"] = numProxies
                        for inputIdx in range(numProxies):
                            proxyId = inputProp.GetProxy(inputIdx).GetGlobalIDAsString()
                            if inputIdx == 0:
                                source["parent"] = proxyId
                            else:
                                source[f"parent_{inputIdx}"] = proxyId
                    elif numProxies == 1:
                        source["parent"] = inputProp.GetProxy(0).GetGlobalIDAsString()
                else:
                    source["parent"] = inputProp.GetGlobalIDAsString()

            sources.append(source)
            node_map[source["id"]] = source
            leaves.discard(source["parent"])

        # Attach delete action to leaves only
        for leaf in leaves:
            node_map[leaf]["actions"] = ["delete"]

        self.server.state.pipeline_sources = sources

    def update(self, **kwargs):
        self.update_sources(**kwargs)
        self.update_active(**kwargs)

from paraview import simple


def initialize(server):
    state, ctrl = server.state, server.controller

    @state.change("active_controls")
    def update_active_panel(active_controls, **kwargs):
        state.main_drawer = active_controls is not None

    @ctrl.add("on_active_proxy_change")
    def update_active_proxies(**kwargs):
        if simple is None:
            state.active_proxy_source_id = 0
            state.active_proxy_representation_id = 0
            return

        active_view = simple.GetActiveView()
        state.active_proxy_view_id = active_view.GetGlobalIDAsString()

        active_source = simple.GetActiveSource()
        if active_source is None:
            state.active_proxy_source_id = 0
            state.active_proxy_representation_id = 0
        else:
            state.active_proxy_source_id = active_source.GetGlobalIDAsString()
            rep = simple.GetRepresentation(proxy=active_source, view=active_view)
            state.active_proxy_representation_id = rep.GetGlobalIDAsString()

    # Initialize state values
    update_active_proxies()

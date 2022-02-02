from trame import state


@state.change("active_controls")
def update_active_panel(active_controls, **kwargs):
    state.drawer_visibility = active_controls is not None

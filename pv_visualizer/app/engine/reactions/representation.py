from paraview import simple
from paraview.modules.vtkRemotingViews import vtkSMRepresentationProxy


def unwrap(p):
    if hasattr(p, "SMProxy"):
        return p.SMProxy
    return p


def initialize(server, mapper):
    state, ctrl = server.state, server.controller

    def update_representation_type(name):
        proxy = simple.GetRepresentation()
        vtkSMRepresentationProxy.SetRepresentationType(unwrap(proxy), name)
        ctrl.view_update()
        ctrl.pxm_refresh_active_proxies()

    def refresh_scalarbar_visibility():
        visible = 0
        view = simple.GetActiveView()
        source = simple.GetActiveSource()
        if view and source:
            proxy = simple.GetRepresentation(source, view)
            visible = proxy.IsScalarBarVisible(view)
        state.active_representation_scalarbar_visibility = visible

    def toggle_scalarbar_visibility():
        visible = not state.active_representation_scalarbar_visibility
        state.active_representation_scalarbar_visibility = visible
        view = simple.GetActiveView()
        source = simple.GetActiveSource()
        if view and source:
            proxy = simple.GetRepresentation(source, view)
            proxy.SetScalarBarVisibility(view, visible)

        ctrl.view_update()

    def color_by(value=None):
        rep = simple.GetRepresentation()
        association = 0
        arrayname = rep.ColorArrayName.GetArrayName()
        component = None

        if value is None or value[0] is None:
            rep.SetScalarColoring(None, association)
            return

        if not isinstance(value, (tuple, list)):
            value = (value,)

        if len(value) == 1:
            arrayname = value[0]

        elif len(value) >= 2:
            arrayname = value[0]
            association = value[1]

        if len(value) == 3:
            # component name provided
            component = value[2]
            if component == "Magnitude":
                component = -1
            else:
                array = None
                if association == 0:
                    array = rep.Input.PointData.GetArray(arrayname)
                if association == 1:
                    array = rep.Input.CellData.GetArray(arrayname)
                if array:
                    # looking for corresponding component name
                    for i in range(0, array.GetNumberOfComponents()):
                        if component == array.GetComponentName(i):
                            component = i
                            break
                        # none have been found, try to use the name as an int
                        if i == array.GetNumberOfComponents() - 1:
                            try:
                                component = int(component)
                            except ValueError:
                                pass

        if component is None:
            rep.SetScalarColoring(arrayname, association)
        else:
            rep.SetScalarColoring(arrayname, association, component)
        rep.RescaleTransferFunctionToDataRange()
        ctrl.view_update()
        refresh_scalarbar_visibility()

    # -----------------------------------------------------------------------------
    TRIGGER_MAPPING = {
        "pv_reaction_representation_type": update_representation_type,
        "pv_reaction_representation_color_by": color_by,
        "pv_reaction_representation_scalarbar_update": refresh_scalarbar_visibility,
        "pv_reaction_representation_scalarbar_toggle": toggle_scalarbar_visibility,
    }
    mapper(ctrl, TRIGGER_MAPPING)
    # -----------------------------------------------------------------------------

    refresh_scalarbar_visibility()

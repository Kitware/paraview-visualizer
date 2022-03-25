from paraview import simple
from trame import controller as ctrl

from paraview.modules.vtkRemotingViews import vtkSMRepresentationProxy


def unwrap(p):
    if hasattr(p, "SMProxy"):
        return p.SMProxy
    return p


def updateRepresentationType(name):
    proxy = simple.GetRepresentation()
    vtkSMRepresentationProxy.SetRepresentationType(unwrap(proxy), name)
    ctrl.view_update()


# -----------------------------------------------------------------------------
TRIGGER_MAPPING = {
    "pv_reaction_representation_type": updateRepresentationType,
}
# -----------------------------------------------------------------------------

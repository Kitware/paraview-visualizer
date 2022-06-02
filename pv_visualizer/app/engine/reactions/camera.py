from paraview import simple


def initialize(server, mapper):
    ctrl = server.controller

    def resetCamera(closest=False):
        view = simple.GetRenderView()

        if hasattr(view, "ResetDisplay"):
            view.ResetDisplay()

        if hasattr(view, "ResetCamera"):
            view.ResetCamera(closest)

        ctrl.view_update()

    def resetPositiveX():
        resetDirection(1, 0, 0, 0, 0, 1)

    def resetPositiveY():
        resetDirection(0, 1, 0, 0, 0, 1)

    def resetPositiveZ():
        resetDirection(0, 0, 1, 0, 1, 0)

    def resetNegativeX():
        resetDirection(-1, 0, 0, 0, 0, 1)

    def resetNegativeY():
        resetDirection(0, -1, 0, 0, 0, 1)

    def resetNegativeZ():
        resetDirection(0, 0, -1, 0, 1, 0)

    def resetDirection(look_x, look_y, look_z, up_x, up_y, up_z):
        view = simple.GetRenderView()
        view.CameraPosition = (0, 0, 0)
        view.CameraFocalPoint = (look_x, look_y, look_z)
        view.CameraViewUp = (up_x, up_y, up_z)
        resetCamera()

    def zoomToData(closest=False):
        view = simple.GetRenderView()
        rep = simple.GetRepresentation()
        if view and rep:
            view.ZoomTo(rep, closest)
            ctrl.view_update()

    def rotateCamera(angle):
        view = simple.GetRenderView()
        view.GetActiveCamera().Roll(angle)
        ctrl.view_update()

    # -----------------------------------------------------------------------------
    TRIGGER_MAPPING = {
        "pv_reaction_camera_reset": resetCamera,
        "pv_reaction_camera_x": resetPositiveX,
        "pv_reaction_camera_y": resetPositiveY,
        "pv_reaction_camera_z": resetPositiveZ,
        "pv_reaction_camera_nx": resetNegativeX,
        "pv_reaction_camera_ny": resetNegativeY,
        "pv_reaction_camera_nz": resetNegativeZ,
        "pv_reaction_camera_direction": resetDirection,
        "pv_reaction_camera_zoom": zoomToData,
        "pv_reaction_camera_rotate": rotateCamera,
    }
    mapper(ctrl, TRIGGER_MAPPING)
    # -----------------------------------------------------------------------------

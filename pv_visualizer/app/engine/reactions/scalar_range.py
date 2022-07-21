import logging
from paraview import simple
from paraview.modules.vtkRemotingViews import vtkSMPVRepresentationProxy

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def unwrap(p):
    if hasattr(p, "SMProxy"):
        return p.SMProxy
    return p


def initialize(server, mapper):
    ctrl = server.controller

    def resetScalarRangeToData():
        logger.info("resetScalarRangeToData")
        proxy = simple.GetRepresentation()
        if proxy and vtkSMPVRepresentationProxy.GetUsingScalarColoring(unwrap(proxy)):
            vtkSMPVRepresentationProxy.RescaleTransferFunctionToDataRange(unwrap(proxy))
            ctrl.view_update()

    def resetScalarRangeToCustom(data_range, opacity_range=None):
        logger.info("resetScalarRangeToCustom")
        separateOpacity = False
        proxy = simple.GetRepresentation()
        if proxy:
            if proxy.GetProperty("UseSeparateOpacityArray"):
                separateOpacity = int(proxy.UseSeparateOpacityArray)
            lut = proxy.LookupTable
            if lut:
                lut.RescaleTransferFunction(data_range[0], data_range[1])
                if separateOpacity:
                    if opacity_range is None:
                        opacity_range = data_range
                    lut.ScalarOpacityFunction.RescaleTransferFunction(
                        opacity_range[0], opacity_range[1]
                    )
                ctrl.view_update()

    def resetScalarRangeToDataOverTime():
        logger.info("resetScalarRangeToDataOverTime")
        proxy = simple.GetRepresentation()
        if proxy and vtkSMPVRepresentationProxy.GetUsingScalarColoring(unwrap(proxy)):
            vtkSMPVRepresentationProxy.RescaleTransferFunctionToDataRangeOverTime(
                unwrap(proxy)
            )
            ctrl.view_update()

    def resetScalarRangeToVisible():
        logger.info("resetScalarRangeToVisible")
        view = simple.GetActiveView()
        rep = simple.GetRepresentation()
        if view and rep:
            vtkSMPVRepresentationProxy.RescaleTransferFunctionToVisibleRange(
                unwrap(rep), unwrap(view)
            )
            ctrl.view_update()

    # -----------------------------------------------------------------------------
    TRIGGER_MAPPING = {
        "pv_reaction_scalar_range_data": resetScalarRangeToData,
        "pv_reaction_scalar_range_custom": resetScalarRangeToCustom,
        "pv_reaction_scalar_range_time": resetScalarRangeToDataOverTime,
        "pv_reaction_scalar_range_visible": resetScalarRangeToVisible,
    }
    mapper(ctrl, TRIGGER_MAPPING)
    # -----------------------------------------------------------------------------

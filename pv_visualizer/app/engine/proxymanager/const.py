import os

# -----------------------------------------------------------------------------
# DEBUG Simput state exchange
# -----------------------------------------------------------------------------

LOG_DIR = "/Users/sebastien.jourdain/Documents/code/open-source/Web/apps/pv-visualizer/pv_visualizer/logs"
# os.environ["SIMPUT_LOG_DIR"] = LOG_DIR

# -----------------------------------------------------------------------------

# C++ to Simput type definition
PROPERTY_TYPES = {
    "vtkSMIntVectorProperty": "int32",
    "vtkSMDoubleVectorProperty": "float64",
    "vtkSMStringVectorProperty": "string",
    "vtkSMProxyProperty": "proxy",
    "vtkSMInputProperty": "proxy",
    # "vtkSMProperty": "command", # FIXME ?
}

# Attribute to extract for decorators if present
DECORATOR_ATTRS = [
    "type",
    "mode",
    "exclude",
    "index",
    "name",
    "property",
    "value",
    "values",
    "inverse",
    "number_of_components",
    "function",
    "components",
]

# XML panel_widget mapping to custom UI
PANEL_WIDGETS = {
    "color_selector": "sw-color-selector",
    "color_selector_with_palette": "sw-color-selector",
    "ColorEditor": "sw-color-editor",
    # ------ partial
    "proxy_editor": "sw-proxy-editor",  # pop-up to edit proxy on the side
    # ------ default fallback
    "display_representation_selector": "",  # need to call vtkSMRepresentationProxy::SetRepresentationType
    "InteractiveBox": "",  # clip > Box
    # ------ skip
    "data_assembly_editor": "skip",
    "DataAssemblyEditor": "skip",
    "FontEditor": "skip",
    "input_selector": "skip",
    "int_mask": "skip",
    "texture_selector": "skip",
    "transfer_function_editor": "skip",
}

# Simple domain mapping to widget UI (i.e.: range -> slider)
WIDGETS = {
    # toggle switch
    "vtkSMBooleanDomain": "sw-switch",
    # slider
    "vtkSMDoubleRangeDomain": "sw-slider",  # "sw-text-field", # slider don't work for floats
    "vtkSMIntRangeDomain": "sw-slider",
    # drop down
    "vtkSMEnumerationDomain": "sw-select",
    "vtkSMRepresentationTypeDomain": "sw-select",
    "vtkSMProxyListDomain": "sw-select",
    "vtkSMArrayListDomain": "sw-select",
    # text-field ???????????????????????
    # "vtkSMDataTypeDomain": "sw-text-field",
    # "vtkSMInputArrayDomain": "sw-text-field",
    # "vtkSMProxyGroupDomain": "sw-text-field",
    # "vtkSMDataAssemblyDomain": "sw-text-field",
    # "vtkSMRepresentedArrayListDomain": "sw-text-field",
    # "vtkSMBoundsDomain": "sw-text-field",
    # "vtkSMArrayRangeDomain": "sw-text-field",
    # "vtkSMNumberOfComponentsDomain": "sw-text-field",
    # "vtkSMRangedTransferFunctionDomain": "sw-text-field",
    # "vtkSMMaterialDomain": "sw-text-field",
    # "vtkSMArraySelectionDomain": "sw-text-field",
}


# -----------------------------------------------------------------------------
# ParaView Domain class to extract helper
# -----------------------------------------------------------------------------
from . import domain_helpers

DOMAIN_TYPE_DEFAULT = domain_helpers.domain_unknown

DOMAIN_TYPES = {
    "vtkSMBooleanDomain": domain_helpers.domain_bool,
    "vtkSMDoubleRangeDomain": domain_helpers.domain_range,
    "vtkSMIntRangeDomain": domain_helpers.domain_range,
    "vtkSMEnumerationDomain": domain_helpers.domain_list_entries,
    "vtkSMRepresentationTypeDomain": domain_helpers.domain_list_strings,
    "vtkSMProxyListDomain": domain_helpers.domain_list_proxies_simput_ids,
    "vtkSMArrayListDomain": domain_helpers.domain_list_arrays,
    "vtkSMRepresentedArrayListDomain": domain_helpers.domain_list_arrays,
    # ------------------------------------------------
    "vtkSMDataTypeDomain": DOMAIN_TYPE_DEFAULT,
    "vtkSMInputArrayDomain": DOMAIN_TYPE_DEFAULT,
    "vtkSMProxyGroupDomain": DOMAIN_TYPE_DEFAULT,
    "vtkSMDataAssemblyDomain": DOMAIN_TYPE_DEFAULT,
    "vtkSMBoundsDomain": DOMAIN_TYPE_DEFAULT,
    "vtkSMArrayRangeDomain": DOMAIN_TYPE_DEFAULT,
    "vtkSMNumberOfComponentsDomain": DOMAIN_TYPE_DEFAULT,
    "vtkSMRangedTransferFunctionDomain": DOMAIN_TYPE_DEFAULT,
    "vtkSMMaterialDomain": DOMAIN_TYPE_DEFAULT,
    "vtkSMArraySelectionDomain": DOMAIN_TYPE_DEFAULT,
}

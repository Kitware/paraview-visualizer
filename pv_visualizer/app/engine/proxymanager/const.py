from . import domain_helpers

# -----------------------------------------------------------------------------
# DEBUG Simput state exchange
# -----------------------------------------------------------------------------

LOG_DIR = "/Users/sebastien.jourdain/Documents/code/open-source/Web/apps/pv-visualizer/pv_visualizer/logs"
# os.environ["SIMPUT_LOG_DIR"] = LOG_DIR

# -----------------------------------------------------------------------------

AUTO_COMMIT_XML_GROUPS = [
    "representations",
    "views",
    "annotations",
    "settings",
]

SETTINGS_PROXIES = [
    ("General", "GeneralSettings", "mdi-application-cog-outline"),
    # ("Camera", "RenderViewInteractionSettings", "mdi-rotate-3d"),
    ("Render View", "RenderViewSettings", "mdi-cube-scan"),
    # ("Color Arrays", "RepresentedArrayListSettings", "mdi-database-eye-outline"),
    ("Color Palette", "ColorPalette", "mdi-palette"),
]

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
    "display_representation_selector": "sw-display-representation-selector",
    # ------ partial
    "proxy_editor": "sw-proxy-editor",  # pop-up to edit proxy on the side
    # ------ default fallback
    "InteractiveBox": "",  # clip > Box
    # ------ skip
    "data_assembly_editor": "skip",
    "DataAssemblyEditor": "skip",
    "FontEditor": "skip",
    "input_selector": "skip",
    "int_mask": "skip",
    "texture_selector": "skip",
    "transfer_function_editor": "skip",
    "FontEditor": "skip",
    "camera_manipulator": "skip",
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
    # custom widgets
    "vtkSMArrayRangeDomain": "sw-scalar-range",
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # text-field ???????????????????????
    # "vtkSMDataTypeDomain": "sw-text-field",
    # "vtkSMInputArrayDomain": "sw-text-field",
    # "vtkSMProxyGroupDomain": "sw-text-field",
    # "vtkSMDataAssemblyDomain": "sw-text-field",
    # "vtkSMRepresentedArrayListDomain": "sw-text-field",
    # "vtkSMBoundsDomain": "sw-text-field",
    # "vtkSMNumberOfComponentsDomain": "sw-text-field",
    # "vtkSMRangedTransferFunctionDomain": "sw-text-field",
    # "vtkSMMaterialDomain": "sw-text-field",
    # "vtkSMArraySelectionDomain": "sw-text-field",
}


# -----------------------------------------------------------------------------
# ParaView Domain class to extract helper
# -----------------------------------------------------------------------------

DOMAIN_TYPE_DEFAULT = domain_helpers.domain_unknown

DOMAIN_TYPES = {
    "vtkSMBooleanDomain": domain_helpers.domain_bool,
    "vtkSMDoubleRangeDomain": domain_helpers.domain_range,
    "vtkSMIntRangeDomain": domain_helpers.domain_range,
    "vtkSMEnumerationDomain": domain_helpers.domain_list_entries,
    "vtkSMRepresentationTypeDomain": domain_helpers.domain_list_strings,
    "vtkSMRendererDomain": domain_helpers.domain_list_strings,
    "vtkSMProxyListDomain": domain_helpers.domain_list_proxies_simput_ids,
    "vtkSMArrayListDomain": domain_helpers.domain_list_arrays,
    "vtkSMRepresentedArrayListDomain": domain_helpers.domain_list_arrays,
    "vtkSMArrayRangeDomain": domain_helpers.domain_range,
    "vtkSMStringListDomain": domain_helpers.domain_list_strings,
    # ------------------------------------------------
    # "vtkSMDataTypeDomain": DOMAIN_TYPE_DEFAULT,
    "vtkSMInputArrayDomain": DOMAIN_TYPE_DEFAULT,
    "vtkSMProxyGroupDomain": DOMAIN_TYPE_DEFAULT,
    "vtkSMDataAssemblyDomain": DOMAIN_TYPE_DEFAULT,
    "vtkSMBoundsDomain": DOMAIN_TYPE_DEFAULT,
    "vtkSMNumberOfComponentsDomain": DOMAIN_TYPE_DEFAULT,
    "vtkSMRangedTransferFunctionDomain": DOMAIN_TYPE_DEFAULT,
    "vtkSMMaterialDomain": DOMAIN_TYPE_DEFAULT,
    "vtkSMArraySelectionDomain": DOMAIN_TYPE_DEFAULT,
}

DOMAINS_TO_SKIP = {
    "vtkSMDataTypeDomain": 1,
}

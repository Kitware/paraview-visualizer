import sys
from simput.core import ProxyDomain, PropertyDomain
from .pv_core import unwrap, id_to_proxy

# -----------------------------------------------------------------------------
# General util functions
# -----------------------------------------------------------------------------


SIMPUT_HELPER = None


def set_helper(helper):
    global SIMPUT_HELPER
    SIMPUT_HELPER = helper


def pv_id_to_simput(pv_id):
    return SIMPUT_HELPER.handle_proxy(id_to_proxy(pv_id))


# -----------------------------------------------------------------------------
# Domain extract helpers
# -----------------------------------------------------------------------------


def domain_range(domain):
    if domain.GetClassName() == "vtkSMDoubleRangeDomain":
        _max = sys.float_info.max
    else:
        _max = sys.maxsize

    level = 0
    value_range = [-_max, _max]

    if domain.GetMinimumExists(0):
        value_range[0] = domain.GetMinimum(0)
        level += 1

    if domain.GetMaximumExists(0):
        value_range[1] = domain.GetMaximum(0)
        level += 1

    return value_range


# -----------------------------------------------------------------------------
def domain_list_entries(domain):
    size = domain.GetNumberOfEntries()
    values = []
    for i in range(size):
        values.append(
            {
                "text": domain.GetEntryText(i),
                "value": domain.GetEntryValue(i),
            }
        )
    return values


# -----------------------------------------------------------------------------
def domain_list_strings(domain):
    size = domain.GetNumberOfStrings()
    values = []
    for i in range(size):
        values.append(
            {
                "text": domain.GetString(i),
                "value": domain.GetString(i),
            }
        )
    return values


# -----------------------------------------------------------------------------
def domain_list_proxies(domain):
    size = domain.GetNumberOfProxies()
    values = []
    for i in range(size):
        proxy = domain.GetProxy(i)
        values.append(
            {
                "text": proxy.GetXMLLabel(),
                "value": proxy.GetGlobalIDAsString(),
            }
        )
    return values


# -----------------------------------------------------------------------------
def domain_list_arrays(domain):
    field_type = f"{domain.GetAttributeType()}"
    return [
        {
            "text": entry.get("text"),
            "value": [
                "",
                "",
                "",
                field_type,
                entry.get("value"),
            ],
        }
        for entry in domain_list_strings(domain)
    ]


# -----------------------------------------------------------------------------
def domain_bool(domain):
    return {}


# -----------------------------------------------------------------------------
def domain_unknown(domain):
    # print("domain_unknown", domain)
    print("domain_unknown::class", domain.GetClassName())
    return {}


# -----------------------------------------------------------------------------
# Transform helper
# -----------------------------------------------------------------------------


def transform_noop(property_domain, extract):
    return extract


# -----------------------------------------------------------------------------
def transform_values_ids(property_domain, extract):
    return [
        {
            "text": entry.get("text"),
            "value": pv_id_to_simput(entry.get("value")),
        }
        for entry in extract
    ]


# -----------------------------------------------------------------------------
# ParaView Domain class to extract helper
# -----------------------------------------------------------------------------

DOMAIN_TYPES = {
    "vtkSMBooleanDomain": (domain_bool, transform_noop),
    "vtkSMDoubleRangeDomain": (domain_range, transform_noop),
    "vtkSMIntRangeDomain": (domain_range, transform_noop),
    "vtkSMEnumerationDomain": (domain_list_entries, transform_noop),
    "vtkSMRepresentationTypeDomain": (domain_list_strings, transform_noop),
    "vtkSMProxyListDomain": (domain_list_proxies, transform_values_ids),
    "vtkSMArrayListDomain": (domain_list_arrays, transform_noop),
    # ------------------------------------------------
    "vtkSMDataTypeDomain": (domain_unknown, transform_noop),
    "vtkSMInputArrayDomain": (domain_unknown, transform_noop),
    "vtkSMProxyGroupDomain": (domain_unknown, transform_noop),
    "vtkSMDataAssemblyDomain": (domain_unknown, transform_noop),
    "vtkSMRepresentedArrayListDomain": (domain_unknown, transform_noop),
    "vtkSMBoundsDomain": (domain_unknown, transform_noop),
    "vtkSMArrayRangeDomain": (domain_unknown, transform_noop),
    "vtkSMNumberOfComponentsDomain": (domain_unknown, transform_noop),
    "vtkSMRangedTransferFunctionDomain": (domain_unknown, transform_noop),
    "vtkSMMaterialDomain": (domain_unknown, transform_noop),
    "vtkSMArraySelectionDomain": (domain_unknown, transform_noop),
}


# -----------------------------------------------------------------------------
# Generic ParaView domain adapter
# -----------------------------------------------------------------------------


class ParaViewDomain(PropertyDomain):
    def __init__(self, _proxy, _property, _domain_manager=None, **kwargs):
        super().__init__(_proxy, _property, _domain_manager, **kwargs)
        self._pv_proxy = unwrap(_proxy.object)
        self._pv_property = unwrap(self._pv_proxy.GetProperty(_property))
        self._pv_class = kwargs.get("pv_class")
        self._pv_name = kwargs.get("pv_name")
        self._helpers = DOMAIN_TYPES.get(self._pv_class, domain_unknown)
        self._pv_domain = None

        if self._pv_property is None:
            print(f"!> No property {_property} on proxy {self._pv_proxy.GetXMLName()}")
            print("~" * 80)
            return

        # Find PV domain instance
        iter = self._pv_property.NewDomainIterator()
        iter.Begin()
        while not iter.IsAtEnd():
            domain = iter.GetDomain()
            domain_class = domain.GetClassName()
            domain_name = domain.GetXMLName()

            if self._pv_class == domain_class and self._pv_name == domain_name:
                self._pv_domain = domain

            iter.Next()

        self._message = kwargs.get(
            "message", f"{_property}>{self._pv_class}::{self._pv_name}"
        )

    def set_value(self):
        # Do PV domain have API to set value?
        return False

    def available(self):
        values = self._helpers[1](self, self._helpers[0](self._pv_domain))
        print(f"{self._pv_class}::{self._pv_name}", values)
        return values

    def valid(self, required_level=2):
        if self._level < required_level:
            return True
        # What method to call on PV domain?
        return True


# -----------------------------------------------------------------------------

ProxyDomain.register_property_domain("ParaViewDomain", ParaViewDomain)

# -----------------------------------------------------------------------------
# UI handling
# -----------------------------------------------------------------------------

WIDGETS = {
    # toggle switch
    "vtkSMBooleanDomain": "sw-switch",
    # slider
    "vtkSMDoubleRangeDomain": "sw-slider",
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


def get_domain_widget(domain):
    keep = True
    name = domain.GetXMLName()
    widget = WIDGETS.get(domain.GetClassName(), "sw-text-field")

    if widget == "sw-select":
        name = "List"

    if domain.GetClassName() in ["vtkSMDoubleRangeDomain", "vtkSMIntRangeDomain"]:
        keep = domain.GetMinimumExists(0) and domain.GetMaximumExists(0)

    return keep, name, widget

import sys
from . import paraview
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# -----------------------------------------------------------------------------
# General util functions
# -----------------------------------------------------------------------------

PV_PXM = None


def ensure_pxm():
    global PV_PXM
    if PV_PXM is None:
        from .core import ParaviewProxyManager

        PV_PXM = ParaviewProxyManager()


def id_pv_to_simput(pv_id):
    if PV_PXM is None:
        ensure_pxm()
    return PV_PXM.handle_proxy(paraview.id_to_proxy(pv_id))


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
def domain_list_proxies_simput_ids(domain):
    return [
        {
            "text": entry.get("text"),
            "value": id_pv_to_simput(entry.get("value")),
        }
        for entry in domain_list_proxies(domain)
    ]


# -----------------------------------------------------------------------------
def domain_list_arrays(domain):
    proxy = domain.GetProperty().GetParent()
    data_info = None
    if proxy.IsA("vtkSMRepresentationProxy"):
        data_info = proxy.GetRepresentedDataInformation()
    result_list = []

    for idx, entry in enumerate(domain_list_strings(domain)):
        label = entry.get("text")
        name = entry.get("value")
        association = domain.GetFieldAssociation(idx)
        entry = {
            "text": label,
            "value": [
                "",
                "",
                "",
                f"{association}",
                name,
            ],
        }
        if data_info:
            components_list = []
            array_info = data_info.GetArrayInformation(label, association)
            if array_info:
                nb_components = array_info.GetNumberOfComponents()
                if nb_components > 1:
                    components_list.append(array_info.GetComponentName(-1))
                    for i in range(nb_components):
                        components_list.append(array_info.GetComponentName(i))
                    entry["components"] = components_list

        result_list.append(entry)

    return result_list


# -----------------------------------------------------------------------------
def domain_bool(domain):
    return {}


# -----------------------------------------------------------------------------
UNKNOWN_DOMAINS = set()


def domain_unknown(domain):
    class_name = domain.GetClassName()

    if class_name not in UNKNOWN_DOMAINS:
        UNKNOWN_DOMAINS.add(class_name)
        logger.info("domain_unknown::class(%s)", class_name)

    return {}

import sys
import yaml
import xml.etree.ElementTree as ET

try:
    from paraview import servermanager
except:
    servermanager = None

PROPERTY_TYPES = {
    "vtkSMIntVectorProperty": "int32",
    "vtkSMDoubleVectorProperty": "float64",
    "vtkSMStringVectorProperty": "string",
    "vtkSMProxyProperty": "proxy",
    "vtkSMInputProperty": "proxy",
}

DOMAIN_TYPES = {
    "vtkSMBooleanDomain": "Boolean",
    "vtkSMDoubleRangeDomain": "Range",
    "vtkSMIntRangeDomain": "Range",
    "vtkSMEnumerationDomain": "LabelList",
    "vtkSMRepresentationTypeDomain": "RepresentationList",
    "vtkSMProxyListDomain": "ProxyListDomain",
    # ----
    # ----
    "vtkSMDataTypeDomain": "xxxxxxxxxxxxxxxx",
    "vtkSMInputArrayDomain": "xxxxxxxxxxxxxx",
    "vtkSMProxyGroupDomain": "xxxxxxxxxxxxxx",
    "vtkSMDataAssemblyDomain": "xxxxxxxxxxxx",
    "vtkSMRepresentedArrayListDomain": "xxxx",
    "vtkSMBoundsDomain": "xxxxxxxxxxxxxxxxxx",
    "vtkSMArrayListDomain": "xxxxxxxxxxxxxxx",
    "vtkSMArrayRangeDomain": "xxxxxxxxxxxxxx",
    "vtkSMNumberOfComponentsDomain": "xxxxxx",
    "vtkSMRangedTransferFunctionDomain": "xx",
    "vtkSMMaterialDomain": "xxxxxxxxxxxxxxxx",
    "vtkSMArraySelectionDomain": "xxxxxxxxxx",
    # ----
    "1": "ProxyBuilder",
    "2": "FieldSelector",
    "3": "BoundsCenter",
}

DOMAIN_DEBUG = {}

PROXY_TO_SIMPUT_ID = None

def set_helper(helper):
    global PROXY_TO_SIMPUT_ID
    PROXY_TO_SIMPUT_ID = helper.handle_proxy


def domain_bool(domain):
    return {}


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

    if level == 0:
        return {"skip": True}

    return {"level": level, "value_range": value_range}


def domain_label_list(domain):
    size = domain.GetNumberOfEntries()
    values = []
    for i in range(size):
        values.append(
            {
                "text": domain.GetEntryText(i),
                "value": domain.GetEntryValue(i),
            }
        )

    return {"name": "List", "values": values}

def domain_rep_list(domain):
    size = domain.GetNumberOfStrings()
    values = []
    for i in range(size):
        values.append(
            {
                "text": domain.GetString(i),
                "value": domain.GetString(i),
            }
        )
    return {"name": "List", "type": "LabelList", "values": values}

def domain_proxy_list(domain):
    size = domain.GetNumberOfProxies()
    values = []
    for i in range(size):
        proxy = domain.GetProxy(i)
        values.append(
            {
                "text": proxy.GetXMLLabel(),
                "value": PROXY_TO_SIMPUT_ID(proxy),
            }
        )
    return {"name": "List", "type": "LabelList", "values": values}


DOMAIN_HANDLERS = {
    "Boolean": domain_bool,
    "Range": domain_range,
    "LabelList": domain_label_list,
    "RepresentationList": domain_rep_list,
    "ProxyListDomain": domain_proxy_list,
    # "ProxyBuilder": [""],
    # "FieldSelector": ["property", "location", "size", "isA"],
}


def proxy_type(proxy):
    group, name = proxy.GetXMLGroup(), proxy.GetXMLName()
    return f"{group}__{name}"


def property_domains_yaml(property):
    domains = []

    iter = property.NewDomainIterator()
    iter.Begin()
    while not iter.IsAtEnd():
        domain = iter.GetDomain()
        domain_class = domain.GetClassName()
        domain_name = domain.GetXMLName()
        domain_type = DOMAIN_TYPES.get(domain_class)

        if domain_type is None:
            print(f"Don't know how to handle domain: {domain_class}")
        elif domain_class in DOMAIN_DEBUG:
            print("~" * 40)  # <<< DEBUG
            print(domain_class)  # <<< DEBUG
            print("~" * 40)  # <<< DEBUG
            for method_name in dir(domain):  # <<< DEBUG
                if method_name[0] != "_":  # <<< DEBUG
                    print(f" > {method_name}")  # <<< DEBUG
        elif DOMAIN_HANDLERS.get(domain_type) is not None:
            domain_entry = {
                "name": domain_name,
                "type": domain_type,
                **DOMAIN_HANDLERS[domain_type](domain),
            }
            if domain_entry.get("skip") is None:
                domains.append(domain_entry)

        # move to next domain
        iter.Next()

    return domains


def property_yaml(property):
    property_definition = {}
    property_name = property.GetXMLName()

    if (
        property.GetPanelVisibility() == "never"
        or property.GetInformationOnly()
        or property.GetIsInternal()
    ):
        return {}

    if property.GetXMLLabel():
        property_definition["_label"] = property.GetXMLLabel()

    if (
        property.GetDocumentation() is not None
        and property.GetDocumentation().GetDescription()
    ):
        _help = property.GetDocumentation().GetDescription().replace("\n", " ").strip()
        while "  " in _help:
            _help = _help.replace("  ", " ")
        property_definition["_help"] = _help

    property_definition["type"] = PROPERTY_TYPES[property.GetClassName()]

    # Might not be correct
    size = (
        property.GetNumberOfElements()
        if hasattr(property, "GetNumberOfElements")
        else 1
    )
    if size > 1:
        property_definition["size"] = size

    # Domains
    property_definition["domains"] = property_domains_yaml(property)

    return {property_name: property_definition}


# -----------------------------------------------------------------------------
# External API
# -----------------------------------------------------------------------------


def proxy_yaml(proxy):
    type_proxy = proxy_type(proxy)

    proxy_definition = {}
    prop_iter = proxy.NewPropertyIterator()
    prop_iter.Begin()
    while not prop_iter.IsAtEnd():
        property = prop_iter.GetProperty()
        proxy_definition.update(property_yaml(property))
        prop_iter.Next()

    # print("#"*80)
    # print(yaml.dump({type_proxy: proxy_definition}))
    # print("#"*80)

    return yaml.dump({type_proxy: proxy_definition})


def property_xml(property):
    print()
    if property.IsA("vtkSMProxyProperty"):
        container = ET.Element("col")
        container.append(ET.Element("input", name=property.GetXMLName()))
        container.append(ET.Element("proxy", name=property.GetXMLName()))
        return container
    return ET.Element("input", name=property.GetXMLName())


def proxy_ui(proxy):
    if hasattr(proxy, "SMProxy"):
        proxy = proxy.SMProxy

    # 1) fill groups
    prop_to_group = {}
    xml_groups = {}
    g_size = proxy.GetNumberOfPropertyGroups()
    for g_idx in range(g_size):
        group = proxy.GetPropertyGroup(g_idx)
        p_size = group.GetNumberOfProperties()

        xml_group = ET.Element("col")
        xml_group.append(
            ET.Element("text", attrib={"class": "text-h6"}, content=group.GetXMLLabel())
        )
        xml_group.append(ET.Element("divider", attrib={"class": "mb-2"}))
        xml_groups[group] = xml_group

        for p_idx in range(p_size):
            property = group.GetProperty(p_idx)
            prop_to_group[property] = group
            xml_group.append(property_xml(property))

    # 2) ordered list of xml elements
    group_used = set()
    ordered_properties = []
    prop_iter = servermanager.vtkSMOrderedPropertyIterator()
    prop_iter.SetProxy(proxy)
    prop_iter.Begin()
    while not prop_iter.IsAtEnd():
        property = prop_iter.GetProperty()
        group = prop_to_group.get(property)

        if group is None:
            ordered_properties.append(property_xml(property))
        elif group not in group_used:
            group_used.add(group)
            ordered_properties.append(xml_groups[group])

        prop_iter.Next()

    # 3) fill layout > ui > *ordered_properties
    layouts = ET.Element("layouts")
    ui = ET.SubElement(layouts, "ui", id=proxy_type(proxy))
    for xml_elem in ordered_properties:
        ui.append(xml_elem)

    ET.indent(layouts)
    return ET.tostring(layouts, encoding="UTF-8").decode("utf-8")

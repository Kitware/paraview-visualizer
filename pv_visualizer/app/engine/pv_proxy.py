import yaml
import xml.etree.ElementTree as ET

from .pv_core import unwrap
from .domains import get_domain_widget, set_helper

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

        keep, name, widget = get_domain_widget(domain)
        domain_entry = {
            "name": name,
            "type": "ParaViewDomain",
            "pv_class": domain_class,
            "pv_name": domain_name,
            "widget": widget,
        }
        if keep:
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

    return yaml.dump({type_proxy: proxy_definition})


def property_xml(property):
    if property.IsA("vtkSMProxyProperty"):
        container = ET.Element("col")
        container.append(ET.Element("input", name=property.GetXMLName()))
        container.append(ET.Element("proxy", name=property.GetXMLName()))
        return container
    return ET.Element("input", name=property.GetXMLName())


def should_skip(property):
    if property.GetXMLName() in ["Input"]:
        # Reserved prop name without UI
        return True

    if property.GetIsInternal():
        # print("skip internal")
        return True

    visibility = property.GetPanelVisibility()
    if visibility in [None, "never"]:
        # print("skip visibility", visibility)
        return True

    return False


def proxy_ui(proxy):
    proxy = unwrap(proxy)

    # 1) fill groups
    prop_to_group = {}
    xml_groups = {}
    g_size = proxy.GetNumberOfPropertyGroups()
    for g_idx in range(g_size):
        group = proxy.GetPropertyGroup(g_idx)
        p_size = group.GetNumberOfProperties()

        # skip groups
        if group.GetPanelVisibility() in [None, "never"]:
            continue

        xml_group = ET.Element("col")
        xml_group.append(
            ET.Element("text", attrib={"class": "text-h6"}, content=group.GetXMLLabel())
        )
        xml_group.append(ET.Element("divider", attrib={"class": "mb-2"}))
        xml_groups[group] = xml_group

        for p_idx in range(p_size):
            property = group.GetProperty(p_idx)
            prop_to_group[property] = group
            if not should_skip(property):
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

        if should_skip(property):
            prop_iter.Next()
            continue

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

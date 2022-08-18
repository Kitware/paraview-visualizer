import logging
import yaml
import json
import base64
import xml.etree.ElementTree as ET

from . import paraview, domains
from .const import PROPERTY_TYPES, DECORATOR_ATTRS, AUTO_COMMIT_XML_GROUPS

from paraview import servermanager

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# -----------------------------------------------------------------------------
# Spec key
# -----------------------------------------------------------------------------


def proxy_type(proxy):
    group, name = proxy.GetXMLGroup(), proxy.GetXMLName()
    return f"{group}__{name}"


# -----------------------------------------------------------------------------
# Model generators
# -----------------------------------------------------------------------------


def xml_to_json(xml_elem, attr_list=DECORATOR_ATTRS):
    if xml_elem is None:
        return {}

    entry = {
        "elem_name": xml_elem.GetName(),
    }

    for attr_name in attr_list:
        attr_value = xml_elem.GetAttribute(attr_name)
        if attr_value is not None:
            entry[attr_name] = attr_value

    size = xml_elem.GetNumberOfNestedElements()
    if size:
        children = []
        entry["children"] = children
        for i in range(size):
            children.append(xml_to_json(xml_elem.GetNestedElement(i)))

    return entry


def property_widget_decorator_yaml(property):
    hints = property.GetHints()
    if hints is None:
        return []

    result = []
    size = hints.GetNumberOfNestedElements()
    for i in range(size):
        xml_elem = hints.GetNestedElement(i)
        if xml_elem.GetName() == "PropertyWidgetDecorator":
            result.append(
                {
                    "name": "decorator",
                    "type": "ParaViewDecoratorDomain",
                    "properties": xml_to_json(xml_elem),
                }
            )

    return result


def merge_decorators(*decorators):
    if len(decorators) > 1:
        return [
            {
                "name": "decorator",
                "type": "ParaViewDecoratorDomain",
                "properties": {
                    "type": "CompositeDecorator",
                    "children": [
                        {
                            "type": "and",
                            "children": [
                                decorator.get("properties") for decorator in decorators
                            ],
                        }
                    ],
                },
            }
        ]

    return decorators


def property_widget_decorator_advanced_yaml(property):
    if property.GetPanelVisibility() == "advanced":
        return [
            {
                "name": "decorator",
                "type": "ParaViewDecoratorDomain",
                "properties": {
                    "type": "AdvancedDecorator",
                    "name": property.GetXMLName(),
                },
            }
        ]
    return []


# -----------------------------------------------------------------------------


def property_domains_yaml(property):
    result = []

    iter = property.NewDomainIterator()
    iter.Begin()
    while not iter.IsAtEnd():
        domain = iter.GetDomain()
        domain_class = domain.GetClassName()
        domain_name = domain.GetXMLName()

        keep, name, widget, ui_attributes = domains.get_domain_widget(domain)
        domain_entry = {
            "name": name,
            "type": "ParaViewDomain",
            "pv_class": domain_class,
            "pv_name": domain_name,
            "widget": widget,
            "ui_attributes": ui_attributes,
        }
        if keep:
            result.append(domain_entry)

        # move to next domain
        iter.Next()

    return result


# -----------------------------------------------------------------------------


def property_yaml(property):
    property_definition = {}

    if (
        property.GetInformationOnly()
        or property.GetIsInternal()
        or property.GetClassName() not in PROPERTY_TYPES
    ):
        return False

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
    size = 1
    if hasattr(property, "GetNumberOfElements"):
        size = property.GetNumberOfElements()
    if hasattr(property, "GetNumberOfProxies"):
        size = property.GetNumberOfProxies()

    if property.GetRepeatable():
        size = -1

    if size > 1:
        property_definition["size"] = size

    if size < 1:
        property_definition["size"] = -1

    # Skip proxy property with n proxies (??? FIXME ???)
    # currently simput don't properly manage list of proxy as property...
    # i.e. views.RenderView.Representations
    if property_definition["type"] == "proxy" and size != 1:
        logger.info(
            "Skip multi-proxy property Proxy(%s)::Property(%s)",
            property.GetParent().GetXMLName(),
            property.GetXMLName(),
        )
        return False

    # Domains
    property_definition["domains"] = [
        *property_domains_yaml(property),
        *merge_decorators(
            *property_widget_decorator_yaml(property),
            *property_widget_decorator_advanced_yaml(property),
        ),
    ]

    if len(property_definition):
        return property_definition

    return False


# -----------------------------------------------------------------------------
# UI generators
# -----------------------------------------------------------------------------


def json_base64(obj):
    return base64.b64encode(json.dumps(obj).encode("utf-8")).decode("ascii")


def property_xml(property):
    widget = domains.PANEL_WIDGETS.get(property.GetPanelWidget())
    if widget and widget != "skip":
        return ET.Element(
            widget,
            name=property.GetXMLName(),
            hints=json_base64(xml_to_json(property.GetHints())),
        )

    if property.IsA("vtkSMProxyProperty"):
        container = ET.Element("col", attrib={"class": "pa-0"})
        container.append(ET.Element("input", name=property.GetXMLName()))
        container.append(ET.Element("proxy", name=property.GetXMLName()))
        return container

    attrib = {}
    if domains.get_property_size(property) == 6:
        attrib["layout"] = "l2"

    return ET.Element("input", name=property.GetXMLName(), attrib=attrib)


# -----------------------------------------------------------------------------


def should_skip(property):
    # Skip vtkSMProperty
    # if property.GetClassName() not in PROPERTY_TYPES:
    #     return True

    if property.GetIsInternal():
        # logger.info("skip internal")
        return True

    visibility = property.GetPanelVisibility()
    if visibility in ["never"]:
        # logger.info("skip visibility", visibility)
        return True

    if property.IsA("vtkSMProxyProperty"):
        selection_input = (
            property.GetHints()
            and property.GetHints().FindNestedElementByName("SelectionInput")
        )
        domain = None
        domain_iter = property.NewDomainIterator()
        domain_iter.Begin()
        while not domain_iter.IsAtEnd():
            domain = domain_iter.GetDomain()
            domain_iter.Next()

        if selection_input or (domain and domain.IsA("vtkSMProxyListDomain")):
            return False

        return True

    return False


# -----------------------------------------------------------------------------
# External API
# -----------------------------------------------------------------------------


def proxy_model(proxy):
    type_proxy = proxy_type(proxy)

    # Make representations and views proxy auto apply
    _tags = []
    proxy_definition = {"_tags": _tags}
    if proxy.GetXMLGroup() in AUTO_COMMIT_XML_GROUPS:
        _tags.append("auto_commit")

    # Track all the properties
    prop_iter = proxy.NewPropertyIterator()
    prop_iter.Begin()
    while not prop_iter.IsAtEnd():
        property_name = prop_iter.GetKey()
        property = prop_iter.GetProperty()
        property_definition = property_yaml(property)
        prop_iter.Next()

        # Skip empty properties
        if property_definition:
            proxy_definition[property_name] = property_definition

    # Look for group with widget decorator to fake prop with domain
    g_size = proxy.GetNumberOfPropertyGroups()
    group_decorator_count = 0
    for g_idx in range(g_size):
        group = proxy.GetPropertyGroup(g_idx)
        hints = group.GetHints()
        if hints is None:
            continue

        result = []
        size = hints.GetNumberOfNestedElements()
        for i in range(size):
            xml_elem = hints.GetNestedElement(i)
            if xml_elem.GetName() == "PropertyWidgetDecorator":
                result.append(
                    {
                        "name": "decorator",
                        "type": "ParaViewDecoratorDomain",
                        "properties": xml_to_json(xml_elem),
                    }
                )

        result = merge_decorators(*result)
        if len(result) == 0:
            continue

        # we have decorators to register as domain
        prop_key = f"internal__group__{g_idx}"
        proxy_definition[prop_key] = {"domains": list(result)}
        group_decorator_count += 1

    return yaml.dump({type_proxy: proxy_definition})


# -----------------------------------------------------------------------------


def proxy_ui(proxy):
    proxy = paraview.unwrap(proxy)

    # 1) fill groups
    prop_to_group = {}
    xml_groups = {}
    g_size = proxy.GetNumberOfPropertyGroups()
    for g_idx in range(g_size):
        group = proxy.GetPropertyGroup(g_idx)
        group_key = group.GetXMLLabel()
        p_size = group.GetNumberOfProperties()

        # skip groups
        if group.GetPanelVisibility() in [None, "never"]:
            group_key = "skip"

        # Skip custom widget until they get implemented
        if domains.PANEL_WIDGETS.get(group.GetPanelWidget()) == "skip":
            group_key = "skip"
            # logger.info(f"> Skip {group.GetPanelWidget()}")

        # Create group
        xml_group = xml_groups.get(group_key)
        if xml_group is None:
            xml_group = ET.Element(
                "sw-group",
                attrib={
                    "title": group.GetXMLLabel(),
                    "name": f"internal__group__{g_idx}",
                },
            )

            # Lookup custom group-widgets
            group_elem = domains.PANEL_WIDGETS.get(group.GetPanelWidget())
            if group_elem:
                el = ET.Element(group_elem, attrib={"label": group.GetXMLLabel()})
                xml_group.append(el)
                xml_group = el

            xml_groups[group_key] = xml_group

        for p_idx in range(p_size):
            property = group.GetProperty(p_idx)
            prop_to_group[property] = group_key
            if not should_skip(property):
                xml_group.append(property_xml(property))

    # 2) ordered list of xml elements
    group_used = set("skip")
    ordered_properties = []
    prop_iter = servermanager.vtkSMOrderedPropertyIterator()
    prop_iter.SetProxy(proxy)
    prop_iter.Begin()
    while not prop_iter.IsAtEnd():
        property = prop_iter.GetProperty()
        group_key = prop_to_group.get(property)

        if should_skip(property) or group_key == "skip":
            prop_iter.Next()
            continue

        if group_key is None:
            ordered_properties.append(property_xml(property))
        elif group_key not in group_used:
            group_used.add(group_key)
            ordered_properties.append(xml_groups[group_key])

        prop_iter.Next()

    # 3) fill layout > ui > *ordered_properties
    layouts = ET.Element("layouts")
    ui = ET.SubElement(layouts, "ui", id=proxy_type(proxy))

    # DEBUG !!!!
    # ui.append(ET.Element("sw-life-cycle", attrib={"uiType": proxy_type(proxy) }))

    for xml_elem in ordered_properties:
        ui.append(xml_elem)

    ET.indent(layouts)
    return ET.tostring(layouts, encoding="UTF-8").decode("utf-8")

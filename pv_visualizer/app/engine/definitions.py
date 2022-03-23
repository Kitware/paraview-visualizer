import yaml
import xml.etree.ElementTree as ET

from . import paraview, domains

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

# -----------------------------------------------------------------------------
# Spec key
# -----------------------------------------------------------------------------


def proxy_type(proxy):
    group, name = proxy.GetXMLGroup(), proxy.GetXMLName()
    return f"{group}__{name}"


# -----------------------------------------------------------------------------
# Model generators
# -----------------------------------------------------------------------------

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


def xml_to_json(xml_elem, attr_list=DECORATOR_ATTRS):
    entry = {}

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
    property_definition["domains"] = [
        *property_domains_yaml(property),
        *merge_decorators(
            *property_widget_decorator_yaml(property),
            *property_widget_decorator_advanced_yaml(property),
        ),
    ]

    return {property_name: property_definition}


# -----------------------------------------------------------------------------
# UI generators
# -----------------------------------------------------------------------------


def property_xml(property):
    if property.IsA("vtkSMProxyProperty"):
        container = ET.Element("col", attrib={"class": "pa-0"})
        container.append(ET.Element("input", name=property.GetXMLName()))
        container.append(ET.Element("proxy", name=property.GetXMLName()))
        return container
    return ET.Element("input", name=property.GetXMLName())


# -----------------------------------------------------------------------------


def should_skip(property):
    # if property.GetXMLName() in ["Input"]:
    #     # Reserved prop name without UI
    #     return True

    if property.GetIsInternal():
        # print("skip internal")
        return True

    visibility = property.GetPanelVisibility()
    if visibility in [None, "never"]:
        # print("skip visibility", visibility)
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

    proxy_definition = {}
    prop_iter = proxy.NewPropertyIterator()
    prop_iter.Begin()
    while not prop_iter.IsAtEnd():
        property = prop_iter.GetProperty()
        proxy_definition.update(property_yaml(property))
        prop_iter.Next()

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
        p_size = group.GetNumberOfProperties()

        # skip groups
        if group.GetPanelVisibility() in [None, "never"]:
            continue

        # Create group
        xml_group = ET.Element("col", attrib={"class": "px-0"})

        # Lookup custom group-widgets
        group_elem = domains.PANEL_WIDGETS.get(group.GetPanelWidget())
        if group_elem:
            xml_group = ET.Element(group_elem, attrib={"label": group.GetXMLLabel()})

        xml_group.append(
            ET.Element(
                "text", attrib={"class": "text-h6 px-2"}, content=group.GetXMLLabel()
            )
        )
        xml_group.append(ET.Element("divider", attrib={"class": "mb-2"}))
        xml_groups[group] = xml_group

        for p_idx in range(p_size):
            property = group.GetProperty(p_idx)
            prop_to_group[property] = group
            if not should_skip(property):
                xml_group.append(property_xml(property))
        xml_group.append(ET.Element("divider", attrib={"class": "mt-2"}))

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

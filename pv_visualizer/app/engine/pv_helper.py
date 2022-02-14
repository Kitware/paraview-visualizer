import yaml
from paraview import servermanager

DOMAIN_RANGE_ATTRIBUTES = [
    {
        "name": "min",
        "attribute": "min",
        "convert": float,
    },
    {
        "name": "max",
        "attribute": "max",
        "convert": float,
    },
]

PROPERTY_ATTRIBUTES = [
    {
        "name": "__name",
        "attribute": "name",
    },
    {
        "name": "_label",
        "attribute": "name",
    },
    {
        "name": "size",
        "attribute": "number_of_elements",
        "default": 1,
        "convert": int,
    },
    {
        "name": "internal",
        "attribute": "is_internal",
        "default": 0,
        "convert": int,
        "skip": 1,
    },
    {
        "name": "information",
        "attribute": "information_only",
        "default": 0,
        "convert": int,
        "skip": 1,
    },
    {
        "name": "_panel",
        "attribute": "panel_visibility",
        "default": "default",
        "skip": "never",
    },
    {
        "name": "initial",
        "attribute": "default_values",
    },
]

ELEM_NAME_TO_TYPES = {
    "DoubleVectorProperty": "float64",
    "IntVectorProperty": "int32",
    "StringVectorProperty": "string",
    "BooleanVectorProperty": "bool",
}

ELEM_NAME_TO_CONVERT = {
    "DoubleVectorProperty": float,
    "IntVectorProperty": int,
    "StringVectorProperty": str,
    "BooleanVectorProperty": bool,
}


def convert(type_name, value, size):
    type = ELEM_NAME_TO_CONVERT[type_name]
    if size > 1:
        tokens = value.split(" ")
        if len(tokens) != size:
            print("Invalid size({size}) for value '{value}'")
        return list(map(type, tokens))
    return type(value)


def xml_attr_helper(xml_elem, dict_to_fill, attr_map):
    for attr_entry in attr_map:
        # Fill with default
        if "default" in attr_entry and "skip" not in attr_entry:
            dict_to_fill[attr_entry.get("name")] = attr_entry.get("default")

        # Extract standard attributes
        attr = xml_elem.GetAttribute(attr_entry.get("attribute"))
        if attr is not None:
            value = attr_entry.get("convert", str)(attr)
            if "skip" in attr_entry and value == attr_entry.get("skip"):
                return False
            else:
                dict_to_fill[attr_entry.get("name")] = value

    return True


class ProxyManagerHelper:
    def __init__(self, disable_domains=False):
        self._debug = True
        self._cache_proxy_def = {}
        self._disable_domains = disable_domains

    def mapIdToProxy(self, poxy_id):
        try:
            poxy_id = int(poxy_id)
        except:
            return None
        if poxy_id <= 0:
            return None
        return servermanager._getPyProxy(
            servermanager.ActiveConnection.Session.GetRemoteObject(poxy_id)
        )

    def debug(self, msg):
        if self._debug == True:
            print(msg)

    # --------------------------------------------------------------------------
    # Convenience method to get proxy defs, cached if available
    # --------------------------------------------------------------------------
    def getProxyDefinition(self, group, name):
        cacheKey = "%s:%s" % (group, name)
        if cacheKey in self._cache_proxy_def:
            return self._cache_proxy_def[cacheKey]

        xmlElement = servermanager.ActiveConnection.Session.GetProxyDefinitionManager().GetCollapsedProxyDefinition(
            group, name, None
        )
        # print('\n\n\n (%s, %s): \n\n' % (group, name))
        # xmlElement.PrintXML()
        self._cache_proxy_def[cacheKey] = xmlElement
        return xmlElement

    def xml_extract_property_domain(self, xml_element):
        if self._disable_domains:
            return

        elem_name = xml_element.GetName()
        domain = None

        if "Range" in elem_name:
            domain = {"type": "Range"}
            xml_attr_helper(xml_element, domain, DOMAIN_RANGE_ATTRIBUTES)
        elif elem_name == "BooleanDomain":
            domain = {"type": "Boolean"}
        else:
            print(f">>> No handler for domain: {elem_name} <<<")

        return domain

    def xml_extract_property_inners(self, xml_element):
        """Process documentation tags + domains"""
        add_on = {}
        domains = []
        children_size = xml_element.GetNumberOfNestedElements()
        for i in range(children_size):
            xml_child = xml_element.GetNestedElement(i)
            elem_name = xml_child.GetName()

            if elem_name == "Documentation":
                add_on["_help"] = (
                    xml_child.GetCharacterData().replace("\n", " ").replace("  ", " ")
                )
                while "  " in add_on["_help"]:
                    add_on["_help"] = add_on["_help"].replace("  ", " ")
            elif elem_name.endswith("Domain"):
                domain = self.xml_extract_property_domain(xml_child)
                if domain is not None:
                    domains.append(domain)

        if len(domains):
            add_on["domains"] = domains

        return add_on

    def xml_extract_properties(self, xml_element):
        properties = []
        children_size = xml_element.GetNumberOfNestedElements()

        for i in range(children_size):
            xml_child = xml_element.GetNestedElement(i)
            elem_name = xml_child.GetName()

            if not elem_name.endswith("Property"):
                print(f"Skip handling {elem_name}")
                continue

            # Fill prop with attributes
            prop = {}
            if not xml_attr_helper(xml_child, prop, PROPERTY_ATTRIBUTES):
                continue

            # Assign property type
            if elem_name == "ProxyProperty" or elem_name == "InputProperty":
                prop["type"] = "proxy"
            elif elem_name.endswith("Property"):
                prop["type"] = ELEM_NAME_TO_TYPES[elem_name]
                if "initial" in prop:
                    prop["initial"] = convert(elem_name, prop["initial"], prop["size"])

            # Extract property internals (_help, domains, ...)
            prop.update(self.xml_extract_property_inners(xml_child))

            # Register property
            properties.append(prop)

        return properties

    def spec_name(self, proxy):
        group, name = proxy.GetXMLGroup(), proxy.GetXMLName()
        return f"{group}__{name}"

    def yaml(self, proxy):
        spec_name = self.spec_name(proxy)
        group, name = proxy.GetXMLGroup(), proxy.GetXMLName()
        xml_elem = self.getProxyDefinition(group, name)
        props = self.xml_extract_properties(xml_elem)
        yaml_txt = yaml.dump({spec_name: props})
        output = []
        for line in yaml_txt.split("\n"):
            if "- __name: " in line:
                output.append(line.replace("- __name: ", " ") + ":")
            else:
                output.append(line)

        return "\n".join(output)

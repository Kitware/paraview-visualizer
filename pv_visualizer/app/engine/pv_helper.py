import yaml
from paraview import simple, servermanager
from trame import state, controller as ctrl

PENDING = True

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
            print(f"Invalid size({size}) for value '{value}'")
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


class PVObjectFactory:
    def __init__(self):
        self._next = None

    def next(self, proxy):
        self._next = proxy

    def create(self, name, **kwargs):
        obj = self._next
        self._next = None

        return obj


from simput.core import Proxy


def proxy_push(simput_item):
    pv_proxy = simput_item.object
    change_count = 0

    for name in simput_item.edited_property_names:
        value = simput_item[name]
        if isinstance(value, Proxy):
            value = value.object if value else None
        elif value is None:
            continue

        property = pv_proxy.GetProperty(name)

        if isinstance(value, (list, tuple)):
            for i, v in enumerate(value):
                before = property.GetElement(i)
                property.SetElement(i, v)
                after = property.GetElement(i)
                if before != after:
                    change_count += 1
        else:
            before = property.GetElement(0)
            property.SetElement(0, value)
            after = property.GetElement(0)
            if before != after:
                change_count += 1

    if change_count:
        pv_proxy.UpdateVTKObjects()

    return change_count


class ProxyManagerHelper:
    def __init__(self, disable_domains=False):
        self._debug = True
        self._cache_proxy_def = {}
        self._disable_domains = disable_domains
        self._id_pv_to_simput = {}
        self._factory = PVObjectFactory()
        self._pxm = None
        self._ui_manager = None

    @property
    def factory(self):
        return self._factory

    def set_simput(self, pxm, ui):
        self._pxm = pxm
        self._ui_manager = ui

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

    # --------------------------------

    def handle_proxy(self, proxy):
        if proxy is None:
            return 0

        spec_name = self.spec_name(proxy)
        proxy_id = proxy.GetGlobalIDAsString()

        try:
            self._pxm.get_definition(spec_name)
        except KeyError:
            self._proxy_ensure_definition(proxy)

        if proxy_id not in self._id_pv_to_simput:
            self._proxy_ensure_binding(proxy)

        return self._id_pv_to_simput.get(proxy_id, 0)

    def _proxy_extract_sub(
        self, proxy, list_to_fill=None, property_types=["vtkSMProxyProperty"]
    ):
        if list_to_fill is None:
            list_to_fill = []

        nb_groups = proxy.GetNumberOfPropertyGroups()
        for g_idx in range(nb_groups):
            group = proxy.GetPropertyGroup(g_idx)
            nb_props = group.GetNumberOfProperties()
            for p_idx in range(nb_props):
                prop = group.GetProperty(p_idx)
                if prop.GetClassName() in property_types:
                    size = prop.GetNumberOfProxies()
                    for i in range(size):
                        s_proxy = prop.GetProxy(i)
                        if s_proxy is not None:
                            print("add sub proxy", s_proxy.GetClassName())
                            list_to_fill.append(s_proxy)

        return list_to_fill

    def _proxy_ensure_definition(self, proxy):
        try:
            spec_name = self.spec_name(proxy)
            self._pxm.get_definition(spec_name)
            return
        except KeyError:
            pass  # Let's get to work...

        # Look first on our dependencies
        sub_proxies = self._proxy_extract_sub(proxy)
        for sub_p in sub_proxies:
            self._proxy_ensure_definition(sub_p)

        # Add definition
        yaml_txt = self.yaml(proxy)
        self._pxm.load_model(yaml_content=yaml_txt)
        self._ui_manager.load_language(yaml_content=yaml_txt)

    def _proxy_ensure_binding(self, proxy):
        proxy_id = proxy.GetGlobalIDAsString()
        if proxy_id in self._id_pv_to_simput:
            return

        # Reserve spot to prevent any recursive loop
        self._id_pv_to_simput[proxy_id] = PENDING

        if hasattr(proxy, "SMProxy"):
            proxy = servermanager._getPyProxy(proxy)

        # Look first on our dependencies
        sub_proxies = self._proxy_extract_sub(proxy)
        for sub_p in sub_proxies:
            self._proxy_ensure_binding(sub_p)

        # Take care of ourself
        spec_name = self.spec_name(proxy)
        self._factory.next(proxy)
        simput_entry = self._pxm.create(spec_name, _push_fn=proxy_push)
        self._id_pv_to_simput[proxy_id] = simput_entry.id

        # Read property from proxy and update simput entry
        # TODO

        return simput_entry.id

    def delete_entry(self, pv_id):
        pv_view = simple.GetActiveView()

        s_id = self._id_pv_to_simput[pv_id]
        s_source = self._pxm.get(s_id)

        pv_source = s_source.object
        pv_rep = simple.GetRepresentation(proxy=pv_source, view=pv_view)

        s_id = self._id_pv_to_simput[pv_rep.GetGlobalIDAsString()]
        s_rep = self._pxm.get(s_id)

        self._pxm.delete(s_rep.id)
        self._pxm.delete(s_source.id)

        pv_rep.Visibility = 0 # Not sure why still around after delete
        simple.Delete(pv_rep)
        simple.Delete(pv_source)

        # Trigger some life cycle events
        ctrl.on_active_proxy_change()
        ctrl.on_data_change()

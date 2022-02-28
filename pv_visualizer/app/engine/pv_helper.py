from trame import controller as ctrl
from simput.core import Proxy

from . import pv_proxy

try:
    from paraview import simple, servermanager
except:
    simple = None
    servermanager = None

PENDING = True
HELPER = None


class PVObjectFactory:
    def __init__(self):
        self._next = None

    def next(self, proxy):
        self._next = proxy

    def create(self, name, **kwargs):
        obj = self._next
        self._next = None

        return obj


def proxy_pull(pv_proxy, si_item):
    _id = si_item.id
    for name in si_item.list_property_names():
        pv_property = pv_proxy.GetProperty(name)
        if hasattr(pv_property, "SMProperty"):
            pv_property = pv_property.SMProperty

        if pv_property is None:
            print(f"No property {name} for proxy {pv_proxy.GetXMLName()}")
            continue

        # Custom handling for proxy
        property_class = pv_property.GetClassName()
        if property_class in ["vtkSMProxyProperty", "vtkSMInputProperty"]:
            value = []
            size = pv_property.GetNumberOfProxies()
            for i in range(size):
                proxy = pv_property.GetProxy(i)
                value.append(HELPER.handle_proxy(proxy))

            if size > 1:
                si_item.set_property(name, value)
            elif len(value):
                si_item.set_property(name, value[0])
        else:
            size = pv_property.GetNumberOfElements()
            if size == 0:
                continue

            if size > 1:
                value = []
                for i in range(size):
                    value.append(pv_property.GetElement(i))
            else:
                value = pv_property.GetElement(0)

            # print(f"{property_class}({size})::{name} = {value} ({type(value)})")
            si_item.set_property(name, value)

    si_item.commit()


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
        elif property.GetClassName() in ["vtkSMInputProperty", "vtkSMProxyProperty"]:
            if hasattr(value, "SMProxy"):
                value = value.SMProxy
            before = property.GetProxy(0)
            property.SetProxy(0, value)
            after = property.GetProxy(0)
            if before != after:
                change_count += 1
        else:
            try:
                before = property.GetElement(0)
            except AttributeError as e:
                print("Error", property.GetClassName())
                raise(e)
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
        #
        global HELPER
        HELPER = self
        pv_proxy.set_helper(self)

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

    def handle_proxy(self, proxy):
        if proxy is None:
            return 0

        proxy_type = pv_proxy.proxy_type(proxy)
        proxy_id = proxy.GetGlobalIDAsString()

        if self._pxm.get_definition(proxy_type) is None:
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
        proxy_type = pv_proxy.proxy_type(proxy)
        if self._pxm.get_definition(proxy_type) is not None:
            return

        # Look first on our dependencies
        sub_proxies = self._proxy_extract_sub(proxy)
        for sub_p in sub_proxies:
            self._proxy_ensure_definition(sub_p)

        # print('#'*80)
        # print(pv_proxy.proxy_ui(proxy))
        # print('#'*80)

        # Add definition
        yaml_txt = pv_proxy.proxy_yaml(proxy)
        self._pxm.load_model(yaml_content=yaml_txt)
        self._ui_manager.load_language(yaml_content=yaml_txt)
        self._ui_manager.load_ui(xml_content=pv_proxy.proxy_ui(proxy))

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
        proxy_type = pv_proxy.proxy_type(proxy)
        self._factory.next(proxy)
        simput_entry = self._pxm.create(proxy_type, _push_fn=proxy_push)
        self._id_pv_to_simput[proxy_id] = simput_entry.id

        # Read property from proxy and update simput entry
        proxy_pull(proxy, simput_entry)

        return simput_entry.id

    def delete_entry(self, pv_id):
        """FIXME as it is not working properly"""
        pv_view = simple.GetActiveView()

        s_id = self._id_pv_to_simput[pv_id]
        s_source = self._pxm.get(s_id)

        pv_source = s_source.object
        pv_rep = simple.GetRepresentation(proxy=pv_source, view=pv_view)

        s_id = self._id_pv_to_simput[pv_rep.GetGlobalIDAsString()]
        s_rep = self._pxm.get(s_id)

        self._pxm.delete(s_rep.id)
        self._pxm.delete(s_source.id)

        pv_rep.Visibility = 0  # Not sure why still around after delete
        simple.Delete(pv_rep)
        simple.Delete(pv_source)

        # Trigger some life cycle events
        ctrl.on_active_proxy_change()
        ctrl.on_data_change()

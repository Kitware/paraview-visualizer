import os
import logging
from pathlib import Path

from trame.app.singleton import Singleton
from trame_simput import get_simput_manager
from trame_simput.core.mapping import ProxyObjectAdapter
from trame_simput.core.proxy import Proxy

from pv_visualizer.app.engine.proxymanager.const import SETTINGS_PROXIES

from . import paraview, domains, definitions, data_informations
from .decorators import AdvancedDecorator

from paraview import simple

PENDING = True

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# -----------------------------------------------------------------------------
# PV <=> Simput proxy state exchange
# -----------------------------------------------------------------------------


class ParaViewProxyObjectAdapter(ProxyObjectAdapter):
    @staticmethod
    def commit(simput_proxy):
        pv_proxy = simput_proxy.object
        change_count = 0

        for name in simput_proxy.edited_property_names:
            value = simput_proxy[name]
            if isinstance(value, Proxy):
                value = paraview.unwrap(value.object if value else None)
            elif value is None:
                continue

            property = pv_proxy.GetProperty(name)

            if isinstance(value, (list, tuple)):
                if len(value) != property.GetNumberOfElements():
                    property.SetNumberOfElements(len(value))
                for i, v in enumerate(value):
                    before = property.GetElement(i)
                    property.SetElement(i, v)
                    after = property.GetElement(i)
                    if before != after:
                        change_count += 1
            elif property.GetClassName() in [
                "vtkSMInputProperty",
                "vtkSMProxyProperty",
            ]:
                before = property.GetProxy(0)
                property.SetProxy(0, value)
                after = property.GetProxy(0)
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

    @staticmethod
    def reset(simput_proxy):
        pv_proxy = simput_proxy.object
        for name in simput_proxy.edited_property_names:
            pv_property = pv_proxy.GetProperty(name)
            if pv_property is not None:
                pv_property.ClearUncheckedElements()

    @staticmethod
    def fetch(simput_proxy):
        pv_proxy = simput_proxy.object
        for name in simput_proxy.list_property_names():
            pv_property = paraview.unwrap(pv_proxy.GetProperty(name))

            if pv_property is None:
                # logger.info(f"No property {name} for proxy {pv_proxy.GetXMLName()}")
                continue

            # Custom handling for proxy
            property_class = pv_property.GetClassName()
            if property_class in ["vtkSMProxyProperty", "vtkSMInputProperty"]:
                value = []
                size = pv_property.GetNumberOfProxies()
                for i in range(size):
                    proxy = pv_property.GetProxy(i)
                    value.append(PV_PXM.handle_proxy(proxy))

                if size > 1:
                    simput_proxy.set_property(name, value)
                elif len(value):
                    simput_proxy.set_property(name, value[0])
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

                # logger.info(f"{property_class}({size})::{name} = {value} ({type(value)})")
                simput_proxy.set_property(name, value)

        simput_proxy.commit()

    @staticmethod
    def update(simput_proxy, *property_names):
        pv_proxy = simput_proxy.object

        for name in property_names:
            value = simput_proxy[name]
            if isinstance(value, Proxy):
                value = paraview.unwrap(value.object if value else None)
            elif value is None:
                continue

            property = pv_proxy.GetProperty(name)

            if property.GetClassName() in [
                "vtkSMInputProperty",
                "vtkSMProxyProperty",
            ]:
                if isinstance(value, (list, tuple)):
                    for i, v in enumerate(value):
                        if isinstance(v, Proxy):
                            v = paraview.unwrap(v.object if v else None)
                        property.SetUncheckedProxy(i, v)
                else:
                    property.SetUncheckedProxy(0, value)
            elif isinstance(value, (list, tuple)):
                if len(value) != property.GetNumberOfUncheckedElements():
                    property.SetNumberOfUncheckedElements(len(value))
                for i, v in enumerate(value):
                    property.SetUncheckedElement(i, v)
            else:
                property.SetUncheckedElement(0, value)

    @staticmethod
    def before_delete(simput_proxy):
        pv_proxy = simput_proxy.object
        logger.info(
            "Deleting PV proxy",
            simput_proxy.id,
            pv_proxy.GetGlobalIDAsString(),
            pv_proxy.GetReferenceCount(),
        )
        simple.Delete(pv_proxy)
        logger.info("simple.Delete() => done", pv_proxy.GetReferenceCount())


# -----------------------------------------------------------------------------


class PVObjectFactory:
    def __init__(self):
        self._next = None

    def next(self, proxy):
        self._next = proxy

    def create(self, name, **kwargs):
        obj = self._next
        self._next = None

        return obj


@Singleton
class ParaviewProxyManager:
    def __init__(self):
        # Manage relationship between pv and simput
        self._factory = PVObjectFactory()
        self._cache_proxy_def = {}
        self._id_pv_to_simput = {}
        domains.register_domains()

        # Load Simput models and layouts
        self._simput = get_simput_manager(
            "pxm",
            object_factory=self._factory,
            object_adapter=ParaViewProxyObjectAdapter(),
        )

        self._pxm = self._simput.proxymanager
        self._pxm.on(self.on_pxm_event)

        # Debug
        self._write_definitions_base = str(
            Path(Path(__file__).parent / "definitions").resolve().absolute()
        )

    def set_server(self, server):
        self._server = server
        self._state = server.state
        self._ctrl = server.controller

        # Controller binding
        self._ctrl.on_data_change.add(self.on_active_change)
        self._ctrl.on_delete = self.on_proxy_delete
        self._ctrl.on_active_proxy_change.add(self.on_active_change)
        self._ctrl.pxm_refresh_active_proxies = self.refresh_active_proxies

        # No active simput proxy just yet
        self._state.source_id = 0
        self._state.representation_id = 0
        self._state.active_data_information = {}
        self._state.change("ui_advanced")(self.update_advanced)

        # Should init active proxies
        self.update_active_proxies()

    def update_advanced(self, ui_advanced, **kwargs):
        AdvancedDecorator.advance_mode = ui_advanced
        self.reload_domains()

    def update_active_proxies(self):
        setting_proxies = []
        for item in SETTINGS_PROXIES:
            setting_proxies.append(
                {
                    "name": item[0],
                    "id": self.handle_proxy(simple.GetSettingsProxy(item[1])),
                    "icon": item[2],
                }
            )
        self._state.setting_proxies = setting_proxies

        view = simple.GetActiveView()
        if view is None:
            view = simple.GetRenderView()
            simple.SetActiveView(view)
        self._state.view_id = self.handle_proxy(view)

    @property
    def factory(self):
        return self._factory

    @property
    def pxm(self):
        return self._pxm

    @property
    def ui_manager(self):
        return self._simput

    def on_pxm_event(self, topic, **kwrags):
        if topic == "commit":
            self._ctrl.on_data_change()  # Trigger render

    def reload_domains(self):
        self._server.js_call("simput", "reload", "domain")

    def reload_data(self):
        self._server.js_call("simput", "reload", "data")

    def on_active_change(self, **kwargs):
        source = simple.GetActiveSource()
        view = simple.GetActiveView()
        representation = None
        if source is not None:
            representation = simple.GetRepresentation(proxy=source, view=view)
            self._state.active_proxy_source_id = source.GetGlobalIDAsString()
            self._state.active_proxy_representation_id = (
                representation.GetGlobalIDAsString()
            )

        self._state.source_id = self.handle_proxy(source)
        self._state.representation_id = self.handle_proxy(representation)
        self._state.view_id = self.handle_proxy(view)
        self._ctrl.pv_reaction_representation_scalarbar_update()
        self._state.active_data_information = data_informations.get_data_information(
            source
        )

    def on_proxy_delete(self, pv_id):
        pv_view = simple.GetActiveView()
        pv_active = simple.GetActiveSource()

        # clear active proxy if deleted one
        if pv_active and pv_active.GetGlobalIDAsString() == pv_id:
            self._state.source_id = "0"
            self._state.representation_id = "0"
            simple.SetActiveSource(None)

        s_source_id = self._id_pv_to_simput[pv_id]
        s_source = self._pxm.get(s_source_id)

        pv_source = s_source.object
        pv_rep_ids = []
        for i in range(10):  # prob the first 10 ports
            pv_rep = pv_view.FindRepresentation(pv_source, i)
            if pv_rep:
                pv_rep_ids.append(pv_rep.GetGlobalIDAsString())

        for pv_rep_id in pv_rep_ids:
            s_id = self._id_pv_to_simput[pv_rep_id]
            self._pxm.delete(s_id)

        self._pxm.delete(s_source_id)

        # Trigger some life cycle events
        # ctrl.pipeline_update()
        self._ctrl.on_active_proxy_change()
        self._ctrl.on_data_change()

    def handle_proxy(self, proxy):
        if proxy is None:
            return 0

        proxy_type = definitions.proxy_type(proxy)
        proxy_id = proxy.GetGlobalIDAsString()

        if self.pxm.get_definition(proxy_type) is None:
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
                            # logger.info("add sub proxy", s_proxy.GetClassName())
                            list_to_fill.append(s_proxy)

        return list_to_fill

    def _write_definition(self, proxy_type, extension, content):
        file_name = (
            Path(self._write_definitions_base)
            / f"{'/'.join(proxy_type.split('__'))}.{extension}"
        )
        os.makedirs(file_name.parent, exist_ok=True)
        with open(file_name, "w") as file:
            file.write(content)

    def _proxy_ensure_definition(self, proxy):
        proxy_type = definitions.proxy_type(proxy)
        if self.pxm.get_definition(proxy_type) is not None:
            return

        # Look first on our dependencies
        sub_proxies = self._proxy_extract_sub(proxy)
        for sub_p in sub_proxies:
            self._proxy_ensure_definition(sub_p)

        # Add definition
        model_yaml = definitions.proxy_model(proxy)
        ui_xml = definitions.proxy_ui(proxy)
        self._pxm.load_model(yaml_content=model_yaml)
        self.ui_manager.load_language(yaml_content=model_yaml)
        self.ui_manager.load_ui(xml_content=ui_xml)

        # Write definitions
        if self._write_definitions_base:
            self._write_definition(proxy_type, "yaml", model_yaml)
            self._write_definition(proxy_type, "xml", ui_xml)

    def _proxy_ensure_binding(self, proxy):
        proxy = paraview.unwrap(proxy)
        proxy_id = proxy.GetGlobalIDAsString()
        if proxy_id in self._id_pv_to_simput:
            return

        # Reserve spot to prevent any recursive loop
        self._id_pv_to_simput[proxy_id] = PENDING

        # Look first on our dependencies
        sub_proxies = self._proxy_extract_sub(proxy)
        for sub_p in sub_proxies:
            self._proxy_ensure_binding(sub_p)

        # Take care of ourself
        proxy_type = definitions.proxy_type(proxy)
        self._factory.next(proxy)
        simput_entry = self._pxm.create(proxy_type)
        self._id_pv_to_simput[proxy_id] = simput_entry.id

        # Read property from proxy and update simput entry
        simput_entry.fetch()

        return simput_entry.id

    def refresh_active_proxies(self):
        for _id in [self._state.source_id, self._state.representation_id]:
            simput_rep = self._pxm.get(_id)
            if simput_rep:
                simput_rep.fetch()
            self._ctrl.simput_push(proxy=_id)


# -----------------------------------------------------------------------------

PV_PXM = ParaviewProxyManager()

import os

from trame import Singleton, state, controller as ctrl

from paraview import simple

from simput.core import ProxyManager, UIManager, ProxyDomainManager
from simput.ui.web import VuetifyResolver
from simput.domains import register_domains
from simput.values import register_values

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Simput registrations
register_domains()
register_values()

from .pv_helper import ProxyManagerHelper


@Singleton
class ParaviewProxyManager:
    def __init__(self):
        self._helper = ProxyManagerHelper(disable_domains=True)
        self._pv_to_simput_id = {}

        # Load Simput models and layouts
        self._pxm = ProxyManager()
        ui_resolver = VuetifyResolver()
        self._ui_manager = UIManager(self._pxm, ui_resolver)
        self._pdm = ProxyDomainManager()
        self._pxm.add_life_cycle_listener(self._pdm)

        self._pxm.load_model(yaml_file=os.path.join(BASE_DIR, "model/sample.yaml"))
        self._ui_manager.load_language(
            yaml_file=os.path.join(BASE_DIR, "model/sample.yaml")
        )
        # self._ui_manager.load_ui(xml_file=os.path.join(BASE_DIR, "model/soil_ui.xml"))

        source = self._pxm.create("Source")
        representation = self._pxm.create("Representation")

        state.source_id = source.id
        state.representation_id = representation.id

    @property
    def pxm(self):
        return self._pxm

    @property
    def pdm(self):
        return self._pdm

    @property
    def ui_manager(self):
        return self._ui_manager

    def on_active_change(self):
        proxy = simple.GetActiveSource()
        if proxy is None:
            state.source_id = 0
            return

        proxy_id = proxy.GetGlobalIDAsString()
        spec_name = self._helper.spec_name(proxy)

        try:
            self._pxm.get_definition(spec_name)
        except KeyError:
            yaml_txt = self._helper.yaml(proxy)
            self._pxm.load_model(yaml_content=yaml_txt)
            self._ui_manager.load_language(yaml_content=yaml_txt)

        if proxy_id not in self._pv_to_simput_id:
            source = self._pxm.create(spec_name)
            state.source_id = source.id
            self._pv_to_simput_id[proxy_id] = source.id
        else:
            state.source_id = self._pv_to_simput_id[proxy_id]


# -----------------------------------------------------------------------------
# Life cycle listener
# -----------------------------------------------------------------------------

ctrl.on_active_proxy_change.add(ParaviewProxyManager().on_active_change)

# -----------------------------------------------------------------------------

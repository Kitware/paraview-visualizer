import os

from trame import Singleton, state, controller as ctrl

from simput.core import ProxyManager, UIManager, ProxyDomainManager
from simput.ui.web import VuetifyResolver
from simput.domains import register_domains
from simput.values import register_values

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Simput registrations
register_domains()
register_values()

from .pv_helper import ProxyManagerHelper


try:
    from paraview import simple
except:
    simple = None


@Singleton
class ParaviewProxyManager:
    def __init__(self):
        self._helper = ProxyManagerHelper(disable_domains=True)

        # Load Simput models and layouts
        self._pxm = ProxyManager(self._helper.factory)
        ui_resolver = VuetifyResolver()
        self._ui_manager = UIManager(self._pxm, ui_resolver)
        self._pdm = ProxyDomainManager()
        self._pxm.add_life_cycle_listener(self._pdm)

        # Connect to helper
        self._helper.set_simput(self._pxm, self._ui_manager)
        self._pxm.on(self.on_pxm_event)

        # Controller binding
        ctrl.on_data_change.add(self.on_active_change)
        ctrl.on_delete = self.on_proxy_delete

        # TMP - fake models
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

    def on_pxm_event(self, topic, **kwrags):
        if topic == "commit":
            ctrl.on_data_change()  # Trigger render

    def on_active_change(self, **kwargs):
        source = simple.GetActiveSource()
        view = simple.GetActiveView()
        representation = None
        if source is not None:
            representation = simple.GetRepresentation(proxy=source, view=view)
            state.active_proxy_source_id = source.GetGlobalIDAsString()
            state.active_proxy_representation_id = representation.GetGlobalIDAsString()

        state.source_id = self._helper.handle_proxy(source)
        state.representation_id = self._helper.handle_proxy(representation)

    def on_proxy_delete(self, pv_id):
        self._helper.delete_entry(pv_id)


# -----------------------------------------------------------------------------
# Life cycle listener
# -----------------------------------------------------------------------------

ctrl.on_active_proxy_change.add(ParaviewProxyManager().on_active_change)

# -----------------------------------------------------------------------------

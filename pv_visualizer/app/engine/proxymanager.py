import os

from trame import state

from .singleton import Singleton

from simput.core import ProxyManager, UIManager, ProxyDomainManager
from simput.ui.web import VuetifyResolver
from simput.domains import register_domains
from simput.values import register_values

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Simput registrations
register_domains()
register_values()


@Singleton
class ParaviewProxyManager:
    def __init__(self):
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

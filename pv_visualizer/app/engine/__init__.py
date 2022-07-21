r"""
Define your classes and create the instances that you need to expose
"""
import logging
from .reactions import register_reactions
from .proxymanager import ParaviewProxyManager
from paraview import simple

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ---------------------------------------------------------
# Methods
# ---------------------------------------------------------


def initialize(server, plugins=None):
    pxm = ParaviewProxyManager()
    pxm.set_server(server)

    if plugins:
        logger.info("\nLoading ParaView plugins:")
        for plugin in plugins:
            logger.info(f"  - {plugin}")
            simple.LoadDistributedPlugin(plugin)

    # Bind methods to controller + trigger name
    register_reactions(server)

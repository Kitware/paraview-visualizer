r"""
Define your classes and create the instances that you need to expose
"""
from .reactions import register_reactions
from .proxymanager import ParaviewProxyManager
from paraview import simple

# ---------------------------------------------------------
# Methods
# ---------------------------------------------------------


def initialize(server):
    args, _ = server.cli.parse_known_args()
    #
    pxm = ParaviewProxyManager()
    pxm.set_server(server)

    plugins = args.plugins.split(",") if args.plugins else []
    if plugins:
        print("\nLoading ParaView plugins:")
        for plugin in plugins:
            print(f"  - {plugin}")
            simple.LoadDistributedPlugin(plugin)
        print()

    # Bind methods to controller + trigger name
    register_reactions(server)

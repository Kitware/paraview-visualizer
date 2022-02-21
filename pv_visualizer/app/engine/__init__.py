r"""
Define your classes and create the instances that you need to expose
"""
from ..cli import get_args

try:
    from paraview import simple
except:
    simple = None

# ---------------------------------------------------------
# Methods
# ---------------------------------------------------------


def initialize():
    args = get_args()
    plugins = args.plugins.split(",") if args.plugins else []
    if plugins:
        print("\nLoading ParaView plugins:")
        for plugin in plugins:
            print(f"  - {plugin}")
            simple.LoadDistributedPlugin(plugin)
        print()


# ---------------------------------------------------------
# Listeners
# ---------------------------------------------------------

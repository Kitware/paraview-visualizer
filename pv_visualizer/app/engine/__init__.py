r"""
Define your classes and create the instances that you need to expose
"""
from trame import state, controller as ctrl
from ..cli import get_args
from paraview import simple

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


@state.change("my_title")
def title_change(my_title, **kwargs):
    print(f" => title changed to {my_title}")

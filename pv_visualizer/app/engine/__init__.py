r"""
Define your classes and create the instances that you need to expose
"""
from trame import state, controller as ctrl
from paraview import simple

# ---------------------------------------------------------
# Methods
# ---------------------------------------------------------


def initialize():
    pass


# ---------------------------------------------------------
# Listeners
# ---------------------------------------------------------


@state.change("my_title")
def title_change(my_title, **kwargs):
    print(f" => title changed to {my_title}")

from . import camera, scalar_range, representation

from trame import controller as ctrl

# List of all reactions modules
REACTIONS = [
    camera,
    scalar_range,
    representation,
]

# Bind reactions from map
def register_triggers(mapping):
    for key, fn in mapping.items():
        ctrl[key] = fn
        ctrl.trigger(key)(ctrl[key])


def register_reactions():
    for reaction in REACTIONS:
        register_triggers(reaction.TRIGGER_MAPPING)

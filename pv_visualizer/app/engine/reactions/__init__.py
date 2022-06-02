from . import camera, scalar_range, representation

# List of all reactions modules
REACTIONS = [
    camera,
    scalar_range,
    representation,
]


def register_triggers(ctrl, mapping):
    for key, fn in mapping.items():
        ctrl[key] = fn
        ctrl.trigger(key)(ctrl[key])


def register_reactions(server):
    for reaction in REACTIONS:
        reaction.initialize(server, register_triggers)

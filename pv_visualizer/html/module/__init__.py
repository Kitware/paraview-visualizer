from pathlib import Path

# Compute local path to serve
serve_path = str(Path(__file__).with_name("serve").resolve())

# Serve directory for JS/CSS files
serve = {"__pv_visualizer": serve_path}

# List of JS files to load (usually from the serve path above)
scripts = ["__pv_visualizer/vue-pv_visualizer.umd.min.js"]

# List of CSS files to load (usually from the serve path above)
# Uncomment to add styles
# styles = ["__pv_visualizer/vue-pv_visualizer.css"]

# List of Vue plugins to install/load
vue_use = ["pv_visualizer"]

# Uncomment to add vuetify config
vuetify = {
    "icons": {
        "values": {
            "pqEditColor": {"component": "pq-edit-color"},
            "pqEditScalarBar": {"component": "pq-edit-scalar-bar"},
            "pqFavorites": {"component": "pq-favorites"},
            "pqResetRange": {"component": "pq-reset-range"},
            "pqResetRangeCustom": {"component": "pq-reset-range-custom"},
            "pqResetRangeTemporal": {"component": "pq-reset-range-temporal"},
            "pqScalarBar": {"component": "pq-scalar-bar"},
            "pqSeparateColorMap": {"component": "pq-separate-color-map"},
        }
    }
}

# Uncomment to add entries to the shared state
# state = {}

# Optional if you want to execute custom initialization at module load
def setup(app, **kwargs):
    """Method called at initialization with possibly some custom keyword arguments"""
    pass

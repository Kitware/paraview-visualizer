## Running ParaView within Jupyter

### Install packages

```bash
python3.9 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install pv-visualizer
pip install jupyterlab
```

### Run example

```bash
export PYTHONPATH=/Applications/ParaView-5.10.1.app/Contents/Python
export DYLD_LIBRARY_PATH=/Applications/ParaView-5.10.1.app/Contents/Libraries
source .venv/bin/activate
jupyter-lab
```

Then in a cell

```python
from pv_visualizer.app.jupyter import show
show()
```

## Running Jupyter within ParaView

This path is not yet working.
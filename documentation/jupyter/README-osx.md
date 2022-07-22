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

This path is not yet working and would require the following:
- Add OpenSSL in our Python dependencies
- Rework the `sys.executable` path to be valid
- Make pvpython natively aware of some env variable to enable venv at startup so the iKernel could start without issue
- And maybe something else but I haven't been that far...

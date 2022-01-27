import base64
import mimetypes
from pathlib import Path

ASSET_ROOT = Path(__file__).parent.resolve().absolute()

def to_mime(file_path):
    return mimetypes.guess_type(file_path)[0]

def to_path(local_name):
    return Path(f"{ASSET_ROOT}/{local_name}").absolute()

def to_url(file_path):
    with open(file_path, "rb") as bin_file:
        encoded = base64.b64encode(bin_file.read()).decode("ascii")
        mime = to_mime(file_path)
        return f"data:{mime};base64,{encoded}"

PV_LOGO_PATH = to_path("pv_logo.svg")
PV_LOGO_URL = to_url(PV_LOGO_PATH)
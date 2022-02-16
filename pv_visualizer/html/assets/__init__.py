import base64
import mimetypes
from pathlib import Path

mimetypes.init()
BASE_DIR = Path(__file__).parent.absolute().resolve()

FILE_DELETE = str(Path(BASE_DIR, "database-remove-outline.svg"))


def to_mime(file_path):
    return mimetypes.guess_type(file_path)[0]


def read_file_as_base64_url(full_path):
    with open(full_path, "rb") as bin_file:
        encoded = base64.b64encode(bin_file.read()).decode("ascii")
        mime = to_mime(full_path)
        return f"data:{mime};base64,{encoded}"


ICON_URL_DELETE = read_file_as_base64_url(FILE_DELETE)

from trame import get_cli_parser
from pathlib import Path

# Initialize
parser = get_cli_parser()
parser.add_argument(
    "--data", help="Path to browse", dest="data", default=str(Path.home())
)
parser.add_argument(
    "--plugins", help="List of distributed plugins to load", dest="plugins"
)


def get_args():
    parser = get_cli_parser()
    args, _ = parser.parse_known_args()
    return args
